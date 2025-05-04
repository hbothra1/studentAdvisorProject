
# import requests
import json
import re

# FIRECRAWL_API_KEY = "your_api_key_here"
# FIRECRAWL_EXTRACT_URL = "https://api.firecrawl.dev/extract"

# Load course embedding data
with open("course_data_forembedding.json", "r") as f:
    course_data = json.load(f)

# Load list of URLs from a text file
with open("allURLs.txt", "r") as f:
    url_list = [line.strip() for line in f.readlines() if line.strip()]

# Pattern for valid syllabus/course URLs
valid_pattern = re.compile(r"http[s]?://courses\.cs\.washington\.edu/courses/[a-z]{3}[a-zA-Z0-9]{3,5}/\d{2}(sp|wi|au|su)(/syllabus(\.html)?)?/?$")
# Secondary valid patterns for fallback matching (no trailing slash)
fallback_pattern = re.compile(r"http[s]?://courses\.cs\.washington\.edu/courses/[a-z]{3}[a-zA-Z0-9]{3,5}(/(\d{2}(sp|wi|au|su))?)?$")

# Initialize abnormal URL dictionary and log output
abnormal_urls = {}
log_messages = []

# Normalize course keys and build a new dictionary
normalized_course_data = {}
for course_code in list(course_data.keys()):
    normalized_code = re.sub(r"(?<=^[a-zA-Z]{3})\s+", "", course_code).upper()
    if normalized_code not in normalized_course_data:
        normalized_course_data[normalized_code] = course_data[course_code]
    if normalized_code != course_code:
        del course_data[course_code]  # Remove old entry

# Merge normalized data back
course_data.update(normalized_course_data)

# Go through each normalized course code
for course_code, content in course_data.items():
    formatted_code = course_code.lower()
    matching_urls = [url for url in url_list if formatted_code in url]

    normal_count = 1
    abnormal_count = 1

    for url in matching_urls:
        if valid_pattern.match(url) or fallback_pattern.match(url):
            key_name = f"url{normal_count}"
            course_data[course_code][key_name] = url
            log_messages.append(f"* normal url found for {course_code}: {url}")
            normal_count += 1
        else:
            if course_code not in abnormal_urls:
                abnormal_urls[course_code] = {}
            key_name = f"url{abnormal_count}"
            abnormal_urls[course_code][key_name] = url
            log_messages.append(f"abnormal url found for {course_code}: {url}")
            abnormal_count += 1

# Save the updated course data back to a new temp file
with open("course_data_forembedding_temp_withfallback_5.json", "w") as f:
    json.dump(course_data, f, indent=2)

# Save abnormal URLs to a separate file
with open("course_embeddings_urls_abnormal_withfallback_5.json", "w") as f:
    json.dump(abnormal_urls, f, indent=2)

# Print the log messages
print("\n".join(log_messages))
print("\nURL processing complete. Valid URLs added to course data. Abnormal URLs stored separately.")
