# agent/apply.py
import json
import time
import os
import re
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
    CANDIDATE_GITHUB,
    CANDIDATE_CITY,
    CANDIDATE_STATE,
    CANDIDATE_STATE_ABBR,
    CANDIDATE_POSTAL_CODE,
    CANDIDATE_WORK_HISTORY,
    CANDIDATE_EDUCATION,
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
        "State/Province",
    ],
    "postal_code": [
        "Postal Code",
        "postal code",
        "Zip Code",
        "zip code",
        "ZIP",
        "Zip",
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
    "school": ["School", "school", "University", "university", "College", "college"],
    "degree": ["Degree", "degree", "Degree Level"],
    "discipline": [
        "Discipline",
        "discipline",
        "Major",
        "major",
        "Field of Study",
        "field of study",
    ],
    "gpa": ["GPA", "gpa", "Grade Point Average", "grade point average"],
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
        f"{CANDIDATE_CITY}, {CANDIDATE_STATE}, United States",
        f"{CANDIDATE_CITY}, {CANDIDATE_STATE}",
        f"{CANDIDATE_CITY}, {CANDIDATE_STATE_ABBR}",
        CANDIDATE_CITY,
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
    "state": [
        CANDIDATE_STATE,
        CANDIDATE_STATE_ABBR,
    ],
    "postal_code": CANDIDATE_POSTAL_CODE,
    "school": [
        "Northeastern University",
        "northeastern university",
        "Northeastern",
    ],
    "degree": [
        "Bachelor's Degree",
        "Bachelor's",
        "Bachelors",
        "Bachelor of Science",
        "BS",
        "B.S.",
    ],
    "discipline": [
        "Computer Science",
        "computer science",
        "CS",
    ],
    "gpa": CANDIDATE_EDUCATION["gpa"],
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
            elif possible_field == "school":
                try:
                    print(
                        f"Interacting with SCHOOL field. field_id: {field_id}, possible_field from field variation map: {possible_field}"
                    )
                    # Try dropdown approach first (type + select)
                    try:
                        field_locator.click(timeout=2000)
                        time.sleep(0.3)
                        browser_page.keyboard.type("Northeastern University")
                        time.sleep(0.5)
                        # Try to click exact match
                        try:
                            browser_page.get_by_text(
                                "Northeastern University", exact=True
                            ).first.click(timeout=2000)
                            print("✓ Filled school (dropdown)")
                        except:
                            # If no exact match, just press Enter
                            browser_page.keyboard.press("Enter")
                            print("✓ Filled school (dropdown with Enter)")
                    except:
                        # Fallback: just type into text field if not a dropdown
                        field_locator.fill("Northeastern University")
                        print("✓ Filled school (text input)")
                except Exception as e:
                    print(f"❌ Could not fill SCHOOL field; exception {e}")
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
        field_tag_name = ejf_locator.evaluate(
            "element => element.tagName.toLowerCase()"
        )
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
        # Use attribute selector to handle IDs that start with numbers
        try:
            field_aria = browser_page.locator(f'[id="{field_aria_raw}"]').text_content(
                timeout=2000
            )
        except:
            field_aria = field_aria_raw
    else:
        field_aria = field_aria_raw

    # If no ARIA label, try to find label via parent structure (for checkboxes)
    if not field_aria and field_tag_name == "input":
        input_type = ejf_locator.get_attribute("type") or ""
        if input_type == "checkbox":
            # Try to find associated label or parent text
            try:
                # Check for label with for attribute matching this field's ID
                label = browser_page.locator(f'label[for="{field_id}"]').first
                field_aria = label.text_content(timeout=1000).strip()
            except:
                # Try to find parent fieldset legend or preceding label
                try:
                    parent_legend = ejf_locator.evaluate(
                        "el => el.closest('fieldset')?.querySelector('legend')?.textContent"
                    )
                    if parent_legend:
                        field_aria = parent_legend.strip()
                except:
                    pass

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


def autofill_misc_unknown_questions(questions, company_name, job_title=""):
    autofilled_count = 0
    for q in questions:
        if q["Field Aria"]:
            aria_lower = q["Field Aria"].lower()
            company_lower = company_name.lower()

            if (
                "non-compete" in q["Field Aria"]
                or "non-competetition" in q["Field Aria"]
            ) and "*" in q["Field Aria"]:
                q["Response"] = "No"
                autofilled_count += 1
                print(f"  ✓ Auto-filled non-compete: {q['Field Aria']}")
            if (
                "require any immigration support" in q["Field Aria"]
                and "*" in q["Field Aria"]
            ):
                q["Response"] = "No"
                autofilled_count += 1
                print(f"  ✓ Auto-filled immigration: {q['Field Aria']}")
            if "authorized" in aria_lower and (
                "work" in aria_lower or "employment" in aria_lower
            ):
                q["Response"] = "Yes"
                autofilled_count += 1
                print(f"  ✓ Auto-filled work authorization: {q['Field Aria']}")
            if company_lower in aria_lower and (
                "ever worked for" in aria_lower
                or ("worked for" in aria_lower and "before" in aria_lower)
            ):
                q["Response"] = "No"
                autofilled_count += 1
                print(f"  ✓ Auto-filled work history: {q['Field Aria']}")
            if "will you" in aria_lower and (
                "require sponsorship" in aria_lower or "sponsor" in aria_lower
            ):
                q["Response"] = "No"
                autofilled_count += 1
                print(f"  ✓ Auto-filled sponsorship: {q['Field Aria']}")
            # LinkedIn URL autofill
            if "linkedin" in aria_lower and (
                "profile" in aria_lower or "url" in aria_lower or "link" in aria_lower
            ):
                q["Response"] = CANDIDATE_LINKEDIN
                autofilled_count += 1
                print(f"  ✓ Auto-filled LinkedIn: {q['Field Aria']}")
            # GitHub URL autofill
            if "github" in aria_lower and (
                "profile" in aria_lower
                or "url" in aria_lower
                or "link" in aria_lower
                or "page" in aria_lower
                or "account" in aria_lower
            ):
                q["Response"] = CANDIDATE_GITHUB
                autofilled_count += 1
                print(f"  ✓ Auto-filled GitHub: {q['Field Aria']}")
            # Salary expectations - handle via LLM with job title context
            if ("salary" in aria_lower or "compensation" in aria_lower) and (
                "expectation" in aria_lower
                or "desired" in aria_lower
                or "requirement" in aria_lower
            ):
                # Mark this field to be handled by LLM with special context
                q["needs_salary_context"] = True
            # Current city question variants
            if "city" in aria_lower and (
                "currently" in aria_lower
                or "current" in aria_lower
                or "live" in aria_lower
                or "reside" in aria_lower
            ):
                q["Response"] = CANDIDATE_CITY
                autofilled_count += 1
                print(f"  ✓ Auto-filled current city: {q['Field Aria']}")
            # Current state question variants
            if "state" in aria_lower and (
                "currently" in aria_lower
                or "current" in aria_lower
                or "live" in aria_lower
                or "reside" in aria_lower
            ):
                # Check if it's a dropdown with state abbreviations
                if (
                    "dropdown_options" in q and len(q["dropdown_options"]) > 20
                ):  # Likely state dropdown
                    q["Response"] = CANDIDATE_STATE_ABBR
                else:
                    q["Response"] = CANDIDATE_STATE
                autofilled_count += 1
                print(f"  ✓ Auto-filled current state: {q['Field Aria']}")
            # Willing to relocate
            if (
                "willing" in aria_lower or "able" in aria_lower or "open" in aria_lower
            ) and "relocat" in aria_lower:
                q["Response"] = "Yes"
                autofilled_count += 1
                print(f"  ✓ Auto-filled willing to relocate: {q['Field Aria']}")
            # Committed to in-person/office work
            if (
                "committed" in aria_lower
                or "willing" in aria_lower
                or "able" in aria_lower
            ) and (
                "in person" in aria_lower
                or "in-person" in aria_lower
                or "office" in aria_lower
                or "on-site" in aria_lower
                or "onsite" in aria_lower
            ):
                q["Response"] = "Yes"
                autofilled_count += 1
                print(f"  ✓ Auto-filled committed to in-person work: {q['Field Aria']}")
            # Policy/agreement checkboxes
            if q.get("field_type") == "checkbox" or (
                q.get("Field Tag") == "input"
                and "checkbox" in str(q.get("field_type", "")).lower()
            ):
                # Auto-check policy/agreement checkboxes
                if any(
                    keyword in aria_lower
                    for keyword in [
                        "policy",
                        "agree",
                        "understand",
                        "acknowledge",
                        "terms",
                        "consent",
                        "privacy notice",
                        "read and understand",
                    ]
                ):
                    q["Response"] = "checked"
                    autofilled_count += 1
                    print(f"  ✓ Auto-checked checkbox: {q['Field Aria']}")

            # Salary expectations checkboxes (multi-select)
            if "salary" in aria_lower and "expectation" in aria_lower:
                # For new grad SWE roles, select $80k-$99k and $100k+ ranges
                field_id = q.get("Field ID", "")
                # Check if this is one of the higher salary range checkboxes
                # We want to check the $80k-$89k, $90k-$99k, and $100k+ options
                # These are typically the last 3 checkboxes in the salary list
                # Mark this as needing special salary handling
                q["needs_salary_checkbox"] = True

            # GPA range dropdowns
            if "gpa" in aria_lower and "dropdown_options" in q:
                gpa_value = float(CANDIDATE_EDUCATION["gpa"])
                options = q["dropdown_options"]

                # Try to find the right range
                for option in options:
                    option_lower = option.lower()
                    # Match patterns like "3.2 - 3.49" or "3.20-3.49" or "3.2-3.49"
                    range_match = re.search(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", option)
                    if range_match:
                        range_min = float(range_match.group(1))
                        range_max = float(range_match.group(2))
                        if range_min <= gpa_value <= range_max:
                            q["Response"] = option
                            autofilled_count += 1
                            print(
                                f"  ✓ Auto-filled GPA range: {q['Field Aria']} = {option}"
                            )
                            break

    print(f"\n✓ Auto-filled {autofilled_count} fields")
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
                "checkbox",
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
            # Filter out irrelevant fields before adding to unknown_fields
            should_skip = False

            # Skip search input fields (phone number country code search, etc.)
            if field_id and (
                "search-input" in field_id.lower() or "search" in field_id.lower()
            ):
                should_skip = True

            # Skip unnamed fields with no aria label
            if field_id == "Unnamed Field" and not field_aria:
                should_skip = True

            # Skip fields with "Search" as aria label
            if field_aria and field_aria.strip() == "Search":
                should_skip = True

            if should_skip:
                i += 1
                continue

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


def handle_checkbox_groups(browser_page, job_title=""):
    """
    Handles special checkbox groups that don't have individual ARIA labels:
    1. Salary expectations (multi-select checkboxes)
    2. Privacy notice agreements
    """
    # Handle salary expectation checkboxes
    try:
        # Find all checkboxes with IDs matching the salary pattern (question_*[]_*)
        salary_checkboxes = browser_page.locator('input[type="checkbox"][id*="question"][id*="[]"]').all()

        for checkbox in salary_checkboxes:
            try:
                # Get the associated label
                checkbox_id = checkbox.get_attribute("id")
                label = browser_page.locator(f'label[for="{checkbox_id}"]').first
                label_text = label.text_content(timeout=1000).strip()

                # Check if this is a salary checkbox
                if "$" in label_text and any(keyword in label_text.lower() for keyword in ["salary", "expect", "compens"]):
                    # For new grad SWE: select $80k-$89k, $90k-$99k, and $100k+
                    should_check = any(range_text in label_text for range_text in ["$80,000", "$90,000", "$100,000+"])

                    if should_check and not checkbox.is_checked(timeout=1000):
                        checkbox.click(timeout=2000)
                        print(f"  ✓ Checked salary range: {label_text}")

                # Check if this is a privacy notice checkbox
                elif any(keyword in label_text.lower() for keyword in ["privacy notice", "read and understand", "job applicant privacy"]):
                    if not checkbox.is_checked(timeout=1000):
                        checkbox.click(timeout=2000)
                        print(f"  ✓ Checked privacy notice: {label_text}")
            except:
                continue
    except Exception as e:
        print(f"  ⚠️ Could not process checkbox groups: {e}")


def handle_unknown_fields_workflow(
    browser_page, unknown_fields, company_name, job_title=""
):
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
    unknown_fields = autofill_misc_unknown_questions(
        unknown_fields, company_name, job_title
    )
    print(f"\nunknown fields after autofill: {len(unknown_fields)} fields")

    # Then, use LLM to fill remaining fields
    print("\n🤖 Getting LLM responses for unknown fields...")
    unknown_fields = get_adaptive_responses(unknown_fields, job_title)

    # Fill the fields with the responses
    print("\n📝 Filling unknown fields with responses...")
    fill_unknown_fields_with_responses(browser_page, unknown_fields)

    # Handle special checkbox groups (salary expectations, privacy notices)
    print("\n📋 Handling checkbox groups...")
    handle_checkbox_groups(browser_page, job_title)

    # Show final unknown fields status
    print(f"\n📋 Final unknown fields summary:")
    for field in unknown_fields:
        has_response = "✓" if "Response" in field else "✗"
        field_name = field.get("Field Aria") or field.get("Field ID")
        print(f"  {has_response} {field_name}")


def check_required_fields_filled(browser_page):
    """
    Checks if all required fields (marked with *) are filled.
    Returns: (all_filled: bool, unfilled_fields: list)
    """
    unfilled_required_fields = []

    try:
        # Find all required field labels (containing *)
        # Common patterns: "Field Name*", "Field Name *"
        all_inputs = browser_page.locator('input:not([type="hidden"]):not([type="submit"]):not([type="button"]), select, textarea').all()

        for input_elem in all_inputs:
            try:
                # Check if field is required
                is_required = input_elem.get_attribute("required") is not None
                aria_required = input_elem.get_attribute("aria-required") == "true"

                if is_required or aria_required:
                    # Check if field is filled
                    input_type = input_elem.get_attribute("type") or "text"
                    field_id = input_elem.get_attribute("id") or "unknown"

                    if input_type == "checkbox":
                        if not input_elem.is_checked(timeout=500):
                            # Get label text
                            try:
                                label = browser_page.locator(f'label[for="{field_id}"]').first
                                label_text = label.text_content(timeout=1000).strip()
                                unfilled_required_fields.append(label_text or field_id)
                            except:
                                unfilled_required_fields.append(field_id)
                    else:
                        value = input_elem.input_value(timeout=500)
                        if not value or value.strip() == "":
                            # Get field label
                            try:
                                # Try aria-labelledby
                                aria_label_id = input_elem.get_attribute("aria-labelledby")
                                if aria_label_id:
                                    label_elem = browser_page.locator(f'[id="{aria_label_id}"]').first
                                    label_text = label_elem.text_content(timeout=1000).strip()
                                    unfilled_required_fields.append(label_text or field_id)
                                else:
                                    # Try label[for]
                                    label = browser_page.locator(f'label[for="{field_id}"]').first
                                    label_text = label.text_content(timeout=1000).strip()
                                    unfilled_required_fields.append(label_text or field_id)
                            except:
                                unfilled_required_fields.append(field_id)
            except:
                continue

    except Exception as e:
        print(f"  ⚠️ Error checking required fields: {e}")
        return True, []  # Assume filled if we can't check

    return len(unfilled_required_fields) == 0, unfilled_required_fields


def submit_application(browser_page):
    """
    Submits the application and checks for confirmation.
    Returns: (success: bool, message: str)
    """
    print("\n🚀 Preparing to submit application...")

    # First, check if all required fields are filled
    all_filled, unfilled_fields = check_required_fields_filled(browser_page)

    if not all_filled:
        print(f"\n❌ SKIPPING SUBMISSION - {len(unfilled_fields)} required field(s) not filled:")
        for field in unfilled_fields[:10]:  # Show first 10
            print(f"  • {field}")
        if len(unfilled_fields) > 10:
            print(f"  ... and {len(unfilled_fields) - 10} more")
        print("\n⚠️ This job application cannot be fully automated. Skipping.")
        return False, "Required fields unfilled"

    print("✓ All required fields are filled")

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
            return False, "Submit button not found"
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
                return True, "Success"
            else:
                print(f"\n⚠️ Could not confirm submission - please verify on the page")
                return False, "Could not confirm"

    except Exception as e:
        print(f"❌ Error during submission: {e}")
        print("Please review the form and submit manually if needed")
        return False, str(e)


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
        job_title = job.get("title", "")
        handle_unknown_fields_workflow(
            browser_page, unknown_fields, job["company"], job_title
        )

        # Fill education section
        fill_education_section(browser_page)

        # Fill employment history section
        fill_employment_section(browser_page)

        # Submit the application
        success, message = submit_application(browser_page)

        # Final summary
        print(f"\nFinal URL: {browser_page.url}")
        if success:
            print(f"✅ Application status: Submitted successfully")
        else:
            print(f"⚠️ Application status: Skipped - {message}")
            print(f"   Reason: Form has required fields that couldn't be automated")

        input("Press Enter to close browser...")
        browser_page.wait_for_load_state("networkidle")

        return success


def is_eeo_field(field):
    """
    Determines if a field is a voluntary EEO disclosure field.
    These fields should not be sent to the LLM.
    """
    if not field.get("Field Aria"):
        return False

    aria_lower = field["Field Aria"].lower()

    # EEO field patterns
    eeo_patterns = [
        "gender",
        "race",
        "ethnicity",
        "hispanic",
        "latino",
        "veteran",
        "disability",
        "sexual orientation",
        "transgender",
        "lgbtq",
    ]

    return any(pattern in aria_lower for pattern in eeo_patterns)


def is_sensitive_address_field(field):
    """
    Determines if a field is asking for street/home address (too sensitive to auto-fill).
    """
    if not field.get("Field Aria"):
        return False

    aria_lower = field["Field Aria"].lower()

    # Don't auto-fill street addresses
    if "address" in aria_lower and (
        "street" in aria_lower
        or "residence" in aria_lower
        or "home" in aria_lower
        or "permanent" in aria_lower
    ):
        return True

    return False


def is_education_field(field):
    """
    Determines if a field is part of the education section.
    These fields follow patterns like: degree--0, discipline--0, start-month--0, etc.
    Note the double dash (--) pattern for education vs single dash (-) for employment.
    """
    field_id = field.get("Field ID", "")
    field_aria = field.get("Field Aria")

    # Check ID patterns for education fields (note the double dash --)
    education_id_patterns = [
        "degree--",
        "discipline--",
        "major--",
        "school--",
        "university--",
        "start-month--",
        "start-year--",
        "end-month--",
        "end-year--",
    ]

    if any(pattern in field_id for pattern in education_id_patterns):
        return True

    # Also check ARIA labels for education-specific terms
    if field_aria:
        aria_lower = field_aria.lower()
        # Education section has degree/discipline in ARIA with -- pattern in ID
        if "--" in field_id and any(
            term in aria_lower
            for term in ["degree", "discipline", "major", "school", "university"]
        ):
            return True
        # Start/end date with -- pattern is likely education
        if "--" in field_id and (
            "start date" in aria_lower or "end date" in aria_lower
        ):
            return True

    return False


def is_employment_field(field):
    """
    Determines if a field is part of the employment history section.
    These fields follow patterns like: title-0, company-0, start-date-month-0, etc.
    """
    field_id = field.get("Field ID", "")
    field_aria = field.get("Field Aria")

    # Check ID patterns for employment fields
    employment_id_patterns = [
        "title-",
        "company-",
        "employer-",
        "start-date-month-",
        "start-date-year-",
        "end-date-month-",
        "end-date-year-",
        "current-role-",
    ]

    if any(pattern in field_id for pattern in employment_id_patterns):
        return True

    # Also check ARIA labels
    if field_aria:
        aria_lower = field_aria.lower()
        # Look for employment-specific patterns in ARIA
        if "title" in aria_lower and (
            "start date" in field_id or "end date" in field_id or "-0" in field_id
        ):
            return True
        if ("start date" in aria_lower or "end date" in aria_lower) and (
            "month" in aria_lower or "year" in aria_lower
        ):
            # But make sure it's not education dates
            if "title-" in field_id or "company-" in field_id or "-0" in field_id:
                return True

    return False


def fill_education_section(browser_page):
    """
    Fills the education section with data from CANDIDATE_EDUCATION.
    Handles fields with double-dash pattern: degree--0, discipline--0, start-month--0, etc.
    """
    if not CANDIDATE_EDUCATION:
        print("  ℹ️  No education data available, skipping education section")
        return

    print(f"\n🎓 Filling education section...")

    # Map month names to their full form
    month_map = {
        "September": "September",
        "May": "May",
    }

    try:
        # Fill school name (if exists)
        try:
            school_field = browser_page.locator(
                '[id*="school"][id*="--0"], [id="school--0"]'
            ).first
            school_field.click(timeout=2000)
            time.sleep(0.3)
            browser_page.keyboard.type(CANDIDATE_EDUCATION["school"])
            time.sleep(0.5)
            # Try to click exact match
            try:
                browser_page.get_by_text(
                    CANDIDATE_EDUCATION["school"], exact=True
                ).first.click(timeout=2000)
            except:
                browser_page.keyboard.press("Enter")
            print(f"  ✓ School: {CANDIDATE_EDUCATION['school']}")
        except:
            # School field might not exist, that's okay
            pass

        # Fill degree
        try:
            degree_field = browser_page.locator('[id="degree--0"]').first
            degree_field.click(timeout=2000)
            time.sleep(0.5)
            browser_page.keyboard.type("Bachelor")
            time.sleep(0.5)
            # Try to click exact match
            try:
                browser_page.get_by_text("Bachelor's Degree", exact=True).first.click(
                    timeout=2000
                )
            except:
                browser_page.keyboard.press("Enter")
            print(f"  ✓ Degree: Bachelor's Degree")
        except Exception as e:
            print(f"  ⚠️ Could not fill degree: {e}")

        # Fill discipline/major
        try:
            discipline_field = browser_page.locator('[id="discipline--0"]').first
            discipline_field.click(timeout=2000)
            time.sleep(0.5)
            browser_page.keyboard.type("Computer Science")
            time.sleep(0.5)
            # Try to click exact match
            try:
                browser_page.get_by_text("Computer Science", exact=True).first.click(
                    timeout=2000
                )
            except:
                browser_page.keyboard.press("Enter")
            print(f"  ✓ Discipline: Computer Science")
        except Exception as e:
            print(f"  ⚠️ Could not fill discipline: {e}")

        # Fill start month
        try:
            start_month_field = browser_page.locator('[id="start-month--0"]').first
            start_month_field.click(timeout=2000)
            time.sleep(0.5)
            browser_page.keyboard.type(CANDIDATE_EDUCATION["start_month"])
            time.sleep(0.3)
            browser_page.keyboard.press("Enter")
            print(f"  ✓ Start month: {CANDIDATE_EDUCATION['start_month']}")
        except Exception as e:
            print(f"  ⚠️ Could not fill start month: {e}")

        # Fill start year
        try:
            start_year_field = browser_page.locator('[id="start-year--0"]').first
            start_year_field.fill(CANDIDATE_EDUCATION["start_year"], timeout=2000)
            print(f"  ✓ Start year: {CANDIDATE_EDUCATION['start_year']}")
        except Exception as e:
            print(f"  ⚠️ Could not fill start year: {e}")

        # Fill end month
        try:
            end_month_field = browser_page.locator('[id="end-month--0"]').first
            end_month_field.click(timeout=2000)
            time.sleep(0.5)
            browser_page.keyboard.type(CANDIDATE_EDUCATION["end_month"])
            time.sleep(0.3)
            browser_page.keyboard.press("Enter")
            print(f"  ✓ End month: {CANDIDATE_EDUCATION['end_month']}")
        except Exception as e:
            print(f"  ⚠️ Could not fill end month: {e}")

        # Fill end year
        try:
            end_year_field = browser_page.locator('[id="end-year--0"]').first
            end_year_field.fill(CANDIDATE_EDUCATION["end_year"], timeout=2000)
            print(f"  ✓ End year: {CANDIDATE_EDUCATION['end_year']}")
        except Exception as e:
            print(f"  ⚠️ Could not fill end year: {e}")

    except Exception as e:
        print(f"  ❌ Error filling education section: {e}")

    print(f"  ✓ Education section filled\n")


def fill_employment_section(browser_page):
    """
    Fills the employment history section with data from CANDIDATE_WORK_HISTORY.
    Handles multiple job entries by filling first job, then clicking "Add another" for subsequent jobs.
    """
    if not CANDIDATE_WORK_HISTORY:
        print("  ℹ️  No work history data available, skipping employment section")
        return

    # Check if employment fields exist on this form (single dash pattern: company-0, title-0)
    try:
        browser_page.locator('[id="company-0"], [id="title-0"]').first.wait_for(
            timeout=1000
        )
    except:
        print("  ℹ️  No employment section found on this form, skipping")
        return

    print(f"\n💼 Filling employment section with {len(CANDIDATE_WORK_HISTORY)} jobs...")

    for job_index, job in enumerate(CANDIDATE_WORK_HISTORY):
        try:
            print(
                f"  📝 Filling job #{job_index + 1}: {job['company']} - {job['title']}"
            )

            # Fill company name
            try:
                company_field = browser_page.locator(
                    f'[id*="company"][id*="-{job_index}"], [id="company-{job_index}"]'
                ).first
                company_field.fill(job["company"], timeout=2000)
                print(f"    ✓ Company: {job['company']}")
            except:
                print(f"    ⚠️ Could not find company field for job {job_index}")

            # Fill title
            try:
                title_field = browser_page.locator(f'[id="title-{job_index}"]').first
                title_field.fill(job["title"], timeout=2000)
                print(f"    ✓ Title: {job['title']}")
            except:
                print(f"    ⚠️ Could not find title field for job {job_index}")

            # Fill start date month
            try:
                start_month_field = browser_page.locator(
                    f'[id="start-date-month-{job_index}"]'
                ).first
                start_month_field.click(timeout=2000)
                time.sleep(0.5)
                browser_page.keyboard.type(job["start_month"])
                time.sleep(0.3)
                browser_page.keyboard.press("Enter")
                print(f"    ✓ Start month: {job['start_month']}")
            except:
                print(f"    ⚠️ Could not fill start month for job {job_index}")

            # Fill start date year
            try:
                start_year_field = browser_page.locator(
                    f'[id="start-date-year-{job_index}"]'
                ).first
                start_year_field.fill(job["start_year"], timeout=2000)
                print(f"    ✓ Start year: {job['start_year']}")
            except:
                print(f"    ⚠️ Could not fill start year for job {job_index}")

            # Handle "current role" checkbox
            if job.get("is_current", False):
                try:
                    current_role_checkbox = browser_page.locator(
                        f'[id*="current-role"][id*="{job_index}"]'
                    ).first
                    if not current_role_checkbox.is_checked():
                        current_role_checkbox.click(timeout=2000)
                    print(f"    ✓ Marked as current role")
                except:
                    pass
            else:
                # Fill end date month
                try:
                    end_month_field = browser_page.locator(
                        f'[id="end-date-month-{job_index}"]'
                    ).first
                    end_month_field.click(timeout=2000)
                    time.sleep(0.5)
                    browser_page.keyboard.type(job["end_month"])
                    time.sleep(0.3)
                    browser_page.keyboard.press("Enter")
                    print(f"    ✓ End month: {job['end_month']}")
                except:
                    print(f"    ⚠️ Could not fill end month for job {job_index}")

                # Fill end date year
                try:
                    end_year_field = browser_page.locator(
                        f'[id="end-date-year-{job_index}"]'
                    ).first
                    end_year_field.fill(job["end_year"], timeout=2000)
                    print(f"    ✓ End year: {job['end_year']}")
                except:
                    print(f"    ⚠️ Could not fill end year for job {job_index}")

            # If there are more jobs, click "Add another" button
            if job_index < len(CANDIDATE_WORK_HISTORY) - 1:
                try:
                    add_another_button = browser_page.get_by_role(
                        "button", name="Add another"
                    )
                    if add_another_button.is_visible(timeout=1000):
                        add_another_button.click(timeout=2000)
                        time.sleep(1)  # Wait for new fields to appear
                        print(f"    ✓ Clicked 'Add another' for next job")
                except:
                    print(
                        f"    ℹ️  Could not find 'Add another' button, stopping at {job_index + 1} jobs"
                    )
                    break

        except Exception as e:
            print(f"  ❌ Error filling job {job_index}: {e}")
            continue

    print(
        f"  ✓ Employment section filled with {min(job_index + 1, len(CANDIDATE_WORK_HISTORY))} jobs\n"
    )


def get_adaptive_responses(questions, job_title=""):
    """
    Uses Groq LLM to generate responses for unknown fields that don't have pre-filled responses.
    Returns the questions list with Response fields added.
    """
    # Filter out questions that already have responses
    questions_needing_responses = [q for q in questions if "Response" not in q]

    # Filter out EEO, address, education, and employment fields from LLM processing
    eeo_fields = [q for q in questions_needing_responses if is_eeo_field(q)]
    address_fields = [
        q
        for q in questions_needing_responses
        if is_sensitive_address_field(q) and not is_eeo_field(q)
    ]
    education_fields = [
        q
        for q in questions_needing_responses
        if is_education_field(q)
        and not is_eeo_field(q)
        and not is_sensitive_address_field(q)
    ]
    employment_fields = [
        q
        for q in questions_needing_responses
        if is_employment_field(q)
        and not is_eeo_field(q)
        and not is_sensitive_address_field(q)
        and not is_education_field(q)
    ]
    questions_for_llm = [
        q
        for q in questions_needing_responses
        if not is_eeo_field(q)
        and not is_sensitive_address_field(q)
        and not is_education_field(q)
        and not is_employment_field(q)
    ]

    if eeo_fields:
        print(f"  ⏭️  Skipping {len(eeo_fields)} EEO disclosure fields (will not fill)")
    if address_fields:
        print(
            f"  ⏭️  Skipping {len(address_fields)} street address fields (will not fill)"
        )
    if education_fields:
        print(
            f"  ⏭️  Skipping {len(education_fields)} education fields (handled separately)"
        )
    if employment_fields:
        print(
            f"  ⏭️  Skipping {len(employment_fields)} employment fields (handled separately)"
        )

    if not questions_for_llm:
        print("  ℹ️  All non-EEO questions already have responses from autofill")
        return questions

    print(f"  📤 Sending {len(questions_for_llm)} questions to LLM")

    llm_candidate_context = get_candidate_info_for_llm()

    # Check if any questions need salary context
    has_salary_field = any(
        q.get("needs_salary_context", False) for q in questions_for_llm
    )
    salary_instruction = ""
    if has_salary_field and job_title:
        salary_instruction = f"\n\n# Salary Expectations:\n- Job title: {job_title}\n- Research typical market rate for this role for a new graduate with 2 years experience\n- Provide a reasonable salary expectation (annual, in USD)\n- If the job description mentions a salary range, aim for the middle of that range\n- Format as a number (e.g., '120000' for $120k)"

    # Format questions for LLM (only non-EEO questions)
    questions_json = json.dumps(questions_for_llm, indent=2)

    system_prompt = """You are filling out a job application form on behalf of Vidyuth Subbiah Ramkumar, a new graduate software/ML engineer.

""" + llm_candidate_context + salary_instruction + """

# Availability & Relocation:
- Vidyuth is OPEN TO RELOCATING to ANY location in the USA (any city, any state)
- Vidyuth is graduating in May 2026 and is available to start full-time positions anytime after May 2026
- For questions asking "Can you be in [location] and ready to start...", answer YES and mention availability after May 2026 graduation
- For questions about relocation, in-person work, or office commitment, answer YES

# GPA Information:
- Vidyuth's GPA is 3.41
- For GPA range dropdowns (e.g., "3.0-3.19", "3.2-3.49"), select the range that contains 3.41
- 3.41 falls in the range 3.2-3.49 (or 3.20-3.49)

# Instructions:
- Add a "Response" field to EVERY question provided
- For questions with "dropdown_options", you MUST select EXACTLY one option from that list (copy it exactly, including capitalization)
- If candidate lacks experience for a question (like "Where have you worked in X?"), respond with "N/A" or "No direct experience" - DO NOT skip it
- Answer ALL questions about skills, preferences, relocation, websites, LinkedIn/GitHub URLs, etc.
- For salary questions, provide a realistic market-rate number based on the job title and candidate's experience level
- Keep responses concise and professional

# CRITICAL OUTPUT FORMAT:
- Return ONLY the JSON array, nothing else
- NO markdown code blocks (no ```json)
- NO explanatory text before or after the JSON
- NO notes or comments
- Start your response with [ and end with ]
- Example: [{"Field ID": "x", "Response": "y"}]
"""

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": "Here are the form fields that need responses:\n" + questions_json,
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

        # If response has text before JSON, extract just the JSON array
        if not response_content.strip().startswith("["):
            # Find the first [ and extract from there
            start_idx = response_content.find("[")
            if start_idx != -1:
                response_content = response_content[start_idx:]

        # Remove any trailing text after the JSON array
        if response_content.strip().endswith("]"):
            pass  # Already clean
        else:
            # Find the last ] and truncate after it
            end_idx = response_content.rfind("]")
            if end_idx != -1:
                response_content = response_content[: end_idx + 1]

        responded_questions = json.loads(response_content)

        # Merge responses back into original questions list (only for non-EEO fields)
        for original_q in questions:
            if "Response" not in original_q and not is_eeo_field(original_q):
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
                browser_page.locator(f'[id="{field_id}"]').fill(response, timeout=3000)
                print(f"✓ Filled {field_id} with: {response[:50]}...")
                filled_count += 1
            elif field_tag == "input":
                field_type = field.get("field_type", "text")
                # Handle checkbox fields
                if field_type == "checkbox" or "checkbox" in str(field_type).lower():
                    if response == "checked":
                        locator = browser_page.locator(f'[id="{field_id}"]')
                        if not locator.is_checked(timeout=2000):
                            locator.click(timeout=3000)
                        print(f"✓ Checked {field_id}")
                        filled_count += 1
                elif field_type in ["text", "email", "url", "tel", "number"]:
                    # Use attribute selector for IDs starting with numbers
                    locator = browser_page.locator(f'[id="{field_id}"]')

                    # Check if this field has dropdown options (from extraction phase)
                    if "dropdown_options" in field:
                        # This is a dropdown - use keyboard typing like country/city (most reliable for React Select)
                        try:
                            locator.click(timeout=3000)
                            time.sleep(0.8)  # Wait for React Select to render

                            # Type the value to trigger React's onChange
                            browser_page.keyboard.type(response)
                            time.sleep(0.5)  # Let autocomplete filter

                            # Try to click the exact match option
                            try:
                                browser_page.get_by_text(
                                    response, exact=True
                                ).first.click(timeout=2000)
                                print(f"✓ Filled {field_id} with: {response}")
                                filled_count += 1
                            except:
                                # If exact match click fails, just press Enter
                                browser_page.keyboard.press("Enter")
                                time.sleep(0.3)
                                print(
                                    f"✓ Filled {field_id} with: {response} (keyboard)"
                                )
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
