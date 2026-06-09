# agent/apply.py
import json
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
                    f"BFF Interacting with RESUME field. field_id: {field_id}, possible_field field variation map: {possible_field}"
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
                return True
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


def extract_field_metadata(ejf_locator, browser_page):
    """
    Extracts metadata from a form field locator.
    Returns: (field_tag_name, field_id, field_aria) or (None, None, None) if error
    """
    try:
        field_tag_name = ejf_locator.evaluate("element => element.tagName.toLowerCase()")
    except:
        return None, None, None

    field_id = ejf_locator.get_attribute("id") or "Unnamed Field"

    # ARIA resolution to label text
    field_aria_raw = (
        ejf_locator.get_attribute("aria-label")
        or ejf_locator.get_attribute("aria-labelledby")
        or None
    )
    if field_aria_raw and field_aria_raw.endswith("-label"):
        field_aria = browser_page.locator(f"#{field_aria_raw}").text_content()
    else:
        field_aria = field_aria_raw

    return field_tag_name, field_id, field_aria


def extract_dropdown_options(browser_page, ejf_locator):
    """
    Attempts to extract dropdown options from a field.
    Returns: list of option strings, or empty list if not a dropdown or extraction fails
    """
    try:
        ejf_locator.click(timeout=2000)
        time.sleep(0.5)  # Wait for dropdown to appear

        options = []
        try:
            option_elements = browser_page.locator(
                "[role='option'], .select-option, li[data-value]"
            ).all()
            for opt in option_elements:
                if opt.is_visible(timeout=500):
                    opt_text = opt.text_content()
                    if opt_text and opt_text.strip():
                        options.append(opt_text.strip())
        except:
            pass

        # Close dropdown
        browser_page.keyboard.press("Escape")
        return options
    except:
        return []


def autofill_misc_unknown_questions(questions, company_name):
    for q in questions:
        if q["Field Aria"]:
            aria_lower = q["Field Aria"].lower()
            company_lower = company_name.lower()

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
            if company_lower in aria_lower and (
                "ever worked for" in aria_lower
                or ("worked for" in aria_lower and "before" in aria_lower)
            ):
                q["Response"] = "No"

    return questions


