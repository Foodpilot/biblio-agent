from supabase import create_client, Client
from rag import get_embedding


SUPABASE_URL = "https://fgzlopreouzxsmcpwclv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZnemxvcHJlb3V6eHNtY3B3Y2x2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDYxOTYwMSwiZXhwIjoyMDYwMTk1NjAxfQ.xUuJpRjL8REgbLJRs3hlB_pQ7RgD8-qW_YHfYdDwUKA"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def print_chunks_table():
    try:
        response = supabase.table("rag").select("*").execute()
        print("✅ Connection successful.")
        return response.data
    except Exception as e:
        print(f"[✗] Failed to fetch rows: {e}")


def insert_chunk(document_id, chunk_id, chunk_text, embedding, metadata):
    data = {
        "document_id": document_id,
        "chunk_id": chunk_id,
        "text": chunk_text,
        "embedding": embedding,
        "metadata": {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "url": metadata.get("url", ""),
            "abstract": metadata.get("abstract", "")
        }
    }

    try:
        supabase.table("rag").insert(data).execute()
        print(f"[✓] Inserted chunk {chunk_id} (doc {document_id})")
    except Exception as e:
        print(f"[✗] Failed to insert chunk {chunk_id}: {e}")

        
        
        
        
def search_similar_chunks(query, max_results=5, model="text-embedding-3-small"):
    try:
        # Génère l'embedding de la question
        query_embedding = get_embedding(query, model=model)

        # Appelle la fonction RPC Supabase
        response = supabase.rpc("distance_rag_chunks", {
            "query_embedding": query_embedding,
            "max_results": max_results
        }).execute()

        if not response.data:
            print("[!] Aucune correspondance trouvée.")
            return
        
        return response.data

    except Exception as e:
        print(f"[✗] Erreur lors de la recherche : {e}")


def get_existing_urls():
    try:
        response = supabase.table("rag").select("metadata->>url").execute()
        urls = {row["metadata"]["url"] for row in response.data if row.get("metadata", {}).get("url")}
        return urls
    except Exception as e:
        print(f"[✗] Failed to fetch existing URLs: {e}")
        return set()

def get_unique_documents_by_url():
    try:
        # Select all metadata objects
        response = supabase.table("rag").select("metadata").execute()
        
        # Extract URLs from metadata
        urls_seen = set()
        unique_docs = []
        
        for row in response.data:
            metadata = row.get("metadata", {})
            url = metadata.get("url")
            
            if url and url not in urls_seen:
                urls_seen.add(url)
                unique_docs.append(metadata)
        
        return unique_docs
    
    except Exception as e:
        print(f"[✗] Failed to fetch unique documents: {e}")
        return []


