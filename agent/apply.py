# agent/apply.py
import time
import os
from playwright.sync_api import sync_playwright

from groq import Groq
from dotenv import load_dotenv
from config.candidate import (
    CANDIDATE_FIRST_NAME,
    CANDIDATE_LAST_NAME,
    CANDIDATE_EMAIL,
    CANDIDATE_PHONE_NUMBER,
    CANDIDATE_RESUME_FILE_PATH,
    CANDIDATE_LINKEDIN,
    get_candidate_info_for_llm,
)

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


POSSIBLE_FORM_FIELDS = {
    "first_name": ["First Name", "first_name", "firstName"],
    "last_name": ["Last Name", "last_name", "lastName"],
    "email": ["Email", "email", "Email Address"],
    "phone": ["Phone", "Phone*", "phone", "Phone Number", "Mobile"],
    "city": [
        "City",
        "city",
        "Location (City)*",
        "Location (City)",
        "Location*",
        "Location",
        "location*",
        "location",
        "Candidate-location",
        "candidate-location",
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
        "LinkedIn URL",
        "Linkedin URL",
    ],
    "resume": ["Resume/CV", "Resume/CV*", "Resume", "CV", "Upload Resume", "resume"],
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


def better_fill_field(browser_page, field_locator, field_id, field_aria):
    for possible_field in POSSIBLE_FORM_FIELDS:
        if (
            field_id in POSSIBLE_FORM_FIELDS[possible_field]
            or field_aria in POSSIBLE_FORM_FIELDS[possible_field]
        ):  # Found it in any of the possible fields' list of field name variations
            print("Found field in PFFs using bff func, field:", field_id)
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
            elif possible_field == "city":
                try:
                    print(
                        f"Interacting with CITY field. field_id: {field_id}, possible_field from field variation map: {possible_field}"
                    )
                    browser_page.locator("#candidate-location").click(
                        timeout=3000
                    )  # Click open the search dropdown
                    browser_page.keyboard.type(
                        "Phoenix, Arizona, United States"
                    )  # Type into it to search
                    browser_page.get_by_text(
                        "Phoenix, Arizona, United States", exact=True
                    ).first.click(
                        timeout=3000
                    )  # click the correct one by exact text
                    print("✓ Filled city")
                except Exception as e:
                    print(f"❌ Could not fill CITY field; exception {e}")
            else:
                try:
                    print(
                        f"Interacting with field_id: {field_id}; possible_field: {possible_field}"
                    )
                    value = FIELD_KEYS_TO_ENTRIES[possible_field]
                    if isinstance(value, list):
                        try_select_or_fill(field_locator, value)
                    else:
                        field_locator.fill(value)
                    print(f"✓ Filled {possible_field}")
                    return True
                except Exception as e:
                    print(
                        f"❌ Could not fill {possible_field.upper()} field; exception {e}"
                    )
    return False


def autofill_misc_unknown_questions(questions):
    for q in questions:
        if q["Field Aria"]:
            if (
                "non-compete" in q["Field Aria"]
                or "non-competetition" in q["Field Aria"]
            ) and "*" in q["Field Aria"]:
                q["Response"] = "No"
            if (
                "require any immigration support" in q["Field Aria"]
                and "*" in q["Field Aria"]
            ):
                q["Response"] = "No"
            if "Are you authorized" in q["Field Aria"]:
                q["Response"] = "Yes"

    return questions


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
        unknown_fields = []
        filled_fields = []
        i = 0
        while i < len(existing_job_field_locators):
            ejf_locator = existing_job_field_locators[i]
            DOM_index = ejf_locator.evaluate(
                "el => Array.from(document.querySelectorAll('input, select, textarea')).indexOf(el)"
            )
            if DOM_index in filled_fields:
                i += 1
                continue

            # GETTING LOCATOR DETAILS (HTML TAG, ID, ARIA)
            # Tag name
            try:
                field_tag_name = ejf_locator.evaluate(
                    "element => element.tagName.toLowerCase()"
                )
            except:
                i += 1
                continue

            # ID
            field_id = ejf_locator.get_attribute("id") or "Unnamed Field"
            # ARIA resolution to label text
            field_aria_raw = (
                ejf_locator.get_attribute("aria-label")
                or ejf_locator.get_attribute("aria-labelledby")
                or None
            )
            if field_aria_raw and field_aria_raw.endswith(
                "-label"
            ):  # if it is an ID reference
                field_aria = browser_page.locator(f"#{field_aria_raw}").text_content()
            else:
                field_aria = field_aria_raw
            print(f"Resolved field_aria: {field_aria}")

            print(
                {
                    "ID": field_id,
                    "tag": field_tag_name,
                    "ARIA": field_aria,
                }
            )

            # FILLING THE FIELD
            if field_tag_name == "textarea":
                was_filled = better_fill_field(
                    browser_page, ejf_locator, field_id, field_aria
                )
                if not was_filled:
                    unknown_fields.append(
                        {
                            "Field ID": field_id,
                            "field_type": ejf_locator.get_attribute("type")
                            or "textarea/select",
                            "Field Aria": field_aria,
                            "Field Tag": field_tag_name,
                        }
                    )
                else:  # Successfully filled
                    filled_fields.append(DOM_index)
            if field_tag_name == "input":
                input_type = ejf_locator.get_attribute("type") or "text"
                input_type = input_type.lower()
                if input_type in [
                    "text",
                    "file",
                    "email",
                    "url",
                    "password",
                    "tel",
                    "number",
                ]:
                    was_filled = better_fill_field(
                        browser_page, ejf_locator, field_id, field_aria
                    )
                    if not was_filled:
                        unknown_fields.append(
                            {
                                "Field ID": field_id,
                                "field_type": ejf_locator.get_attribute("type")
                                or "textarea/select",
                                "Field Aria": field_aria,
                                "Field Tag": field_tag_name,
                            }
                        )
                    else:  # Successfully filled
                        filled_fields.append(DOM_index)
                        field_class = ejf_locator.get_attribute("class") or ""
                        if "select__input" in field_class:
                            existing_job_field_locators = fields_locator_filter.all()
                            i = 0
                            continue
                # if input_type in ["checkbox", "radio"]:
                #     ejf_locator.check()
            i += 1
            # END OF WHILE LOOP

        # SUBMIT

        # try:
        #     for possible_field in POSSIBLE_FORM_FIELDS:
        #         fill_field(browser_page, possible_field)

        #     browser_page.get_by_role("button", name="Submit application").click(timeout=2000)
        #     browser_page.wait_for_load_state("networkidle")
        # except Exception as e:
        #     print(f"Error filling form for {job['title']} at {job['company']}: \n{e}")

        # AUTOFILL UNKNOWN

        if unknown_fields:
            unknown_fields = autofill_misc_unknown_questions(unknown_fields)
        print(f"unknown fields: ", unknown_fields)

        if "confirmation" in browser_page.url:
            print("SUCCESSFULLY SUBMITTED APPLICATION 🎉 🎊 🕺")

        print(f"Final URL: {browser_page.url}")
        input("Press Enter to close browser...")
        browser_page.wait_for_load_state("networkidle")


def get_adaptive_responses(questions):
    llm_candidate_context = get_candidate_info_for_llm()
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"",
            },
            {
                "role": "system",
                "content": f"You are filling out a job application form on behalf of Vidyuth Subbiah Ramkumar, a new graduate software/ML engineer. {llm_candidate_context}.\nAdd a Response field to each of the questions with an appropriate response and return only the JSON. For optional questions without an asterisk (*) such as voluntary disclosures, skip them.",
            },
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content


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
    # test_job = {
    #     "title": "Software Engineer",
    #     "company": "CrunchyRoll",
    #     "url": "https://job-boards.greenhouse.io/crunchyroll/jobs/6696781",
    # }
    test_job = {
        "title": "TPM, AI Performance",
        "company": "Figma",
        "url": "https://job-boards.greenhouse.io/figma/jobs/5837760004?gh_jid=5837760004",
    }
    apply_to_single_job(test_job)
