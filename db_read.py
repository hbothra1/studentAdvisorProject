import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect("courses.db")

# Read courses table into a DataFrame
df_courses = pd.read_sql_query("SELECT * FROM courses;", conn)
df_prereqs = pd.read_sql_query("SELECT * FROM prerequisite_mappings;", conn)

# Display the tables
print("Courses Table:")
print(df_courses.head())

print("\nPrerequisite Mappings Table:")
print(df_prereqs.head())

# Close the connection
conn.close()