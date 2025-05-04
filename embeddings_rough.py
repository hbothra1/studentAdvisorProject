from openai import OpenAI
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
import json


course_text = """
Course Goals
Databases are at the heart of modern commercial application development. 
Their use extends beyond this to many other environments and domains where large amounts of data must be stored for efficient update, retrieval, and analysis. 
The purpose of this course is to provide a comprehensive introduction to the use of management systems for applications. 
Some of the topics covered are the following: 
- Introduces database management systems and writing applications that use such systems; data models (e.g., relational, semi-structured), query languages (e.g., SQL, SQL++), language bindings, conceptual modeling, transactions, security, database tuning, data warehousing, parallelism, and web-data management. 

Prerequisite: CSE 311.

Here is a more specific list of potential topics that will be covered in 414:
- Data models
- Query languages (e.g. SQL)
- Schema, logical, and physical design
- Database applications
- Transactions
- Data analytics
- NoSQL
- Cloud database systems

"""

response = client.embeddings.create(input=course_text,
model="text-embedding-ada-002")

embedding = response.data[0].embedding

# Save embedding to a text file as JSON
with open("course_embedding_cse414.json", "w") as f:
    json.dump(embedding, f)

print("Embedding saved.json")
