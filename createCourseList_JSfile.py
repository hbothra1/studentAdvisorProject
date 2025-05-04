import json

# Load the JSON data
json_file_path = "/Users/hemantbothra/Library/CloudStorage/GoogleDrive-hbothra1@gmail.com/My Drive/Projects/studentAdvisorProject/courses.json"
with open(json_file_path, "r") as file:
    courses_data = json.load(file)

# Convert the JSON data into a JavaScript file
js_content = "const courses = " + json.dumps(courses_data, indent=2) + ";\n\nexport default courses;"

# Save the JavaScript file
js_file_path = "courses.js"
with open(js_file_path, "w") as js_file:
    js_file.write(js_content)

# Provide the download link
js_file_path
