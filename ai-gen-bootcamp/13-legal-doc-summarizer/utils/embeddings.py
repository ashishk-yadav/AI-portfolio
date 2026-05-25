import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()



def embed_texts(texts):
    EMBED_MODEL = "text-embedding-3-small"
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    vecs=[]
    B=90
    for i in range(0,len(texts),B):
        batch = texts[i:i+B]
        resp = client.embeddings.create(model=EMBED_MODEL, input=batch)
        vecs.extend([d.embedding for d in resp.data])
    return np.array(vecs)
