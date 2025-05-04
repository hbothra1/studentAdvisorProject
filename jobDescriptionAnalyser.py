import pdfplumber
import re
import json
import logging

logging.basicConfig(filename='job_description_parser.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define headers and their associated keywords
HEADERS = {
    "About the Company": {
        "keywords": ["About Us", "Who We Are", "Company Overview", "Our Mission", "Mission Statement"],
        "regex": r"^about (?!the job).*"  # Dynamic regex for matching "About xyz" (excluding "About the job")
    },
    "About the Role": {
        "keywords": ["About the Job", "Job Overview", "Role Summary", "Position Overview", "Overview", "About The Role"],
        "regex": None  # No dynamic regex needed here
    },
    "Responsibilities": {
        "keywords": ["Job Responsibilities", "Key Responsibilities", "Your Responsibilities", "Duties and Responsibilities", "Responsibilities"],
        "regex": None
    },
    "Cultural Fit": {
        "keywords": ["Our Culture", "You'll love this role if", "You Are", "You Love"],
        "regex": r"(?i)\w+\s+might\s+be\s+a\s+good\s+fit\s+for\s+you" 
    },
    "Skills & Requirements": {
        "keywords": ["Skills and Qualifications", "Requirements", "What You’ll Need", "What We’re Looking For", "Your Qualifications", "You Might Be a Good Fit If You"],
        "regex": None
    },
    "Nice-to-Haves": {
        "keywords": ["Preferred Qualifications", "Bonus Points", "Good to Have", "Preferred Experience","Nice to Have","Nice-to-Have", "Strong Candidates May Also", "Strong Candidates May Also Have"],
        "regex": None
    },
    "Technology Stack": {
        "keywords": [ "Tech stack", "Technologies you'll work on", "Our Stack", "Our tech stack includes"],
        "regex": None
    }
}

def parse_job_description_pdf(pdf_path, termination_line="Set alert for similar jobs"):
    active_headers = set(HEADERS.keys())  # All headers are active initially
    parsed_sections = {}  # Store extracted content here
    current_header = None  # Currently active header

    # Open and read the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            print(f"Processing page {page_num + 1}")  # Debug: Track page number

            # Extract text line by line
            lines = page.extract_text().splitlines()
            print(f"Extracted {len(lines)} lines from page {page_num + 1}")  # Debug: Number of lines

            # Process each line
            for line in lines:
                line = line.strip()  # Clean up whitespace
                print(f"Processing line: '{line}'")  # Debug: Log current line

                # Terminate processing if termination_line is reached
                if line == termination_line:
                    print("Termination line reached. Stopping processing.")
                    return parsed_sections

                # Check if the line matches any active header
                for header, rules in HEADERS.items():
                    if header in active_headers:
                        # Check for a match in static keywords
                        if isinstance(rules, dict) and "keywords" in rules and any(keyword in line for keyword in rules["keywords"]):
                            current_header = header
                            active_headers.remove(header)  # Deactivate this header
                            parsed_sections[current_header] = []  # Initialize section
                            print(f"Matched static header: {header}")  # Debug: Header matched
                            break

                        # Check for a match in dynamic regex (if defined)
                        if isinstance(rules, dict) and rules.get("regex") and re.match(rules["regex"], line, re.IGNORECASE):
                            current_header = header
                            active_headers.remove(header)  # Deactivate this header
                            parsed_sections[current_header] = []  # Initialize section
                            print(f"Matched dynamic header (regex): {header}")  # Debug: Regex header matched
                            break

                # Add content to the current section
                if current_header:
                    # Check if the line matches another header to skip adding it to the current section
                    if any(keyword in line for keywords in HEADERS.values() for keyword in keywords["keywords"]):
                        print(f"Skipping line as it matches another header: '{line}'")  # Debug: Skipping line
                        continue

                    # Append line to the current header section
                    print(f"Adding content to '{current_header}': '{line}'")  # Debug: Content being added
                    parsed_sections[current_header].append(line)

    print("Finished processing all pages.")  # Debug: All pages processed
    return parsed_sections
def parse_job_description_text(job_text):
    """
    Parse job description from text input using the same logic as PDF parser.
    
    Args:
        job_text (str): The job description text to parse
    
    Returns:
        dict: Parsed sections of the job description
    """
    active_headers = set(HEADERS.keys())  # All headers are active initially
    parsed_sections = {}  # Store extracted content here
    current_header = None  # Currently active header

    # Split the text into lines
    lines = job_text.splitlines()
    print(f"Processing {len(lines)} lines of text")  # Debug: Number of lines

    # Process each line
    for line in lines:
        line = line.strip()  # Clean up whitespace
        print(f"Processing line: '{line}'")  # Debug: Log current line
        matched_header = None
        # Check if the line matches any active header
        for header, rules in HEADERS.items():
            if header in active_headers:
                # Check for a match in static keywords
                if isinstance(rules, dict) and "keywords" in rules and any(keyword in line for keyword in rules["keywords"]):
                    matched_header = header
                    print(f"Matched static header: {header}")  # Debug: Header matched
                    break

                # Check for a match in dynamic regex (if defined)
                if isinstance(rules, dict) and rules.get("regex") and re.match(rules["regex"], line, re.IGNORECASE):
                    matched_header = header
                    print(f"Matched dynamic header (regex): {header}")  # Debug: Regex header matched
                    break

        # Add content to the current section
        if matched_header:
            current_header = matched_header
            active_headers.remove(current_header)
            parsed_sections[current_header] = []
            logging.debug(f"Matched header: {current_header}")
            continue  # Skip adding the header line as content

        # Add content to the current section
        if current_header:
            parsed_sections[current_header].append(line)
            logging.debug(f"Adding content to '{current_header}': '{line}'")

    print("Finished processing all lines.")  # Debug: All lines processed
    return parsed_sections

def save_to_json(data, output_path):
    """Save parsed data to a JSON file."""
    with open(output_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data saved to {output_path}")

# Main function
if __name__ == "__main__":
    # Path to the PDF file
    pdf_path = "/Users/hemantbothra/Projects/studentAdvisorProject/SoftwareEngineering_job description1.pdf"
    
    # Output JSON file
    output_path = "job_description_softwareengineering.json"

    # Parse the job description
    parsed_data = parse_job_description(pdf_path) # type: ignore

    # Save the output to JSON
    save_to_json(parsed_data, output_path)