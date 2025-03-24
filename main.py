import subprocess
import time

if __name__ == "__main__":

    # list of script to run
    scripts = ["00_setting_env.py", "01_customize_resume.py", "02_customize_cover_letter.py",
            "03_upload_to_gsheet.py"]  # List your scripts here

    # Run each script
    for script in scripts:
        start = time.time()  # Start time for each script
        print(f"\nRunning {script}...")
        subprocess.run(["python", script])  # Runs each script
        print(f"Finished {script}.\n")
        end = time.time()
        elapsed_time = end - start
        print(f"Elapsed time for {script}: {elapsed_time:.2f} seconds\n")

