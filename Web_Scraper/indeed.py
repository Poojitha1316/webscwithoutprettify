import pandas as pd 
import numpy as np 
import warnings
warnings.filterwarnings('ignore')
from bs4 import BeautifulSoup
import time
import json
import requests
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from config import Configindeed
import re
import random
import os

# %%
user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
]


# %%
def find_job_types(attributes_list):
    for attr in attributes_list:
        if 'job-types' in attr.get('label', ''):
            if 'attributes' in attr:
                for sub_attr in attr['attributes']:
                    if 'label' in sub_attr:
                        return sub_attr['label']
            return None

def format_salary_range(salary_range):
    if 'min' in salary_range and 'max' in salary_range and 'type' in salary_range:
        min_salary = '${:,.2f}'.format(salary_range['min']) if salary_range['min'] != salary_range['max'] else '$0.00'
        max_salary = '${:,.2f}'.format(salary_range['max'])
        salary_type = salary_range['type'].lower().capitalize()

        return f"{min_salary} - {max_salary} a {salary_type}"
    else:
        return None
def fill_location(row):
    if row['Job Location']:
        return 'Remote'
    else:
        return 'Hybrid/On Site'
column_mapping = {
    'company': 'Company',
    'salary_text': 'Salary',
    'pub_date': 'Date Posted',
    'display_title': 'Title',
    'job_location': 'Location',
    'job_key': 'Job ID',
    'view_job_link': 'Job Link',
    'job_types': 'Job Type',
    'job_key': 'Job ID'
}


# %%
def get_data(soup):
    
    z=soup.find('script',id='mosaic-data')
    script_content = str(z.string)
    pattern = re.compile(r'window\.mosaic\.providerData\["mosaic-provider-jobcards"\]\s*=\s*({.*?});', re.DOTALL)
    match = pattern.search(script_content)
    if match:
        json_data = match.group(1)
        parsed_data = json.loads(json_data)
        # print(parsed_data)
    else:
        print("No match found.")
    w=parsed_data['metaData']
    y=w['mosaicProviderJobCardsModel']
    x=y['results']
    all_inner_dfs=[]
    for i in x:
        fields_to_extract = [
        'company', 'formattedLocation','remoteLocation','estimatedSalary','extractedSalary',
        'jobkey', 'pubDate', 'taxonomyAttributes', 'viewJobLink', 'title'
        ]
        extracted_data = {field: i.get(field) for field in fields_to_extract}
        extracted_salary = extracted_data.get('extractedSalary')
        estimated_salary = extracted_data.get('estimatedSalary')

        if extracted_salary is not None:
            salary_text = format_salary_range(extracted_salary)
        elif estimated_salary is not None:
            salary_text = format_salary_range(estimated_salary)
        else:
            salary_text = None
        pub_date = datetime.utcfromtimestamp(extracted_data['pubDate'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        company = extracted_data['company']
        display_title = extracted_data.get('title', '')
        job_location = extracted_data.get('formattedLocation', '')
        job_key = extracted_data.get('jobkey', '')
        view_job_link = extracted_data.get('viewJobLink', '')
        job_types = find_job_types(extracted_data['taxonomyAttributes'])
        remotelocation=extracted_data['remoteLocation']
        df = pd.DataFrame({
            'company': [company],
            'salary_text': [salary_text],
            'pub_date': [pub_date],
            'display_title': [display_title],
            'job_location': [job_location],
            
            'job_key': [job_key],
            'view_job_link': [view_job_link],
            'job_types': [job_types],
            'Job Location':[remotelocation]
            
        })
        df['Current Date Time']=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df['Remote / Hybrid'] = df.apply(fill_location, axis=1)
        df['view_job_link']='https://www.indeed.com'+df['view_job_link']
        df.rename(columns=column_mapping, inplace=True)
        df.drop(columns='Job Location',axis=1,inplace=True)
        all_inner_dfs.append(df)
    dfs=pd.concat(all_inner_dfs,ignore_index=True)
    return dfs

# %%
# output=input('Please Enter the name you want to save your file:')+('.csv')
# keyword=input('Please Enter the keyword you want to collect the data :')
# output = Config.output_csv
# keyword = Config.keyword


output_directory = Configindeed.output_directory
subdirectory = Configindeed.subdirectory
os.makedirs(os.path.join(output_directory, subdirectory), exist_ok=True)

all_outer_dfs = []
for keyword in Configindeed.keywords:
    Configindeed.keyword = keyword
    # Configindeed.output_csv = Configindeed.output_csv.format(keyword=keyword.replace(" ", "_"))
    # Configindeed.output_csv = Configindeed.output_csv
    # Configindeed.output_csv_path = os.path.join(output_directory, subdirectory, Configindeed.output_csv)
    
    for i in range(0, 120, 10):
        url = Configindeed.url_template.format(keyword=Configindeed.keyword, page=i)
        user_agent = random.choice(Configindeed.user_agent_list)
        proxy = Configindeed.proxy
        proxies = {"http": proxy, "https": proxy}
        headers = {'User-Agent': user_agent}

        try:
            response = requests.get(url, headers=headers, proxies=proxies, verify=False)
            response.raise_for_status()
            print('Success!')

            soup = BeautifulSoup(response.content, 'html.parser')
            df1 = get_data(soup)

            if df1 is not None:
                all_outer_dfs.append(df1)
                print(f'Success for page {i} - {Configindeed.keyword}')
            else:
                print(f'Sorry, no data found for {Configindeed.keyword} on page {i}. Either you entered the keyword wrong or connection aborted.')

        except requests.RequestException as e:
            print(f"Error: {e}")
            print(f"Sorry, the website blocked your connection or there was another error. Status Code: {response.status_code}")

# %%
final_df=pd.concat(all_outer_dfs,ignore_index=True)
final_df=final_df[final_df['Job Type']!='Full-time']
final_df.drop_duplicates(inplace=True)


# %%
# final_df.to_csv(Config.output_csv,index=False)
output_path = Configindeed.output_csv_path
if not os.path.exists(output_path):
    os.makedirs(output_path)
final_df.to_csv(os.path.join(output_path, Configindeed.output_csv), index=False)
# final_df.to_csv(Configindeed.output_csv_path, index=False)