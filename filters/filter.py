# filters/filter.py

import json
import time
import os
from dotenv import load_dotenv
from groq import Groq
from scrapers.greenhouse import get_all_gh_jobs_filtered
from config.candidate import get_candidate_context_for_job_evaluation

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


filtered_greenhouse_jobs = get_all_gh_jobs_filtered()


def custom_batched(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def groq_batch_evaluate_jobs(jobs):
    evaluations = []
    candidate_context = get_candidate_context_for_job_evaluation()

    for batch_number, job_batch in enumerate(custom_batched(jobs, 3), start=1):
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    # Your Role
                    You are a job relevance filter for a new graduate software engineer.
                    Evaluate whether a job is a good fit and return only valid JSON with no markdown or explanation.

                    {candidate_context}

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
                    """,
                },
                {"role": "user", "content": f"The jobs: {job_batch}"},
            ],
            model="llama-3.1-8b-instant",
        )
        print(f"Processed BATCH #{batch_number}.")
        time.sleep(2)
        raw = chat_completion.choices[0].message.content
        if raw is None:
            raise ValueError("Received empty response from Groq API")
        print(raw)
        # Replace Python booleans with JSON booleans
        sanitized = raw.replace("True", "true").replace("False", "false")
        parsed_json_evaluation = json.loads(sanitized)
        evaluations.append(parsed_json_evaluation)
    return evaluations


def get_jobs_to_apply(groq_evaluations):
    flat_list = [eval for sublist in groq_evaluations for eval in sublist]
    return [eval for eval in flat_list if eval["relevant"] == True]


if __name__ == "__main__":
    llm_evals = groq_batch_evaluate_jobs(filtered_greenhouse_jobs)
    jobs_to_apply = get_jobs_to_apply(llm_evals)
    print(f"\n{len(jobs_to_apply)} relevant jobs found.")
