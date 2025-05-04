#!/usr/bin/env python3
"""
Prerequisite Checker Module

This module provides functionality to build a hierarchical dependency tree of prerequisites
for recommended courses based on a student's transcript and a SQLite database mapping
course prerequisites.

The main features include:
- Recursive traversal of course prerequisites, handling nested and grouped prerequisites.
- Prevention of cyclic dependencies using a visited set.
- Differentiation between mandatory and optional prerequisites.
- Returning the results as a JSON-ready dictionary.

Developers can modify or extend the code as needed.
"""

import sqlite3
import re
import json

def build_prereq_tree(course_code, taken_courses, cursor, visited=None):
    """
    Recursively builds a dependency tree (list of nodes) representing all prerequisites for a given course.

    Each node in the returned list is a dictionary with one of the following structures:
    
    For a standalone prerequisite course:
      {
          "course": <course_code>,        # The course code (e.g., "CSE311")
          "type": "mandatory" or "optional",  # Whether the prerequisite is mandatory or optional
          "prerequisites": [...]          # A list of nested prerequisite nodes for this course
      }
    
    For a grouped prerequisite (where multiple courses satisfy the requirement):
      {
          "group": [                     # A list of alternative courses
              {
                  "course": <course_code>,    # An alternative course code
                  "prerequisites": [...]       # Its own nested prerequisites (if any)
              },
              ...
          ],
          "type": "mandatory" or "optional"   # The overall type for the group (optional if any alternative is optional)
      }
    
    Args:
        course_code (str): The course for which prerequisites are being retrieved.
        taken_courses (set): A set of course codes the student has already taken.
        cursor (sqlite3.Cursor): Database cursor used to query the prerequisite mappings.
        visited (set, optional): A set of course codes already processed in the current recursion branch.
                                 This is used to prevent infinite loops in the presence of cyclic dependencies.
    
    Returns:
        list: A list of prerequisite nodes (each a dictionary) representing the full dependency tree for the course.
    """
    if visited is None:
        visited = set()
    # Prevent processing the same course twice in the same recursion branch.
    if course_code in visited:
        return []
    visited.add(course_code)
    
    # Query the database for prerequisites of the given course.
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
            # Add to the corresponding group.
            groups.setdefault(group_id, []).append((prereq, is_optional))
        else:
            standalone.append((prereq, is_optional))
    
    nodes = []  # List to hold all prerequisite nodes for the current course.
    
    # Process standalone prerequisites.
    for prereq, is_optional in standalone:
        # Only add the prerequisite if the student has not already taken it.
        if prereq not in taken_courses:
            # Recursively build the dependency tree for the standalone prerequisite.
            nested = build_prereq_tree(prereq, taken_courses, cursor, visited.copy())
            node = {
                "course": prereq,
                "type": "optional" if is_optional else "mandatory",
                "prerequisites": nested
            }
            nodes.append(node)
    
    # Process grouped prerequisites.
    for group_id, items in groups.items():
        # Only consider the group if none of the courses in the group have been taken.
        if not any(course in taken_courses for course, _ in items):
            # If any course in the group is optional, mark the entire group as optional.
            group_type = "optional" if any(is_optional for _, is_optional in items) else "mandatory"
            group_nodes = []
            for course, _ in items:
                # Recursively build the dependency tree for each course in the group.
                nested = build_prereq_tree(course, taken_courses, cursor, visited.copy())
                group_nodes.append({
                    "course": course,
                    "prerequisites": nested
                })
            node = {
                "group": group_nodes,
                "type": group_type
            }
            nodes.append(node)
    
    return nodes

def check_prerequisites(response_text, student_transcript, db_path):
    """
    Checks prerequisites for recommended courses specified in the response_text and builds a
    hierarchical JSON structure that reflects direct and nested prerequisites.

    The recommended courses are extracted from the response_text (using a regex pattern).
    For each recommended course, the function constructs a prerequisite tree using the build_prereq_tree function.
    
    The final JSON structure is a dictionary mapping each recommended course (formatted without spaces)
    to an object that contains its prerequisite dependency tree.
    
    Example Output Structure:
    {
        "CSE312": {
            "prerequisites": [
                {
                    "course": "CSE311",
                    "type": "mandatory",
                    "prerequisites": [
                        {
                            "group": [
                                { "course": "CSE123", "prerequisites": [] },
                                { "course": "CSE143", "prerequisites": [] }
                            ],
                            "type": "mandatory"
                        },
                        {
                            "group": [
                                { "course": "MATH126", "prerequisites": [] },
                                { "course": "MATH136", "prerequisites": [] }
                            ],
                            "type": "mandatory"
                        }
                    ]
                }
            ]
        },
        ...
    }
    
    Args:
        response_text (str): The text output (e.g., from an API) that contains recommended course codes.
        student_transcript (list): The student's academic transcript in JSON format.
        db_path (str): File path to the SQLite database containing the prerequisite mappings.
    
    Returns:
        dict: A JSON-ready dictionary mapping recommended course codes to their prerequisite trees.
    """
    # Connect to the SQLite database.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    recommended_courses = {}
    # Build a set of course codes that the student has already taken.
    taken_courses = {course['Course Code'] for entry in student_transcript for course in entry['Courses']}
    
    # Regex pattern to extract course codes (e.g., CSE312).
    pattern = re.compile(r'\b(CSE)(\d{3}[A-Za-z]?)\b', re.IGNORECASE)
    response_lines = response_text.split("\n")
    
    # Process each line in the response text.
    for line in response_lines:
        match = pattern.search(line)
        if match:
            # Standardize the course code format.
            formatted_course_code = f"{match.group(1)} {match.group(2).upper()}"
            formatted_nospace_course_code = f"{match.group(1)}{match.group(2).upper()}"
            # Build the prerequisite tree for the recommended course.
            prereq_tree = build_prereq_tree(formatted_course_code, taken_courses, cursor)
            recommended_courses[formatted_nospace_course_code] = {
                "prerequisites": prereq_tree
            }
    
    conn.close()
    return recommended_courses

# For testing and demonstration purposes.
if __name__ == "__main__":
    # Example response text containing recommended courses.
    response_text = (
        "Based on the student's record, consider taking:\n"
        "CSE312 - Foundations of Computing II\n"
        "CSE332 - Data Structures and Parallelism\n"
        "CSE452 - Data Structures and Parallelism\n"
    )
    
    # Example student transcript with one course taken.
    student_transcript = [
        {
            "Quarter": "Fall 2022",
            "Courses": [
                {"Course Name": "Intro to Computer Science", "Course Code": "CSE 101", "Credits": 4, "Grade": "A"}
            ]
        }
    ]
    
    # Update this path to your actual SQLite database location.
    db_path = "course_database.db"
    
    # Get the prerequisite JSON structure.
    output = check_prerequisites(response_text, student_transcript, db_path)
    # Print the JSON with indentation for easy reading.
    print(json.dumps(output, indent=2))
