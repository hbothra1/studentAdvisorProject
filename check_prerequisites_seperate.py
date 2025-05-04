import re
import sqlite3

student_courses = [
    {
        "Quarter": "AUTUMN 2023 CSE",
        "Courses": [
            {
                "Course Code": "ENGL 121",
                "Course Name": "SPECIAL TOPICS",
                "Credits": "5.0",
                "Grade": "4.0"
            },
            {
                "Course Code": "PHYS 121",
                "Course Name": "MECHANICS",
                "Credits": "5.0",
                "Grade": "4.0"
            },
            {
                "Course Code": "CSE 121",
                "Course Name": "INTR CMP PRGR",
                "Credits": "4.0",
                "Grade": "4.0"
            },
            {
                "Course Code": "MATH 121",
                "Course Name": "CALCULUS ANLYT GEOM",
                "Credits": "5.0",
                "Grade": "4.0"
            }
        ]
    },
    {
        "Quarter": "WINTER 2024 CSE 8",
        "Courses": [
            {
                "Course Code": "MATH 208",
                "Course Name": "MTRX ALGB & APPL",
                "Credits": "3.0",
                "Grade": "WIP"
            },
            {
                "Course Code": "CSE 154",
                "Course Name": "WEB PRGRM",
                "Credits": "5.0",
                "Grade": "WIP"
            },
            {
                "Course Code": "CSE 311",
                "Course Name": "FONDRN COMPT",
                "Credits": "4.0",
                "Grade": "WIP"
            }
        ]
    },
    {
        "Quarter": "SPRING 2024 CSE 8",
        "Courses": [
            {
                "Course Code": "CSE 312",
                "Course Name": "FOUNDATIONS OF COMPUTING II",
                "Credits": "4.0",
                "Grade": "WIP"
            },
            {
                "Course Code": "CSE 332",
                "Course Name": "DATA STRUCTURES AND PARALLELISM",
                "Credits": "4.0",
                "Grade": "WIP"
            },
            {
                "Course Code": "CSE 351",
                "Course Name": "THE HARDWARE/SOFTWARE INTERFACE",
                "Credits": "4.0",
                "Grade": "WIP"
            }
        ]
    }
]

response_text = """Based on the job description, here are the recommended courses:

1. **CSE412 - Introduction to Data Visualization** (4 credits)
2. **CSE444 -Introduction to Database Systems ** (4 credits)
3. **CSE452 - Introduction to Artificial IntelligenceCoursePrerequisite:¬†CSE 373.** (4 credits)
"""

# Run function

def check_prerequisites(response_text, student_transcript, db_path):
    #print("Checking prerequisites...")  # Debugging linesqlite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    recommended_courses = {}
    taken_courses = {course['Course Code'] for entry in student_transcript for course in entry['Courses']}
    
    # Define the regex pattern to match "CSExyz" or "CSExyzb"
    pattern = re.compile(r'\b(CSE)(\d{3}[A-Za-z]?)\b', re.IGNORECASE)   

    response_lines = response_text.split("\n")
    for line in response_lines:
        match = pattern.search(line)
        if match:
            # Split CSE and XYZ with a space
            formatted_course_code = f"{match.group(1)} {match.group(2).upper()}"
            formatted_nospace_course_code = f"{match.group(1)}{match.group(2).upper()}"
            #print(f"Matched course code: {formatted_course_code}")  # Debugging line
            cursor.execute("SELECT prerequisite_code, group_id FROM prerequisite_mappings WHERE course_code = ?", (formatted_course_code,))
            rows = cursor.fetchall()
            standalone_prerequisites = set()
            group_prerequisites = {}

            for row in rows:
                prerequisite, group_id = row[0].strip(), row[1]
                if group_id is not None:
                    # Handle grouped prerequisites
                    if group_id not in group_prerequisites:
                        group_prerequisites[group_id] = set()
                    group_prerequisites[group_id].add(prerequisite)
                else:
                    # Handle standalone prerequisites
                    standalone_prerequisites.add(prerequisite)

            # Process grouped prerequisites
            grouped_output = set()
            for group_id, prerequisites in group_prerequisites.items():
                if not any(prereq in taken_courses for prereq in prerequisites):
                    grouped_output.add(" or ".join(sorted(prerequisites)))
            
            # ✅ Process standalone prerequisites (those with None as group_id)
            final_standalone_prereqs = {prereq for prereq in standalone_prerequisites if prereq not in taken_courses}

            grouped_output = {" or ".join(group) for group in group_prerequisites.values()}

            # Combine grouped and standalone prerequisites into one set
            all_prereqs = final_standalone_prereqs.union(grouped_output) 
            recommended_courses[formatted_nospace_course_code] = all_prereqs if all_prereqs else {"No Prereqs"}

    conn.close()
    
    if recommended_courses:
        formatted_output = "\nBefore taking some of the recommended courses, consider completing these prerequisites:\n"
        for course, prereqs in recommended_courses.items():
            formatted_output += f"{course}: {', '.join(prereqs)}\n"
        return formatted_output
    else:
        return "No additional prerequisites needed."    

missing_prereqs = check_prerequisites(response_text, student_courses, "course_database.db")

# Display result
print("Missing Prerequisites:", missing_prereqs)