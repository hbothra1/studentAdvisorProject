from openai import OpenAI
import numpy as np
client = OpenAI()
from utils.embedding_utils import get_embedding, compute_similarity_scores, compare_embeddings

import logging
from openai import OpenAIError  
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - jd_processor.py: %(message)s",
    handlers=[
        logging.FileHandler("jd_processor_log.log"),
        logging.StreamHandler()  # Add this to print logs to the terminal
    ]
)

def rearrange_jd_with_gpt(jd_text):
    prompt = f"""
    Given the following job description, organize it into the following logical sections. Keep the content as verbatim as possible, only reordering and grouping similar lines under these headers:

    - About The Role
    - Responsibilities
    - Required Qualifications
    - Preferred Qualifications

    Return only the reordered text with these headers. If some of the text does not fit into any of these categories, but is an important part of the job description,include it under "Other". Do not add any additional text or explanations. Remove parts that are not relevant to the embedding of the job description, such as whether the company is an equal opportunity employer, or things like benefits or number of holidays offered, Accommodations, or remote working policy.

    ---
    {jd_text}
    ---
    """
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo-0125",  # more cost-effective than gpt-4 or earlier 3.5s
        messages=[
            {"role": "system", "content": "You are a helpful assistant that restructures job descriptions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=1500)
        logging.info(f"jd_processor.py: Job Description reorganized successfully.")
        with open("reorganized_jd_output.txt", "w") as file:
            file.write(response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        error_message = f"jd_processor.py: Error while calling OpenAI API: {e}"
        logging.error(error_message)
        return None

def embed_reorganized_jd(reorganized_jd_text):
    jd_embedding = get_embedding(reorganized_jd_text)
    with open("jd_embedding.json", "w") as json_file:
        json.dump({"jd_embedding": jd_embedding, "jd_text": reorganized_jd_text}, json_file)
    return get_embedding(reorganized_jd_text)

def match_jd_to_courses(jd_embedding, course_embeddings_dict, top_n=3):
    course_description_scores = []
    learning_goals_scores = []
    topics_covered_scores = []
    tools_scores = []

    for course_code, course_embedding_record in course_embeddings_dict.items():
        try:
            logging.info(f"jd_processor.py: Calculating similarity for course: {course_code}")
            scores = compute_similarity_scores(jd_embedding, course_embedding_record,course_code)
        except Exception as e:
            logging.error(f"jd_processor.py: Error calculating cosine similarity for course {course_code}: {e}")
            scores = {
                "course_description_similarity": float('-inf'),
                "learning_goals_similarity": float('-inf'),
                "topics_covered_similarity": float('-inf'),
                "tools_similarity": float('-inf')
            }
        course_description_scores.append((course_code, scores["course_description_similarity"]))
        learning_goals_scores.append((course_code, scores["learning_goals_similarity"]))
        topics_covered_scores.append((course_code, scores["topics_covered_similarity"]))
        tools_scores.append((course_code, scores["tools_similarity"]))

    course_description_ranking = sorted(course_description_scores, key=lambda x: x[1], reverse=True)[:top_n]
    learning_goals_ranking = sorted(learning_goals_scores, key=lambda x: x[1], reverse=True)[:top_n]
    topics_covered_ranking = sorted(topics_covered_scores, key=lambda x: x[1], reverse=True)[:top_n]
    tools_ranking = sorted(tools_scores, key=lambda x: x[1], reverse=True)[:top_n]

    return {
        "course_description_ranking": course_description_ranking,
        "learning_goals_ranking": learning_goals_ranking,
        "topics_covered_ranking": topics_covered_ranking,
        "tools_ranking": tools_ranking
    }

def match_jd_to_courses_combinedembedding(jd_embedding, combined_text_embedding_dict, top_n=100):
    combined_text_scores = []
    
    logging.info("\n\n *** Initiating combined embedding scoring.*** \n\n")
    print(f"**\n\n Type of jd_embedding: {type(jd_embedding)}\n\n**")
    print(f"**\n\n Type of combined_text_embedding_dict: {type(combined_text_embedding_dict)}\n\n**")
    
    if np.isnan(jd_embedding).any():
        logging.error("\\n ❌ JD embedding contains NaN values before comparison even starts! \n\n")
    else:
        logging.info("\n\n ✅ JD embedding is clean before starting comparisons. \n\n")

    for course_code, course_embedding_record in combined_text_embedding_dict.items():
        try:
            print(f"jd_processor.py: Calculating combined similarity for course: {course_code}")
            score = compare_embeddings(jd_embedding, course_embedding_record.get("combined_text_embedding"))
            if score is None:
                score = float('-inf')
                print(f"jd_processor.py: No combined text embedding found for course {course_code}. Score set to -inf.")
            else:
                logging.info(f"jd_processor.py: Successfully Calculated combined similarity for course: {course_code}. Score: {score}, Type: {type(score)}")

        except Exception as e:
            logging.error(f"Error comparing embeddings for course {course_code}: {e}")
            score = float('-inf')
        combined_text_scores.append((course_code, score))
    
    combined_score_ranking = sorted(combined_text_scores, key=lambda x: x[1], reverse=True)[:top_n]
    logging.info(f"Combined score ranking calculated for top {top_n} courses.")
    return {
        "combined_score_ranking": combined_score_ranking
    }
