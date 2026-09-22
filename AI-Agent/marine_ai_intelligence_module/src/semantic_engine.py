import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .config import DATA_PATH

model = SentenceTransformer("all-MiniLM-L6-v2")

df = pd.read_csv(DATA_PATH)

columns = list(df.columns)

column_embeddings = model.encode([c.replace("_"," ") for c in columns])


def detect_metric(question):

    q_embedding = model.encode([question])

    similarities = cosine_similarity(q_embedding,column_embeddings)[0]

    index = similarities.argmax()

    return columns[index]