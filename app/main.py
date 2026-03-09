from fastapi import FastAPI, Depends
from app.db.database import init_db
from app.auth.auth_routes import router as auth_router
from app.auth.auth_service import get_current_user
from app.auth.auth_service import require_role
from app.services.trials_api_service import fetch_trials_from_api
from app.db.database import get_connection
from app.services.embedding_service import get_embedding
from app.services.vector_store import add_trial_embedding, search_similar_trials
from app.services.vector_store import get_total_embeddings
from app.services.vector_store import collection
from app.services.explanation_service import generate_explanation
from pydantic import BaseModel

class PatientTextRequest(BaseModel):
    patient_profile: str


app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()


app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Clinical Matcher Backend Running"}

@app.get("/debug-token")
def debug_token(user=Depends(get_current_user)):
    return user

@app.get("/protected")
def protected_route(user=Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user": user
    }

@app.get("/admin-only")
def admin_route(user=Depends(require_role("admin"))):
    return {
        "message": "Welcome Admin",
        "user": user
    }

@app.get("/search-trials")
def search_trials(condition: str, user=Depends(get_current_user)):

    conn = get_connection()
    cursor = conn.cursor()

    # 1️⃣ Try to get from SQLite cache
    cursor.execute(
        "SELECT * FROM trials WHERE condition LIKE ?",
        (f"%{condition}%",)
    )

    rows = cursor.fetchall()

    trials = []

    if rows:
        # Convert rows to dict format
        for row in rows:
            trials.append({
                "nct_id": row["nct_id"],
                "title": row["title"],
                "condition": row["condition"],
                "phase": row["phase"],
                "eligibility_text": row["eligibility_text"],
            })

    else:
        # 2️⃣ Fetch from API
        trials = fetch_trials_from_api(condition)

        # 3️⃣ Store in SQLite
        for trial in trials:
            cursor.execute(
                """
                INSERT OR IGNORE INTO trials 
                (nct_id, title, condition, phase, eligibility_text)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    trial["nct_id"],
                    trial["title"],
                    trial["condition"],
                    trial["phase"],
                    trial["eligibility_text"],
                )
            )

        conn.commit()

    conn.close()

    # 4️⃣ Ensure embeddings exist in Chroma (CRITICAL)
    for trial in trials:

        existing = collection.get(ids=[trial["nct_id"]])

        if not existing["ids"]:
            embedding = get_embedding(trial["eligibility_text"])

            add_trial_embedding(
                trial_id=trial["nct_id"],
                embedding=embedding,
                metadata={
                    "title": trial["title"],
                    "condition": trial["condition"]
                }
            )

    return trials

@app.get("/test-embedding")
def test_embedding(user=Depends(get_current_user)):
    sample_text = "Patient with stage IV lung cancer"
    embedding = get_embedding(sample_text)

    return {
        "embedding_length": len(embedding)
    }


    
@app.get("/semantic-test")
def semantic_test(user=Depends(get_current_user)):

    query_text = "Female patient with early stage breast cancer"

    query_embedding = get_embedding(query_text)

    results = search_similar_trials(query_embedding, n_results=3)

    return results


@app.get("/debug-collection")
def debug_collection(user=Depends(get_current_user)):
    return {
        "total_embeddings": get_total_embeddings()
    }


# @app.post("/match-patient")
# def match_patient(request: PatientTextRequest, user=Depends(get_current_user)):

#     # 1️⃣ Use raw patient text directly
#     query_text = request.patient_profile

#     # 2️⃣ Generate embedding
#     query_embedding = get_embedding(query_text)

#     # 3️⃣ Search vector DB
#     results = search_similar_trials(query_embedding, n_results=5)

#     ids = results["ids"][0]
#     metadatas = results["metadatas"][0]
#     distances = results["distances"][0]

#     matches = []

#     for i in range(len(ids)):

#         distance = distances[i]

#         # Filter weak matches
#         if distance > 1.2:
#             continue

#         similarity_score = round(1 / (1 + distance), 3)

#         reason = generate_explanation(
#         query_text,
#         metadatas[i].get("title", ""),
#         metadatas[i].get("condition", "")
#     )

#     matches.append({
#         "nct_id": ids[i],
#         "title": metadatas[i].get("title", ""),
#         "condition": metadatas[i].get("condition", ""),
#         "similarity_score": similarity_score,
#         "reason": reason
#     })

#     return {
#         "matches": matches[:3]
#     }
@app.post("/match-patient")
def match_patient(request: PatientTextRequest, user=Depends(get_current_user)):

    # 1️⃣ Use raw patient text
    query_text = request.patient_profile

    # 2️⃣ Generate embedding
    query_embedding = get_embedding(query_text)

    # 3️⃣ Search vector DB
    results = search_similar_trials(query_embedding, n_results=5)

    ids = results["ids"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    matches = []

    # 4️⃣ Connect to SQLite
    conn = get_connection()
    cursor = conn.cursor()

    for i in range(len(ids)):

        distance = distances[i]

        # Skip weak matches
        if distance > 1.2:
            continue

        similarity_score = round(1 / (1 + distance), 3)

        trial_id = ids[i]

        # 5️⃣ Fetch eligibility text from DB
        cursor.execute(
            "SELECT eligibility_text FROM trials WHERE nct_id = ?",
            (trial_id,)
        )

        row = cursor.fetchone()

        eligibility_text = row["eligibility_text"] if row else ""

        # 6️⃣ Generate explanation
        reason = generate_explanation(
            query_text,
            metadatas[i].get("title", ""),
            metadatas[i].get("condition", ""),
            eligibility_text
        )

        matches.append({
            "nct_id": trial_id,
            "title": metadatas[i].get("title", ""),
            "condition": metadatas[i].get("condition", ""),
            "similarity_score": similarity_score,
            "reason": reason
        })

    conn.close()

    return {
        "matches": matches[:3]
    }