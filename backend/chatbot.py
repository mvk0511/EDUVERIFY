import os
import numpy as np
from fastapi import APIRouter
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

router = APIRouter()

# --- Advanced Knowledge Base (The "Training" Data) ---
# Each entry includes role-based context and a set of diverse patterns/phrases.
KNOWLEDGE_BASE = [
    {
        "role": "all",
        "patterns": ["plagiarism rules", "plagiarism policy", "similarity threshold", "how to check similarity", "what is high plagiarism", "40%", "detection algorithm"],
        "reply": "Our system flags any assignment with over 40% similarity as 'High Plagiarism'. We use TF-IDF and Cosine Similarity to compare your work against every other submission in the database."
    },
    {
        "role": "all",
        "patterns": ["file formats", "supported files", "can I upload pdf", "zip file", "docx support", "submission file types"],
        "reply": "The Smart Assignment System primarily supports PDF files. You can also upload .docx or .zip files if your instructor has enabled those formats for a specific assignment."
    },
    {
        "role": "student",
        "patterns": ["how to submit", "upload assignment", "send my homework", "pending assignments", "where is the upload button", "turn in my work", "how do I submit"],
        "reply": "To submit your work, go to the 'My Assignments' tab on your student dashboard. Find the relevant assignment in the grid and click the 'Submit Now' button to upload your PDF."
    },
    {
        "role": "student",
        "patterns": ["check results", "my grades", "marks", "academic results", "score", "feedback", "how did I do", "view my marks"],
        "reply": "You can find your grades, similarity scores, and teacher feedback in the 'Academic Results' section. Just click the tab on your sidebar to see your performance history."
    },
    {
        "role": "student",
        "patterns": ["upload certificates", "my achievements", "past certificates", "semester results", "certify", "pdf certifications"],
        "reply": "Navigate to the 'Certificates' tab on the sidebar. From there, you can upload images or PDFs of your past achievements (like semester results) for your teachers to review."
    },
    {
        "role": "teacher",
        "patterns": ["view reports", "plagiarism reports", "check similarity", "submission records", "who plagiarized", "see student work", "grade submissions"],
        "reply": "As a teacher, you can access detailed 'Submission Reports' and 'Plagiarism Detection' tools on the sidebar. This allows you to review student files and see exact similarity percentages."
    },
    {
        "role": "teacher",
        "patterns": ["manage students", "student list", "registration info", "roll numbers", "view enrolled students"],
        "reply": "The 'Student List' section provides a complete overview of everyone registered in your classes, including their roll numbers, names, and registration dates."
    },
    {
        "role": "all",
        "patterns": ["contact support", "help", "need assistance", "it's not working", "customer service", "email support"],
        "reply": "If you are experiencing technical difficulties, please click on 'Help & Contact' in the sidebar or reach out to our team at support@smartassignment.edu."
    },
    {
        "role": "all",
        "patterns": ["what is this system", "how does it work", "eduassist ai", "who are you", "what can you do", "bot goals"],
        "reply": "I am EduAssist AI, your virtual assistant for the Smart Assignment Submission & Verification (SSV) System. I help you navigate the platform, understand plagiarism rules, and manage your academic tasks!"
    },
    {
        "role": "all",
        "patterns": ["hi", "hello", "hey", "greetings", "good morning", "good afternoon"],
        "reply": "Hello! I'm EduAssist AI. How can I help you with your assignments or your dashboard today?"
    }
]

# --- NLP Engine (Feature Expansion) ---
# We use ngram_range=(1,2) to understand both single words and 2-word phrases.
# We use stop_words='english' to ignore noise like "the", "a", "is", etc.
documents = [" ".join(kb["patterns"]) for kb in KNOWLEDGE_BASE]
vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english').fit(documents)
kb_vectors = vectorizer.transform(documents)

class ChatRequest(BaseModel):
    user_id: int
    role: str
    message: str

@router.post("/api/chatbot/ask")
async def ask_chatbot(request: ChatRequest):
    user_msg = request.message.strip().lower()
    user_role = request.role.lower()
    
    # 1. Vectorize with phrase support
    user_vector = vectorizer.transform([user_msg])
    
    # 2. Semantic lookup via Cosine Similarity
    similarities = cosine_similarity(user_vector, kb_vectors).flatten()
    best_idx = np.argmax(similarities)
    max_sim = similarities[best_idx]
    
    # --- Confidence Layer ---
    # Low threshold for broader matching (0.10)
    if max_sim > 0.10:
        match = KNOWLEDGE_BASE[best_idx]
        
        # --- Role Logic Layer ---
        if match["role"] != "all" and match["role"] != user_role:
            if user_role == "student" and match["role"] == "teacher":
                return {"reply": "I'm sorry, those reporting features are only available to staff members on the Teacher Dashboard. Is there something else I can help you with?"}
            elif user_role == "teacher" and match["role"] == "student":
                return {"reply": "That's a student-focused action (like uploading personal certificates). You can guide your students to their dashboard to manage that!"}

        return {"reply": match.get("reply")}
    
    # --- Intelligent Fallback ---
    return {"reply": "I'm not exactly sure about that. Try asking about 'plagiarism scores', 'how to submit assignments', or 'viewing academic results'. I'm here to help!"}



