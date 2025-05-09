from config import DB_PATH
from flask import Flask, request, jsonify, session
from flask_cors import CORS, cross_origin
from jobDescriptionAnalyser import parse_job_description_pdf, save_to_json as save_job_description_to_json
from Transcript_Analyzer import extract_transcript_data, save_to_json as save_transcript_to_json
from model_Interactor import generate_advisory_prompt, send_prompt_to_openai, get_shortlisted_course_details
from prereq_checker import check_prerequisites
from scripts.jd_processor import embed_reorganized_jd, rearrange_jd_with_gpt, match_jd_to_courses_combinedembedding
from utils.analysis_utils import get_unique_courses_in_top_rankings
from utils.embedding_utils import load_course_embeddings
import sqlite3
import json

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session storage

db_path = DB_PATH
CORS(app, resources={r"/*": {"origins": ["studentadvisor.hemantbothra.com","https://studentadvisorproject.onrender.com", "http://localhost:5173"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type"]}})

def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enables dict-like row access
    return conn

@app.route("/api/courses", methods=["GET"])
@cross_origin()
def get_courses():
    """
    Fetch all courses or filter by search term (if provided).
    Example:
      - `/api/courses` → returns all courses
      - `/api/courses?search=math` → returns courses matching 'math'
    """
    search_term = request.args.get("search", "").strip().lower()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if search_term:
            cursor.execute("SELECT course_code, course_title cfr courses WHERE course_code LIKE ? OR course_title LIKE ?", 
                           (f"%{search_term}%", f"%{search_term}%"))
        else:
            cursor.execute("SELECT course_code, course_title FROM courses")

        courses = cursor.fetchall()
        conn.close()

        return jsonify([{"course_code": row["course_code"], "course_name": row["course_title"]} for row in courses])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
@cross_origin()
def home():
    return jsonify({"message": "Flask API is running!"})

@app.route("/process_transcript", methods=["POST"])
@cross_origin()
def process_transcript():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        filepath = f"/tmp/{file.filename}"
        file.save(filepath)
        transcript_json = extract_transcript_data(filepath)
        save_transcript_to_json(transcript_json, "transcript.json")
        session["transcript_json"] = transcript_json
        return jsonify({"message": "Transcript uploaded and processed", "transcript_json": transcript_json})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/process_transcript_json", methods=["POST"])
@cross_origin()
def process_transcript_json():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        transcript_json = data
        session["transcript_json"] = transcript_json
        
        return jsonify({
            "message": "Transcript JSON processed successfully",
            "transcript_json": transcript_json
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/process_job_description", methods=["POST"])
@cross_origin()
def process_job_description():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        filepath = f"/tmp/{file.filename}"
        file.save(filepath)
        job_description_json = parse_job_description_pdf(filepath)
        save_job_description_to_json(job_description_json, "job_description.json")
        session["job_description_json"] = job_description_json
        return jsonify({"message": "Job description uploaded and processed", "job_description_json": job_description_json})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/process_job_description_text", methods=["POST", "OPTIONS"])
@cross_origin()
def process_job_description_text():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight request successful"}), 200

    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "No text data provided"}), 400

        #code in case we use determinisitic parsing of job description 
        # job_text = data["text"]
        # job_description_json = parse_job_description_text(job_text)
        # save_job_description_to_json(job_description_json, "job_description.json")
        #session["job_description_json"] = job_description_json
        # code in case we use gpt to parse job description
        # job_text = data["text"]
        
        session["job_description_string"] = data["text"]
        
        return jsonify({
            "message": "Job description text processed successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_job_description_json", methods=["GET"])
@cross_origin()
def get_job_description_json():
    job_description_json = session.get("job_description_json")
    if not job_description_json:
        return jsonify({"error": "No job description data found in session."}), 400
    return jsonify({"job_description_json": job_description_json})

@app.route("/get_transcript_json", methods=["GET"])
@cross_origin()
def get_transcript_json():
    transcript_json = session.get("transcript_json")
    if not transcript_json:
        return jsonify({"error": "No transcript data found in session."}), 400
    return jsonify({"transcript_json": transcript_json})

@app.route('/generate_recommendation', methods=['POST'])
@cross_origin()
def generate_recommendation():
    """
    Endpoint to generate a prompt for course recommendations.
    Expects job description and student transcript as input.
    """
    try:
        #cheap option: use job_description_json if using deterministic parsing, which is weaker since it can omit sections and constantly needs to be updated. 
        #job_description_json = session.get("job_description_json")
        # expensive option: use job_description_string if using gpt to parse job description, which is stronger since it can parse any job description, with ideally minimal loss. 
        job_description_string = rearrange_jd_with_gpt(session.get("job_description_string"))
        student_transcript = session.get("transcript_json")
        
        if not job_description_string or not student_transcript:
            return jsonify({"error": "Missing job description or transcript data"}), 400
        
        
        # 1. Create JD embedding
        #cheap option
        #jd_embedding = embed_reorganized_jd(job_description_json["text"])  # or however it's stored
        # expensive option
        jd_embedding = embed_reorganized_jd(job_description_string)  # or however it's stored
        # 2. Load course embeddings from DB
        course_embeddings_dict = load_course_embeddings(db_path)

        # 3. Get top ranked courses
        # rankings = match_jd_to_courses(jd_embedding, course_embeddings_dict)
        #shortlisted_courses = get_unique_courses_in_top_rankings(rankings, top_k=10)
        rankings_combined = match_jd_to_courses_combinedembedding(jd_embedding, course_embeddings_dict)  # Added back the combined embedding call
        # 4. Store course codes
        shortlisted_courses_combined = get_unique_courses_in_top_rankings(rankings_combined)
        # session["shortlisted_courses"] = shortlisted_courses_combined
        # Generate the prompt
        
        shortlisted_course_details = get_shortlisted_course_details(
            shortlisted_courses_combined, 
            db_path=db_path
        )
        prompt = generate_advisory_prompt(job_description_string, student_transcript, shortlisted_course_details = shortlisted_course_details)
        
        # Send prompt to OpenAI API
        recommendations = send_prompt_to_openai(prompt)
        
        # Check prerequisites
        # prerequisites = check_prerequisites(recommendations, student_transcript, db_path)
        
        # Combine recommendations and prerequisites into one text
        # combined_text = f"{prerequisites}"
        
        return jsonify({"recommendation_text": recommendations})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# def recommend_courses_raw():
#     """
#     Endpoint to generate course recommendations using OpenAI.
#     Expects job description and uses transcript stored in session.
#     """
#     try:
#         data = request.get_json()
#         job_description = data.get("job_description")
#         student_transcript = session.get("transcript_json")  # Use session value

#         if not student_transcript:
#             return jsonify({"error": "No transcript data found in session. Please upload a transcript first."}), 400

#         # Generate the prompt
#         prompt = generate_advisory_prompt(job_description, student_transcript)

#         # Send prompt to OpenAI API
#         recommendations = send_prompt_to_openai(prompt)
#         prerequisite_recommendations = check_prerequisites(recommendations, student_transcript, db_path)
#         return jsonify({"recommended_courses": recommendations, "prerequisites": prerequisite_recommendations})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route("/check_prerequisites", methods=["POST"])
@cross_origin()
def check_prerequisites_api():
    """
    Endpoint to check prerequisites for recommended courses.
    Expects the OpenAI response and uses transcript stored in session.
    """
    try:
        data = request.get_json()
        response_text = data.get("response_text")
        db_path = "course_database.db"  # Update with actual path
        
        student_transcript = session.get("transcript_json")  # Use session value
        
        if not student_transcript:
            return jsonify({"error": "No transcript data found in session. Please upload a transcript first."}), 400

        prerequisites = check_prerequisites(response_text, student_transcript, db_path)
        return jsonify({"prerequisites": prerequisites})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route("/transcript_analyzer", methods=["POST"])
# @cross_origin()
# def transcript_analyzer():
#     """
#     Endpoint to upload a PDF transcript, extract text, and convert it into structured JSON.
#     """
#     if "file" not in request.files:
#         return jsonify({"error": "No file part"}), 400
    
#     file = request.files["file"]
#     if file.filename == "":
#         return jsonify({"error": "No selected file"}), 400
    
#     filepath = f"/tmp/{file.filename}"
#     file.save(filepath)
    
#     # Extract transcript data
#     transcript_json = extract_transcript_data(filepath)
#     session["transcript_json"] = transcript_json  # Store JSON in session
    
#     return jsonify({"message": "Transcript uploaded and processed", "transcript_json": transcript_json})

if __name__ == "__main__":
    app.run(port=5000)  # Runs locally on http://127.0.0.1:5000
