import sqlite3
from openai import OpenAI
import openai
import numpy as np
import os
from openai import OpenAIError 
import json
import logging
import math
import re
import datetime


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - embedding_utils.py: %(message)s",
    handlers=[
        logging.FileHandler("embedding_utils_log.log"),
        logging.StreamHandler()  # Add this to print logs to the terminal
    ]
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def get_embedding(text, model="text-embedding-3-small"):
   try:
        response = client.embeddings.create(input=[text], model="text-embedding-3-small")
        return response.data[0].embedding
   except OpenAIError as e:
        logging.error(f"get_embedding: OpenAI API error: {str(e)}")
        return None

def cosine_similarity(vec1, vec2):
    v1, v2 = np.array(vec1), np.array(vec2)
    
    if np.isnan(v1).any():
        logging.warning(f"cosine_similarity: NaN detected in vec1: {v1}")
        return float('-inf')
    if np.isnan(v2).any():
        logging.warning(f"cosine_similarity: NaN detected in vec2: {v2}")
        return float('-inf')
    
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    if np.isnan(norm_v1) or np.isnan(norm_v2):
        logging.warning(f"cosine_similarity: NaN detected in norms: norm_v1={norm_v1}, norm_v2={norm_v2}")
        return float('-inf')
   
    if norm_v1 == 0.0 or norm_v2 == 0.0:
        logging.warning("Zero vector encountered in cosine_similarity. Returning -inf.")
        return float('-inf')  # or 0.0 if you prefer neutral similarity
    
    return float(np.dot(v1, v2) / (norm_v1 * norm_v2))


def compare_embeddings(jd_embedding, course_embedding):
    """Return the cosine similarity score between JD and a course embedding."""
    try:
        return cosine_similarity(jd_embedding, course_embedding)
    except OpenAIError as e:
        error_msg = f"compare_embeddings - OpenAIError during similarity comparison: {e}"
        logging.error(error_msg)
        return None
    except Exception as e:
        error_msg = f"compare_embeddings - Unexpected error during similarity comparison: {e}"
        logging.error(error_msg)
        return None

