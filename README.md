# AIforJob
Using llm to customize resume and cover letter for job search.


## How this works
* 00_setting_env.ipynb will create folder necessary for the program to run.
* 01_customize_resume.ipynb will read the user's current resume placed in *source_resume*. User should copy the job description they want to apply to. Then the user will extract data such as company name, job title, and relevant skills. Those information is required to revamp the resume. After this step, the codes will prompt the llm (deepseek and openai) to revamp each section to match the relevant skills. Then the code will output pdf file of the revamped resume.
* 02_customize_cover_letter.ipynb similar flow as the previous code.
* 03_upload_to_gsheet.ipynb will upload the dataset of the job that is created as the job that interest the user, it will be saved in cloud google sheet that can be accessed and monitored anytime the user want.

