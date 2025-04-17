import requests
from db_supabase import get_unique_documents_by_url  

# Replace with your actual keys and IDs
NOTION_API_KEY = "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"
NOTION_DATABASE_ID = "1cfebcf202ca805dbdb7cf06059f2027"

def get_documents_from_notion():
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()

        results = response.json().get("results", [])
        documents = []

        for page in results:
            props = page["properties"]

            # Extract each field safely
            title = props["Title"]["title"][0]["text"]["content"] if props["Title"]["title"] else "Untitled"
            author = props["Authors"]["rich_text"][0]["text"]["content"] if props["Authors"]["rich_text"] else "Unknown"
            url_field = props["Url"]["rich_text"][0]["text"]["content"] if props["Url"]["rich_text"] else ""
            abstract = props["Excerpt"]["rich_text"][0]["text"]["content"] if props["Excerpt"]["rich_text"] else ""

            # Clean the URL field if it contains a prefix like 'URL https://...'
            url_clean = url_field.split(" ", 1)[-1] if " " in url_field else url_field

            documents.append({
                "title": title,
                "author": author,
                "url": url_clean,
                "abstract": abstract
            })

        return documents

    except requests.RequestException as e:
        print(f"[✗] Failed to fetch documents from Notion: {e}")
        return []

def create_notion_page(metadata):
    
    title = metadata.get("title", "Untitled")
    author = metadata.get("author", "Unknown")
    url_text = metadata.get("url", "")
    abstract = metadata.get("abstract", "")

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # Format the URL as plain text since "Url" is a rich_text field in your DB
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Title": {
                "title": [{"text": {"content": title}}]
            },
            "Authors": {
                "rich_text": [{"text": {"content": author}}]
            },
            "Url": {
                "rich_text": [{"text": {"content": f"{url_text}"}}]
            },
            "Excerpt": {
                "rich_text": [{"text": {"content": f"{abstract}"}}]
            }
        }
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"[✓] Added to Notion: {title}")
    else:
        print(f"[✗] Failed to add: {title} - {response.text}")

def sync_documents_to_notion():
    print("[…] Fetching unique documents from Supabase...")
    documents = get_unique_documents_by_url()

    for doc in documents:
        create_notion_page(doc)


if __name__ == "__main__":
    sync_documents_to_notion()
    # print(get_documents_from_notion())
