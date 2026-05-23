# agent/apply.py

from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()

phone_number = os.getenv('PHONE_NUMBER')
resume_file_path = os.getenv('RESUME_FILE_PATH')

def apply_to_single_job(job):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(job['url'])
        page.get_by_role("button", name="Apply").click()
        page.get_by_label('First Name').fill(os.getenv('CANDIDATE_FIRST_NAME'))
        page.get_by_label('Last Name').fill(os.getenv('CANDIDATE_LAST_NAME'))
        page.get_by_label('Email').fill(os.getenv('CANDIDATE_EMAIL'))
        # await page.getByLabel('Country').fill('')
        page.get_by_label('Phone').fill(os.getenv('CANDIDATE_PHONE_NUMBER'))
        page.get_by_label('Linkedin').fill(os.getenv('CANDIDATE_PHONE_NUMBER'))
        page.get_by_label('Resume/CV').set_input_files(resume_file_path)
        page.get_by_role("button", name="Submit").click()





apply_tool_schema = {
  "type": "function",
  "function": {
    "name": "apply_greenhouse_job",
    "description": f"Apply to a specific job on the Greenhouse Job Board with correct profile/resume information on candidate {os.getenv('CANDIDATE_FIRST_NAME') + ' ' + os.getenv('CANDIDATE_LAST_NAME')}.",
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
