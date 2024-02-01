import os
import requests
from datetime import datetime
import pandas as pd
from urllib.parse import urlparse, parse_qs
from config import Configdice

class Wrapper:
    def __init__(self):
        self.config = Configdice()

    def parse_url(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        q = query_params.get('q', [None])[0]
        location = query_params.get('location', [None])[0]
        latitude = query_params.get('latitude', [None])[0]
        longitude = query_params.get('longitude', [None])[0]

        return q, location, latitude, longitude

    def fill_location(self, row):
        return 'Remote' if row['Work type(remote/on-site)'] else 'Hybrid/Onsite'

    def run(self):
        # Create the output directory if it doesn't exist
        output_path = os.path.join(self.config.OUTPUT_CSV_PATH, self.config.output_csv)
        os.makedirs(self.config.OUTPUT_CSV_PATH, exist_ok=True)

        for keyword in self.config.KEYWORDS:
            params = self.get_params(keyword)

            response = requests.get(
                self.config.URL,
                params=params,
                headers=self.config.HEADERS,
                timeout=30,
            ).json()

            try:
                data = response["data"]
            except Exception as e:
                print(f"Sorry could not get the data for {keyword}: {e}")
                continue

            if data:
                df = pd.DataFrame(data)
                df['jobLocation'] = df['jobLocation'].apply(lambda x: x['displayName'] if isinstance(x, dict) and 'displayName' in x else None)
                df1 = df[['id', 'title', 'postedDate', 'detailsPageUrl', 'jobLocation', 'salary', 'companyName', 'employmentType',
                          'workFromHomeAvailability', 'isRemote', 'modifiedDate']]
                df1.rename(columns=self.get_column_mapping(), inplace=True)
                df1['Current date time'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                df1['Work type(remote/on-site)'] = df1.apply(self.fill_location, axis=1)
                df1['Job Title'] = keyword  # Add a new column for the job title
                df1.to_csv(output_path, mode='a', header=not os.path.exists(output_path), index=False)
                print(f'Successfully saved the data for {keyword}')
            else:
                print(f"Sorry we can't get the data for {keyword}. Please try again with correct url or keywords")

    def get_params(self, keyword):
        if self.config.SEARCH_TYPE == '1':
            return self.get_keyword_params(keyword)
        elif self.config.SEARCH_TYPE == '2':
            return self.get_url_params(keyword)
        else:
            print("Invalid search type")
            return {}

    def get_keyword_params(self, keyword):
        return {
            "q": keyword,
            "countryCode2": "US",
            "radius": "30",
            "radiusUnit": "mi",
            "page": "1",
            "pageSize": "100",
            "facets": "employmentType|postedDate|workFromHomeAvailability|employerType|easyApply|isRemote",
            "fields": "id|jobId|guid|summary|title|postedDate|modifiedDate|jobLocation.displayName|detailsPageUrl|salary|clientBrandId|companyPageUrl|companyLogoUrl|positionId|companyName|employmentType|isHighlighted|score|easyApply|employerType|workFromHomeAvailability|isRemote|debug",
            "culture": "en",
            "recommendations": "true",
            "interactionId": "0",
            "fj": "true",
            "includeRemote": "true",
            "filters.employmentType": "CONTRACTS|PARTTIME"
        }

    def get_url_params(self, keyword):
        q, location, latitude, longitude = self.parse_url(keyword)
        return {
            "countryCode2": "US",
            "radius": "100",
            "radiusUnit": "mi",
            "page": "1",
            "q": q,
            "locationPrecision": 'city',
            "latitude": latitude,
            "longitude": longitude,
            "pageSize": "100",
            "facets": "employmentType|postedDate|workFromHomeAvailability|employerType|easyApply|isRemote",
            "fields": "id|jobId|guid|summary|title|postedDate|modifiedDate|jobLocation.displayName|detailsPageUrl|salary|clientBrandId|companyPageUrl|companyLogoUrl|positionId|companyName|employmentType|isHighlighted|score|easyApply|employerType|workFromHomeAvailability|isRemote|debug",
            "culture": "en",
            "recommendations": "true",
            "interactionId": "0",
            "fj": "true",
            "includeRemote": "true",
            "filters.employmentType": "CONTRACTS|PARTTIME"
        }

    def get_column_mapping(self):
        return {
            'id': 'Job_id',
            'companyName': 'Vendor company name',
            'title': 'Job title',
            'employmentType': 'Job type',
            'salary': 'Pay rate',
            'detailsPageUrl': 'Job posting url',
            'jobLocation': 'Job location',
            'postedDate': 'Job posting date',
            'isRemote': 'Work type(remote/on-site)',
            'workFromHomeAvailability': 'Work from availability',
            'modifiedDate': 'Modified Date'
        }


if __name__ == "__main__":
    wrapper = Wrapper()
    wrapper.run()
