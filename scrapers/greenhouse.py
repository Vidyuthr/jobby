import html
import requests
from bs4 import BeautifulSoup as bs

COMPANY_SLUGS = ['hubspot', 
                #  'anthropic', 
                 'gleanwork', 'spacex', 'verkada', 
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

# Helper for fetch_jobs()
# Gets the most relevant portions of the job description
def extract_relevant_description(text):
    keywords = [
        'You Will', 'You\'ll', 'Responsibilities', 'Requirements',
        'What You', 'You Have', 'Experience', 'Qualifications',
        'We Are Looking', 'About the Role', 'Who You',
        'you will', 'you\'ll', 'responsibilities', 'requirements', 
        'what you', 'you have', 'experience', 'qualifications', 
        'we are looking', 'about the role', 'who you'
    ]
    excerpts = []
    seen_positions = []
    low_priority_indices = []
    for kw in keywords:
        idx = text.lower().find(kw)
        if idx != -1:
            # avoid grabbing overlapping sections
            if not any(abs(idx - pos) < 200 for pos in seen_positions):
                current_excerpt = text[idx:idx + 800]
                seen_positions.append(idx)
                
                if len(excerpts) < 2:
                    excerpts.append(current_excerpt)
                    if not current_excerpt[0].isupper():
                        low_priority_indices.append(len(excerpts) - 1)
                elif low_priority_indices and current_excerpt[0].isupper():
                    # replace the first low priority excerpt with this better one
                    replace_idx = low_priority_indices.pop(0)
                    excerpts[replace_idx] = current_excerpt
        if len(excerpts) == 2:
            break
    return ' ... '.join(excerpts)

# Gets active job postings for a given company
def fetch_jobs(slug):
    url = f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs'
    try:
        r = requests.get(url, params={"content": "true"}, timeout=30)
        r.raise_for_status()
        clean_jobs_list = []
        jobs = r.json()['jobs']
        for j in jobs:
            description_html = html.unescape(j["content"])
            description_soup = bs(description_html, 'html.parser')
            clean_description_text = description_soup.get_text()
            relevant_description_text = extract_relevant_description(clean_description_text)
            clean_jobs_list.append({
                "gh_job_id": j["id"],
                "internal_job_id": j["internal_job_id"],
                "title": j["title"],
                "company": j["company_name"],
                "description": relevant_description_text,
                "location": j["location"]["name"],
                "url": j["absolute_url"],
            })
        return clean_jobs_list

    except requests.exceptions.HTTPError as e:
        print(f'Fetch for {slug} jobs failed: {e}')
        return []
    except requests.exceptions.ReadTimeout:
        print(f'{slug}: timed out, skipping')
        return []


# Gets all active job postings currently on Greenhouse job board, across all companies
# Loops through COMPANY_SLUGS and calls GH Job Board API with each slug, aggregating all the job postings for all the companies
def fetch_all_greenhouse_jobs():
    result = []
    for slug in COMPANY_SLUGS:
        result.extend(fetch_jobs(slug))
    return result

all_jobs = fetch_all_greenhouse_jobs()



# filters to:
# new grad level (omitting senior/executive/founder-related roles)
# swe/ai/ml/product related (omitting all irrelevant roles like Cybersecurity, Data Center Technician, IT Support,
# Medical-related, Accounting, Sales reps, etc)

# {'gh_job_id': 5221910008, 
# 'internal_job_id': 4475499008,
# 'title': 'Account Executive, Beneficial Deployments (French Speaking)',
# 'company': 'Anthropic',
# 'location': 'Dublin, IE;
# London, UK',
# 'url': 'https://job-boards.greenhouse.io/anthropic/jobs/5221910008'}

def filter_all_gh_jobs():
    bad_keywords = {'senior', 'recruit', 'principal', 'architect', 'manager', 
                'director', 'sales', 'founder', 'ceo', 'coo', 'chief', 
                'president', 'vice'}
    irrelevant_domains = {'electrical', 'mechanical', 'cyber', 'embedded', 
                      'firmware', 'hardware', 'chip', 'account', 'legal', 
                      'finance', 'design', 'operations', 'people'}
    
    all_bad = bad_keywords | irrelevant_domains
    relevant_jobs = [j for j in all_jobs if not any(kw in j['title'].lower() for kw in all_bad)]
    usa_jobs = [j for j in relevant_jobs if 'united states' in j["location"].lower()]

    return usa_jobs
 
filtered = filter_all_gh_jobs()
for i in filtered[0:5]:
    print('--------------------------------------------------------------------------------')
    print(i['title'])
    print(i['description'])
