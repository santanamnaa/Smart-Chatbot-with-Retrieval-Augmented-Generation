import json
import pandas as pd
import mysql.connector
from sentence_transformers import SentenceTransformer

# Create instance for embedder
embedder = SentenceTransformer('BAAI/bge-m3')

# Connect db
db_connection= mysql.connector.connect(
  host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
  port = 4000,
  user = "H9XdAvETFW3AD85.root",
  password = "oXoRlTZPQPxSN2ux",
  database = "rag_app",
  ssl_ca = "/etc/ssl/cert.pem",
  ssl_verify_cert = True,
  ssl_verify_identity = True
)

# Create cursor
cursor = db_connection.cursor()

# Read Data Knowledge
df = pd.read_csv("data_knowledge.csv")

for index, row in df.iterrows():
    text = str(row['question']) + " " + str(row['answer'])
    
    try:
        embedding_list = embedder.encode(text).tolist()
        embedding_str = json.dumps(embedding_list)

        sql_query = """
                        INSERT INTO documents (text, embedding) VALUES (%s, %s)
                """
        cursor.execute(sql_query, (text, embedding_str))
        print(f"data index-{index} inserted successfully")
    except Exception as e:
        print(f"data index-{index} Error: {e}")
        print(f"data index-{index} failed to insert")

db_connection.commit()