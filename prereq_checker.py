# prereq_checker.py
import sqlite3
import re
import json
import logging

def build_prereq_tree(course_code, taken_courses, cursor, visited=None):
    """
    Recursively builds a tree representing all prerequisites for a given course.
    
    Each node in the returned list is a dictionary:
      - For a standalone course: 
            { "course": <course_code>, "type": "mandatory"/"optional", "prerequisites": [...] }
      - For a group (multiple courses satisfying a requirement):
            { "group": [ { "course": <course_code>, "prerequisites": [...] }, ... ],
              "type": "mandatory"/"optional" }
    
    Args:
        course_code (str): The course to look up prerequisites for.
        taken_courses (set): Courses the student has already taken.
        cursor (sqlite3.Cursor): Database cursor to run queries.
        visited (set): Courses already processed in the current recursion branch.
    
    Returns:
        list: A list of prerequisite nodes (each a dict) for the given course.
    """
    if visited is None:
        visited = set()
    # Prevent cycles by returning an empty list if this course was already visited
    if course_code in visited:
        return []
    # Mark the current course as visited in this branch.
    visited.add(course_code)
    
    cursor.execute(
        """SELECT prerequisite_code, group_id, is_optional 
           FROM prerequisite_mappings 
           WHERE course_code = ?""",
        (course_code,)
    )
    rows = cursor.fetchall()

    # Separate rows into standalone prerequisites and grouped prerequisites.
    standalone = []  # List of tuples: (prereq, is_optional)
    groups = {}      # Mapping: group_id -> list of tuples (prereq, is_optional)
    
    for row in rows:
        prereq = row[0].strip()
        group_id = row[1]
        is_optional = row[2]
        if group_id:
            groups.setdefault(group_id, []).append((prereq, is_optional))
        else:
            standalone.append((prereq, is_optional))
    
    nodes = []
    
    # Process standalone prerequisites.
    for prereq, is_optional in standalone:
        if prereq not in taken_courses:
            # Recurse to build nested prerequisites for this course.
            nested = build_prereq_tree(prereq, taken_courses, cursor, visited.copy())
            node = {
                "course": prereq,
                "type": "optional" if is_optional else "mandatory",
                "prerequisites": nested
            }
            nodes.append(node)
    
    # Process grouped prerequisites.
    for group_id, items in groups.items():
        # Include the group only if none of the courses in the group have been taken.
        if not any(course in taken_courses for course, _ in items):
            # Assume that if any course in the group is optional, the whole group is optional.
            group_type = "optional" if any(is_optional for _, is_optional in items) else "mandatory"
            group_nodes = []
            for course, _ in items:
                nested = build_prereq_tree(course, taken_courses, cursor, visited.copy())
                cursor.execute(
                    "SELECT course_description FROM courses WHERE course_code = ?",
                    (course,)
                )
                description_row = cursor.fetchone()
                course_description = description_row[0] if description_row else "Description not available"
                group_nodes.append({
                    "course": course,
                    "prerequisites": nested,
                    "course_description": course_description
                })
            node = {
                "group": group_nodes,
                "type": group_type
            }
            nodes.append(node)
    
    return nodes

