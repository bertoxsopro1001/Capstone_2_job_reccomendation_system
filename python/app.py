import pandas as pd
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

app = Flask(__name__)

# Load jobs data from CSV file into a DataFrame
jobs_data = pd.read_csv('python/jobs.csv')

# TF-IDF vectorization for job titles
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(jobs_data['title'])

# Function to extract numeric value from string
def extract_numeric(value):
    match = re.search(r'\d+', str(value))  # Ensure value is converted to string before searching
    if match:
        return int(match.group())
    return 0  # Return 0 if no numeric value found

# Function to parse salary range or single value
def parse_range(input_str):
    if isinstance(input_str, int):
        return input_str, input_str  # Handle single integer input
    parts = re.findall(r'\d+', str(input_str))  # Extract all numeric parts
    if len(parts) == 2:
        return int(parts[0]), int(parts[1])
    elif len(parts) == 1:
        return int(parts[0]), int(parts[0])  # Handle single value as range
    else:
        return 0, 0  # Return default values if parsing fails

@app.route('/recommend_jobs', methods=['POST'])
def recommend_jobs():
    user_input = request.get_json()

    # Extract user input
    user_personality = user_input['personality']
    user_work_experience_min, user_work_experience_max = parse_range(user_input['work_experience'])
    user_work_hours_min, user_work_hours_max = parse_range(user_input['work_hours'])
    user_salary_min, user_salary_max = parse_range(user_input['salary'])

    print(f"User Input:\n"
          f"  Personality: {user_personality}\n"
          f"  Work Experience Range: {user_work_experience_min}-{user_work_experience_max}\n"
          f"  Work Hours Range: {user_work_hours_min}-{user_work_hours_max}\n"
          f"  Salary Range: {user_salary_min}-{user_salary_max}")

    # Filter jobs based on user's personality (exact match)
    filtered_jobs = jobs_data[jobs_data['personality'] == user_personality]

    if filtered_jobs.empty:
        print("No jobs found matching the specified personality.")
        return jsonify([])

    print(f"Filtered Jobs Count: {filtered_jobs.shape[0]}")

    # Vectorize user preferences
    user_preferences = f"{user_personality} {user_work_experience_min} {user_work_hours_min} {user_salary_min}"
    user_preferences_vector = vectorizer.transform([user_preferences])

    # Calculate cosine similarity only for jobs with the same personality
    filtered_tfidf_matrix = tfidf_matrix[filtered_jobs.index]
    similarities = cosine_similarity(user_preferences_vector, filtered_tfidf_matrix)

    valid_jobs = []
    for idx, sim in enumerate(similarities.flatten()):
        job_idx = filtered_jobs.index[idx]
        job = jobs_data.loc[job_idx]

        job_salary = int(job['salary'])
        job_experience = extract_numeric(job['work_experience'])
        job_hours = extract_numeric(job['work_hours'])

        # Check if job's salary, experience, and hours match or fall within user's specified range
        if (user_salary_min <= job_salary <= user_salary_max and
            user_work_experience_min <= job_experience <= user_work_experience_max and
            user_work_hours_min <= job_hours <= user_work_hours_max):
            valid_jobs.append((job_idx, sim))

    # Sort valid jobs by similarity score in descending order
    valid_jobs = sorted(valid_jobs, key=lambda x: x[1], reverse=True)[:3]

    # Format recommended jobs
    recommended_jobs = []
    for job_idx, score in valid_jobs:
        job = jobs_data.loc[job_idx]
        recommended_jobs.append({
            'title': job['title'],
            'salary': int(job['salary']),
            'personality': job['personality'],
            'work_experience': extract_numeric(job['work_experience']),
            'work_hours': extract_numeric(job['work_hours'])
        })

    print("Recommended Jobs:")
    for job in recommended_jobs:
        print(f"  Title: {job['title']}")
        print(f"    Salary: {job['salary']}")
        print(f"    Personality: {job['personality']}")
        print(f"    Work Experience: {job['work_experience']}")
        print(f"    Work Hours: {job['work_hours']}")

    return jsonify(recommended_jobs)

if __name__ == '__main__':
    app.run(debug=True)
