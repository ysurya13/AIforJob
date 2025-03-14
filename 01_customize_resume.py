#!/usr/bin/env python
# coding: utf-8

# In[1]:


from openai import OpenAI
import os
import asyncio
from pyppeteer import launch
import nest_asyncio
from pypdf import PdfReader
import pandas as pd
import glob


# In[2]:


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


# In[3]:


# read job description txt file for now
def read_job_description():
    path = os.path.join(os.getcwd(), "source_job_desc", "job_data.txt")
    with open(path, "r") as file:
        return file.read()


# In[4]:


def model_selection(model):
    if model == "openai":
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        ai_model = "gpt-4o-mini"
    elif model == "deepseek":
        client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
        ai_model = "deepseek-chat"
    else:
        raise Exception("Invalid model")
    return client, ai_model


# In[37]:


# find keywords in job description
def find_keywords(client, ai_model):

    response = client.chat.completions.create(
        #model="deepseek-chat",
        model=ai_model,
        messages=[
            {"role": "system", "content": "You are a expert in recruitment."},
            {"role": "user", "content": f"Job Description: {read_job_description()}"},
            {"role": "user", "content": "Find the company_name, job_title, and relevant_skills in the job description. Do not rephrase!"},
            #{"role": "user", "content": "Output format: Company; [company name], Job Title: [job title], Skills: [skills]"},
            {"role": "user", "content": "Only output 3 parameters: company_name, job_title, relevant_skills. Output in csv format!"}
            ],
        stream=False
    )

    return response.choices[0].message.content


# In[6]:


def save_job_description():
    job_description = input("Please enter the job description: ")
    path = os.path.join(os.getcwd(), "source_job_desc", "job_data.txt")
    with open(path, "w") as file:
        file.write(job_description)
    print("Job description saved successfully.")


# In[54]:


# Headline
def find_headline(client, ai_model, job_title, relevent_skills):
    #client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model=ai_model,
        messages=[
            {"role": "system", "content": "You are a expert in ATS friendly resume writing."},
            #{"role": "user", "content": "Based on job description and my resume below:"},
            {"role": "user", "content": f"Current resume: {read_current_resume()}"},
            {"role": "user", "content": f"Relevant skills: {relevent_skills}"},
            {"role": "user", "content": f"Job Title: {job_title}"},
            {"role": "user", "content": """Make only the headline section. Use these formats:
            Results-Oriented Business Analyst with 7 Years of Experience, Finance Manager with 10 Years of Experience in the Banking Industry,
            Human Resources Professional with 5 Years of Experience in Recruitment and Employee Relations"""},
            {"role": "user", "content": "Use the exact same job title and skills you found in the job description."},
            {"role": "user", "content": "Do not include your explanation in the output."},
            ],
        stream=False
    )

    headline = response.choices[0].message.content
    return headline


# In[9]:


# Work Experience
def work_experience(client, ai_model, jobdesc):

    response = client.chat.completions.create(
        model=ai_model,
        messages=[
            {"role": "system", "content": "You are a expert in ATS friendly resume writing."},
            {"role": "user", "content": "Based on job description and my resume below:"},
            {"role": "user", "content": f"Current resume: {read_current_resume()}"},
            {"role": "user", "content": f"Job Description: {jobdesc}"},
            {"role": "user", "content": "Modify the work experience section of my resume to include all the relevant skills and experience from the job description."},
            {"role": "user", "content": "Change the job title to match the job description."},
            {"role": "user", "content": "Format: Job Title - Company Name - Location - Start Date to End Date in one line followed by a bullet point list of responsibilities and achievements."},
            {"role": "user", "content": "Do not include your explanation and section title in the output. Only include the modified work experience section."},
            ],
        stream=False
    )

    work_experience = response.choices[0].message.content
    return work_experience


# In[10]:


# Skills section
def skills_section(client, ai_model, jobdesc):
    response = client.chat.completions.create(
        model=ai_model,
        messages=[
            {"role": "system", "content": "You are a expert in ATS friendly resume writing."},
            {"role": "user", "content": "Based on job description and my resume below:"},
            {"role": "user", "content": f"Current resume: {read_current_resume()}"},
            {"role": "user", "content": f"Job Description: {jobdesc}"},
            {"role": "user", "content": "Provide the skills from the job description that you have and are relevant to the job."},
            {"role": "user", "content": "Add the skills that are not in my resume but relevant to the job. Group them into categories like Technical Skills, Soft Skills, etc."},
            {"role": "user", "content": "Format: [Category Name]: [Skill 1], [Skill 2], [Skill 3]"},
            {"role": "user", "content": "Do not include your explanation and section title in the output. "},
            ],
        stream=False
    )

    skills = response.choices[0].message.content
    return skills


# In[11]:


