import sqlite3
import json
import re
from scripts.jd_processor import rearrange_jd_with_gpt, embed_reorganized_jd, match_jd_to_courses
from utils.embedding_utils import get_embedding, compare_embeddings, load_course_embeddings as load_course_embeddings_fromutils
from datetime import datetime
import os

DB_PATH = '/Users/hemantbothra/Library/CloudStorage/GoogleDrive-hbothra1@gmail.com/My Drive/Projects/studentAdvisorProject/course_database.db'
TABLE_NAME = "embeddings"

def is_valid_course(course_code):
    match = re.search(r"[A-Za-z]{2,4}\s?(\d{3,4})", course_code)
    if match:
        return int(match.group(1)) > 350
    return False

def inspect_one_embedding_row(db_path, table_name="embeddings"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT course_code, course_description_embedding
        FROM {table_name}
        WHERE course_code = 'CSE 121'
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()

    course_code, embedding_raw = row
    print(f"Sample course code: {course_code}")
    print(f"Raw stored embedding (truncated): {embedding_raw[:100]}...")

    try:
        parsed = json.loads(embedding_raw)
        print(f"Parsed type: {type(parsed)}, Length: {len(parsed)}, Sample: {parsed[:5]}")
    except Exception as e:
        print(f"❌ Error decoding embedding for {course_code}: {e}")

def load_course_embeddings(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT course_code, 
               course_description_embedding, 
               learning_goals_embedding, 
               topics_covered_embedding, 
               tools_embedding 
               combined_text_embedding,
        FROM {TABLE_NAME}
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

def print_rankings_human_readable(rankings_dict, jd_text):
    print("\nRanked Courses Based on JD Similarity :\n")
    headers = list(rankings_dict.keys())
    print(" | ".join(h.replace("_", " ").title() for h in headers))
    print("-" * 80)

    max_len = max(len(rankings_dict[h]) for h in headers)
    for i in range(max_len):
        row = []
        for h in headers:
            try:
                course, score = rankings_dict[h][i]
                row.append(f"{course} ({score:.3f})")
            except IndexError:
                row.append(" " * 20)
        print(" | ".join(row))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"rankings_{timestamp}.txt"
    with open(output_filename, "w") as f:
        # Write JD text
        f.write("Job Description:\n")
        f.write(jd_text.strip() + "\n\n")

        # Write rankings
        f.write("Ranked Courses Based on JD Similarity:\n")
        f.write(" | ".join(h.replace("_", " ").title() for h in headers) + "\n")
        f.write("-" * 80 + "\n")

        for i in range(max_len):
            row = []
            for h in headers:
                try:
                    course, score = rankings_dict[h][i]
                    row.append(f"{course} ({score:.3f})")
                except IndexError:
                    row.append(" " * 20)
            f.write(" | ".join(row) + "\n")

    print(f"\nRankings and JD text saved to {output_filename}")

# === Run this ===
if __name__ == "__main__":
    jd_text = """
    About the job
    Meta Reality Labs - Android/Display Operating Systems Engineer 

    Location: Redmond, WA (Hybrid 2-3 days onsite)
    Compensation: $130,000-$180,000
    Benefits: Medical, Dental, Vision, 401K, Equipment, PTO ect.

    *Must have previous Android Operating System Engineering expertise OR Linux OS engineering experience with display interfaces/display pipelines*

    Summary

    We are looking for an Android/Display Operating Systems Engineer that can apply the principles of computer science and mathematical analysis to the design, development, testing, and evaluation of the display systems and pipelines that we build for prototyping new components and experiences for augmented and mixed reality glasses.

    Job Responsibilities

    Analyze, design, develop, and debug display-related software enabling customers to meet their goals.
    Develop, prepare, and support SW for display demos.
    Collaborate in a team environment across multiple, product focused, research, and engineering disciplines.

    Required Skills (Must Have)

    Experience with software design and programming in C/C++ for development, debugging, testing, and performance analysis.
    Experience with Operating Systems, Android Internals, Linux OS/Kernel Development
    Experience with Android Open Source Project development.
    Experience with display interfaces (e.g. DisplayPort) and display pipelines (e.g. compositors).
    Experience with scripting languages like Python, Bash, etc.
    Verbal and written communication skills, problem solving skills, customer service and interpersonal skills.

    Nice to Have:

    Experience with Continuous Integration and Continuous Deployment (CI/CD) solutions
    Experience with DSP and graphics development.
    Experience with peripherals such as USB, SPI, MIPI CSI/DSI, I2C, UART, GPIO etc.
    Experience with wireless and wired communication protocols, including USB, TCP/IP, Ethernet, Bluetooth and 802.11."""

    # rearranged_jd = rearrange_jd_with_gpt(jd_text)

    # if not rearranged_jd:
    #     print("Failed to process job description.")
    #     exit()

    # jd_embedding = embed_reorganized_jd(jd_text)
    # with open("jd_embedding.json", "r") as f:
        # data = json.load(f)
    
    # jd_embedding = json.loads(data["jd_embedding"])
    # print(f"Parsed type: {type(jd_embedding)}, Length: {len(jd_embedding)}, Sample: {jd_embedding[:5]}")

    #inspect_one_embedding_row(DB_PATH, table_name="embeddings")
    course_embeddings_dict = load_course_embeddings_fromutils(DB_PATH)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = os.path.join(
        os.path.dirname(DB_PATH), 
        f"data/course_embeddings_dict_{timestamp}.json"
    )
    with open(output_file_path, "w") as json_file:
        json.dump(course_embeddings_dict, json_file, indent=4)    
   
    # Write the course_embeddings_dict to a JSON file

    # data_folder = "../data"
    # os.makedirs(data_folder, exist_ok=True)
    # output_file_path = os.path.join(data_folder, "course_embeddings_dict.json")

    # print(f"Course embeddings dictionary saved to {output_file_path}")

    # rankings = match_jd_to_courses(jd_embedding, course_embeddings_dict, top_n=100)

    # print_rankings_human_readable(rankings)