def check_prerequisites(response_text, student_transcript, db_path):
    """
    Checks prerequisites for recommended courses in the response_text using the student's transcript 
    and a SQLite database. Builds a hierarchical JSON structure reflecting nested prerequisites.
    
    Args:
        response_text (str): Text that contains recommended courses.
        student_transcript (list): The student's transcript in JSON format.
        db_path (str): Path to the SQLite database containing prerequisite mappings.
    
    Returns:
        dict: JSON-ready dictionary mapping recommended course codes to their prerequisite trees.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    recommended_courses = {}
    # Build a set of courses the student has taken.
    taken_courses = {course['Course Code'] for entry in student_transcript for course in entry['Courses']}
    
    pattern = re.compile(r'\b(CSE)(\d{3}[A-Za-z]?)\b', re.IGNORECASE)
    response_lines = response_text.split("\n")
    
    for line in response_lines:
        match = pattern.search(line)
        if match:
            # Format the course code consistently.
            formatted_course_code = f"{match.group(1)} {match.group(2).upper()}"
            formatted_nospace_course_code = f"{match.group(1)}{match.group(2).upper()}"
            # Build the prerequisite tree for this recommended course.
            cursor.execute(
                "SELECT course_description FROM courses WHERE course_code = ?",
                (formatted_course_code,)
            )
            description_row = cursor.fetchone()
            course_description = description_row[0] if description_row else "Description not available"
            
            prereq_tree = build_prereq_tree(formatted_course_code, taken_courses, cursor)
            recommended_courses[formatted_nospace_course_code] = {
                "prerequisites": prereq_tree,
                "description": course_description
            }
    
    conn.close()
    return recommended_courses

def run_tests():
    """
    Runs all predefined test cases for the prerequisite checker.
    Logs the expected and actual outputs for verification.
    """

    logging.info("Starting prerequisite checker tests.")

    test_cases = [
        {
            "name": "Test Case 1a: Empty Transcript (New Student)",
            "student_courses": [],
            "response_text": "Based on the job description, here are the recommended courses:\n1. **CSE312 - Foundations of Computing II** (4 credits)",
            "expected_output": "Expected: Since the student has no courses, the prerequisite tree for CSE312 should list all prerequisites."
        },
        {
            "name": "Test Case 1b: Single Quarter Transcript",
            "student_courses": [
                {
                    "Quarter": "AUTUMN 2023 CSE",
                    "Courses": [
                        {"Course Code": "ENGL 121", "Course Name": "SPECIAL TOPICS", "Credits": "5.0", "Grade": "4.0"},
                        {"Course Code": "PHYS 121", "Course Name": "MECHANICS", "Credits": "5.0", "Grade": "4.0"},
                        {"Course Code": "CSE 121", "Course Name": "INTR CMP PRGR", "Credits": "4.0", "Grade": "4.0"},
                        {"Course Code": "MATH 121", "Course Name": "CALCULUS ANLYT GEOM", "Credits": "5.0", "Grade": "4.0"}
                    ]
                }
            ],
            "response_text": "Based on the job description, here are the recommended courses:\n1. **CSE312 - Foundations of Computing II** (4 credits)",
            "expected_output": "Expected: CSE312's prerequisites should be checked against the single-quarter transcript."
        },
        {
            "name": "Test Case 2: Student Missing Some Prerequisites",
            "student_courses": [
                {"Quarter": "Autumn 2023", 
                 "Courses": [
                     {"Course Code": "MATH 208", "Course Name": "Discrete Mathematics", "Credits": "4.0", "Grade": "3.7"},
                     {"Course Code": "CSE 143", "Course Name": "Dummy Name", "Credits": "4.0", "Grade": "3.8"},
                     {"Course Code": "MATH 126", "Course Name": "Dummy Name", "Credits": "4.0", "Grade": "3.8"},
                    ]
                 
                },
                {"Quarter": "Winter 2024", "Courses": [{"Course Code": "CSE 142", "Course Name": "Introduction to Programming", "Credits": "4.0", "Grade": "3.5"}]}
            ],
            "response_text": "Based on the job description, here are the recommended courses:\n1. **CSE312 - Foundations of Computing II** (4 credits)\n2. **CSE332 - Data Structures and Parallelism** (4 credits)\n3. **CSE451 - Introduction to Operating Systems** (4 credits)",
            "expected_output": "Expected: Function should return missing prerequisites for CSE312, CSE332, and CSE451."
        },
        {
            "name": "Test Case 3: Student Missing No Prerequisites",
            "student_courses": [
                {"Quarter": "Autumn 2023", 
                 "Courses": [
                     {"Course Code": "MATH 208", "Course Name": "Discrete Mathematics", "Credits": "4.0", "Grade": "3.7"},
                     {"Course Code": "CSE 143", "Course Name": "Dummy Name", "Credits": "4.0", "Grade": "3.8"},
                     {"Course Code": "MATH 126", "Course Name": "Dummy Name", "Credits": "4.0", "Grade": "3.8"},
                    ]
                 
                },
                {"Quarter": "Winter 2024", 
                 "Courses": [
                     {"Course Code": "CSE 142", "Course Name": "Introduction to Programming", "Credits": "4.0", "Grade": "3.5"},
                     {"Course Code": "CSE 311", "Course Name": "Introduction to Programming", "Credits": "4.0", "Grade": "3.5"},
                     ]
                }
            ],
            "response_text": "Based on the job description, here are the recommended courses:\n1. **CSE312 - Foundations of Computing II** (4 credits)\n2. **CSE332 - Data Structures and Parallelism** (4 credits)\n3.",
            "expected_output": "Expected: Function should return no missing prerequisites for CSE312 and CSE332."
        }
        
    ]

    for test in test_cases:
        logging.info("--------------------------------------------------")
        logging.info("Running %s", test["name"])
        logging.info("Expected output: %s", test["expected_output"])

        # Run the prerequisite checker
        result = check_prerequisites(test["response_text"], test["student_courses"], "course_database.db")

        # Log actual output
        result_json = json.dumps(result, indent=2)
        logging.info("Actual output: %s", result_json)

        # Print to console (useful in VS Code Output Panel)
        print("==================================================")
        print("Test: ", test["name"])
        print("Expected: ", test["expected_output"])
        print("Actual: ")
        print(result_json)
        print("==================================================\n")

    logging.info("Finished all tests.")

# For testing purposes: 
if __name__ == "__main__":
    run_tests()
    # response_text = (
    #     "Based on the student's record, consider taking:\n"
    #     "CSE312 - Foundations of Computing II\n"
    #     "CSE332 - Data Structures and Parallelism\n"
    #     "CSE452 - Data Structures and Parallelism\n"
    # )
    
    # student_transcript = [
    #     {
    #         "Quarter": "Fall 2022",
    #         "Courses": [
    #             {"Course Name": "Intro to Computer Science", "Course Code": "CSE 101", "Credits": 4, "Grade": "A"}
    #         ]
    #     }
    # ]
    
    # db_path = "course_database.db"
    # output = check_prerequisites(response_text, student_transcript, db_path)
    # # Print JSON with indentation.
    # print(json.dumps(output, indent=2))
