import requests
import xml.etree.ElementTree as ET

def search_arxiv(query, limit=3):
    """
    Search arXiv for papers based on a keyword.
    Returns a list of (title, link) tuples.
    """
    base_url = "http://export.arxiv.org/api/query?"
    search = f"search_query=all:{query}&start=0&max_results={limit}"
    url = base_url + search

    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.text)

        results = []
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
            link = entry.find('{http://www.w3.org/2005/Atom}id').text.strip()
            results.append((title, link))

        return results

    except Exception as e:
        print("❌ arXiv API Error:", e)
        return []
