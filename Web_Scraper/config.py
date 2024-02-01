# config.py for zipRecruiter
from datetime import datetime
class Configzip:
    PROXY = "http://4985462b823f2071f48ff52fb687708658d0d488:@proxy.zenrows.com:8001"
    ZIPRECRUITER_SEARCH_URL = "https://www.ziprecruiter.com/jobs-search"
    USER_AGENT_LIST = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    ]
    output_csv = "output_ZipRecruiter.csv"
    output_directory = "output"
    subdirectory = datetime.now().strftime('%Y-%m-%d')

    # Modify this line to include the full path
    OUTPUT_CSV_PATH = f"output/{datetime.now().strftime('%Y-%m-%d')}"
    keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]

# config.py for Indeed
class Configindeed:
    proxy = "http://4985462b823f2071f48ff52fb687708658d0d488:@proxy.zenrows.com:8001"
    url_template = "https://www.indeed.com/jobs?q={keyword}&sc=0kf%3Ajt%28contract%29%3B&page={page}"
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"
    ]

    # Output CSV file name
    # output_csv = "output_.csv"
    output_directory = "output"
    output_csv = "output_Indeed.csv"
    subdirectory = datetime.now().strftime('%Y-%m-%d')

    # Modify this line to include the full path
    output_csv_path = f"output/{datetime.now().strftime('%Y-%m-%d')}"

    # Keywords for job search
    keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]

# config.y for Dice
class Configdice:
    API_KEY = "1YAt0R9wBg4WfsF9VB2778F5CHLAPMVW3WAZcKd8"
    HEADERS = {
        "authority": "job-search-api.svc.dhigroupinc.com",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "x-api-key": API_KEY,
    }
    # CSV_FILENAME = "output_dice.csv"
    output_csv = "output_Dice.csv"
    output_directory = "output"
    subdirectory = datetime.now().strftime('%Y-%m-%d')
    SEARCH_TYPE = "1"

    # Modify this line to include the full path 
    OUTPUT_CSV_PATH = f"{output_directory}/{subdirectory}"
    # f"output/{datetime.now().strftime('%Y-%m-%d')}"
    KEYWORDS = ["Data Analyst", "Business Analyst"]
    # , "System Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]
    URL = "https://job-search-api.svc.dhigroupinc.com/v1/dice/jobs/search"
    
    
#  config.py for careerBuilder
class Configcareer:
    URL_TEMPLATE = "https://www.careerbuilder.com/jobs?cb_apply=false&cb_workhome=all&emp=jtct%2Cjtc2%2Cjtcc&keywords={keyword}&location=&pay=&posted=&sort=date_desc&page={page}"
    # OUTPUT_FILENAME_TEMPLATE = "output.csv"
    output_csv = "output_CareerBuilder.csv"
    output_directory = "output"
    subdirectory = datetime.now().strftime('%Y-%m-%d')

    # Modify this line to include the full path
    OUTPUT_CSV_PATH = f"{output_directory}/{subdirectory}"
    # f"output/{datetime.now().strftime('%Y-%m-%d')}"
    KEYWORD = ["data analyst", "business analyst", "system analyst", "data scientists", "data engineer", "business system analyst"]
    PROXY = "http://4985462b823f2071f48ff52fb687708658d0d488:@proxy.zenrows.com:8001"

