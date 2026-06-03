# agent/apply.py
import time

from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()

# Candidate information
CANDIDATE_FIRST_NAME = "Vidyuth"
CANDIDATE_LAST_NAME = "Ramkumar"
CANDIDATE_EMAIL = "vidyuth.ramkumar@gmail.com"
CANDIDATE_PHONE_NUMBER = os.getenv("CANDIDATE_PHONE_NUMBER")
CANDIDATE_RESUME_FILE_PATH = os.getenv("RESUME_FILE_PATH")
CANDIDATE_LINKEDIN = "https://www.linkedin.com/in/vidyuth-ramkumar/"

POSSIBLE_FORM_FIELDS = {
    "first_name": ["First Name", "first_name", "firstName"],
    "last_name": ["Last Name", "last_name", "lastName"],
    "email": ["Email", "email", "Email Address"],
    "phone": ["Phone", "Phone*", "phone", "Phone Number", "Mobile"],
    "city": [
        "City",
        "city",
    ],
    "state": [
        "State",
        "state",
    ],
    "country": ["Country", "Country*", "country", "Country Code"],
    "linkedin": [
        "LinkedIn",
        "Linkedin",
        "LinkedIn Profile",
        "Linkedin Profile",
        "LinkedIn URL",
        "Linkedin URL",
    ],
    "resume": ["Resume/CV", "Resume/CV*", "Resume", "CV", "Upload Resume"],
    "authorized_to_work": [],
}

