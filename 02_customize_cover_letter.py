#!/usr/bin/env python
# coding: utf-8

# In[81]:


from openai import OpenAI
import os
import asyncio
from pyppeteer import launch
import nest_asyncio
from pypdf import PdfReader
from datetime import datetime
import pandas as pd
import glob
import logging

# Set the logging level to ERROR
logging.getLogger('pypdf').setLevel(logging.ERROR)


# read current resume
def read_current_resume():
    # get pdf file in source_resume folder
    pdf_files = glob.glob("./source_resume/*.pdf")
    if not pdf_files:
        raise FileNotFoundError("No PDF files found in the source_resume folder.")
    pdf_file = pdf_files[0]
    reader = PdfReader(pdf_file)
    number_of_pages = len(reader.pages)
    texts = ""
    for page_number in range(number_of_pages):
        page = reader.pages[page_number]
        text = page.extract_text()
        texts = texts + f"Page {page_number + 1}:\n{text}\n---"
    return texts


# In[83]:


# read job description txt file for now
def job_description():
    job_desc = pd.read_csv("job_description.csv")
    company_name = job_desc.iloc[-1].company_name
    job_title = job_desc.iloc[-1].job_title
    relevant_skills = job_desc.iloc[-1].relevant_skills
    job_desc = f"Company Name: {company_name}\nJob Title: {job_title}\nJob Description: {relevant_skills}"
    return company_name, job_title, job_desc


# In[84]:


def model_selection(model):
    if model == "openai":
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        ai_model = "gpt-4o"
    elif model == "deepseek":
        client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
        ai_model = "deepseek-chat"
    else:
        raise Exception("Invalid model")
    return client, ai_model


# In[85]:


# read cover letter draft
def read_cover_letter_draft():
    pdf_files = glob.glob("./source_cover_letter/*.pdf")
    if not pdf_files:
        raise FileNotFoundError("No PDF files found in the source_resume folder.")
    pdf_file = pdf_files[0]
    reader = PdfReader(pdf_file)
    number_of_pages = len(reader.pages)
    texts = ""
    for page_number in range(number_of_pages):
        page = reader.pages[page_number]
        text = page.extract_text()
        texts = texts + f"Page {page_number + 1}:\n{text}\n---"
    return texts


# In[86]:


# Work Experience
def cover_letter_txt(client, ai_model, jobdesc, resume, about_me, address):
    today_date = datetime.today().strftime('%B %d, %Y')
    response = client.chat.completions.create(
        model=ai_model,
        messages=[
            {"role": "system", "content": "You are human expert in cover letter writing. Use simple language and write like you mean it."},
            {"role": "user", "content": f"Job decsription: {jobdesc}"},
            {"role": "user", "content": f"Resume: {resume}"},
            {"role": "user", "content": f"About me: {about_me}"},
            {"role": "user", "content": f"Today's date: {today_date}. My address: {address}"},
            {"role": "user", "content": "Use my personal information. Do not leave any place holder remain empty!"},
            {"role": "user", "content": "Make the opening more engaging, arrange story with high specificity in skills, stronger call to action. Only response with the cover letter no need explanation."},
            ],
        stream=False
    )

    cl = response.choices[0].message.content
    return cl


# In[87]:


# Cover letter to html
def cover_letter_html(client, ai_model, cover_letter, html_format):
    
    response = client.chat.completions.create(
        model=ai_model,
        messages=[
            {"role": "system", "content": "You are a expert in html language."},
            {"role": "user", "content": "Format the cover letter to html format."},
            {"role": "user", "content": f"Cover Letter: {cover_letter}"},
            {"role": "user", "content": f"Guidelines: {html_format}"},
            {"role": "user", "content": "Make sure the html is formatted correctly and 1 letter page long."},
            {"role": "user", "content": "Font size should be max 12px and font family should be Arial."},
            {"role": "user", "content": "Do not include your explanation in the output."},
            ],
        stream=False
    )

    html_file = response.choices[0].message.content
    clean_html = html_file.replace("```html", "")
    clean_html = clean_html.replace("```", "")
    return clean_html


# In[88]:


def html_to_pdf(clean_html, name):

    nest_asyncio.apply()
    
    pdf_path = os.path.join(os.getcwd(), 'results', 'cover_letter', f"{name}_Cover_Letter.pdf")

    async def generate_pdf_from_html(html_content, pdf_path):
        browser = await launch()
        page = await browser.newPage()
        
        await page.setContent(html_content)
        
        await page.pdf({
            'path': pdf_path,
            'format': 'A4',
            'margin': {
                'top': '0.5in',
                'right': '0.5in',
                'bottom': '0.5in',
                'left': '0.5in'
            },
            'printBackground': True
        })
        
        await browser.close()

    # HTML content
    html_content = clean_html

    # Run the function
    asyncio.get_event_loop().run_until_complete(generate_pdf_from_html(html_content, pdf_path))



def customize_cover_letter():
    client, ai_model = model_selection("openai")
    jobdesc = job_description()[2]
    resume = read_current_resume()
    about_me = read_cover_letter_draft()
    cover_letter = cover_letter_txt(client, ai_model, jobdesc, resume, about_me, address)
    print("Cover Letter Drafted")
    return cover_letter


# In[91]:


def cl_to_pdf():
    company_name = job_description()[0]
    job_title = job_description()[1]
    client, ai_model = model_selection("deepseek")
    html_cover_letter = cover_letter_html(client, ai_model, customize_cover_letter(), html_format)
    html_to_pdf(html_cover_letter, f"{company_name}_{job_title}")
    print("Cover Letter PDF Generated")


if __name__ == "__main__":
    address = "208 N Homewood Ave, Pittsburgh, PA 15208"
    html_format = """
        Guidelines:
        Use Semantic HTML

        Wrap the cover letter in <section> and <div> tags.
        Use <h3> for the candidate’s name, <h3> for section titles, and <p> or <ul> for content.

        Ensure PDF-Friendly Styling

        Set body { margin: 0; padding: 20px; } to prevent extra margins when rendering PDFs.
        Use page-break-before: always; where necessary to manage page flow.
        Set max-width: 800px; to keep content properly aligned.
    """
    cl_to_pdf()

