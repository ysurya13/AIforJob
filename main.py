import subprocess
import time

if __name__ == "__main__":

    # list of script to run
    scripts = ["00_setting_env.py", "01_customize_resume.py", "02_customize_cover_letter.py",
            "03_upload_to_gsheet.py"]  # List your scripts here
    actions = ["adding job description data ...", "customizing resume ...", "customizing cover letter ...", "uploading to Google Sheet ..."]
    # Run each script
    for script, action in zip(scripts,actions):
        start = time.time()  # Start time for each script
        print(f"\n{action}...")
        subprocess.run(["python", script])  # Runs each script
        print(f"Finished {action}.\n")
        end = time.time()
        elapsed_time = end - start
        print(f"Elapsed time for {script}: {elapsed_time:.2f} seconds\n")

