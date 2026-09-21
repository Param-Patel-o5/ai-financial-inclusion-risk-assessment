# run this one-off check, paste the output
import sqlite3
conn = sqlite3.connect("rag/reg_chunks.db")
cur = conn.cursor()
cur.execute("SELECT chunk_id, typeof(embedding), embedding FROM reg_chunks LIMIT 1")
row = cur.fetchone()
print("chunk_id:", row[0])
print("typeof:", row[1])
print("embedding preview:", str(row[2])[:100])
conn.close()