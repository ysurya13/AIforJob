#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
import sys
from openai import OpenAI
import pandas as pd
import time


# In[3]:
def save_job_description():
    print("Enter job description (Press Ctrl+D to save and exit):")

    # Read multiple lines from stdin
    lines = sys.stdin.read()
    path = os.path.join(os.getcwd(), "source_job_desc", "job_data.txt")

    # Save to a text file
    with open(path, "w") as file:
        file.write(lines)

    print("\nJob description saved successfully.")


# read job description txt file for now
def read_job_description():
    path = os.path.join(os.getcwd(), "source_job_desc", "job_data.txt")
    with open(path, "r") as file:
        return file.read()
    
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
    newcontent.columns = ['company_name','job_title','relevant_skills']
    newcontent['Date'] = pd.to_datetime('today').strftime('%Y-%m-%d')

    job_desc_data = pd.read_csv('job_description.csv')
    # append the new content to the existing job description data
    job_desc_data = pd.concat([job_desc_data, newcontent], ignore_index=True)
    #job_desc_data.replace('"', '', regex=True, inplace=True)
    job_desc_data.to_csv('job_description.csv', index=False)

    print("Job description data added successfully.")

# find keywords in job description
def find_keywords(client, ai_model):

    response = client.chat.completions.create(
        #model="deepseek-chat",
        model=ai_model,
        messages=[
            {"role": "system", "content": "You are a expert in recruitment."},
            {"role": "user", "content": f"Job Description: {read_job_description()}"},
            {"role": "user", "content": "Find the company_name, job_title, and relevant_skills in the job description. Do not rephrase!"},
            {"role": "user", "content": "Only output 3 parameters: company_name, job_title, relevant_skills. Output in csv format!"}
            ],
        stream=False
    )

    # refine the response
    response1 = client.chat.completions.create(
        model=ai_model,
        messages=[
            {"role": "system", "content": "You are a expert in recruitment."},
            {"role": "user", "content": f"Job Description: {read_job_description()}"},
            {"role": "user", "content": f"Refine this response: {response.choices[0].message.content}"},
            {"role": "user", "content": "Only output 3 parameters: company_name, job_title, relevant_skills. Output in csv format!"}
            ],
        stream=False
    )

    return response1.choices[0].message.content

def makefolders():
    # make directory to store the test files
    os.makedirs('source_resume', exist_ok=True)
    os.makedirs('source_job_desc', exist_ok=True)
    os.makedirs('source_cover_letter', exist_ok=True)
    os.makedirs('results/resume', exist_ok=True)
    os.makedirs('results/cover_letter', exist_ok=True)
    os.makedirs('no_upload', exist_ok=True)

if __name__ == "__main__":
    # add job description data to csv file
    
    makefolders()

    add_jobdesc_data()

    print("Environment setup completed successfully.")

