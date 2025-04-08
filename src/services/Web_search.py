import requests

GOOGLE_API_KEY = "YOUR_KEY"
SEARCH_ENGINE_ID = "YOUR_ID"
def web_search(query, num_results=3):
    try:    
        url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": SEARCH_ENGINE_ID,
            "q": query,
            "num": num_results
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()

        snippets = []
        for item in results.get("items", []):
            title = item.get("title")
            snippet = item.get("snippet")
            link = item.get("link")
            snippets.append(f"{title}: {snippet}\n{link}")

        return "\n\n".join(snippets)

    except requests.exceptions.RequestException as e:
        return f"Search failed due to an error: {str(e)}"


