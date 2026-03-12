from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: int
    role: str
    message: str

@router.post("/api/chatbot/ask")
def ask_chatbot(request: ChatRequest, db: Session = Depends(get_db)):
    msg = request.message.lower()
    
    # NLP logic (Mocked NLP/Keyword matching for simplicity as requested)
    if request.role == 'student':
        if "due" in msg or "assignments" in msg:
            assignments = db.query(models.Assignment).limit(3).all()
            titles = [f"'{a.title}' due on {a.deadline.strftime('%Y-%m-%d')}" for a in assignments]
            if not titles: return {"reply": "You have no upcoming assignments."}
            return {"reply": "Here are your upcoming assignments: " + ", ".join(titles)}
        
        elif "submit" in msg:
            return {"reply": "To submit an assignment, go to 'My Assignments' on your dashboard, click the 'Upload' button next to the specific task, select your file, and hit submit. The system will automatically check for plagiarism."}
        
        elif "plagiarism" in msg:
            return {"reply": "Plagiarism rules: Anything above 40% similarity is considered High Plagiarism and may be flagged. Always cite your sources properly to avoid this."}
            
    elif request.role == 'teacher':
        if "plagiarism" in msg or "reports" in msg:
            return {"reply": "You can view detailed Plagiarism Reports under the 'Plagiarism Detection' tab on your sidebar. Currently, 15% of recent submissions have been flagged."}
        
        elif "submissions" in msg:
            return {"reply": "Navigate to the 'Submission Reports' tab on the sidebar to review all recent student submissions and their corresponding similarity scores."}

    return {"reply": "I'm EduAssist AI. I can help with assignments, schedules, and plagiarism rules. How can I assist you further?"}
