import pandas as pd
import json
import re
from datetime import datetime
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# Load CSV data
# -----------------------------
student_profile = pd.read_csv("student_profile.csv").to_dict(orient="records")[0]
learning_history = pd.read_csv("learning_history.csv").to_dict(orient="records")
concept_requests = pd.read_csv("concept_requests.csv").to_dict(orient="records")
student_answers = pd.read_csv("student_answers.csv").to_dict(orient="records")
exercise_requests = pd.read_csv("exercise_requests.csv").to_dict(orient="records")

# -----------------------------
# Process concept explanation
# -----------------------------
if len(concept_requests) > 0:
    req = concept_requests[-1]  # take last request
    subject = req["subject"]
    concept = req["concept"]
    difficulty_level = req["difficulty_level"]

    profile_context = json.dumps(student_profile, indent=2)
    relevant_history = [h for h in learning_history if h.get("subject") == subject]
    history_context = json.dumps(relevant_history[-3:], indent=2) if relevant_history else "No prior history"

    prompt = f"""
    Explain the following educational concept, adapting to the student's profile:

    SUBJECT: {subject}
    CONCEPT: {concept}
    DIFFICULTY LEVEL: {difficulty_level} (1-5 scale)

    STUDENT PROFILE:
    {profile_context}

    RELEVANT LEARNING HISTORY:
    {history_context}

    Explain this concept using the following approach:
    1. Simple definition
    2. Real-world analogy
    3. Break down into sequential components
    4. Examples of increasing complexity
    5. Connect to previous learning
    6. 2-3 practice questions
    """

    response = client.responses.create(model="gpt-4o-mini", input=prompt, temperature=0)
    explanation = response.output_text

    # Extract practice questions
    practice_questions = []
    pattern = r"(?:Question|Q)\.?\s*(\d+)[.:]?\s*(.*?)(?=(?:Question|Q)\.?\s*\d+|$)"
    matches = re.findall(pattern, explanation, re.DOTALL)

    if matches:
        for _, content in matches:
            practice_questions.append(content.strip())
    else:
        for q in re.findall(r"(.*?\?)", explanation):
            if len(q.split()) > 5:
                practice_questions.append(q.strip())

    # Save to learning history
    learning_history.append({
        "timestamp": datetime.now().isoformat(),
        "subject": subject,
        "concept": concept,
        "difficulty_level": difficulty_level,
        "interaction_type": "concept_explanation",
        "practice_questions": json.dumps(practice_questions),
        "content": explanation
    })

# -----------------------------
# Evaluate student answer
# -----------------------------
if len(student_answers) > 0:
    ans = student_answers[-1]
    question = ans["question"]
    student_answer = ans["student_answer"]
    subject = ans["subject"]

    prompt = f"""
    Evaluate this student's answer:

    SUBJECT: {subject}
    QUESTION: {question}
    STUDENT ANSWER: {student_answer}

    Provide:
    1. Correctness
    2. Strengths
    3. Misconceptions
    4. Correct solution
    5. Suggestions for improvement
    6. Follow-up question
    """

    response = client.responses.create(model="gpt-4o-mini", input=prompt, temperature=0)
    evaluation = response.output_text

    learning_history.append({
        "timestamp": datetime.now().isoformat(),
        "subject": subject,
        "interaction_type": "answer_evaluation",
        "question": question,
        "student_answer": student_answer,
        "content": evaluation
    })

# -----------------------------
# Generate personalized exercise
# -----------------------------
if len(exercise_requests) > 0:
    ex = exercise_requests[-1]
    subject = ex["subject"]
    concept = ex["concept"]
    difficulty_level = ex["difficulty_level"]
    exercise_type = ex["exercise_type"]

    concept_history = [h for h in learning_history if h.get("subject") == subject and h.get("concept") == concept]
    knowledge_context = f"Student has {len(concept_history)} prior interactions with this concept." if concept_history else "No prior history."

    prompt = f"""
    Create a personalized {exercise_type} exercise:

    SUBJECT: {subject}
    CONCEPT: {concept}
    DIFFICULTY LEVEL: {difficulty_level}
    EXERCISE TYPE: {exercise_type}

    STUDENT PROFILE:
    {json.dumps(student_profile, indent=2)}

    KNOWLEDGE CONTEXT:
    {knowledge_context}

    Include:
    - Instructions
    - Exercise
    - Detailed solution
    - Learning objectives
    """

    response = client.responses.create(model="gpt-4o-mini", input=prompt, temperature=0)
    exercise = response.output_text

    learning_history.append({
        "timestamp": datetime.now().isoformat(),
        "subject": subject,
        "concept": concept,
        "difficulty_level": difficulty_level,
        "interaction_type": "personalized_exercise",
        "exercise_type": exercise_type,
        "content": exercise
    })
    print(exercise)
# -----------------------------
# Save updated history
# -----------------------------
pd.DataFrame(learning_history).to_csv("learning_history.csv", index=False)


print("✅ Completed processing. Updated learning_history.csv")