def load_course_embeddings_dict(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT course_code, 
               course_description_embedding, 
               learning_goals_embedding, 
               topics_covered_embedding, 
               tools_embedding, 
                combined_text_embedding
        FROM embeddings
    """)
    rows = cursor.fetchall()
    conn.close()

    course_embeddings = {}
    for row in rows:
        course_code = row[0]
        try:
            try:
                course_embeddings[course_code] = {
                    "course_description_embedding": json.loads(row[1]) if row[1] else float('-inf'),
                    "learning_goals_embedding": json.loads(row[2]) if row[2] else float('-inf'),
                    "topics_covered_embedding": json.loads(row[3]) if row[3] else float('-inf'),
                    "tools_embedding": json.loads(row[4]) if row[4] else float('-inf'),
                    "combined_text_embedding": json.loads(row[5]) if row[5] else float('-inf')
                }
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for {course_code}: {e}")
                course_embeddings[course_code] = {
                    "course_description_embedding": float('-inf'),
                    "learning_goals_embedding": float('-inf'),
                    "topics_covered_embedding": float('-inf'),
                    "tools_embedding": float('-inf'),
                    "combined_text_embedding": float('-inf')
                }
        except Exception as e:
            print(f"Error parsing embeddings for {course_code}: {e}")
    return course_embeddings



def update_course_data_from_json(json_file_path, db_path):
    """
    Updates the course database with data from a JSON file.

    Args:
        json_file_path (str): Path to the JSON file containing course data.
        db_path (str): Path to the SQLite database.

    Returns:
        None
    """
    # Load the JSON file
    with open(json_file_path, "r") as f:
        course_data = json.load(f)

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for course_code, course_details in course_data.items():
        # Add a space between the first three alphabets and the remaining string if not already present
        formatted_course_code = re.sub(r"^([A-Za-z]{3})([A-Za-z]?\d{3}[A-Za-z]{0,2})$", r"\1 \2", course_code)

        # Extract course details
        course_description = course_details.get("course_description", "None")
        learning_goals = course_details.get("learning_goals", "None")
        topics_covered = course_details.get("topics_covered", "None")
        tools = course_details.get("tools", "None")
        source_url = course_details.get("source_url", "None")

        # Check if the course exists in the database
        cursor.execute("SELECT 1 FROM embeddings WHERE course_code = ?", (formatted_course_code,))
        if cursor.fetchone():
            # Update the database with the course details
            cursor.execute("""
                UPDATE embeddings
                SET course_description = ?, 
                    learning_goals = ?, 
                    topics_covered = ?, 
                    tools = ?, 
                    source_url = ?
                WHERE course_code = ?
            """, (course_description, learning_goals, topics_covered, tools, source_url, formatted_course_code))
            print(f"Updated course: {formatted_course_code}")
        else:
            print(f"Course not found in database: {formatted_course_code}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("Database update complete.")
    
def compute_similarity_scores(jd_embedding, course_embedding_record, course_code=None):
    """
    Compare jd_embedding with course_embedding_record containing keys:
    - course_description_embedding
    - learning_goals_embedding
    - topics_covered_embedding
    - tools_embedding

    Returns a dictionary of similarity scores.
    """
    try:
        def safe_compare(key):
            """Helper function to safely compute similarity."""
            embedding = course_embedding_record.get(key)# 'get' is used to extract a value from the dictionary
            

            if embedding is None:  # Handle NULL values
                logging.warning(f"{key} is NULL or missing in course_embedding_record so returning -inf for the comparison.")
                return -math.inf  # Return -inf for missing embeddings
            if not isinstance(embedding, list):
                logging.warning(f"BAD EMBEDDING for {key} in {course_code}: {type(embedding)}, value={embedding}. Returning -inf for the comparison.")
                return -math.inf  # Return -inf for invalid embeddings

            if not isinstance(jd_embedding, list):
                logging.warning(f"BAD JD EMBEDDING: {type(jd_embedding)}, value={jd_embedding}. Returning -inf for the comparison.")
                return -math.inf
            
            return compare_embeddings(jd_embedding, embedding)

        return {
            "course_description_similarity": safe_compare("course_description_embedding"),
            "learning_goals_similarity": safe_compare("learning_goals_embedding"),
            "topics_covered_similarity": safe_compare("topics_covered_embedding"),
            "tools_similarity": safe_compare("tools_embedding"),
        }
    except Exception as e:
        error_msg = f"Error computing similarity scores: {e}"
        logging.error(error_msg) 
        return None

def load_course_embeddings(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT course_code, 
               course_description_embedding, 
               learning_goals_embedding, 
               topics_covered_embedding, 
               tools_embedding,
               combined_text_embedding  
        FROM embeddings
    """)
    rows = cursor.fetchall()
    conn.close()

    course_embeddings = {}
    for row in rows:
        course_code = row[0]
        try:
            try:
                course_embeddings[course_code] = {
                    "course_description_embedding": json.loads(row[1]) if row[1] else float('-inf'),
                    "learning_goals_embedding": json.loads(row[2]) if row[2] else float('-inf'),
                    "topics_covered_embedding": json.loads(row[3]) if row[3] else float('-inf'),
                    "tools_embedding": json.loads(row[4]) if row[4] else float('-inf'),
                    "combined_text_embedding": json.loads(row[5]) if row[5] else float('-inf')
                }
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for {course_code}: {e}")
                course_embeddings[course_code] = {
                    "course_description_embedding": float('-inf'),
                    "learning_goals_embedding": float('-inf'),
                    "topics_covered_embedding": float('-inf'),
                    "tools_embedding": float('-inf'),
                    "combined_text_embedding": float('-inf')
                }
        except Exception as e:
            print(f"Error parsing embeddings for {course_code}: {e}")
    return course_embeddings

def create_course_embeddings_json(db_path=None):
    
    if db_path is None:
        course_embeddings_dict = load_course_embeddings("/Users/hemantbothra/Library/CloudStorage/GoogleDrive-hbothra1@gmail.com/My Drive/Projects/studentAdvisorProject/course_database.db")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_path = os.path.join(
            os.path.dirname("/Users/hemantbothra/Library/CloudStorage/GoogleDrive-hbothra1@gmail.com/My Drive/Projects/studentAdvisorProject/data"), 
            f"course_embeddings_dict_{timestamp}.json"
        )
        with open(output_file_path, "w") as json_file:
            json.dump(course_embeddings_dict, json_file, indent=4)
        
    print(f"Course embeddings dictionary saved to {output_file_path}")

if __name__ == "__main__":
    
    # db_path = "/Users/hemantbothra/Library/CloudStorage/GoogleDrive-hbothra1@gmail.com/My Drive/Projects/studentAdvisorProject/course_database.db"
    # json_file_path = "/Users/hemantbothra/Library/CloudStorage/GoogleDrive-hbothra1@gmail.com/My Drive/Projects/studentAdvisorProject/course_data_forembedding_temp_withfallback_5.json"
    
    create_course_embeddings_json()

    # update_course_data_from_json(json_file_path, db_path)