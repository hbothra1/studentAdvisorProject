import re
import sqlite3
import pdfplumber
import logging
from CoursesDatabase import normalize_course_code
from CoursesDatabase import COURSE_PATTERN

logging.basicConfig(filename='my_log.log', level=logging.INFO)

class CourseDatabase:
    min_grade_pattern = re.compile(r'minimum grade of ([0-9\.]+) in (.+)', re.IGNORECASE)
    quarter_pattern = re.compile(r'\bOffered:(A|W|Sp|S|AWSpS)\b', re.IGNORECASE)

    # def normalize_course_code(self, course_code):
    #     if isinstance(course_code, str):
    #         normalized_code_temp = re.sub(r'(?i)\b(CSE)(\d{3})\b', r'\1 \2', course_code.strip().upper ()) #Debugging Line
    #         return re.sub(r'(?i)\b(CSE)(\d{3}[A-Za-z]?)\b', r'\1 \2', course_code.strip().upper())
    #     return course_code  # Return as is if not a string

    def __init__(self, db_path='course_database.db'):
        self.db_path = db_path


    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.setup_database()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def setup_database(self):
        # Create courses table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                course_code TEXT PRIMARY KEY,
                course_title TEXT,
                course_description TEXT,
                credits TEXT
            )
        ''')

        # Create prerequisites table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS prerequisite_mappings (
                course_code TEXT,
                prerequisite_code TEXT,
                group_id INTEGER,
                is_optional INTEGER,
                minimum_grade REAL,
                FOREIGN KEY (course_code) REFERENCES courses (course_code),
                FOREIGN KEY (prerequisite_code) REFERENCES courses (course_code),
                PRIMARY KEY (course_code, prerequisite_code)
            )
        ''')
        self.conn.commit()

    def extract_course_info_from_pdf(self, pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            all_text = ""
            for page in pdf.pages:
                all_text += page.extract_text() + "\n"
            cnc = ''
            lines = all_text.split('\n')
            course_found = False
            course_description = ""
            course_code = ""
            course_title = ""
            credits = ""
            group_counter = 0
            for line in lines:
                url_pattern = re.compile(r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})')
                if url_pattern.search(line):
                    continue
                if course_found == False: #assumes that the very first course found isn't a prerequisite listing but the actual course
                    course_match = COURSE_PATTERN.search(line)                    
                    logging.info(f"Course code found: {course_code}")
                    course_found = True
                    if course_match:
                        course_code = f"{course_match.group(1)}"
                        logging.info(f"Course code found: {course_code}")
                        # Extract course name
                        course_title_start = course_match.end()
                        if '(' in line:
                            course_title_end = line.index('(')
                            course_title = line[course_title_start:course_title_end].strip()
                        #print(course_name)
                        # Extract credits
                            credits_pattern = re.compile(r'\((.*?)\)')
                            credits_match = credits_pattern.search(line)
                            if credits_match:
                                credits = credits_match.group(1)
                            #print(credits)
                elif line.startswith("View course details in MyPlan"):
                    logging.info(f"End of {course_code}'s course description found")
                    if course_code and course_title:
                        cnc = 1 if 'credit/no-credit only' in course_description.lower() else 0
                        
                        # Add quarter_offered column if it doesn't exist
                        # Extract quarter offered
                        quarter_match = self.quarter_pattern.search(course_description)
                        quarter_offered = quarter_match.group(0) if quarter_match else None 

                        print(f"Adding course {course_code} to database")
                        
                        try:
                            #print(f"Adding course {course_code} to database")
                            self.cursor.execute("""
                                INSERT OR REPLACE INTO courses (course_code, course_title, course_description, credits, cnc, quarter_offered)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (normalize_course_code(course_code), course_title, course_description.strip(), credits, cnc, quarter_offered))
                            self.conn.commit()
                        except sqlite3.Error as e:
                            print(f"Error adding course {course_code}: {e}")
                    course_found = False
                else:
                        logging.info(f"line of {course_code}'s course description found")
                        #print(f"adding line to course_description:.q {line}")
                        course_description += " " + line.strip()
                        #print(course_description)
                
                    #begins to enter prerequisites once course_description is fully populated  
                
                self.conn.commit()
                if(course_found == False):
                    if re.search(r'prerequisite', course_description, re.IGNORECASE):
                        
                        prerequisite_index = course_description.index('Prerequisite')
                        prerequisite_text = course_description[prerequisite_index + len('Prerequisite:'):].strip()
                        logging.info(f"Prerequisite(s) found: {prerequisite_text}")
                        requirements = re.split(r'\s*(?:;| and )\s*', prerequisite_text)
                        for requirement in requirements:
                                # Check if "recommended" is present (mark as optional)
                            is_optional = 1 if "recommended" in requirement else 0
                            if ' or ' in requirement.lower():
                                group_id = group_counter  # Assign a unique group ID
                                min_grade_match = re.search(r'minimum grade of ([0-9\.]+) in (.+)', requirement)
                                if min_grade_match:
                                    min_grade = min_grade_match.group(1)
                                else:
                                    min_grade = None
                                options = requirement
                                normalized_options = []
                                matches = COURSE_PATTERN.findall(options) 
                                if matches:
                                    for match in matches:
                                        normalized_prereq_code = normalize_course_code(match)
                                        normalized_options.append(normalized_prereq_code)
                                        #print(f"Matched course code: {course_code}")
                                        #print(f"Normalized course code: {normalized_course_code}")
                                else:
                                    print(f"No-course course prerequisites found: {options}")
                                    options = [option.strip() for option in re.split(r'\s*\bor\b\s*', options) if option and ('.' not in option or option.index('.') > 0)]
                                    if '.' in options[-1]:
                                        options[-1] = options[-1].split('.')[0].strip()
                                    for option in options:
                                        normalized_options.append(normalize_course_code(option))
                                        
                                
                                    

                                options = normalized_options

                                for prereq in options:
                                    
                                    print(f"Inserting either/or prerequisite mapping {prereq} for course: {course_code}")  # Debugging line
                                    try:
                                        self.cursor.execute("""
                                        INSERT INTO prerequisite_mappings (course_code, prerequisite_code, group_id, is_optional, minimum_grade)
                                        VALUES (?, ?, ?, ?, ?)
                                        ON CONFLICT(course_code, prerequisite_code) DO NOTHING;
                                        """, (normalize_course_code(course_code), prereq, group_id, is_optional, min_grade if min_grade else None))
                                    except Exception as e:
                                        print(f"Error inserting either/or prerequisite for {normalize_course_code(course_code)} -> {prereq}: {e}")
                                group_counter += 1  # Increment for next "either/or" case
                            else:
                            # Handle prerequisites with a minimum grade
                                min_grade_match = re.search(r'minimum grade of ([0-9\.]+) in (.+)', requirement)
                                if min_grade_match:
                                    min_grade = float(min_grade_match.group(1))
                                    match = COURSE_PATTERN.search(requirement) 
                                    if match:
                                        prereq_code = normalize_course_code(match.group(0)) 

                                else:
                                    min_grade = None
                                    match = COURSE_PATTERN.search(requirement)
                                    if match:
                                        prereq_code = normalize_course_code(match.group(0))
                                    else:
                                        requirement = requirement.split('.', 1)[0].strip()
                                        prereq_code = requirement
                                print(f"Prerequisite mapping for {course_code} -> {prereq_code}")    
                                
                                try:
                                    self.cursor.execute("""
                                    INSERT INTO prerequisite_mappings (course_code, prerequisite_code, minimum_grade, is_optional)
                                    VALUES (?, ?, ?, ?)
                                    ON CONFLICT(course_code, prerequisite_code) DO NOTHING;
                                    """, (normalize_course_code(course_code), prereq_code, min_grade, is_optional))
                                    prereq_code = None
                                except Exception as e:
                                    print(f"Error inserting prerequisite mapping for {course_code} -> {prereq_code}: {e}")
                        course_description = ""
                        

    def add_course(self, course_code, course_title):
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO courses (course_code, course_title)
                VALUES (?, ?)
            ''', (course_code, course_title))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding course {course_code}: {e}")

    def identify_and_add_prerequisites(self, course_code, description):
        # Look for prerequisites in the format HCDE XXX
        
        prerequisites = re.findall(COURSE_PATTERN, description)
        
        for prereq in prerequisites:
            prereq_code = f"{prereq}"
            if prereq_code != course_code:  # Don't add the course as its own prerequisite
                try:
                    self.cursor.execute('''
                        INSERT OR IGNORE INTO prerequisites (course_code, prerequisite_code)
                        VALUES (?, ?)
                    ''', (course_code, prereq_code))
                    self.conn.commit()
                except sqlite3.Error as e:
                    print(f"Error adding prerequisite {prereq_code} for {course_code}: {e}")

    def close(self):
        self.conn.close()

def main():
    with CourseDatabase() as db:
        # Replace 'path_to_your_pdf.pdf' with the actual path to your PDF file
        pdf_path = '/Users/hemantbothra/Library/CloudStorage/GoogleDrive-hbothra1@gmail.com/My Drive/Projects/studentAdvisorProject/HCDE_Course_Descriptions.pdf'
        db.extract_course_info_from_pdf(pdf_path)

if __name__ == "__main__":
    main()