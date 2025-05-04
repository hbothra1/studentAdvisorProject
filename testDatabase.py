import sqlite3

def fetch_prerequisites(course_code):
    # Connect to the database
    conn = sqlite3.connect('course_database.db')
    cursor = conn.cursor()
    
    # Execute the query
    cursor.execute("SELECT * FROM prerequisite_mappings WHERE course_code = ?", (course_code,))
    
    # Fetch all results
    rows = cursor.fetchall()
    
    # Print the output
    for row in rows:
        print(row)
    
    # Close the connection
    conn.close()

# Fetch and print prerequisites for course code 'CSE 451'
fetch_prerequisites('CSE 446')