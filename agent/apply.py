# agent/apply.py

from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()

# Candidate information
CANDIDATE_FIRST_NAME = 'Vidyuth'
CANDIDATE_LAST_NAME = 'Ramkumar'
CANDIDATE_EMAIL = 'vidyuth.ramkumar@gmail.com'
CANDIDATE_PHONE_NUMBER = os.getenv('CANDIDATE_PHONE_NUMBER', '4809257843')
RESUME_FILE_PATH = os.getenv('RESUME_FILE_PATH')
LINKEDIN = 'https://www.linkedin.com/in/vidyuth-ramkumar/'

def apply_to_single_job(job):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(job['url'])
        page.wait_for_load_state('networkidle')
        try:
            page.get_by_role("button", name="Apply").click()
            page.get_by_label('First Name').fill(CANDIDATE_FIRST_NAME)
            page.get_by_label('Last Name').fill(CANDIDATE_LAST_NAME)
            page.get_by_label('Email').fill(CANDIDATE_EMAIL)
            # await page.getByLabel('Country').fill('')
            page.get_by_label('Phone').fill(CANDIDATE_PHONE_NUMBER)
            page.get_by_label('Linkedin').fill(LINKEDIN)
            page.get_by_label('Resume/CV').set_input_files(RESUME_FILE_PATH)
            page.get_by_role("button", name="Submit").click()
        except Exception as e:
            print(f"Error filling form for {job['title']} at {job['company']}: \n{e}")

        page.wait_for_load_state('networkidle')





apply_tool_schema = {
  "type": "function",
  "function": {
    "name": "apply_greenhouse_job",
    "description": f"Apply to a specific job on the Greenhouse Job Board with correct profile/resume information on candidate {CANDIDATE_FIRST_NAME} {CANDIDATE_LAST_NAME}.",
    "parameters": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "description": "The title of the Greenhouse job role that you need to apply to"
        },
        "url": {
            "type": "string",
            "description": "The Greenhouse job posting url that you need to access to apply to the job"
        }
      },
      "required": ["title", "url"]
    }
  }
}
