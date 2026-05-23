# agent/filter.py

import json
import time
import os
from dotenv import load_dotenv
from groq import Groq
from scrapers import greenhouse


load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

CANDIDATE_FIRST_NAME = 'Vidyuth'
CANDIDATE_LAST_NAME = 'Ramkumar'
CANDIDATE_EMAIL = 'vidyuth.ramkumar@gmail.com'
CANDIDATE_LINKEDIN = 'https://www.linkedin.com/in/vidyuth-ramkumar/'
OVERALL_CANDIDATE_PROFILE = "- Name: Vidyuth Subbiah Ramkumar - Education: BS Computer Science + Business Administration, Northeastern University Honors Program, May 2026. Dean\'s List. - Experience level: roughly 2 years, targeting strong new grad / junior roles - Target roles: Vidyuth is looking for full-time permanent roles or internships only, not research fellowships or contractor positions. AI/ML Engineer, Software Engineer, Product roles, at AI startups. If not, moderately relevant roles are fine too. - Open to: all roles in USA. Vidyuth is open to relocation within the USA - Work authorization: Vidyuth has work authorization as he is a permanent resident of the USA and he does NOT require any visa sponsorship."
CANDIDATE_SKILLS = "Languages: Python, JavaScript, TypeScript, SQL, Swift, Java\nFrameworks & Tools: TensorFlow, Scikit-learn, HuggingFace, Redis, Apache Spark, Apache Airflow, NumPy, Pandas, Databricks, Docker, PostgreSQL, MongoDB, Firebase, React JS, Node JS, Tailwind, Stripe\nAI/ML: Machine Learning, LLMs, RAG pipelines, Deep Learning, Feature Engineering, Model Evaluation, Agents"
CANDIDATE_EXPERIENCE = "- Beatleaf (Co-Founder): Full stack version control software for music producers , React/Express/PostgreSQL/Supabase, audio version control, 30+ users. strong product/startup understanding of PMF, market/user interviewing, engineering prioritization, etc.\n- Credit One Bank (SWE Intern): Production data engineering including complex SQL, Apache Airflow, Spark to help monitor internal data platform that handled complex and vast data in 300 terabytes\n- Objectways (AI/ML Engineer, Jun 2024 - Dec 2024): Engineered production full stack Express.js backend with Firebase NoSQL Firestore database, Python LLM tokenization service, and Stripe payment processing for Sheetwise — an AI-powered Google Sheets extension with 220+ organic user signups and multiple paid subscribers on Google Sheets Marketplace. Built production Databricks RAG pipelines in Python, Spark, and SQL powering a customer support chatbot (60% faster response time) and a vehicle AI assistant (85% accuracy across 300+ models).\n- Sparrow (Tech Intern): Python web scraping via BS4 and requests, HTML work, PowerBI work"
CANDIDATE_PROJECTS = "- Safe Stack Overflow: Full stack Q&A platform with AI content moderation\n- Nightcap: React Native IoT sleep startup, 12,000+ views on social media, finalist in University startup challenge. Product was not built"
CANDIDATE_CERTIFICATIONS = "Stanford ML Specialization (Supervised learning, deep learning, and reinforcement learning),CrewAI Building MultiAgent Systems, Databricks basics (ML + Data Engineering), Google LLM/GenAI, Anthropic Agent Skills"
CANDIDATE_PERSONALITY = "- Very very curious and eager to learn everything deeply. Constant learner, loves new things. Asks lots of questions. Passionate. - Constantly thinks of ideas, being a two-time founder. Always thinking how to improve processes/operations, or just ideas in general for products/solutions/features. - Approachable, kind, and loves to work with people, able to explain/present very very well due to speech & debate nationalist in highschool and many startup pitches/competitions – so he has soft skills and presentation skills to both technical and non-technical audiences"



filtered_greenhouse_jobs = greenhouse.get_all_gh_jobs_filtered()


def custom_batched(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]



def groq_batch_evaluate_jobs(jobs):
    evaluations = []
    for batch_number, job_batch in enumerate(custom_batched(jobs, 3), start = 1):
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    # Your Role
                    You are a job relevance filter for a new graduate software engineer.
                    Evaluate whether a job is a good fit and return only valid JSON with no markdown or explanation.

                    # Overall Candidate Profile:
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
                    {CANDIDATE_PERSONALITY}
                    

                    # How to Respond
                    - Respond with only this JSON array format: each job evaluation item in the array is a JSON like this:
                    {{
                    "title": "___",
                    "company": "___",
                    "url": "___",
                    "gh_job_id": "___"
                    "relevant": true or false (use lowercase JSON boolean, not a string)",
                    "matching_skills": "list containing all the tech skills that match well with candidate like [Python, React, etc]",
                    "reason": "2 sentence explanation that does not include work authorization in US as reason, because candidate is authorized in US."
                    }}
                    - Multiple of these JSON evaluation items in an array
                    - Only give that array, nothing before or after, so that it is parsable in code.
                    """
                },
                {
                    "role": "user",
                    "content": f"The jobs: {job_batch}"
                }
            ],
            model="llama-3.1-8b-instant",
        )
        print(f"Processed BATCH #{batch_number}.")
        time.sleep(2)
        raw = chat_completion.choices[0].message.content
        # Replace Python booleans with JSON booleans
        sanitized = raw.replace('True', 'true').replace('False', 'false')
        parsed_json_evaluation = json.loads(sanitized)
        evaluations.append(parsed_json_evaluation)
    return evaluations

llm_evals = groq_batch_evaluate_jobs(filtered_greenhouse_jobs)

def get_jobs_to_apply(groq_evaluations):
    flat_list = [eval for sublist in groq_evaluations for eval in sublist]
    return [eval for eval in flat_list if eval['relevant'] == True]