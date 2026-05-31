# agent/apply.py

from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()

# Candidate information
CANDIDATE_FIRST_NAME = 'Vidyuth'
CANDIDATE_LAST_NAME = 'Ramkumar'
CANDIDATE_EMAIL = 'vidyuth.ramkumar@gmail.com'
CANDIDATE_PHONE_NUMBER = os.getenv('CANDIDATE_PHONE_NUMBER')
CANDIDATE_RESUME_FILE_PATH = os.getenv('RESUME_FILE_PATH')
CANDIDATE_LINKEDIN = 'https://www.linkedin.com/in/vidyuth-ramkumar/'

POSSIBLE_FORM_FIELDS = {
    'first_name': ['First Name', 'first_name', 'firstName'],
    'last_name': ['Last Name', 'last_name', 'lastName'],
    'email': ['Email', 'email', 'Email Address'],
    'phone': ['Phone', 'phone', 'Phone Number', 'Mobile'],
    'city': ['City', 'city',],
    'state': ['State', 'state',],
    'country': ['Country', 'country', 'Country Code'],
    'linkedin': ['LinkedIn', 'Linkedin', 'LinkedIn Profile', 'LinkedIn URL'],
    'resume': ['Resume/CV', 'Resume', 'CV', 'Upload Resume'],
}

FIELD_KEYS_TO_ENTRIES = {
    'first_name': CANDIDATE_FIRST_NAME,
    'last_name': CANDIDATE_LAST_NAME,
    'email': CANDIDATE_EMAIL,
    'phone': CANDIDATE_PHONE_NUMBER,
    'linkedin': CANDIDATE_LINKEDIN,
    'resume': CANDIDATE_RESUME_FILE_PATH,
    'city': ['Phoenix, Arizona, United States', 'Phoenix, Arizona', 'Phoenix, AZ', 'Phoenix'],
    'country': [
      'United States of America', 'United States', 'USA', 'US', 'U.S.A.', 'U.S.', 'America',
      '+1', '1', 'US (+1)', 'USA (+1)', 'United States (+1)', 'United States of America (+1)',
      '+1 (United States)', '+1 (USA)', '+1 (US)', '1 (United States)', '1 (USA)', '1 (US)',
      'United States +1', 'USA +1', 'US +1'],
    'state': 'AZ',
}

def try_select_or_fill(locator, values):
    for value in values:
        try:
            locator.select_option(label=value)
            return True
        except:
            try:
                locator.select_option(value=value)
                return True
            except:
                try:
                    locator.fill(value)
                    return True
                except:
                    pass
    return False


def fill_field(page, field_key):
    # role_type = element.get_attribute("role") or element.get_attribute("type")

    
    for possible_field_name in POSSIBLE_FORM_FIELDS[field_key]:
        try:  
          locator = page.get_by_label(possible_field_name)
              
          if locator.is_visible(timeout=2000):
            if field_key == 'resume':
              locator.set_input_files(CANDIDATE_RESUME_FILE_PATH)
            elif field_key == 'country':
              try_select_or_fill(locator, FIELD_KEYS_TO_ENTRIES['country'])
            elif field_key == 'city':
                try_select_or_fill(locator, FIELD_KEYS_TO_ENTRIES['city'])
            else:
              locator.fill(FIELD_KEYS_TO_ENTRIES[field_key])
            break
        except Exception as e:
            pass

def apply_to_single_job(job):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        browser_page = browser.new_page()
        browser_page.goto(job['url'])
        browser_page.wait_for_load_state('networkidle')
        try:
            for possible_field in POSSIBLE_FORM_FIELDS:
               fill_field(browser_page, possible_field)
            browser_page.get_by_role("button", name="Apply").click()
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
