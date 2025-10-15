# sagan_chat.py
from openai import OpenAI
import faiss
import numpy as np
import json
from dotenv import load_dotenv
import os
import requests
import gdown

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --- 1. Get project root folder ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # pyweb/
AI_DIR = os.path.join(BASE_DIR, "ai")
os.makedirs(AI_DIR, exist_ok=True)  # ensures folder exists

# --- 2. FAISS index path ---
FAISS_PATH = os.path.join(AI_DIR, "sagan_index.faiss")
FAISS_FILE_ID = "1n-Emm343C5NlkutYPfmsXymIdJZtpTP9"

# --- 3. Download if missing ---
if not os.path.exists(FAISS_PATH):
    print("Downloading FAISS index...")
    gdown.download(
        f"https://drive.google.com/uc?export=download&id={FAISS_FILE_ID}",
        FAISS_PATH,
        quiet=False
    )

index = faiss.read_index(FAISS_PATH)
sagan_chunks = json.load(open(os.path.join(AI_DIR, "sagan_chunks.json"), "r", encoding="utf-8"))


def retrieve_context(query, top_k=3):
    query_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    D, I = index.search(np.array([query_emb]).astype("float32"), top_k)
    return [sagan_chunks[i] for i in I[0]]

def generate_response(query):
    context = retrieve_context(query)
    prompt = f"""
    You are an AI educator inspired by Carl Sagan.
    Speak with calm wonder, scientific curiosity, and poetic clarity.
    Use the following context from his works to inform your answer:

    {context}

    Question: {query}
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )

    return completion.choices[0].message.content


# if __name__ == "__main__":
#     while True:
#         q = input("\nAsk Carl Sagan: ")
#         if q.lower() in ["exit", "quit"]:
#             break
#         print("\nCarl Sagan AI:", generate_response(q))
