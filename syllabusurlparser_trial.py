#import openai
import json
import requests
from bs4 import BeautifulSoup

# openai.api_key = "your_openai_api_key"

# URL of the course page
url = "https://courses.cs.washington.edu/courses/cse123/25wi/syllabus/"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract the main content inside <div id="content">
content_div = soup.find("div", id="content")

if content_div:
    elements = content_div.find_all(["h1", "h2", "h3", "p", "li"])
else:
    elements = soup.find_all(["h1", "h2", "h3", "p", "li"])

# Join all selected elements' text
course_text = "\n\n".join([el.get_text(strip=True) for el in elements])

print(course_text)
# Fallback if nothing meaningful is extracted
# if not course_text.strip():
#     course_text = soup.get_text()

# # Create embedding
# embedding_response = openai.Embedding.create(
#     input=course_text,
#     model="text-embedding-ada-002"
# )
# embedding = embedding_response["data"][0]["embedding"]

# # Save embedding to a text file as JSON
# with open("course_embedding.json", "w") as f:
#     json.dump(embedding, f)

# print("✅ Embedding saved to course_embedding.json")
