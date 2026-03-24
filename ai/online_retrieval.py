import re
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

MIN_WORDS = 5

def clean_text(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return sentences


def get_online_data(query):
    results = []
    q_words = set(re.findall(r'\w+', query.lower()))

    with DDGS() as ddgs:
        links = ddgs.text(query, max_results=5)

        for r in links:
            try:
                res = requests.get(r["href"], timeout=5)
                soup = BeautifulSoup(res.text, "html.parser")

                for tag in soup(["script","style","nav","footer","header"]):
                    tag.decompose()

                raw = " ".join(p.get_text() for p in soup.find_all("p"))
                sentences = clean_text(raw)

                for s in sentences:
                    if len(s.split()) < MIN_WORDS:
                        continue

                    overlap = len(q_words & set(re.findall(r'\w+', s.lower())))
                    if overlap >= 1:
                        results.append(s)

            except:
                continue

    return results[:5]