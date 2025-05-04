from flask import Flask, request, jsonify, session
from studentAdvisorProject.jobDescriptionAnalyser import parse_job_description, save_to_json
from studentAdvisorProject.Transcript_Analyzer import extract_transcript_data
from studentAdvisorProject.model_Interactor import generate_advisory_prompt, send_prompt_to_openai
from studentAdvisorProject.prereq_checker import check_prerequisites

app = Flask(__name__)
app.secret_key = 'your_secret_key'
db_path = 'path_to_your_database.db'  # Define the path to your database

@app.route("/upload_transcript", methods=["POST"])
def upload_transcript():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        filepath = f"/tmp/{file.filename}"
        file.save(filepath)
        transcript_json = extract_transcript_data(filepath)
        save_to_json(transcript_json, "transcript.json")
        session["transcript_json"] = transcript_json
        return jsonify({"message": "Transcript uploaded and processed", "transcript_json": transcript_json})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/upload_job_description", methods=["POST"])
def upload_job_description():
    try:
        data = request.get_json()
        job_description = data.get("job_description")
        job_description_json = parse_job_description(job_description)
        save_to_json(job_description_json, "job_description.json")
        session["job_description_json"] = job_description_json
        return jsonify({"message": "Job description uploaded and processed", "job_description_json": job_description_json})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate_AIresponse", methods=["POST"])
def generate_prompt():
    try:
        job_description_json = session.get("job_description_json")
        student_transcript = session.get("transcript_json")
        if not job_description_json or not student_transcript:
            return jsonify({"error": "Missing job description or transcript data"}), 400
        prompt = generate_advisory_prompt(job_description_json, student_transcript)
        recommendations = send_prompt_to_openai(prompt)
        prerequisites = check_prerequisites(recommendations, student_transcript, db_path)
        return jsonify({"recommended_courses": prerequisites})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)