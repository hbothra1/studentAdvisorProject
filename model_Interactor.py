#formats the job description, student transcript, and course descriptions into a single prompt
from openai import OpenAI
import os
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
import json
import pandas as pd
import tiktoken
import sqlite3

# --- Data Loading Functions ---
def load_job_description(filepath):
    with open(filepath) as f:
        return json.load(f)

def load_student_transcript(filepath):
    with open(filepath) as f:
        return json.load(f)

def load_course_descriptions(filepath):
    return pd.read_csv(filepath, encoding='ISO-8859-1')

# --- Formatting Functions ---
def format_job_description(job_description):
    formatted_text = ""
    if 'About the Company' in job_description:
        formatted_text += "About the Company:\n" + "\n".join(job_description['About the Company']) + "\n\n"
    else:
        formatted_text += "About the Company: Information not available.\n\n"

    if 'About the Role' in job_description:
        formatted_text += "About the Role:\n" + "\n".join(job_description['About the Role']) + "\n\n"
    else:
        formatted_text += "About the Role: Information not available.\n\n"

    if 'Responsibilities' in job_description:
        formatted_text += "Responsibilities:\n" + "\n".join(job_description['Responsibilities']) + "\n\n"
    else:
        formatted_text += "Responsibilities: Information not available.\n\n"

    if 'Skills & Requirements' in job_description:
        formatted_text += "Skills & Requirements:\n" + "\n".join(job_description['Skills & Requirements']) + "\n\n"
    else:
        formatted_text += "Skills & Requirements: Information not available.\n\n"

    if 'Nice-to-Haves' in job_description:
        formatted_text += "Nice-to-Haves:\n" + "\n".join(job_description['Nice-to-Haves']) + "\n\n"
    else:
        formatted_text += "Nice-to-Haves: Information not available.\n\n"

    if 'Cultural Fit' in job_description:
        formatted_text += "Cultural Fit:\n" + "\n".join(job_description['Cultural Fit']) + "\n\n"
    else:
        formatted_text += "Cultural Fit: Information not available.\n\n"

    if 'Technology Stack' in job_description:
        formatted_text += "Technology Stack:\n" + "\n".join(job_description['Technology Stack']) + "\n\n"
    else:
        formatted_text += "Technology Stack: Information not available.\n\n"

    return formatted_text

def format_student_courses(student_transcript):
    formatted_text = ""
    for entry in student_transcript:
        formatted_text += f"Quarter: {entry['Quarter']}\n"
        for course in entry['Courses']:
            formatted_text += f"  {course['Course Name']} ({course['Course Code']}): {course['Credits']} credits, Grade: {course['Grade']}\n"
        formatted_text += "\n"
    return formatted_text

def add_course_descriptions(course_descriptions):
    
    course_info = []
    
    for _, row in course_descriptions.iterrows():
        course_code = row['Course Code']
        if pd.isna(course_code) or course_code == "":
            continue
        course_title = row['Course Title']
        credits = row['Credits']
        course_info.append(f"{course_code} - {course_title}: {credits}.")
    return course_info

def get_shortlisted_course_details(shortlisted_courses, db_path):
        """
        Fetches detailed information for shortlisted courses from the database.

        Args:
            shortlisted_courses (list): List of shortlisted course codes.
            db_path (str): Path to the course database.

        Returns:
            list: A list of formatted strings containing course details.
        """

        course_details = []

        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for course_code in shortlisted_courses:
            # Query the database for the course details
            cursor.execute("""
                SELECT course_description, learning_goals, topics_covered, tools
                FROM embeddings
                WHERE course_code = ?
            """, (course_code,))

            result = cursor.fetchone()
            if result:
                course_description, learning_goals, topics_covered, tools = result
                formatted_detail = (
                    f"{course_code}: \nCourse Description: {course_description} \n\n"
                    f"Learning Goals: \n{learning_goals} \n\n"
                    f"Topics Covered: \n{topics_covered} \n\n"
                    f"Tools:\n{tools}\n\n\n"
                )
                course_details.append(formatted_detail)

        # Close the database connection
        conn.close()

        return course_details

