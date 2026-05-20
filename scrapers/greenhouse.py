import requests

COMPANY_SLUGS = ['hubspot', 'anthropic', 'gleanwork', 'spacex', 'verkada', 
                 'engine',
                 'calendly',
                 'superserve',
                 'formic',
                 'natera',
                 'nebius',
                 'galileofinancialtechnologies',
                 'networkoptix',
                 'onetrust',
                 'atomicmachines',
                 'fireworksai',
                 'planetlabs',
                 'veza',
                 'Moloco',
                 'kikoff',
                 'pubmatic',
                 'upstart',
                 'abnormalsecurity',
                 'motional',
                 'earnest',
                 'astranis',
                 'nexhealth',
                 'dropbox',
                 'kodiak',
                 'crunchyroll',
                 'vivodyne',
                 'flexport',
                 'amperesand',
                 'lively43',
                 'zoominfo',
                 'atomicmachines',
                 'fireworksai',
                 'altruist',
                 'figma',
                 'airtable',
                 'thatch',
                 'dataiku',
                 'checkr',
                 'codepath',
                 'skildai-careers',
                 'doordashusa',
                 'canonical',
                 'samsungsemiconductor',
                 'samsungresearchamerica',
                 'lucidmotors',
                 'partnerstack',
                 'brex',
                 'agoda',
                 'ouihelp',
                 ]


def fetch_jobs(slug):
    url = f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs'
    try:
        r = requests.get(url, params={"content": "true"}, timeout=10)
        r.raise_for_status()
        clean_jobs_list = []
        jobs = r.json()['jobs']
        for j in jobs:
            clean_jobs_list.append({
                "gh_job_id": j["id"],
                "internal_job_id": j["internal_job_id"],
                "title": j["title"],
                "company": j["company_name"],
                "location": j["location"]["name"],
                "url": j["absolute_url"],
            })
        return clean_jobs_list

    except requests.exceptions.HTTPError as e:
        print(f'Fetch for {slug} jobs failed: {e}')
        return []



def fetch_all_greenhouse_jobs():
    result = []
    for slug in COMPANY_SLUGS:
        result.extend(fetch_jobs(slug))
    return result

all_jobs = fetch_all_greenhouse_jobs()
print(f"\nTotal jobs found: {len(all_jobs)}")
