import json

# Ollama Host
OLLAMA_HOST = "http://localhost:11434"
OllAMA_MODEL = "deepseek-llm:latest"

llm_agent = None  # Lazy-initialized
def get_llm_client():
    global llm_agent
    if llm_agent is not None:
        return llm_agent
    try:
        import ollama  # Lazy import
        llm_agent = ollama.Client(host=OLLAMA_HOST)
        return llm_agent
    except Exception as e:
        print(f"Error creating LLM client: {e}")
        return None
embedder = None  # Lazy-initialized
db_connection = None  # Lazy-initialized

# Connect db
def get_db_connection():
    global db_connection
    if db_connection is not None:
        return db_connection
    try:
        import mysql.connector  # Lazy import
        db_connection = mysql.connector.connect(
            host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
            port = 4000,
            user = "H9XdAvETFW3AD85.root",
            password = "oXoRlTZPQPxSN2ux",
            database = "rag_app",
            ssl_ca = "/etc/ssl/cert.pem",
            ssl_verify_cert = True,
            ssl_verify_identity = True
        )
        return db_connection
    except Exception as e:
        print(f"Error creating DB connection: {e}")
        return None

def search_document(database, query, k_tops=5):
    results = []
    try:
        # Lazy import and init embedder
        global embedder
        if embedder is None:
            from sentence_transformers import SentenceTransformer  # Lazy import
            embedder = SentenceTransformer('BAAI/bge-m3')

        query_embedding_list = embedder.encode(query).tolist()
        query_embedding_str = json.dumps(query_embedding_list)

        if database is None:
            database = get_db_connection()
            if database is None:
                return []
        cursor = database.cursor()
        # Ensure k_tops is a safe integer for LIMIT
        try:
            k_value = max(1, int(k_tops))
        except Exception:
            k_value = 5
        sql_query = f"""
                        SELECT text,
                               vec_cosine_distance(embedding, %s) AS distance
                        FROM documents
                        ORDER BY distance
                        LIMIT {k_value}
                """

        cursor.execute(sql_query, (query_embedding_str,))
        search_rows = cursor.fetchall()
        cursor.close()

        for row in search_rows:
            text, distance = row
            results.append({
                "text": text,
                "distance": distance
            })

        return results

    except Exception as e:
        print(f"Error in search_document: {e}")
        return []

def response_query(database, query, k_tops=5):
    retrieved_docs = search_document(database, query, k_tops=k_tops)
    context = "\n".join([doc["text"] for doc in retrieved_docs])
    prompt = (
        "Answer the following question based on the provided context. "
        f"\n\nContext:\n{context}\n\nQuestion: {query}"
    )
    client = get_llm_client()
    if client is None:
        return "LLM client unavailable. Ensure Ollama is installed and running at OLLAMA_HOST."

    response = client.chat(
        model=OllAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    return response.get("message", {}).get("content", "")

if __name__ == "__main__":
    print("Chatbot Started")
    try:
        while True:
            try:
                query_text = input("prompt: ")
            except EOFError:
                # Allow non-interactive runs to exit cleanly
                query_text = "exit"

            if query_text.lower() in ['exit', 'quit', 'q', 'bye']:
                print("Chatbot Closed...")
                break

            response = response_query(database=get_db_connection(), query=query_text)
            print("Chatbot: ", response)
    finally:
        if db_connection is not None:
            try:
                db_connection.close()
            except Exception:
                pass
            print("Database Connection Closed...")