FIELD_KEYS_TO_ENTRIES = {
    "first_name": CANDIDATE_FIRST_NAME,
    "last_name": CANDIDATE_LAST_NAME,
    "email": CANDIDATE_EMAIL,
    "phone": CANDIDATE_PHONE_NUMBER,
    "linkedin": CANDIDATE_LINKEDIN,
    "resume": CANDIDATE_RESUME_FILE_PATH,
    "city": [
        "Phoenix, Arizona, United States",
        "Phoenix, Arizona",
        "Phoenix, AZ",
        "Phoenix",
    ],
    "country": [
        "United States of America",
        "United States",
        "USA",
        "US",
        "U.S.A.",
        "U.S.",
        "America",
        "+1",
        "1",
        "US (+1)",
        "USA (+1)",
        "United States (+1)",
        "United States of America (+1)",
        "+1 (United States)",
        "+1 (USA)",
        "+1 (US)",
        "1 (United States)",
        "1 (USA)",
        "1 (US)",
        "United States +1",
        "USA +1",
        "US +1",
    ],
    "state": "AZ",
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


# Tries all the possible field names
# Country code dropdown HTML element is accessed by its id
def fill_field(page, field_key):
    if field_key == "resume":
        try:
            page.locator("#resume").set_input_files(
                CANDIDATE_RESUME_FILE_PATH, timeout=3000
            )
            print(f"✓ Filled resume")
        except Exception as e:
            print(f"✗ Could not find field: resume")
        time.sleep(1)
        return
    elif field_key == "country":
        try:
            page.locator("#country").click(timeout=3000)
            page.keyboard.type("United States")
            page.get_by_text("United States +1", exact=True).first.click(timeout=3000)
            print("✓ Filled country")
        except Exception as e:
            print("Error filling country", e)
        return
    else:
        for possible_field_name in POSSIBLE_FORM_FIELDS[field_key]:
            try:
                locator = page.get_by_label(possible_field_name)

                if locator.is_visible(timeout=2000):
                    if field_key == "city":
                        try_select_or_fill(locator, FIELD_KEYS_TO_ENTRIES["city"])
                    else:
                        locator.fill(FIELD_KEYS_TO_ENTRIES[field_key])
                    print(f"✓ Filled {field_key}")
                    break
            except Exception as e:
                pass
        else:
            print(f"✗ Could not find field: {field_key}")


def better_fill_field(
    browser_page, field_locator, field_tag_name, field_id, field_aria
):
    for possible_field in POSSIBLE_FORM_FIELDS:
        if (
            field_id in POSSIBLE_FORM_FIELDS[possible_field]
            or field_aria in POSSIBLE_FORM_FIELDS[possible_field]
        ):  # Found it in any of the possible fields' list of field name variations
            if possible_field == "resume":
                print(
                    f"Interacting with RESUME field. field_id: {field_id}, possible_field field variation map: {possible_field}"
                )
                try:
                    browser_page.locator("#resume").set_input_files(
                        CANDIDATE_RESUME_FILE_PATH, timeout=3000
                    )
                    print(f"✓ Filled resume")
                except Exception as e:
                    print(f"❌ Could not fill RESUME field; exception {e}")
                time.sleep(1)
                return True
            elif possible_field == "country":
                try:
                    print(
                        f"Interacting with COUNTRY field. field_id: {field_id}, possible_field from field variation map: {possible_field}"
                    )
                    browser_page.locator("#country").click(
                        timeout=3000
                    )  # Click open the search dropdown
                    browser_page.keyboard.type(
                        "United States"
                    )  # Type into it to search
                    browser_page.get_by_text(
                        "United States +1", exact=True
                    ).first.click(
                        timeout=3000
                    )  # click the correct one by exact text
                    print("✓ Filled country")
                except Exception as e:
                    print(f"❌ Could not fill COUNTRY field; exception {e}")
                return True
            else:
                try:
                    print(
                        f"Interacting with field_id: {field_id}; possible_field field variation map: {possible_field}"
                    )
                    field_locator.fill(FIELD_KEYS_TO_ENTRIES[possible_field])
                    print(f"✓ Filled {possible_field}")
                    return True
                except Exception as e:
                    print(
                        f"❌ Could not fill {possible_field.upper()} field; exception {e}"
                    )
    return False


def apply_to_single_job(job):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        browser_page = browser.new_page()
        browser_page.goto(job["url"])
        browser_page.wait_for_load_state("networkidle")

        fields_locator_filter = browser_page.locator(
            "form input:not([type='submit']):not([type='button']), form select, form textarea"
        )
        existing_job_field_locators = fields_locator_filter.all()
        known_fields, unknown_fields = [], []
        # existing_field_statuses = {"In Known Fields": False, "Filled": False}
        for ejf_locator in existing_job_field_locators:
            field_tag_name = ejf_locator.evaluate(
                "element => element.tagName.toLowerCase()"
            )
            field_id = ejf_locator.get_attribute("id") or "Unnamed Field"
            field_aria = ejf_locator.get_attribute("aria-label") or None
            if field_tag_name == "textarea":
                was_filled = better_fill_field(
                    browser_page, ejf_locator, field_tag_name, field_id, field_aria
                )
                if was_filled:
                    known_fields.append(field_id)
                else:
                    unknown_fields.append(
                        {
                            "Field ID": field_id,
                        }
                    )
            if field_tag_name == "input":
                input_type = ejf_locator.get_attribute("type") or "text"
                input_type = input_type.lower()
                if input_type in ["text", "file", "email", "password", "tel", "number"]:
                    was_filled = better_fill_field(
                        browser_page, ejf_locator, field_tag_name, field_id, field_aria
                    )
                    if was_filled:
                        known_fields.append(field_id)
                    else:
                        unknown_fields.append(field_id)
                # elif input_type in ["checkbox", "radio"]:
                #     ejf_locator.check()
            ejf_json = {
                "field_id": ejf_locator.get_attribute("id") or "Unnamed Field",
                "field_type": ejf_locator.get_attribute("type") or "textarea/select",
                "field_aria ": ejf_locator.get_attribute("aria-label")
                or ejf_locator.get_attribute("aria-labelledby")
                or "No Aria",
            }
            print(ejf_json)
        # try:
        #     for possible_field in POSSIBLE_FORM_FIELDS:
        #         fill_field(browser_page, possible_field)

        #     browser_page.get_by_role("button", name="Submit application").click(timeout=2000)
        #     browser_page.wait_for_load_state("networkidle")
        # except Exception as e:
        #     print(f"Error filling form for {job['title']} at {job['company']}: \n{e}")

        if "confirmation" in browser_page.url:
            print("SUCCESSFULLY SUBMITTED APPLICATION 🎉 🎊 🕺")
        print(f"known fields: ", known_fields)
        print(f"unknown fields: ", unknown_fields)
        print(f"Final URL: {browser_page.url}")
        input("Press Enter to close browser...")
        browser_page.wait_for_load_state("networkidle")


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
                    "description": "The title of the Greenhouse job role that you need to apply to",
                },
                "url": {
                    "type": "string",
                    "description": "The Greenhouse job posting url that you need to access to apply to the job",
                },
            },
            "required": ["title", "url"],
        },
    },
}

if __name__ == "__main__":
    test_job = {
        "title": "Software Engineer",
        "company": "CrunchyRoll",
        "url": "https://job-boards.greenhouse.io/crunchyroll/jobs/6696781",
    }
    apply_to_single_job(test_job)
