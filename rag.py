from openai import OpenAI
import numpy as np
import tiktoken
import pandas as pd
import os
from dotenv import load_dotenv


load_dotenv()

# === CONFIG ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# === Truncate to token limit ===
def truncate_tokens(text, max_tokens=8192, model="text-embedding-3-small"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return encoding.decode(tokens[:max_tokens])

def get_embedding(text, model="text-embedding-3-small"):
    text = truncate_tokens(text, max_tokens=8192, model=model)
    response =client.embeddings.create( 
        input=[text],
        model=model
    )
    return response.data[0].embedding
