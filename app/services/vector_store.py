import chromadb

# Persistent storage folder
CHROMA_PATH = "./chroma_storage"

# 🔥 Use PersistentClient (IMPORTANT)
client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = client.get_or_create_collection(
    name="clinical_trials"
)

def add_trial_embedding(trial_id: str, embedding: list, metadata: dict):
    collection.add(
        ids=[trial_id],
        embeddings=[embedding],
        metadatas=[metadata]
    )

def search_similar_trials(query_embedding: list, n_results: int = 3):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results

def get_total_embeddings():
    return collection.count()