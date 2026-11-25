
import requests
import os
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

backend_url = os.getenv(
    "backend_url", "http://localhost:3030"
).rstrip("/")

sentiment_analyzer_url = os.getenv(
    "sentiment_analyzer_url", "http://localhost:5050/"
).rstrip("/") + "/"


def get_request(endpoint, **kwargs):
    request_url = backend_url + "/" + endpoint.lstrip("/")

    try:
        response = requests.get(
            request_url,
            params=kwargs,
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        print("GET request failed:", error)
        return None


def analyze_review_sentiments(text):
    request_url = (
        sentiment_analyzer_url
        + "analyze/"
        + quote(str(text), safe="")
    )

    try:
        response = requests.get(request_url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        print("Sentiment analysis failed:", error)
        return None


def post_review(data_dict):
    request_url = backend_url + "/insert_review"

    try:
        response = requests.post(
            request_url,
            json=data_dict,
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        print("POST request failed:", error)
        return None
