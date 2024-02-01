import re
import os
import time
import json
import random
import warnings
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from config import Configcareer
from datetime import datetime,timedelta
from urllib.parse import urlparse, parse_qs
warnings.filterwarnings('ignore')

user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
]

user_agent = random.choice(user_agent_list)
headers = {'User-Agent': user_agent,}
proxy = Configcareer.PROXY
proxies = {"http": proxy, "https": proxy}

# %%

def categorize_work_type(title):
    if 'Onsite' in title:
        return 'On-site'
    elif 'Hybrid' in title:
        return 'Hybrid'
    elif 'Remote' in title:
        return 'Remote'
    else:
        return None 

def convert_relative_dates(relative_date):
    try:
        if 'today' in relative_date or 'Today' in relative_date:
            return datetime.now().date()
        elif 'yesterday' in relative_date or '1 day ago' in relative_date:
            return (datetime.now() - timedelta(days=1)).date()
        elif 'days ago' in relative_date:
            days_ago = int(relative_date.split()[0])
            return (datetime.now() - timedelta(days=days_ago)).date()
        else:
            return None  # Handle other cases as needed
    except Exception as e:
        # print(f"Error in convert_relative_dates: {e}")
        return None


def get_data(soup):
    try:
        a = soup.find_all('div', class_='collapsed-activated')
        all_inner_dfs = []

        for i in a:
            b = BeautifulSoup(str(i), 'html.parser')
            c = b.find_all('li', class_='data-results-content-parent relative bg-shadow')

            all_innermost_dfs = []

            for j in c:
                inner_job_listings = []
                d = BeautifulSoup(str(j), 'html.parser')
                job_data = {}
                
                try:
                    # Extracting data
                    job_data['publish_time'] = d.find('div', class_='data-results-publish-time').text.strip()
                    job_data['title'] = d.find('div', class_='data-results-title').text.strip()
                    job_data['company'] = d.find('div', class_='data-details').find('span').text.strip()
                    job_data['location'] = d.find('div', class_='data-details').find_all('span')[1].text.strip()
                    job_data['employment_type'] = d.find('div', class_='data-details').find_all('span')[2].text.strip()
                    job_url = j.find('a', class_='data-results-content')['href']
                    job_data['url'] = f"https://www.careerbuilder.com{job_url}"
                    result = d.select('div.block:not(.show-mobile)')
                    job_data['result'] = result[0].get_text(strip=True)
                    
                    inner_job_listings.append(job_data)
                    df = pd.DataFrame(inner_job_listings)
                    all_innermost_dfs.append(df)

                except Exception as e:
                    # print(f"Error in inner loop: {e}")
                    continue  # Skip this iteration if there's an error

            try:
                df2 = pd.concat(all_innermost_dfs, ignore_index=True)
                all_inner_dfs.append(df2)
            except Exception as e:
                # print(f"Error in outer loop: {e}")
                continue  # Skip this iteration if there's an error

        final_df = pd.concat(all_inner_dfs, ignore_index=True)
        final_df['Work Location'] = final_df['location'].apply(categorize_work_type)
        final_df['Date Posted'] = final_df['publish_time'].apply(convert_relative_dates)
        # Add a new column with today's date
        final_df['Current Date'] = datetime.now().date()
        columns_mapping = {
            'title': 'Title',
            'company': 'Company',
            'location': 'Location',
            'employment_type': 'Job_type',
            'url': 'Job_url',
            'result':'Salary'
        }
        final_df.rename(columns=columns_mapping, inplace=True)

        try:
            # Extract job IDs and create a new column
            final_df['Job_id'] = final_df['Job_url'].str.extract(r'/job/(.*)')
        except AttributeError:
            # Handle the case where the regular expression doesn't match (e.g., if 'Job_url' is not a string)
            final_df['Job_id'] = None

        final_df.drop(columns=['publish_time'], inplace=True)
        return final_df

    except Exception as e:
        # print(f"Error in first try block: {e}")
        # Handle the first type of data here if there's an error

        # Additional except block for unexpected errors
        try:
            c = soup.find_all('li', class_='data-results-content-parent relative bg-shadow')

            all_innermost_dfs = []

            for j in c:
                inner_job_listings = []
                d = BeautifulSoup(str(j), 'html.parser')
                job_data = {}
                
                try:
                    # Extracting data
                    job_data['publish_time'] = d.find('div', class_='data-results-publish-time').text.strip()
                    job_data['title'] = d.find('div', class_='data-results-title').text.strip()
                    job_data['company'] = d.find('div', class_='data-details').find('span').text.strip()
                    job_data['location'] = d.find('div', class_='data-details').find_all('span')[1].text.strip()
                    job_data['employment_type'] = d.find('div', class_='data-details').find_all('span')[2].text.strip()
                    # 
                    result = d.select('div.block:not(.show-mobile)')
                    job_data['result'] = result[0].get_text(strip=True)
                    job_url = j.find('a', class_='data-results-content')['href']
                    job_data['url'] = f"https://www.careerbuilder.com{job_url}"
                    
                    inner_job_listings.append(job_data)
                    df = pd.DataFrame(inner_job_listings)
                    all_innermost_dfs.append(df)

                except Exception as e:
                    # print(f"Error in inner loop: {e}")
                    continue  # Skip this iteration if there's an error

            try:
                df2 = pd.concat(all_innermost_dfs, ignore_index=True)
                final_df=df2
            except Exception as e:
                # print(f"Error in outer loop: {e}")
                pass  # Skip this iteration if there's an error
            # final_df = pd.concat(all_inner_dfs, ignore_index=True)
            final_df['Work Location'] = final_df['location'].apply(categorize_work_type)
            final_df['Date Posted'] = final_df['publish_time'].apply(convert_relative_dates)
            # Add a new column with today's date
            final_df['Current Date'] = datetime.now().date()
            columns_mapping = {
                'title': 'Title',
                'company': 'Company',
                'location': 'Location',
                'employment_type': 'Job_type',
                'url': 'Job_url',
                'result':'Salary'
            }
            final_df.rename(columns=columns_mapping, inplace=True)

            try:
                # Extract job IDs and create a new column
                final_df['Job_id'] = final_df['Job_url'].str.extract(r'/job/(.*)')
            except AttributeError:
                # Handle the case where the regular expression doesn't match (e.g., if 'Job_url' is not a string)
                final_df['Job_id'] = None

            final_df.drop(columns=['publish_time'], inplace=True)
            return final_df

        except Exception as e:
            # print(f"Error in second try block: {e}")
            return None


