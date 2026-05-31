# main.py

from filters.filter import groq_batch_evaluate_jobs, get_jobs_to_apply, filtered_greenhouse_jobs
from agent.apply import apply_to_single_job


def main():
    """
    Main entry point for the job application agent.

    Workflow:
    1. Fetch filtered greenhouse jobs from scrapers
    2. Evaluate jobs using LLM to determine relevance
    3. Filter to only relevant jobs
    4. Apply to each relevant job
    """
    print(f"Found {len(filtered_greenhouse_jobs)} filtered greenhouse jobs.")

    # Evaluate jobs using LLM
    print("\nEvaluating jobs with LLM...")
    llm_evaluations = groq_batch_evaluate_jobs(filtered_greenhouse_jobs)

    # Get only relevant jobs
    jobs_to_apply = get_jobs_to_apply(llm_evaluations)
    for i in jobs_to_apply:
        print(i)
        print('-')

    # Apply to each relevant job
    # if jobs_to_apply:
    #     print("\nApplying to jobs...")
    #     for job in jobs_to_apply:
    #         print(f"\nApplying to {job['title']} at {job['company']}")
    #         apply_to_single_job(job)
    #     print(f"\nCompleted applying to {len(jobs_to_apply)} jobs!")
    # else:
    #     print("\nNo relevant jobs to apply to.")


if __name__ == "__main__":
    main()
