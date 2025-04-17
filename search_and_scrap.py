import requests
from openai import OpenAI
import json
import numpy as np
import csv
import tiktoken
import os

from rag import get_embedding
from db_supabase import insert_chunk, get_existing_urls





# === CONFIGURATION ===
SERPAPI_KEY = "74f735f4188c3c38b349eeed3e18b0daa72a0008017bf16a71aa09b8f4b2bdd8"
FIRECRAWL_TOKEN = "fc-2b0d1d4ae8bd44d1bbcff3858ff9721b"
OPENAI_API_KEY = "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"

client = OpenAI(api_key=OPENAI_API_KEY)
CSV_PATH = "res.csv"

# === FUNCTIONS ===
def search_scholar(query):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "engine": "google_scholar",
        "api_key": SERPAPI_KEY,
        "num": 20
    }
    response = requests.get(url, params=params)
    return response.json().get("organic_results", [])

def scrape_content(url):
    headers = {"Authorization": f"Bearer {FIRECRAWL_TOKEN}"}
    data = {
        "url": url,
        "pageOptions": {
            "onlyMainContent": True,
            "replaceAllPathsWithAbsolutePaths": True
        }
    }
    print(f"[✓] Scraping content from {url}...")
    response = requests.post("https://api.firecrawl.dev/v0/scrape", json=data, headers=headers)

    if response.status_code != 200:
        print(f"[✗] Error scraping {url}: {response.status_code}")
        return {}

    return response.json()

def append_to_csv(metadata, row_index, path):
    fieldnames = ["id", "title", "author", "url", "chunks", "embedding"]
    row = {
        "id": row_index,
        "title": metadata.get("title", ""),
        "author": metadata.get("author", ""),
        "url": metadata.get("url", ""),
        "chunks": metadata.get("chunk", ""),
        "embedding": metadata.get("embedding", "")
    }

    file_exists = os.path.exists(path)

    with open(path, "a", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_ALL,
            escapechar='\\'
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
        
        
def get_cleaned_csv():
    input_path = "res.csv"
    output_path = "res_cleaned.csv"

    with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", newline='', encoding="utf-8") as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)

        for row in reader:
            if len(row) < 3:
                continue  # skip incomplete lines
            cleaned_row = row[:4]  # keep only the first 4 columns
            writer.writerow(cleaned_row)

    print("✅ CSV cleaned and saved as res_cleaned.csv")



# === MAIN PIPELINE ===
'''
1. Search Google Scholar for the query
2. For each result:
    2.1. Scrape the content of the article
    2.2 Chunk the content into smaller parts
    2.3. Get the embedding of the content
    2.4. Save the metadata and embedding to a CSV file
'''
def search_and_scrap(query="coffee carbon footprint"):
    results = search_scholar(query)
    existing_urls = get_existing_urls()
    chunk_size = 8192
    
    print('[🔍] Searching for documents related to your query...\n')

    for index, result in enumerate(results, start=1):
        title = result.get("title")
        link = result.get("link")
        
        if not link or link in existing_urls:
            print(f"[⏩] Already exists or no link found: {link}")
            continue
        
        authors = result.get("publication_info", {}).get("authors", [])
        author_names = ", ".join([a.get("name", "") for a in authors]) if authors else "Unknown"
        abstract = result.get("snippet", "")
        document_id = index

        

        scraped = scrape_content(link)
        raw_content = scraped.get("data", {}).get("content", "")
        if not raw_content:
            print("[✗] No content found, skipping...")
            continue

        try:
            for i in range(0, len(raw_content), chunk_size):
                chunk_id = i // chunk_size + 1
                chunk = raw_content[i:i + chunk_size]
                emb = get_embedding(chunk)
                metadata = {
                    "title": title,
                    "author": author_names,
                    "url": link,
                    "abstract": abstract
                }
                insert_chunk(document_id, chunk_id, chunk, emb, metadata)
        except Exception as e:
            print(f"[✗] Failed to embed article: {e}")
            continue

    print("✅ Done.")
    

if __name__ == "__main__":
    search_and_scrap("coffee carbon footprint")
    # res = scrape_content("https://www.sciencedirect.com/science/article/pii/S0167880912000345")
    # print(res)
