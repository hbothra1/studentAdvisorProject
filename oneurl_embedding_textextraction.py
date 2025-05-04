# Test one URL for course text extraction
import requests
from bs4 import BeautifulSoup

# Define the URL to test (you can change this)
url = "https://courses.cs.washington.edu/courses/cse426/25wi/"

# Keywords for filtering
include_keywords = [
    "course goals", "objectives", "learning", "topics", "outcomes",
    "overview", "description", "introduction", "expectations",
    "about the course", "skills", "concepts", "themes"
]

exclude_keywords = [
    "academic honesty", "schedule", "late work", "grading", "accommodations",
    "instructor", "contact", "office hours", "ta", "disability", "textbook",
    "calendar", "exam", "homework", "policy", "plagiarism"
]

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    content_div = soup.find("div", id="content")
    if content_div:
        elements = content_div.find_all(["h1", "h2", "h3", "p", "li"])
    else:
        elements = soup.find_all(["h1", "h2", "h3", "p", "li"])

    sections = []
    include_section = False
    current_block = ""

    for el in elements:
        tag_text = el.get_text(strip=True)
        tag_text_lower = tag_text.lower()

        if el.name in ["h1", "h2", "h3"]:
            if current_block:
                sections.append(current_block.strip())
                current_block = ""
            include_section = any(k in tag_text_lower for k in include_keywords)
            if any(k in tag_text_lower for k in exclude_keywords):
                include_section = False
            if include_section:
                current_block += tag_text + "\n"

        elif include_section and el.name in ["p", "li"]:
            current_block += tag_text + "\n"

    if current_block:
        sections.append(current_block.strip())

    if not sections:
        raise Exception("No relevant headings matched for extraction.")

    course_text = "\n\n".join(sections)
    print("\n✅ Extracted Content:\n")
    print(course_text)

except Exception as e:
    print(f"❌ Extraction failed: {e}")
