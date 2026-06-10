"""
Test script for job application automation.
Run with: python test_apply.py
"""

from agent.apply import apply_to_single_job


def test_apply_to_single_job(job):
    """Test applying to a single job."""
    print(f"\n🧪 Testing application to {job['company']} - {job['title']}")
    print(f"URL: {job['url']}\n")
    apply_to_single_job(job)


if __name__ == "__main__":
    test_job = {
        "title": "Staff AI-Native Platform Engineer",
        "company": "Natera",
        "url": "https://job-boards.greenhouse.io/natera/jobs/5838483004",
    }
    test_apply_to_single_job(test_job)