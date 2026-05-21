
import time
import os
from dotenv import load_dotenv
from itertools import batched

from groq import Groq
from scrapers import greenhouse


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

filtered_jobs = greenhouse.filter_all_gh_jobs()


def custom_batched(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

batch_number = 1

for batch in custom_batched(filtered_jobs, 5):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """
                # Your Role
                You are a job relevance filter for a new graduate software engineer. 
                Evaluate whether a job is a good fit and return only valid JSON with no markdown or explanation.
                
                # Overall Candidate Profile:
                - Name: Vidyuth Subbiah Ramkumar
                - Education: BS Computer Science + Business Administration, Northeastern University Honors Program, May 2026. Dean's List.
                - Experience level: roughly 2 years, targeting strong new grad / junior roles
                - Target roles: AI/ML Engineer, Software Engineer, Product roles, at AI startups. If not, moderately relevant roles are fine too.
                - Open to: all roles in USA
                
                # Vidyuth's Background:
                Languages: Python, JavaScript, TypeScript, SQL, Swift, Java
                Frameworks & Tools: TensorFlow, Scikit-learn, HuggingFace, Redis, Apache Spark, Apache Airflow, NumPy, Pandas, Databricks, Docker, PostgreSQL, MongoDB, Firebase, React JS, Node JS, Tailwind, Stripe
                AI/ML: Machine Learning, LLMs, RAG pipelines, Deep Learning, Feature Engineering, Model Evaluation, Agents

                ## Experience:
                - Beatleaf (Co-Founder): Full stack version control software for music producers , React/Express/PostgreSQL/Supabase, audio version control, 30+ users. strong product/startup understanding of PMF, market/user interviewing, engineering prioritization, etc.
                - Credit One Bank (SWE Intern): Production data engineering including complex SQL, Apache Airflow, Spark to help monitor internal data platform that handled complex and vast data in 300 terabytes
                - Objectways (AI/ML Engineer, Jun 2024 - Dec 2024): Engineered production full stack Express.js backend with Firebase NoSQL Firestore database, Python LLM tokenization service, and Stripe payment processing for Sheetwise — an AI-powered Google Sheets extension with 220+ organic user signups and multiple paid subscribers on Google Sheets Marketplace. Built production Databricks RAG pipelines in Python, Spark, and SQL powering a customer support chatbot (60% faster response time) and a vehicle AI assistant (85% accuracy across 300+ models).
                - Sparrow (Tech Intern): Python web scraping via BS4 and requests, HTML work, PowerBI work

                ## Projects:
                - Safe Stack Overflow: Full stack Q&A platform with AI content moderation
                - Nightcap: React Native IoT sleep startup, 12,000+ views on social media, finalist in University startup challenge. Product was not built

                ## Certifications: Stanford ML Specialization (Supervised learning, deep learning, and reinforcement learning), CrewAI Building MultiAgent Systems, Databricks basics (ML + Data Engineering), Google LLM/GenAI, Anthropic Agent Skills

                # How to Respond
                - Respond with only this JSON array format: each job evaluation item in the array is a JSON like this: {"title": ___, "company": ___, "relevant": true/false, "reason": “2 sentence explanation"}
                - Multiple of these JSON evaluation items in an array
                - Only give that array, nothing before or after, so that it is parsable in code.
                """
            },
            {
                "role": "user",
                "content": f"The jobs: {batch}"
            }
        ],
        model="llama-3.1-8b-instant",
    )
    print(f"Processed BATCH #{batch_number}.")
    time.sleep(2)

