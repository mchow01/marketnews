from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
alphavantage_api_key = os.getenv('ALPHAVANTAGE_API_KEY')
url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=technology&apikey={alphavantage_api_key}"
r = requests.get(url)
data = r.json()
json_formatted_str = json.dumps(data, indent=2)
print(json_formatted_str)