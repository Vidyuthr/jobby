import html
import re
import requests
from bs4 import BeautifulSoup as bs

COMPANY_SLUGS = ['hubspot', 
                 'anthropic', 
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
# Gets the 2 most relevant excerpts of the job description
# Casing of excerpts is important because it can determine start of certain sections of the job desc.
def extract_relevant_description(text):
    keywords = [
        'You Will', 'You\'ll', 'Responsibilities', 'Requirements',
        'Minimum Qualifications', 'minimum qualifications',
        'Must Have', 'must have',
        'Basic Qualifications', 'basic qualifications',
        'Preferred Qualifications', 'preferred qualifications',
        'What You', 'You Have', 'Experience', 'Qualifications',
        'We Are Looking', 'About the Role', 'Who You',
        'you will', 'you\'ll', 'responsibilities', 'requirements', 
        'what you', 'you have', 'experience', 'qualifications', 
        'we are looking', 'about the role', 'who you'
    ]
    final_excerpts_indices_to_texts = {}
    low_priority_description_indices = [] # positions of excerpts that are lower case (could be mid-sentence or not desc section starting points)
    for kw in keywords:
        idx = text.lower().find(kw)
        if idx != -1:
            # only if idx is NOT within 200 chars of ANY gathered excerpts idx pos'ns
            if not any(abs(idx - pos) < 200 for pos in final_excerpts_indices_to_texts.keys()):
                
                if len(final_excerpts_indices_to_texts) < 2: # still have room for more excerpts?
                    current_excerpt = text[idx:idx + 1100] # slice original text, not text.lower() to maintain casing
                    final_excerpts_indices_to_texts[idx] = current_excerpt
                    if not current_excerpt[0].isupper():
                        low_priority_description_indices.append(idx)
                elif low_priority_description_indices and current_excerpt[0].isupper(): # there is any low priority excerpt index and current excerpt is upper case
                    # replace the first low priority excerpt with this better upper case one
                    replace_idx = low_priority_description_indices.pop(0)
                    final_excerpts_indices_to_texts[replace_idx] = current_excerpt
        if len(final_excerpts_indices_to_texts) == 2 and not low_priority_description_indices:
            break
    final_excerpts_texts = list(final_excerpts_indices_to_texts.values())
    if len(final_excerpts_texts) == 2 and final_excerpts_texts[0][:200].strip() == final_excerpts_texts[1][:200].strip():
        return final_excerpts_texts[0]
    return ' ... '.join(final_excerpts_texts)

TECH_SKILLS = {
    'python', 'javascript', 'typescript', 'java', 'golang', 'rust', 'c++', 'c#', 'swift', 'kotlin', 'ruby', 'scala',
    'react', 'node', 'node.js', 'express', 'django', 'flask', 'fastapi', 'nextjs', 'vue', 'angular',
    'postgresql', 'postgres', 'mysql', 'mongodb', 'redis', 'sqlite', 'dynamodb', 'snowflake', 'bigquery',
    'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'terraform', 'kafka', 'airflow', 'spark', 'databricks',
    'pytorch', 'tensorflow', 'scikit-learn', 'huggingface', 'langchain', 'numpy', 'pandas',
    'llm', 'rag', 'machine learning', 'deep learning', 'computer vision', 'nlp', 'reinforcement learning',
    'graphql', 'rest', 'grpc', 'firebase', 'supabase', 'stripe', 'sql'
}

def extract_tech_skills(text):
    text_lower = text.lower()
    found = []
    for skill in TECH_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return found

# Gets active job postings for a given company
def fetch_jobs_by_company(slug):
    url = f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs'
    try:
        r = requests.get(url, params={"content": "true"}, timeout=30)
        r.raise_for_status()
        clean_jobs_list = []
        jobs = r.json()['jobs']
        for j in jobs:
            description_html = html.unescape(j["content"])
            description_soup = bs(description_html, 'html.parser')
            description_text_without_html = description_soup.get_text()
            relevant_description_text = extract_relevant_description(description_text_without_html)
            clean_jobs_list.append({
                "gh_job_id": j["id"],
                "internal_job_id": j["internal_job_id"],
                "title": j["title"],
                "company": j["company_name"],
                "description": relevant_description_text,
                "main_skills": extract_tech_skills(description_text_without_html),
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
        result.extend(fetch_jobs_by_company(slug))
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

def get_all_gh_jobs_filtered():
    bad_keywords = {'senior', 'recruit', 'principal', 'architect', 'manager', 
                'director', 'sales', 'founder', 'ceo', 'coo', 'chief', 
                'president', 'vice', 'solutions'}
    irrelevant_domains = {'electrical', 'mechanical', 'cyber', 'embedded', 
                      'firmware', 'hardware', 'chip', 'account', 'legal', 
                      'finance', 'design', 'operations', 'people'}
    
    all_bad = bad_keywords | irrelevant_domains
    relevant_jobs = [j for j in all_jobs if not any(kw in j['title'].lower() for kw in all_bad)]
    usa_jobs = [j for j in relevant_jobs if 'united states' in j["location"].lower()]

    return usa_jobs