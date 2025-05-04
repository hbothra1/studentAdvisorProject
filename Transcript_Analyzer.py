#Limitations:
#depends on there being columns in the file.  Doesn't throw an error if the columns are not present
#doesn't handle the case where the course code is not present
#doesn't handle the case where the course name is not present
#has not been tested against multiple UW transcripts 

import pdfplumber
import re
import json

def extract_transcript_data(pdf_path):
    data = []
    current_quarter = None
    work_in_progress = False

    # Open and read the PDF
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # Extract left and right columns separately
            left_text, right_text = extract_columns(page)

            # Process lines in the left column first, then the right column
            for column_name, column_lines in [("Left Column", left_text), ("Right Column", right_text)]:
                print(f"\n--- Processing {column_name} on Page {page_num + 1} ---")  # Debugging info
                for line in column_lines:
                    # Debugging: Print each line being processed
                    print(f"Processing line: {line}")

                    # Detect "END OF RECORD" and stop processing
                    if "END OF RECORD" in line:
                        if current_quarter:
                            # Save previous quarter's data
                            data.append(current_quarter)
                            print(f"Saved quarter: {current_quarter['Quarter']}")
                        print("Found 'END OF RECORD', stopping processing.")
                        return data

                    # Detect start of data
                    if line.strip() == "----------------------------------------------------":
                        print("Skipping separator line.")
                        continue

                    # Detect "WORK IN PROGRESS"
                    if "WORK IN PROGRESS" in line:
                        print("Found 'WORK IN PROGRESS'.")
                        work_in_progress = True
                        continue

                    # Handle the "WORK IN PROGRESS" quarter details and courses
                    if work_in_progress:
                        # Detect quarter details
                        quarter_match = re.match(r"(AUTUMN|WINTER|SPRING|SUMMER) \d{4}", line, re.IGNORECASE)
                        if quarter_match:
                            print("'WORK IN PROGRESS' Quarter Found!")
                            if current_quarter:
                                # Save previous quarter's data
                                data.append(current_quarter)
                                print(f"Saved quarter: {current_quarter['Quarter']}")

                            # Start a new quarter for "WORK IN PROGRESS"
                            current_quarter = {
                                "Quarter": line.strip() + " (Work in Progress)",
                                "Courses": [],
                                "Credits Earned": None,
                                "GPA": None
                            }
                            print(f"Started new WIP quarter: {current_quarter['Quarter']}")
                            continue

                        # Detect course data in "WORK IN PROGRESS"
                        if current_quarter and re.match(r"[A-Z]{4}\s+\d{3}", line):
                            print("Processing WIP Course")
                            course_parts = line.split()
                            course_code = course_parts[0] + " " + course_parts[1]
                            course_name = " ".join(course_parts[2:-1])
                            credits = course_parts[-1]
                            grade = "WIP"  # Default grade for "WORK IN PROGRESS"

                            current_quarter["Courses"].append({
                                "Course Code": course_code,
                                "Course Name": course_name,
                                "Credits": credits,
                                "Grade": grade
                            })
                            print(f"Added WIP course: {course_code}, {course_name}, {credits} credits, Grade: {grade}")
                            continue

                        # Skip processing non-WIP logic while inside "WORK IN PROGRESS"
                        continue

                    # Process each quarter
                    quarter_match = re.match(r"(AUTUMN|WINTER|SPRING|SUMMER) \d{4}", line)
                    if quarter_match:
                        if current_quarter:
                            # Save previous quarter's data
                            data.append(current_quarter)
                            print(f"Saved quarter: {current_quarter['Quarter']}")

                        # Start new quarter
                        current_quarter = {
                            "Quarter": line.strip(),
                            "Courses": [],
                        }
                        print(f"Started new quarter: {current_quarter['Quarter']}")
                        continue

                    # Detect course data
                    if current_quarter and re.match(r"[A-Z]{4}\s+\d{3}", line):
                        course_parts = line.split()
                        course_code = course_parts[0] + " " + course_parts[1]
                        course_name = " ".join(course_parts[2:-2])
                        credits = course_parts[-2]
                        grade = course_parts[-1]
                        current_quarter["Courses"].append({
                            "Course Code": course_code,
                            "Course Name": course_name,
                            "Credits": credits,
                            "Grade": grade
                        })
                        print(f"Added course: {course_code}, {course_name}, {credits} credits, Grade: {grade}")
                        continue

                    # Skip rows starting with QTR or CUM that are not needed
                    if line.startswith("QTR") or line.startswith("CUM"):
                        print(f"Skipping unnecessary line: {line}")
                        continue

    # Add the last quarter's data if applicable
    if current_quarter:
        data.append(current_quarter)
        print(f"Saved final quarter: {current_quarter['Quarter']}")

    return data


def extract_columns(page):
    """
    Extracts the text from the left and right columns of the page.
    """
    # Define left and right column boundaries
    left_bbox = (0, 0, page.width / 2, page.height)
    right_bbox = (page.width / 2, 0, page.width, page.height)

    left_text = page.within_bbox(left_bbox).extract_text()
    right_text = page.within_bbox(right_bbox).extract_text()

    # Debugging: Print extracted text
    print("\n--- Extracted Left Column ---")
    print(left_text)
    print("\n--- Extracted Right Column ---")
    print(right_text)

    # Return lines of text for each column
    return left_text.split("\n") if left_text else [], right_text.split("\n") if right_text else []


def save_to_json(data, output_path):
    with open(output_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data saved to {output_path}")


# Main Function
if __name__ == "__main__":
    # Path to the PDF transcript
    pdf_path = "/Users/hemantbothra/Projects/studentAdvisorProject/UW Unofficial Academic Transcript CSE FAKE.pdf"

    # Output JSON file
    output_path = "transcript_json2_CSE.json"

    # Extract and save data
    transcript_data = extract_transcript_data(pdf_path)
    save_to_json(transcript_data, output_path)