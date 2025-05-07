
# pip install transformers
# pip install pandas

# Import necessary libraries
import json
import sqlite3
import re
import pandas as pd
# import openai
import tiktoken
from config import DB_PATH
#from transformers import pipeline

# Modify these paths to where the files are located in the Google Colab environment
job_description_path = r'/Users/hemantbothra/Library/CloudStorage/GoogleDrive-hbothra1@gmail.com/My Drive/Projects/studentAdvisorProject/job_description_softwareengineering.json'
transcript_json_path = r'/Users/hemantbothra/Library/CloudStorage/GoogleDrive-hbothra1@gmail.com/My Drive/Projects/studentAdvisorProject/transcript_json2_CSE.json'
course_list_path = r'/Users/hemantbothra/Library/CloudStorage/GoogleDrive-hbothra1@gmail.com/My Drive/Projects/studentAdvisorProject/Updated_Courses_No_Descriptions_Final_OnlyUndergrad.csv'
db_path = DB_PATH


# Load the job description JSON
with open(job_description_path) as f:
    job_description = json.load(f)

# Load the student transcript JSON
with open(transcript_json_path) as f:
    student_transcript = json.load(f)

# Load the course descriptions CSV
course_descriptions = pd.read_csv(course_list_path, encoding='ISO-8859-1')

# Function to format job description into human-readable text
def format_job_description(job_description):
    formatted_text = ""
    
    # Check if 'About the Company' exists in the job description, else use a default message
    if 'About the Company' in job_description:
        formatted_text += "About the Company:\n" + "\n".join(job_description['About the Company']) + "\n\n"
    else:
        formatted_text += "About the Company: Information not available.\n\n"
    
    # Check if 'About the Role' exists in the job description
    if 'About the Role' in job_description:
        formatted_text += "About the Role:\n" + "\n".join(job_description['About the Role']) + "\n\n"
    else:
        formatted_text += "About the Role: Information not available.\n\n"
    
    # Check if 'Responsibilities' exists in the job description
    if 'Responsibilities' in job_description:
        formatted_text += "Responsibilities:\n" + "\n".join(job_description['Responsibilities']) + "\n\n"
    else:
        formatted_text += "Responsibilities: Information not available.\n\n"
    
    # Check if 'Skills & Requirements' exists in the job description
    if 'Skills & Requirements' in job_description:
        formatted_text += "Skills & Requirements:\n" + "\n".join(job_description['Skills & Requirements']) + "\n\n"
    else:
        formatted_text += "Skills & Requirements: Information not available.\n\n"
    
    # Check if 'Nice-to-Haves' exists in the job description
    if 'Nice-to-Haves' in job_description:
        formatted_text += "Nice-to-Haves:\n" + "\n".join(job_description['Nice-to-Haves']) + "\n\n"
    else:
        formatted_text += "Nice-to-Haves: Information not available.\n\n"
    # Check if 'Cultural Fit exists' exists in the job description        
    if 'Cultural Fit' in job_description:
        formatted_text += "Cultural Fit:\n" + "\n".join(job_description['Cultural Fit']) + "\n\n"
    else:
        formatted_text += "Cultural Fit: Information not available.\n\n"
    # Check if 'Technology Stack' exists in the job description        
    if 'Technology Stack' in job_description:
        formatted_text += "Technology Stack:\n" + "\n".join(job_description['Technology Stack']) + "\n\n"
    else:
        formatted_text += "Technology Stack: Information not available.\n\n"
        
    return formatted_text

# Function to format student's courses into human-readable text
def format_student_courses(student_transcript):
    formatted_text = ""
    for entry in student_transcript:
        formatted_text += f"Quarter: {entry['Quarter']}\n"
        for course in entry['Courses']:
            formatted_text += f"  {course['Course Name']} ({course['Course Code']}): {course['Credits']} credits, Grade: {course['Grade']}\n"
        formatted_text += "\n"
    return formatted_text

# Function to add course descriptions 
def add_course_descriptions(course_descriptions):
    course_info = []
    for _, row in course_descriptions.iterrows():
        course_code = row['Course Code']
        
        # Check if the 'Course Code' is empty or NaN
        if pd.isna(course_code) or course_code == "":
            continue  # Skip this row if the course code is empty or missing
        
        course_title = row['Course Title']  # Assuming there is a column for course titles
        credits = row['Credits']  # Assuming this column exists
      # description = row['Course Descriptions']  # Course description from the CSV

        # Format each course's information with description
        #course_info.append(f"{course_code} - {course_title}: {credits} credits. {description}")
        
        # Format each course's information with description
        course_info.append(f"{course_code} - {course_title}: {credits}.")
    
    return course_info

