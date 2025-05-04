# Reload the CSV and description text files to ensure the data is being processed properly
import pandas as pd
import re

# Load the new CSV and description text file
csv_file_path = '/mnt/data/WithDescriptions_Courses_Winter2024.csv'
df_courses = pd.read_csv(csv_file_path)

course_descriptions_file = '/mnt/data/Course Descriptions.txt'
with open(course_descriptions_file, 'r') as file:
    course_descriptions = file.read()

# Regular expression pattern to match course codes (CSExyz or CSExyzb)
course_code_pattern = r'\bCSE\w{3,4}[A-Z]?\b'

# Function to extract course description based on the course code
def extract_description(course_code, lines):
    description = []
    found_course_code = False

    for line in lines:
        if found_course_code:
            if line.strip() == '':  # An empty line indicates the end of the paragraph
                break
            if re.match(course_code_pattern, line.strip()):  # Another course code found
                break  # Stop when another course code is found
            description.append(line.strip())
        if line.startswith(course_code):  # Look for the course code
            found_course_code = True

    return " ".join(description)

# Traverse the CSV file and extract the descriptions
course_desc_dict = {}
lines = course_descriptions.split("\n")
for _, row in df_courses.iterrows():
    course_code = row['Course Code']
    # Extract the description for the course code
    description = extract_description(course_code, lines)
    # Store the description in the dictionary
    course_desc_dict[course_code] = description if description else 'Description not found'

# Map the descriptions back to the DataFrame
df_courses['Course Descriptions'] = df_courses['Course Code'].apply(
    lambda code: course_desc_dict.get(code.strip(), 'Description not found')  # Default if no description is found
)

# Save the updated DataFrame back to a new CSV file
updated_csv_path_final_with_descriptions = '/mnt/data/Updated_Courses_With_Descriptions_Final.csv'
df_courses.to_csv(updated_csv_path_final_with_descriptions, index=False)

# Display the first few rows to verify
df_courses.head()