def process_form_fields(browser_page, fields_locator_filter):
    """
    Processes all form fields, filling known fields and collecting unknown ones.
    Returns: (unknown_fields, filled_fields)
    """
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

        # Extract field metadata
        field_tag_name, field_id, field_aria = extract_field_metadata(
            ejf_locator, browser_page
        )
        if not field_tag_name:
            i += 1
            continue

        print(f"Resolved field_aria: {field_aria}")
        print({"ID": field_id, "tag": field_tag_name, "ARIA": field_aria})

        # Try to fill the field
        was_filled = False
        if field_tag_name in ["textarea", "input"]:
            input_type = ejf_locator.get_attribute("type") or "text"
            input_type = input_type.lower()

            if field_tag_name == "textarea" or input_type in [
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

        if was_filled:
            # Successfully filled - refresh locators to handle DOM changes
            filled_fields.append(DOM_index)
            existing_job_field_locators = fields_locator_filter.all()
            i = 0
            continue
        else:
            # Add to unknown fields
            field_info = {
                "Field ID": field_id,
                "field_type": ejf_locator.get_attribute("type") or "textarea/select",
                "Field Aria": field_aria,
                "Field Tag": field_tag_name,
            }

            # Check if it's a dropdown and extract options
            field_class = ejf_locator.get_attribute("class") or ""
            if "select" in field_class.lower():
                options = extract_dropdown_options(browser_page, ejf_locator)
                if options:
                    field_info["dropdown_options"] = options
                    print(
                        f"  📋 Dropdown options: {options[:3]}..."
                        if len(options) > 3
                        else f"  📋 Dropdown options: {options}"
                    )

            unknown_fields.append(field_info)

        i += 1

    return unknown_fields, filled_fields


def handle_unknown_fields_workflow(browser_page, unknown_fields, company_name):
    """
    Handles the complete workflow for unknown fields:
    1. Autofill common questions
    2. Get LLM responses
    3. Fill fields with responses
    4. Display summary
    """
    if not unknown_fields:
        return

    # First, autofill common questions
    unknown_fields = autofill_misc_unknown_questions(unknown_fields, company_name)
    print(f"\nunknown fields after autofill: {len(unknown_fields)} fields")

    # Then, use LLM to fill remaining fields
    print("\n🤖 Getting LLM responses for unknown fields...")
    unknown_fields = get_adaptive_responses(unknown_fields)

    # Finally, fill the fields with the responses
    print("\n📝 Filling unknown fields with responses...")
    fill_unknown_fields_with_responses(browser_page, unknown_fields)

    # Show final unknown fields status
    print(f"\n📋 Final unknown fields summary:")
    for field in unknown_fields:
        has_response = "✓" if "Response" in field else "✗"
        field_name = field.get("Field Aria") or field.get("Field ID")
        print(f"  {has_response} {field_name}")


def submit_application(browser_page):
    """
    Submits the application and checks for confirmation.
    """
    print("\n🚀 Submitting application...")
    try:
        # Try different common submit button patterns
        submit_clicked = False
        submit_patterns = [
            "Submit application",
            "Submit Application",
            "Submit",
            "Apply",
        ]

        for name in submit_patterns:
            try:
                submit_button = browser_page.get_by_role("button", name=name)
                if submit_button.is_visible(timeout=2000):
                    submit_button.click(timeout=3000)
                    print(f"✓ Clicked submit button: '{name}'")
                    submit_clicked = True
                    break
            except:
                continue

        if not submit_clicked:
            print("❌ Could not find submit button - please submit manually")
        else:
            # Wait for navigation after clicking submit
            time.sleep(2)  # Give it a moment to start navigating
            browser_page.wait_for_load_state("networkidle", timeout=15000)

            # Check if submission was successful using multiple indicators
            current_url = browser_page.url
            success_indicators = [
                "confirmation" in current_url.lower(),
                "thank" in current_url.lower(),
                "success" in current_url.lower(),
                "submitted" in current_url.lower(),
            ]

            # Also check page content for success messages
            try:
                page_text = browser_page.locator("body").text_content(timeout=3000)
                if page_text:
                    page_text = page_text.lower()
                    text_indicators = [
                        "thank you" in page_text,
                        "application submitted" in page_text,
                        "application received" in page_text,
                        "we've received your application" in page_text,
                    ]
                    success_indicators.extend(text_indicators)
            except:
                pass

            if any(success_indicators):
                print("\n🎉 🎊 🕺 SUCCESSFULLY SUBMITTED APPLICATION 🎉 🎊 🕺")
            else:
                print(f"\n⚠️ Could not confirm submission - please verify on the page")

    except Exception as e:
        print(f"❌ Error during submission: {e}")
        print("Please review the form and submit manually if needed")


def apply_to_single_job(job):
    """
    Main function to apply to a single job posting.
    Orchestrates the entire application workflow.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        browser_page = browser.new_page()
        browser_page.goto(job["url"])
        browser_page.wait_for_load_state("networkidle")

        # Define form fields selector
        fields_locator_filter = browser_page.locator(
            "form input:not([type='submit']):not([type='button']), form select, form textarea"
        )

        # Process all form fields (fill known fields, collect unknown ones)
        unknown_fields, filled_fields = process_form_fields(
            browser_page, fields_locator_filter
        )

        # Handle unknown fields (autofill, LLM, fill)
        handle_unknown_fields_workflow(browser_page, unknown_fields, job["company"])

        # Submit the application
        submit_application(browser_page)

        # Final summary
        print(f"\nFinal URL: {browser_page.url}")
        input("Press Enter to close browser...")
        browser_page.wait_for_load_state("networkidle")


def get_adaptive_responses(questions):
    """
    Uses Groq LLM to generate responses for unknown fields that don't have pre-filled responses.
    Returns the questions list with Response fields added.
    """
    # Filter out questions that already have responses
    questions_needing_responses = [q for q in questions if "Response" not in q]

    if not questions_needing_responses:
        return questions

    llm_candidate_context = get_candidate_info_for_llm()

    # Format questions for LLM
    questions_json = json.dumps(questions_needing_responses, indent=2)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""You are filling out a job application form on behalf of Vidyuth Subbiah Ramkumar, a new graduate software/ML engineer.

{llm_candidate_context}

# Instructions:
- Add a "Response" field to each question with an appropriate response
- For questions with "dropdown_options", you MUST select EXACTLY one option from that list (copy it exactly, including capitalization)
- For optional questions without an asterisk (*) such as voluntary disclosures (gender, ethnicity, veteran status, disability status), skip them by not adding a Response field
- Keep responses concise and professional
- For years of experience questions, be accurate based on the candidate's profile (approximately 2 years)
- Return ONLY valid JSON array with no markdown formatting, no ```json blocks, just the raw JSON array
""",
            },
            {
                "role": "user",
                "content": f"Here are the form fields that need responses:\n{questions_json}",
            },
        ],
        model="llama-3.3-70b-versatile",
    )

    response_content = chat_completion.choices[0].message.content
    if not response_content:
        print("❌ LLM returned empty response")
        return questions
    response_content = response_content.strip()

    # Parse LLM response
    try:
        # Remove markdown code blocks if present
        if response_content.startswith("```"):
            response_content = response_content.split("```")[1]
            if response_content.startswith("json"):
                response_content = response_content[4:]

        responded_questions = json.loads(response_content)

        # Merge responses back into original questions list
        for original_q in questions:
            if "Response" not in original_q:
                # Find matching question in LLM response
                for responded_q in responded_questions:
                    if responded_q.get("Field ID") == original_q.get("Field ID"):
                        if "Response" in responded_q:
                            original_q["Response"] = responded_q["Response"]
                        break

        return questions
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing LLM response: {e}")
        print(f"LLM response was: {response_content}")
        return questions