# Function to check prerequisites for recommended courses
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

# Generate the final prompt
def generate_advisory_prompt(job_description, student_transcript, course_descriptions):
    # Format the job description and student courses
    job_desc_text = format_job_description(job_description)
    student_courses_text = format_student_courses(student_transcript)
    course_info = add_course_descriptions(course_descriptions)

    #final_prompt = job_desc_text + student_courses_text + "Available Courses:\n" + course_info
    # Combine all pieces into the final prompt
    final_prompt = job_desc_text + "Student's Current and Completed Courses:\n" + student_courses_text + "All Available Courses:\n" + "\n".join(course_info)
    return final_prompt

# Generate the advisory prompt

if __name__ == "__main__":
    # Any main execution code that shouldn't run when imported
    print("Running promptMaker_Model directly.")
    system_role_content = (
    "You're an AI-powered student advisor for Computer Science Engineering students at the University of Washington.\n"
    "Given a student's academic history and job aspirations, recommend courses they should take to improve their skillset.\n"
    "Prioritize relevance to the job description provided, considering prerequisites and credit limits (8-18 credits per quarter).\n\n"
)
    final_prompt = generate_advisory_prompt(job_description, student_transcript, course_descriptions)
    print(final_prompt)
    # Define the string

    # Open a file in write mode (this will create the file if it doesn't exist)
    with open("promptGenerated.txt", "w") as file:
    # Write the string to the file
        file.write(final_prompt)

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    token_count = len(encoding.encode(final_prompt))
    print(f"Token Count: {token_count} tokens (accurate count)")

    # Send request to GPT-3.5 Turbo API
    """ response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Optimized for chat-based tasks
        messages=[{"role": "system", "content": system_role_content},
                {"role": "user", "content": final_prompt}],
        max_tokens=1000,  # Adjust to control response length
        temperature=0.7,  # Controls randomness
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    ) """

    response_text = ( "Based on the job description and the student's academic history, here are the recommended courses for the student to enhance their skillset for the Software Engineering position:\n"
    "1. **CSE312 - Foundations of Computing II** (4 credits): This course covers enumeration, discrete probability, randomness in computing, and NP-completeness, which are essential topics for software engineering roles.\n"
    "2. **CSE332 - Data Structures and Parallelism** (4 credits): Understanding abstract data types, data structures, and algorithms is crucial for efficient software development. This course covers sorting, fundamental graph algorithms, and P vs. NP complexity classes.\n"
    "3. **CSE403 - Software Engineering** (4 credits): This course focuses on the fundamentals of software engineering, including software design, testing, analysis, and tools. It involves a group project, which aligns with the collaborative nature of the role.\n"
    "4. **CSE415 - Introduction to Artificial Intelligence** (3 credits): Since the job description mentions applied AI, this course will provide a solid foundation in AI principles, including knowledge representation, logical reasoning, and machine learning.\n"
    "5. **CSE426 - Cryptography** (4 credits): Understanding modern cryptography is valuable for software engineers dealing with data security and encryption. This course covers encryption techniques, message authentication, and security proofs.\n"
    "6. **CSE451 - Introduction to Operating Systems** (4 credits): Knowledge of operating systems principles, process management, memory management, and resource allocation is essential for software development. This course will deepen the student's understanding of system software.\n"
    "These courses will help the student acquire the skills and knowledge necessary for the Software Engineering position, especially in areas like software design, algorithms, AI, cryptography, and operating systems. Make sure to consider prerequisites and credit limits when planning your course schedule.\n\n"
    )

    # Check prerequisites before printing response
    #response_text = response["choices"][0]["message"]["content"].strip()
    prerequisite_suggestion = check_prerequisites(response_text, student_transcript, db_path)

    """ Use GPT-2 for text generation
    Load the GPT-2 model using Hugging Face's pipeline
    generator = pipeline("text-generation", model="gpt2")

    Generate a response from GPT-2 using the final prompt
    response = generator(final_prompt, max_length=300, num_return_sequences=1)

    Print the response generated by GPT-2
    print("GPT-2 Response:")
    print(response[0]['generated_text']) """