"""
Test script for job application automation.
Run with: python test_apply.py
"""

from agent.apply import apply_to_single_job


def test_apply_to_single_job(job):
    """Test applying to a single job by key."""
    # if job_key not in TEST_JOBS:
    #     print(f"❌ Unknown job key: {job_key}")
    #     print(f"Available jobs: {', '.join(TEST_JOBS.keys())}")
    #     return

    # job = TEST_JOBS[job_key]
    # print(f"\n🧪 Testing application to {job['company']} - {job['title']}")
    # print(f"URL: {job['url']}\n")
    apply_to_single_job(job)


# if __name__ == "__main__":
#     # Change this to test different jobs
#     test_single_job(job)