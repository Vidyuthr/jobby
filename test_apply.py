"""
Test script for job application automation.
Run with: python test_apply.py
"""

from agent.apply import apply_to_single_job


def test_apply_to_single_job(job):
    """Test applying to a single job."""
    print(f"\n🧪 Testing application to {job['company']} - {job['title']}")
    print(f"URL: {job['url']}\n")
    success = apply_to_single_job(job)

    print(f"\n{'='*60}")
    if success:
        print(f"✅ TEST RESULT: Application submitted successfully!")
    else:
        print(f"⚠️ TEST RESULT: Application skipped (form not fully automatable)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    test_job = {
        "title": "Software Engineer - Backend Services",
        "company": "Truveta",
        "url": "https://job-boards.greenhouse.io/truveta/jobs/6002807004?gh_src=Simplify",
    }

    test_apply_to_single_job(test_job)