# %%

# Define the output file name based on the config
# output = Config.OUTPUT_FILENAME_TEMPLATE

output_directory = Configcareer.output_directory
output_subdirectory = Configcareer.subdirectory
output_filename = Configcareer.output_csv
output_path = os.path.join(output_directory, output_subdirectory)
output_file_path = os.path.join(output_path, output_filename)

# Define the keyword based on the config
# keyword = Config.KEYWORD.lower()
dfs = []
soups=[]
session = requests.Session()
try:
    for keyword in Configcareer.KEYWORD:
        keyword_lower = keyword.lower()  # Convert the keyword to lowercase
        for u in range(0, 20):
            # Configcareer.OUTPUT_CSV_PATH = os.path.join(output_directory, output_subdirectory, Configcareer.output_csv)
            url = Configcareer.URL_TEMPLATE.format(keyword=keyword_lower.replace(" ", "%20"), page=u)
        # for u in range(0, 20):
        #     url = Config.URL_TEMPLATE.format(keyword=keyword, page=u)
        
            try:
                response = session.get(url, headers=headers, proxies=proxies, verify=False)
                response.raise_for_status()

                if response.status_code == 200:
                    print('success')
                else:
                    print('Sorry, your connection is blocked by the website')
                    continue  # Skip the rest of the loop for this page

                soup = BeautifulSoup(response.content, 'html.parser')
                soups.append(soup)
                res = get_data(soup)

                if res is None or res.empty:
                    print('Sorry, but the bot did not find proper data on this page')
                    continue

                dfs.append(res)
                print(f'Success for the page: {u}')

            except requests.RequestException as e:
                print(f'Request error for page {u}: {e}')

            except Exception as e:
                print(f'Error for page {u}: {e}')

            time.sleep(5)

except Exception as e:
    print(f'An unexpected error occurred: {e}')

# Continue with the rest of your code (e.g., saving the data to a CSV file)


# final_df=pd.concat(dfs,ignore_index=True)
# final_df.drop_duplicates(inplace=True)

# # Save the data to the specified file path
# output_path = Configcareer.OUTPUT_CSV_PATH
# if not os.path.exists(output_path):
#     os.makedirs(output_path)

# output_file_path = os.path.join(output_path, Configcareer.output_csv)
# final_df.to_csv(output_file_path, index=False)

# if not os.path.exists(output_path):
#     os.makedirs(output_path)
# %%
final_df=pd.concat(dfs,ignore_index=True)
# final_df = final_df[final_df['Title'].str.contains(keyword, case=False)]
final_df.drop_duplicates(inplace=True)

# %%
# final_df.to_csv(output_file_path,index=False)

output_path = Configcareer.OUTPUT_CSV_PATH
if not os.path.exists(output_path):
    os.makedirs(output_path)

final_df.to_csv(os.path.join(output_path, Configcareer.output_csv), index=False)