def ats_resume(headline, contact_info, education, work, skills, client, ai_model):
    #client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model=ai_model,
        messages=[
            {"role": "system", "content": "You are a expert in ATS friendly resume writing."},
            {"role": "user", "content": "Make ATS friendly resume based on information below."},
            {"role": "user", "content": f"Headline: {headline}, put it under the name without any section title."},
            {"role": "user", "content": f"Contact Information: {contact_info}"},
            {"role": "user", "content": f"Education: {education}."},
            {"role": "user", "content": f"Work Experience: {work}"},
            {"role": "user", "content": f"Skills: {skills}"},
            {"role": "user", "content": "Do not include your explanation in the output."},
            ],
        stream=False
    )

    print(response.choices[0].message.content)
    resume = response.choices[0].message.content
    return resume


# In[12]:


# format the result to html
def resume_to_html(resume, html_format, client, ai_model):
    #client

    response = client.chat.completions.create(
        model=ai_model,
        messages=[
            {"role": "system", "content": "You are a expert in html language."},
            {"role": "user", "content": "Format the resume to html format"},
            {"role": "user", "content": f"Resume: {resume}"},
            {"role": "user", "content": f"Guidelines: {html_format}"},
            {"role": "user", "content": "Do not include your explanation in the output."},
            ],
        stream=False
    )

    html_file = response.choices[0].message.content
    clean_html = html_file.replace("```html", "")
    clean_html = clean_html.replace("```", "")
    return clean_html


# In[58]:


def html_to_pdf(clean_html, name):

    nest_asyncio.apply()
    pdf_path = os.path.join(os.getcwd(), "results", "resume", f"{name}_Resume.pdf")

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


# In[ ]:


def add_jobdesc_data():
    # get jobs description from user
    save_job_description()

    # analyze the job description
    client, ai_model = model_selection("openai")
    res = find_keywords(client, ai_model)

    # Split the res string into lines
    lines = res.split('\n')
    col_name = lines[1].split(',')
    content = [lines[2].split(',')[0], lines[2].split(',')[1], str(lines[2].split(',')[2:])]
    newcontent = pd.DataFrame([content], columns=col_name)

    job_desc_data = pd.read_csv('job_description.csv')
    # append the new content to the existing job description data
    job_desc_data = pd.concat([job_desc_data, newcontent], ignore_index=True)
    #job_desc_data.replace('"', '', regex=True, inplace=True)
    job_desc_data.to_csv('job_description.csv', index=False)

    print("Job description data added successfully.")
    


# In[ ]:


def custom_resume(company_name, job_title, relevant_skills, llm_model='deepseek'):
    
    
    client, ai_model = model_selection(llm_model)
    # jobdesc = find_keywords(client, ai_model)
    headline = find_headline(client, ai_model, job_title, relevant_skills)
    work = work_experience(client, ai_model, relevant_skills)
    skills = skills_section(client, ai_model, relevant_skills)

    # Contact information
    contact_info = """ 
    Name: Yusuf Surya
    Phone: +1 412 579 2443
    Email: ysurya@andrew.cmu.edu
    LinkedIn: linkedin.com/in/yusuf-pradana""" 

    # Education
    education = """
    Carnegie Mellon University, Heinz College - Master of Public Policy and Management – Data Analytics (Expected 05/2025)
    Bandung Institute of Technology - Bachelor of Engineering (07/2017)
    """

    html_format = """
    Guidelines:
    Center the name, headline, and contact information.
    Add separator between sections.
    Use a 12px font size for the name and headline.
    Use a 10px font size for the contact information.
    Use Arial font family.
    Use 1.5 line spacing.
    Use a 20px margin between sections.
    Use a 10px margin between the name and headline.

    Use Semantic HTML

    Wrap the resume in <section> and <div> tags.
    Use <h1> for the candidate’s name, <h2> for section titles, and <p> or <ul> for content.

    Set body { margin: 0; padding: 20px; }.
    Use page-break-before: always; where necessary to manage page flow.
    Set max-width: 800px; to keep content properly aligned.
    """

    resume = ats_resume(headline, contact_info, education, work, skills, client, ai_model)
    html_file = resume_to_html(resume, html_format, client, ai_model)
    html_to_pdf(html_file, name=company_name)


# In[46]:


add_jobdesc_data()


# In[ ]:


jobs = pd.read_csv('job_description.csv')
company_name = jobs['company_name'].iloc[-1]
job_title = jobs['job_title'].iloc[-1]
relevant_skills = jobs['relevant_skills'].iloc[-1]


# In[48]:


jobs


# In[50]:


company_name = jobs['company_name'].iloc[-1]
job_title = jobs['job_title'].iloc[-1]
relevant_skills = jobs['relevant_skills'].iloc[-1]


# In[59]:


custom_resume(company_name, job_title, relevant_skills, llm_model='deepseek')

