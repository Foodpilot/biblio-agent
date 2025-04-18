from openai import OpenAI
from rag import get_embedding
from db_supabase import search_similar_chunks, print_chunks_table
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from search_and_scrap import search_and_scrap
import json
import pandas as pd
import csv
import time
import threading
import sys
import re





def ai_generate_queries(user_question):
    start_time = time.time()
    # prompt = f"""
    # You are an AI researcher. A user asked you this question:

    # "{user_question}"

    # Break it down into multiple precise academic search queries for Google Scholar (2 to 5).
    # Return them as a Python list of strings.
    # """
    prompt = f"""
    You are an expert in food systems, supply chains, and sustainability.

    You are helping build a scientific knowledge base for the product: "{user_question}".

    Generate 8–12 specific, diverse academic search queries for Google Scholar that would help researchers understand the product.

    Your queries should cover topics like:
    - environmental impact
    - supply chain analysis
    - carbon footprint
    - food safety
    - traceability and transparency
    - sustainable farming practices
    - social and economic factors
    - consumer perception
    - certifications and labels
    - nutritional aspects

    Make sure each query is different, focused, with key words and useful for academic research. (for example : "carbon footprint coffee")
    Respond with a Python list of strings.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    queries = eval(response.choices[0].message.content)
    return queries


def ai_rank_and_summarize(user_question, articles):
    # Normalize: make sure all entries are dictionaries
    clean_articles = [a.to_dict() if hasattr(a, "to_dict") else a for a in articles]
    
    stop_timer = False
    def live_timer():
        start = time.time()
        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while not stop_timer:
            elapsed = time.time() - start
            sys.stdout.write(f"\r⏳ GPT is thinking... {spinner[i % len(spinner)]} {elapsed:.1f}s")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        print(f"\r✅ GPT completed in {time.time() - start:.2f}s")

    # Start thread
    t = threading.Thread(target=live_timer)
    t.start()

    prompt = f"""
    The user asked: "{user_question}"

    You received a list of chunked articles from Google Scholar. Each article includes:
    - title
    - author
    - url
    - abstract
        
    Here are the articles:

    {json.dumps(clean_articles, indent=2)}
    
    Answer to the user with a summary of the most relevant articles.
    Give a 10 lines answer based on the articles.
    """
    response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
    )

    raw_content = response.choices[0].message.content.strip()
    # Try parsing directly
    try:
        # return json.loads(raw_content)
        return raw_content
    # except json.JSONDecodeError:
    #     # Try extracting JSON if GPT added extra text
    #     match = re.search(r"\[\s*{.*?}\s*\]", raw_content, re.DOTALL)
    #     if match:
    #         return json.loads(match.group(0))
    #     else:
    #         raise ValueError("GPT output is not valid JSON.")

    finally:
        stop_timer = True
        t.join()



def main():
    # user_question = "What is the carbon footprint of coffee production and how does it vary by country?"
    user_question = "coffee"
    print(f"🧠 AI analyzing question: {user_question}")
    
    

    # Let AI create 2–5 subqueries
    queries = ai_generate_queries(user_question)
    print(f"🔍 AI generated {len(queries)} search queries:\n", queries)

    # Run scholar search for each query => create our own dataset
    all_articles = []
    # all_articles = pd.read_csv("res.csv")
    for q in queries:
        print(f"📚 Searching: {q}")
        results = search_and_scrap(q)
    #     all_articles.extend(results)
    error
    # Get the artciles already chunked in the database (TEST MODE)
    # all_articles = print_chunks_table()

    print(f"📥 Collected {len(all_articles)} total articles")
    
    # Calculate distances with our query
    res = search_similar_chunks(user_question, max_results=10)
    
    

    # Step 3: Let AI pick & summarize the best ones
    top5 = ai_rank_and_summarize(user_question, res)
    print("\n ------------------------------------------------------------------------------- \n")
    print(top5)

    # print("\n🎯 Top 5 Articles:\n")
    # for article in top5:
    #     print(f"🧩 Title: {article['title']}\n📎 URL: {article['url']}\n👤 Author: {article['author']}\n⭐ Score: {article['score']}\n📝 Summary:\n{article['summary']}\n")

    # # # Save results
    # with open("top_5_scholar_results.json", "w", encoding="utf-8") as f:
    #     json.dump(top5, f, indent=2, ensure_ascii=False)
    # print("💾 Saved as top_5_scholar_results.json")


    
if __name__ == "__main__":
    main()
