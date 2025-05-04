#embeddings to database code 
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
import time
import sqlite3
from tqdm import tqdm

# 🔐 API key

# 📅 Load course summaries
with open("UW_CS_AllCourses_Embeddings_160_to_444.json", "r") as f:
    courses = json.load(f)

# 📁 Connect to SQLite database
conn = sqlite3.connect("course_database.db")
cursor = conn.cursor()

# 📝 Ensure the 'embeddings' table exists with necessary columns
cursor.execute("""
CREATE TABLE IF NOT EXISTS embeddings (
    course_code TEXT PRIMARY KEY,
    course_description_embedding TEXT,
    learning_goals_embedding TEXT,
    topics_covered_embedding TEXT,
    tools_embedding TEXT
)
""")

# 📄 Process each course and generate embeddings
for course_code, sections in tqdm(courses.items(), desc="Embedding courses"):
    embeddings_row = {
        "Course Description": None,
        "Learning Goals": None,
        "Topics Covered": None,
        "Tools Taught": None
    }
    formatted_course_code = course_code.replace(" ", "")
    for section_title, content in sections.items():
        try:
            response = client.embeddings.create(input=content,
            model="text-embedding-3-small")
            embedding = response.data[0].embedding
            embeddings_row[section_title] = json.dumps(embedding)
            time.sleep(0.5)  # 🕒 Respect rate limits
        except Exception as e:
            print(f"⚠️ Failed for {course_code} - {section_title}: {e}")
            embeddings_row[section_title] = None

    # 📆 Insert the row into the database
    cursor.execute("""
    INSERT OR REPLACE INTO embeddings (
        course_code,
        course_description_embedding,
        learning_goals_embedding,
        topics_covered_embedding,
        tools_embedding
    ) VALUES (?, ?, ?, ?, ?)
    """, (
        formatted_course_code,
        embeddings_row["Course Description"],
        embeddings_row["Learning Goals"],
        embeddings_row["Topics Covered"],
        embeddings_row["Tools Taught"]
    ))

# 🔐 Commit and close
conn.commit()
conn.close()

print("✅ Embeddings saved to SQLite database 'course_database.db'")
