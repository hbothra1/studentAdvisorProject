from openai import OpenAI
import json
import sqlite3
import re
import os
import logging
from openai import OpenAIError  # Import OpenAI error handling

# Setup logging to both file and terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler("embedding_log_batch.txt"),
        logging.StreamHandler()  # Add this to print logs to the terminal
    ]
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load course data
with open("course_data_forembedding_temp_withfallback_5.json", "r") as f:
    course_data = json.load(f)

# Connect to the database
conn = sqlite3.connect("course_database.db")
cursor = conn.cursor()

# Ensure source_url column exists
cursor.execute("PRAGMA table_info(embeddings)")
columns = [col[1] for col in cursor.fetchall()]
if "source_url" not in columns:
    cursor.execute("ALTER TABLE embeddings ADD COLUMN source_url TEXT")
    logging.info("Added source_url column to embeddings table")

# Helper function to reformat course codes
def format_course_code(code):
    return re.sub(r'^([A-Z]{3})(\d+)', r'\1 \2', code)

# Generate embedding from text
def get_embedding(text):
    try:
        response = client.embeddings.create(input=[text], model="text-embedding-3-small")
        return json.dumps(response.data[0].embedding)
    except OpenAIError as e:
        logging.error(f"OpenAI API error: {str(e)}")
        return None

# Main processing loop
for code, data in course_data.items():
    formatted_code = format_course_code(code)
    logging.info(f"Processing {code} → {formatted_code}")

    try:
        print ("\n\n")
        desc = data.get("course_description", "no data.")
        goals = data.get("learning_goals", "no data.")
        topics = data.get("topics_covered", "no data.")
        tools = data.get("tools", "no data.")
        # url = data.get("source_url", "")  
        # Check if all fields are "no data."
        if desc == "no data." and goals == "no data." and topics == "no data." and tools == "no data.":
            combined_text_emb = None
            print(f"All fields are 'no data.' for {formatted_code}. Skipping embedding.")   
        else:
            combined_text = (
            f"Course description: {desc}\n\n"
            f"Learning goals: {goals}\n\n"
            f"Topics Covered: {topics}\n\n"
            f"Tools: {tools}"
            )
            print(f"Combined text: {combined_text}\n\n")
            combined_text_emb = get_embedding(combined_text)
       
        cursor.execute("SELECT 1 FROM embeddings WHERE course_code = ?", (formatted_code,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE embeddings
                SET combined_text_embedding = ?
                WHERE course_code = ?
            """, (combined_text_emb, formatted_code))
            logging.info(f"Updated combined embeddings for {formatted_code}")
        else:
            cursor.execute("""
                INSERT INTO embeddings (
                    course_code, combined_text_embedding
                ) VALUES (?,?)
            """, (formatted_code, combined_text_emb))
            logging.info(f"Inserted combined embeddings for {formatted_code}")
            
    except Exception as e:
            logging.error(f"Error processing {formatted_code}: {str(e)}")


        # Check if any field is "no data." and set embedding to None
        # desc_emb = get_embedding(desc) if desc != "no data." else None
        # goals_emb = get_embedding(goals) if goals != "no data." else None
        # topics_emb = get_embedding(topics) if topics != "no data." else None
        # tools_emb = get_embedding(tools) if tools != "no data." else None
    
        
        # cursor.execute("""
        #     INSERT INTO embeddings (
        #         course_code, combined_text_embedding
        #     ) VALUES (?,?)
        # """, (formatted_code, combined_text_emb))
# Check if course_code already exists; if yes, update, else insert
            
    
# Commit changes and close the database connection
conn.commit()
conn.close()