def fill_unknown_fields_with_responses(browser_page, unknown_fields):
    """
    Fills form fields for unknown fields that have Response values.
    Uses field IDs and appropriate Playwright methods to fill the fields.
    """
    filled_count = 0
    for field in unknown_fields:
        if "Response" not in field or not field["Response"]:
            continue

        field_id = field["Field ID"]
        field_tag = field["Field Tag"]
        response = field["Response"]

        try:
            # Use ID selector to find the field
            if field_tag == "textarea":
                browser_page.locator(f"#{field_id}").fill(response, timeout=3000)
                print(f"✓ Filled {field_id} with: {response[:50]}...")
                filled_count += 1
            elif field_tag == "input":
                field_type = field.get("field_type", "text")
                if field_type in ["text", "email", "url", "tel", "number"]:
                    locator = browser_page.locator(f"#{field_id}")

                    # Check if this field has dropdown options (from extraction phase)
                    if "dropdown_options" in field:
                        # This is a dropdown - click and select exact match
                        locator.click(timeout=3000)
                        time.sleep(0.5)

                        try:
                            # Click the exact option text
                            browser_page.get_by_text(response, exact=True).first.click(
                                timeout=2000
                            )
                            print(f"✓ Filled {field_id} with: {response}")
                            filled_count += 1
                        except Exception as e:
                            print(
                                f"⚠️ Could not select '{response}' from dropdown {field_id}: {e}"
                            )
                    else:
                        # Check if it's a dropdown/select input (fallback for those we missed)
                        field_class = locator.get_attribute("class", timeout=1000) or ""
                        if "select" in field_class.lower():
                            # Try clicking and typing for autocomplete-style selects
                            locator.click(timeout=3000)
                            browser_page.keyboard.type(response)
                            # Try to find exact match in dropdown
                            try:
                                browser_page.get_by_text(
                                    response, exact=True
                                ).first.click(timeout=2000)
                            except:
                                # If no exact match, just press Enter
                                browser_page.keyboard.press("Enter")
                            print(f"✓ Filled {field_id} with: {response}")
                            filled_count += 1
                        else:
                            # Regular text input
                            locator.fill(response, timeout=3000)
                            print(f"✓ Filled {field_id} with: {response}")
                            filled_count += 1
        except Exception as e:
            print(f"❌ Could not fill {field_id}: {e}")

    print(f"\n📝 Successfully filled {filled_count} unknown fields using LLM responses")
    return filled_count


# apply_tool_schema = {
#     "type": "function",
#     "function": {
#         "name": "apply_greenhouse_job",
#         "description": f"Apply to a specific job on the Greenhouse Job Board with correct profile/resume information on candidate {CANDIDATE_FIRST_NAME} {CANDIDATE_LAST_NAME}.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "title": {
#                     "type": "string",
#                     "description": "The title of the Greenhouse job role that you need to apply to",
#                 },
#                 "url": {
#                     "type": "string",
#                     "description": "The Greenhouse job posting url that you need to access to apply to the job",
#                 },
#             },
#             "required": ["title", "url"],
#         },
#     },
# }

if __name__ == "__main__":
    # test_job = {
    #     "title": "Software Engineer",
    #     "company": "CrunchyRoll",
    #     "url": "https://job-boards.greenhouse.io/crunchyroll/jobs/6696781",
    # }
    test_job = {
        "title": "Flight Software Engineer",
        "company": "Astranis",
        "url": "https://job-boards.greenhouse.io/astranis/jobs/4015622006",
    }
    apply_to_single_job(test_job)
