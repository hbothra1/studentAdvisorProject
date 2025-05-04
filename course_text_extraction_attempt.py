import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import re
from datetime import datetime

# Connect to the SQLite database
conn = sqlite3.connect("course_database.db")
cursor = conn.cursor()

# Keywords for filtering
include_keywords = [
    "course goals", "objectives", "learning", "topics", "outcomes",
    "overview", "description", "introduction", "expectations",
    "about the course", "skills", "concepts", "themes"
]

exclude_keywords = [
    "academic honesty", "schedule", "late work", "grading", "accommodations",
    "instructor", "contact", "office hours", "ta", "disability", "textbook",
    "calendar", "exam", "homework", "policy", "plagiarism"
]

# Prepare failure log
log_file = "failed_text_detection_courses.txt"

# Read existing log content if the file exists
if os.path.exists(log_file):
    with open(log_file, "r") as fail_log:
        existing_content = fail_log.read()
else:
    existing_content = ""

# Start a new log session
new_log_entries = []
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
new_log_entries.append(f"Log session started at: {timestamp}\n")

# Query all courses from DB
cursor.execute("SELECT course_code, course_title, prerequisite FROM courses")
all_courses = cursor.fetchall()

for course_code, course_title, prerequisite in all_courses:
    if not course_code.startswith("CSE"):
        continue

    formatted_code = course_code.lower().replace(" ", "")
    output_file = f"{formatted_code}_embedding_text.txt"

    # Skip if file already exists
    if os.path.exists(output_file):
        print(f"⏩ Skipping {course_code} — text already extracted")
        continue

    quarters = ["25wi", "24au", "24su", "24sp"]
    success = False
    last_exception = None

    for quarter in quarters:
        urls_to_try = [
            f"https://courses.cs.washington.edu/courses/{formatted_code}/{quarter}/syllabus",
            f"https://courses.cs.washington.edu/courses/{formatted_code}/{quarter}/syllabus.html",
            f"https://courses.cs.washington.edu/courses/{formatted_code}/{quarter}/resources/syllabus.html",
            f"https://courses.cs.washington.edu/courses/{formatted_code}/{quarter}/"
        ]

        for url in urls_to_try:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    raise Exception(f"Status code: {response.status_code}")

                soup = BeautifulSoup(response.text, 'html.parser')
                content_div = soup.find("div", id="content")
                if content_div:
                    elements = content_div.find_all(["h1", "h2", "h3", "p", "li"])
                else:
                    elements = soup.find_all(["h1", "h2", "h3", "p", "li"])

                sections = []
                include_section = False
                current_block = ""

                for el in elements:
                    tag_text = el.get_text(strip=True)
                    tag_text_lower = tag_text.lower()

                    if el.name in ["h1", "h2", "h3"]:
                        if current_block:
                            sections.append(current_block.strip())
                            current_block = ""
                        include_section = any(k in tag_text_lower for k in include_keywords)
                        if any(k in tag_text_lower for k in exclude_keywords):
                            include_section = False
                        if include_section:
                            current_block += tag_text + "\n"

                    elif include_section and el.name in ["p", "li"]:
                        current_block += tag_text + "\n"

                if current_block:
                    sections.append(current_block.strip())

                if not sections:
                    raise Exception("No relevant headings matched for extraction.")

                course_text = "\n\n".join(sections)

                with open(output_file, "w") as f:
                    f.write(course_text)

                print(f"✅ Extracted text for {course_code} ({quarter})")
                success = True
                break  # Exit inner URL loop once successful

            except Exception as e:
                last_exception = str(e)

        if success:
            break  # Exit outer quarter loop once successful

    if not success:
        new_log_entries.append(f"{course_code} - Failed: {last_exception}\n")
        print(f"❌ Failed: {course_code} — {last_exception}")

# Write the updated log content back to the file
with open(log_file, "w") as fail_log:
    fail_log.writelines(new_log_entries + ["\n"] + existing_content.splitlines(keepends=True))

# Finalize
conn.close()
print("🏁 Done extracting text from all CSE courses.")
