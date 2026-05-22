from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()

phone_number = os.getenv('PHONE_NUMBER')
resume_file_path = os.getenv('RESUME_FILE_PATH')

async def apply_to_single_job(job):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(job['url'])
        await page.get_by_role('button', { 'name': 'Apply' }).click()
        await page.getByLabel('First Name').fill(os.getenv('CANDIDATE_FIRST_NAME'))
        await page.getByLabel('Last Name').fill(os.getenv('CANDIDATE_LAST_NAME'))
        await page.getByLabel('Email').fill(os.getenv('CANDIDATE_EMAIL'))
        # await page.getByLabel('Country').fill('')
        await page.getByLabel('Phone').fill(os.getenv('CANDIDATE_PHONE_NUMBER'))
        await page.getByLabel('Linkedin').fill(os.getenv('CANDIDATE_PHONE_NUMBER'))
        await page.getByLabel('Resume/CV').setInputFiles(resume_file_path)
        await page.get_by_role('button', { 'name': 'Submit' }).click()





apply_tool_schema = {
  "type": "function",
  "function": {
    "name": "apply_greenhouse_job",
    "description": "Apply to a specific job on the Greenhouse Job Board with correct profile/resume information on candidate Vidyuth Ramkumar.",
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
      "required": ["expression"]
    }
  }
}
