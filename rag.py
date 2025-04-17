from openai import OpenAI
import numpy as np
import tiktoken
import pandas as pd

# === CONFIG ===
client = OpenAI(api_key="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")


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
