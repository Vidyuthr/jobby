# agent/filter.py

import json
import time
import os
from dotenv import load_dotenv
from groq import Groq
from scrapers import greenhouse


load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

filtered_greenhouse_jobs = greenhouse.get_all_gh_jobs_filtered()[0:10]


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
                    {os.getenv('OVERALL_CANDIDATE_PROFILE')}
                    
                    # Candidate Skills:
                    {os.getenv('CANDIDATE_SKILLS')}

                    ## Experience:
                    {os.getenv('CANDIDATE_EXPERIENCE')}

                    ## Projects:
                    {os.getenv('CANDIDATE_PROJECTS')}

                    ## Certifications: 
                    {os.getenv('CANDIDATE_CERTIFICATIONS')}

                    # Candidate's Personality:
                    {os.getenv('CANDIDATE_PERSONALITY')}
                    

                    # How to Respond
                    - Respond with only this JSON array format: each job evaluation item in the array is a JSON like this:
                    {
                    'title': '___',
                    'company': '___',
                    'relevant': 'true/false (commit to a decisive true or false, no grey area)',
                    'matching_skills': 'list containing all the tech skills that match well with candidate like [Python, React, etc]',
                    'reason': '2 sentence explanation that does not include work authorization in US as reason, because candidate is authorized in US.'
                    }
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
        parsed_json_evaluation = json.loads(chat_completion.choices[0].message.content)
        evaluations.append(parsed_json_evaluation)
    return evaluations

test_evals = groq_batch_evaluate_jobs(filtered_greenhouse_jobs)

def get_jobs_to_apply(groq_evaluations):
    flat_list = [eval for sublist in groq_evaluations for eval in sublist]
    return [eval for eval in flat_list if eval['relevant']]