# --- Prompt Generation ---
def generate_advisory_prompt(job_description, student_transcript, shortlisted_course_details, course_descriptions=None):
    
   
    if isinstance(job_description, dict):
        job_desc_text = format_job_description(job_description)
    else:
        job_desc_text = job_description

    

    student_courses_text = format_student_courses(student_transcript)
    if isinstance(course_descriptions, pd.DataFrame):
        course_descriptions = add_course_descriptions(course_descriptions)
    
    # shortlisted_courses_details= get_shortlisted_course_details(shortlisted_courses, db_path="/Users/hemantbothra/Library/CloudStorage/GoogleDrive-hbothra1@gmail.com/My Drive/Projects/studentAdvisorProject/course_database.db") if shortlisted_courses else None
    course_info = shortlisted_course_details if shortlisted_course_details else add_course_descriptions(course_descriptions)

    final_prompt = (
        job_desc_text +
        "Student's Current and Completed Courses:\n" +
        student_courses_text +
        "Below are the detailed course descriptions, including Learning Goals, Topics Covered, and Tools. Please ground all your examples explicitly in this information. \n" +
        "\n".join(course_info)
    )
    return final_prompt

# --- OpenAI API Interaction ---
def send_prompt_to_openai(prompt, system_role_content=None, model="gpt-3.5-turbo", max_tokens=1000, temperature=0.7):
    """
    Sends the provided prompt to the OpenAI API and returns the generated response.
    """
    messages = []
    
    if system_role_content is None:
        system_role_content = (
            """ 
You are a career advisor specializing in helping Computer Science students at the University of Washington select courses to better prepare for their target jobs.

When recommending courses, you must follow these instructions:

Explicitly reference specific information from the provided course fields:

Learning Goals

Topics Covered

Tools

Course Description

Provide a realistic, concrete job scenario showing how knowledge from that course would be directly applied to succeed in the given job.

The scenario must reference specific skills, technologies, or concepts taught in the course.

Vague statements like "this course will help you understand systems" are not acceptable.

Prioritize relevance to the job description provided, not overall academic value.

Be confident. If you cannot confidently justify a course based on its description, point out that you're not sure.

Write clearly and concisely. Do not add disclaimers like "depending on the student's interests."

Example of an acceptable justification:

"Encrypting massive files securely is a real-world challenge for cloud engineers. CSE 452 covers block ciphers, which allow secure, chunked encryption of large datasets under memory constraints — a direct need for securing multi-tenant hosting architectures like Epic's."

Focus entirely on actionable, confident, and course-grounded recommendations.
        """
        )
    
    messages.append({"role": "system", "content": system_role_content})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(model=model,
    messages=messages,
    max_tokens=max_tokens,
    temperature=temperature)

    # Extract and return the content from the API response
    output = response.choices[0].message.content.strip()
    return output

def count_tokens(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# --- Main Execution Block (For Testing) ---
if __name__ == "__main__":
    # Make sure to set your OpenAI API key!

    # Define file paths as needed
    job_description_path = "job_description.json"
    transcript_json_path = "transcript.json"
    course_list_path = "courses.csv"

    # Load data
    job_description = load_job_description(job_description_path)
    student_transcript = load_student_transcript(transcript_json_path)
    # course_descriptions = load_course_descriptions(course_list_path)
    shortlisted_courses = ['CSE 371', 'CSE 481A', 'CSE 451', 'CSE 442', 'CSE 331', 'CSE 474', 'CSE 481C', 'CSE 403', 'CSE 440', 'CSE 478', 'CSE 351', 'CSE 480', 'CSE 481P', 'CSE 122', 'CSE 455', 'CSE 481L', 'CSE 369', 'CSE 391', 'CSE 462']
    # Generate the prompt
    prompt = generate_advisory_prompt(job_description, student_transcript, shortlisted_courses= shortlisted_courses)

    # Optionally, define your system role content
    system_role_content = (
        "You're an AI-powered student advisor for Computer Science Engineering students at the University of Washington.\n"
        "Based on the student's academic history and job aspirations, recommend courses they should take."
    )

    # Send the prompt to the OpenAI API and get the response
    api_output = send_prompt_to_openai(prompt, system_role_content=system_role_content)

    # Now, api_output contains the text generated by the OpenAI API
    print("Output from OpenAI API:")
    print(api_output)

    # Optionally, print token count
    print(f"Token Count: {count_tokens(prompt)} tokens")
