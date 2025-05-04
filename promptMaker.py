import json
import pandas as pd

# Load the job description JSON
with open('/Users/hemantbothra/Projects/studentAdvisorProject/job_description_softwareengineering.json') as f:
    job_description = json.load(f)

# Load the student transcript JSON
with open('/Users/hemantbothra/Projects/studentAdvisorProject/transcript_json2_CSE.json') as f:
    student_transcript = json.load(f)

# Load the course descriptions CSV
course_descriptions = pd.read_csv('Updated_Courses_With_Descriptions_Final_OnlyUndergrad.csv', encoding='ISO-8859-1')

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
    
    if 'Technology Stack' in job_description:
        formatted_text += "Technology Stack:\n" + "\n".join(job_description['Technology Stack']) + "\n\n"
    else:
        formatted_text += "Technology Stack: Information not available.\n\n"
     # Check if 'Cultural Fit exists' exists in the job description        
    if 'Cultural Fit' in job_description:
        formatted_text += "Cultural Fit:\n" + "\n".join(job_description['Cultural Fit']) + "\n\n"
    else:
        formatted_text += "Cultural Fit: Information not available.\n\n"
    
    
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

# Function to add course descriptions to the courses taken by the student. It adds descriptions to the courses taken by the student. This is wrong
# def add_course_descriptions(courses, course_descriptions):
#     course_info = []
#     for course in courses:
#         # Find the description of the course
#         course_code = course['Course Code']
#         description = course_descriptions[course_descriptions['Course Code'] == course_code]['Course Descriptions'].values
#         if description:
#             course_info.append(f"{course_name} - {description[0]}")
#         else:
#             course_info.append(course_name)
#     return course_info
def add_course_descriptions(course_descriptions):
    course_info = []
    for _, row in course_descriptions.iterrows():
        course_code = row['Course Code']
        
        # Check if the 'Course Code' is empty or NaN
        if pd.isna(course_code) or course_code == "":
            continue  # Skip this row if the course code is empty or missing
        
        course_title = row['Course Title']  # Assuming there is a column for course titles
        credits = row['Credits']  # Assuming this column exists
        description = row['Course Descriptions']  # Course description from the CSV

        # Format each course's information
        course_info.append(f"{course_code} - {course_title}: {credits} credits. {description}")
    
    return course_info


# Generate the final prompt
def generate_advisory_prompt(job_description, student_transcript, course_descriptions):
    # Format the job description and student courses
    job_desc_text = format_job_description(job_description)
    student_courses_text = format_student_courses(student_transcript)
    course_info = add_course_descriptions(course_descriptions)
    # Flatten the student's courses into a list and add descriptions
#     all_courses = []
#     for entry in student_transcript:
#         all_courses.extend(entry['Courses'])
#     
#     course_info = add_course_descriptions(all_courses, course_descriptions)
    
    # Append the advisory text
    advisory_text = ("You're a student advisor in the computer science engineering department at the university of washington. "
                     "You're here to advise current UW students based on the kinds of jobs they want, the skills those jobs will need, "
                     "and how those skills can be acquired by the classes available in the computer science department. Additionally, "
                     "consider all the previous classes taken by the students and the classes currently being taken if any while making "
                     "these recommendations. If those skills can't simply be acquired by taking a class, the recommendation of classes "
                     "should be made in such a way that the student is well positioned to learn those skills in the future. Point this out "
                     "clearly when making the recommendations. When making recommendations clearly outline the skill that a job may require "
                     "and the class that will most likely help in acquiring that skill. Assume an upper credit bound of about 18 credits. "
                     "A minimum of 8 credits.\n\n")
    
    # Combine all pieces into the final prompt
    final_prompt = advisory_text + job_desc_text + "Student's Current and Completed Courses:\n" + student_courses_text + "All Available Courses:\n" + "\n".join(course_info)
    
    return final_prompt

# Generate the advisory prompt
final_prompt = generate_advisory_prompt(job_description, student_transcript, course_descriptions)

# Print or return the final prompt
print(final_prompt)
