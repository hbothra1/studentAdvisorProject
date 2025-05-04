# Description: This script creates a SQLite database and populates it with course data from a CSV file. 
#              It also normalizes course codes and prerequisites, and handles "either/or" cases for prerequisites, stores minimum grade requirements and optional courses
# Known issues: currently it assumes existence of 'or' implies existence of multiple options, and does not handle cases where 'or' does not imply multiple course options
# Known issues: disabled foreign key support due to issues with the CSV data, will be re-enabled once the data is cleaned up. Courses such as CSE360 are not there in the list of classes but do exist in the prerequisites
# ROADMAP: Add support for handling cases where 'or' does not imply multiple course options 
# ROADMAP: Create 'Paths' or 'Tracks' or relations so that it is easy to map courses to prerequisites

import sqlite3
import pandas as pd
import re

# Define the database path

db_path = r"/Users/hemantbothra/Library/CloudStorage/GoogleDrive-hbothra1@gmail.com/My Drive/Projects/studentAdvisorProject/course_database.db"

# Establish connection to SQLite (creates the database if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Enable foreign key support
#cursor.execute("PRAGMA foreign_keys = ON;")
COURSE_PATTERN = re.compile(r'\b(CSE\s?\d{3}[A-Za-z]?|MATH\s?\d{3}[A-Za-z]?|STAT\s?\d{3}[A-Za-z]?|HCDE\s?\d{3}[A-Za-z]?)\b', re.IGNORECASE)

# Function to normalize course codes (ensure "CSE xyz" format)
def normalize_course_code(course_code):
        if isinstance(course_code, str):
            # First normalize any existing patterns with or without space
            normalized = re.sub(r'(?i)\b([A-Z]+)(\d{3}[A-Za-z]?)\b', r'\1 \2', course_code.strip())
            # Convert to uppercase
            return normalized.upper()
        return course_code  # Return as is if not a string

if __name__ == "__main__":
# Create the courses table (if not exists)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        course_code TEXT PRIMARY KEY,
        course_title TEXT NOT NULL,
        quarter_offered TEXT,
        credits INTEGER NOT NULL,
        cnc INTEGER DEFAULT 0,  -- 0 for graded, 1 for credit/no-credit
        course_description TEXT NOT NULL,
        prerequisite TEXT,
        UNIQUE(course_code COLLATE NOCASE)
    );
    """)

    # Create the prerequisite mappings table for better data integrity
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prerequisite_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT NOT NULL,
        prerequisite_code TEXT NOT NULL,
        group_id INTEGER,
        minimum_grade REAL,
        is_optional INTEGER DEFAULT 0,  -- 0 for required, 1 for optional
        FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE CASCADE,
        FOREIGN KEY (prerequisite_code) REFERENCES courses(course_code) ON DELETE CASCADE,
        UNIQUE(course_code COLLATE NOCASE, prerequisite_code COLLATE NOCASE)
    );
    """)

    # Load course data from CSV
    csv_path = r"/Users/hemantbothra/Library/CloudStorage/GoogleDrive-hbothra1@gmail.com/My Drive/Projects/studentAdvisorProject/Updated_Courses_With_Descriptions_Final_OnlyUndergrad_prereqsseperated.csv"
    df = pd.read_csv(csv_path, encoding='ISO-8859-1')

    # Insert course data while handling duplicates
    for _, row in df.iterrows():
        try:
            normalized_course_code = normalize_course_code(row['Course Code'])

            cursor.execute("""
            INSERT INTO courses (course_code, course_title, quarter_offered, credits, course_description, prerequisite)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(course_code) DO UPDATE SET
            course_title=excluded.course_title,
            quarter_offered=excluded.quarter_offered,
            credits=excluded.credits,
            course_description=excluded.course_description,
            prerequisite=excluded.prerequisite;
            """, (normalized_course_code, row['Course Title'], row['Quarter Offered'], row['Credits'], row['Course Descriptions'], row['Prerequisites']))
        except Exception as e:
            print(f"Error inserting {row['Course Code']}: {e}")

    # Extract and insert prerequisites into prerequisite_mappings table, handling "either/or" cases
    group_counter = 1  # Unique ID for prerequisite groups

    for _, row in df.iterrows():
        temp_code = row['Course Code']
        if pd.notna(row['Prerequisites']):
            prerequisite_text = row['Prerequisites'].lower()

            # Split separate requirements using ';' or 'and'
            requirements = re.split(r'\s*(?:;| and )\s*', prerequisite_text)

            for requirement in requirements:
                group_id = group_counter  # Assign a unique group ID

                # Check if "recommended" is present (mark as optional)
                is_optional = 1 if "recommended" in requirement else 0

                # Check for "either" cases
                if "or" in requirement:
                    #options = re.split(r'\s*or\s*', requirement)
                    min_grade_match = re.search(r'minimum grade of ([0-9\.]+) in (.+)', requirement)
                    if min_grade_match:
                        min_grade = float(min_grade_match.group(1))
                    else:
                        min_grade = None
                    
                    options = requirement
                    normalized_options = []
                    #for opt in options:
                    matches = COURSE_PATTERN.findall(options)
                    if matches:
                        for course_code in matches:
                            normalized_course_code = normalize_course_code(course_code)
                            normalized_options.append(normalized_course_code)
                            print(f"Matched course code: {course_code}")  # Debugging line
                            print(f"Normalized course code: {normalized_course_code}")  # Debugging line
                    else:
                        print(f"No match found in option: {options}")  # Debugging line
        
                    options = normalized_options
                
                    for prereq in options:
                        print("Inserting either/or prerequisite mapping: ", prereq)  # Debugging line
                        try:
                            cursor.execute("""
                            INSERT INTO prerequisite_mappings (course_code, prerequisite_code, group_id, is_optional, minimum_grade)
                            VALUES (?, ?, ?, ?, ?)
                            ON CONFLICT(course_code, prerequisite_code) DO NOTHING;
                            """, (normalize_course_code(row['Course Code']), prereq, group_id, is_optional, min_grade if min_grade else None))
                        except Exception as e:
                            print(f"Error inserting either/or prerequisite for {row['Course Code']} -> {prereq}: {e}")
                    group_counter += 1  # Increment for next "either/or" case

                else:
                    # Handle prerequisites with a minimum grade
                    min_grade_match = re.search(r'minimum grade of ([0-9\.]+) in (.+)', requirement)
                    if min_grade_match:
                        min_grade = float(min_grade_match.group(1))
                        match = COURSE_PATTERN.search(requirement)
                        if match:
                            prereq_code = normalize_course_code(match.group(0))

                    else:
                        min_grade = None
                        match = COURSE_PATTERN.search(requirement)
                        if match:
                            prereq_code = normalize_course_code(match.group(0))

                    try:
                        cursor.execute("""
                        INSERT INTO prerequisite_mappings (course_code, prerequisite_code, minimum_grade, is_optional)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(course_code, prerequisite_code) DO NOTHING;
                        """, (normalize_course_code(row['Course Code']), prereq_code, min_grade, is_optional))
                    except Exception as e:
                        print(f"Error inserting prerequisite mapping for {row['Course Code']} -> {prereq_code}: {e}")

    # Commit and close connection
    conn.commit()
    conn.close()

    print("Database setup and data upload complete!")