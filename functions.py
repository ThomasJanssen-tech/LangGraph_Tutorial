from dotenv import load_dotenv
import os
import requests

from bs4 import BeautifulSoup

load_dotenv() 

def google_search(query):

    headers = {
        "Authorization": "Bearer "+os.getenv("BRIGHTDATA_API_KEY"),
        "Content-Type": "application/json"
    }
    data = {
        "zone": "serp_api3",
        "url": "https://www.google.com/search?q="+query.replace(" ", "+"),
        "format": "raw"
    }


    response = requests.post(
        "https://api.brightdata.com/request",
        json=data,
        headers=headers
    )

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()

    return text

 


