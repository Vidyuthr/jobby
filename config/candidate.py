"""
Centralized candidate configuration for use across the application.
Import this module to access candidate information for form filling, LLM calls, etc.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Basic Information
CANDIDATE_FIRST_NAME = "Vidyuth"
CANDIDATE_LAST_NAME = "Ramkumar"
CANDIDATE_EMAIL = "vidyuth.ramkumar@gmail.com"
CANDIDATE_PHONE_NUMBER = os.getenv("CANDIDATE_PHONE_NUMBER")
CANDIDATE_RESUME_FILE_PATH = os.getenv("RESUME_FILE_PATH")
CANDIDATE_LINKEDIN = "https://www.linkedin.com/in/vidyuth-ramkumar/"
CANDIDATE_GITHUB = "https://github.com/Vidyuthr"

# Location Information (from .env to keep private)
CANDIDATE_CITY = os.getenv("CANDIDATE_CITY")
CANDIDATE_STATE = os.getenv("CANDIDATE_STATE")
CANDIDATE_STATE_ABBR = os.getenv("CANDIDATE_STATE_ABBR")
CANDIDATE_POSTAL_CODE = os.getenv("CANDIDATE_POSTAL_CODE")

# Detailed Profile Information
OVERALL_CANDIDATE_PROFILE = "- Name: Vidyuth Subbiah Ramkumar - Education: BS Computer Science + Business Administration, Northeastern University Honors Program, May 2026. Dean's List. - Experience level: roughly 2 years, targeting strong new grad / junior roles - Target roles: Vidyuth is looking for full-time permanent roles or internships only, not research fellowships or contractor positions. AI/ML Engineer, Software Engineer, Product roles, at AI startups. If not, moderately relevant roles are fine too. - Open to: all roles in USA. Vidyuth is open to relocation within the USA - Work authorization: Vidyuth has work authorization as he is a permanent resident of the USA and he does NOT require any visa sponsorship."

CANDIDATE_SKILLS = "Languages: Python, JavaScript, TypeScript, SQL, Swift, Java\nFrameworks & Tools: TensorFlow, Scikit-learn, HuggingFace, Redis, Apache Spark, Apache Airflow, NumPy, Pandas, Databricks, Docker, PostgreSQL, MongoDB, Firebase, React JS, Node JS, Tailwind, Stripe\nAI/ML: Machine Learning, LLMs, RAG pipelines, Deep Learning, Feature Engineering, Model Evaluation, Agents"

CANDIDATE_EXPERIENCE = "- Beatleaf (Co-Founder): Full stack version control software for music producers , React/Express/PostgreSQL/Supabase, audio version control, 30+ users. strong product/startup understanding of PMF, market/user interviewing, engineering prioritization, etc.\n- Credit One Bank (SWE Intern): Production data engineering including complex SQL, Apache Airflow, Spark to help monitor internal data platform that handled complex and vast data in 300 terabytes\n- Objectways (AI/ML Engineer, Jun 2024 - Dec 2024): Engineered production full stack Express.js backend with Firebase NoSQL Firestore database, Python LLM tokenization service, and Stripe payment processing for Sheetwise — an AI-powered Google Sheets extension with 220+ organic user signups and multiple paid subscribers on Google Sheets Marketplace. Built production Databricks RAG pipelines in Python, Spark, and SQL powering a customer support chatbot (60% faster response time) and a vehicle AI assistant (85% accuracy across 300+ models).\n- Sparrow (Tech Intern): Python web scraping via BS4 and requests, HTML work, PowerBI work"

CANDIDATE_PROJECTS = "- Safe Stack Overflow: Full stack Q&A platform with AI content moderation\n- Nightcap: React Native IoT sleep startup, 12,000+ views on social media, finalist in University startup challenge. Product was not built"

CANDIDATE_CERTIFICATIONS = "Stanford ML Specialization (Supervised learning, deep learning, and reinforcement learning),CrewAI Building MultiAgent Systems, Databricks basics (ML + Data Engineering), Google LLM/GenAI, Anthropic Agent Skills"

CANDIDATE_PERSONALITY = "- Very very curious and eager to learn everything deeply. Constant learner, loves new things. Asks lots of questions. Passionate. - Constantly thinks of ideas, being a two-time founder. Always thinking how to improve processes/operations, or just ideas in general for products/solutions/features. - Approachable, kind, and loves to work with people, able to explain/present very very well due to speech & debate nationalist in highschool and many startup pitches/competitions – so he has soft skills and presentation skills to both technical and non-technical audiences"

CANDIDATE_EDUCATION = {
    "degree": "BS Computer Science + Business Administration",
    "discipline": "Computer Science",
    "school": "Northeastern University",
    "honors": "Honors Program, Dean's List",
    "start_month": "September",
    "start_year": "2022",
    "end_month": "May",
    "end_year": "2026",
}


def get_candidate_info_for_llm():
    """
    Returns a formatted string of candidate information for use in LLM prompts.
    This is ideal for system messages or context injection.
    """
    # Format education section from dict
    edu = CANDIDATE_EDUCATION
    education_section = f"""- Degree: {edu['degree']}
- Discipline: {edu['discipline']}
- School: {edu['school']}
- Honors: {edu['honors']}
- Start Date: {edu['start_month']} {edu['start_year']}
- End Date: {edu['end_month']} {edu['end_year']}"""

    return f"""# Candidate Information

## Basic Details
- Name: {CANDIDATE_FIRST_NAME} {CANDIDATE_LAST_NAME}
- Email: {CANDIDATE_EMAIL}
- LinkedIn: {CANDIDATE_LINKEDIN}
- GitHub: {CANDIDATE_GITHUB}

## Education
{education_section}

## Overall Profile
{OVERALL_CANDIDATE_PROFILE}

## Skills
{CANDIDATE_SKILLS}

## Experience
{CANDIDATE_EXPERIENCE}

## Projects
{CANDIDATE_PROJECTS}

## Certifications
{CANDIDATE_CERTIFICATIONS}

## Personality
{CANDIDATE_PERSONALITY}"""


def get_candidate_profile_dict():
    """
    Returns candidate information as a structured dictionary.
    Useful for JSON serialization or structured data access.
    """
    return {
        "first_name": CANDIDATE_FIRST_NAME,
        "last_name": CANDIDATE_LAST_NAME,
        "email": CANDIDATE_EMAIL,
        "phone": CANDIDATE_PHONE_NUMBER,
        "linkedin": CANDIDATE_LINKEDIN,
        "github": CANDIDATE_GITHUB,
        "resume_path": CANDIDATE_RESUME_FILE_PATH,
        "education": CANDIDATE_EDUCATION,
        "overall_profile": OVERALL_CANDIDATE_PROFILE,
        "skills": CANDIDATE_SKILLS,
        "experience": CANDIDATE_EXPERIENCE,
        "projects": CANDIDATE_PROJECTS,
        "certifications": CANDIDATE_CERTIFICATIONS,
        "personality": CANDIDATE_PERSONALITY,
    }


def get_candidate_context_for_job_evaluation():
    """
    Returns a concise candidate context specifically for job evaluation/filtering.
    """
    return f"""# Overall Candidate Profile:
{OVERALL_CANDIDATE_PROFILE}

# Candidate Skills:
{CANDIDATE_SKILLS}

## Experience:
{CANDIDATE_EXPERIENCE}

## Projects:
{CANDIDATE_PROJECTS}

## Certifications:
{CANDIDATE_CERTIFICATIONS}

# Candidate's Personality:
{CANDIDATE_PERSONALITY}"""
