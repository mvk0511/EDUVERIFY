from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
from datetime import datetime

# Local imports
from plagiarism_engine import compute_similarity
import routes
import chatbot
from db import submissions_collection, users_collection

app = FastAPI(title="Smart Assignment System Backend (No DB)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)
app.include_router(chatbot.router)

UPLOAD_DIR = "uploads"
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

class SimpleLogin(BaseModel):
    roll_no: str
    email: str

@app.post("/login")
async def simple_login(login_data: SimpleLogin):
    user = users_collection.find_one({"roll_no": login_data.roll_no, "email": login_data.email})
    if not user:
        users_collection.insert_one({"roll_no": login_data.roll_no, "email": login_data.email})
    return {"message": "Success", "roll_no": login_data.roll_no}


@app.post("/upload")
@app.post("/api/assignments/upload")
async def upload_file(
    student_id: int = 1,
    assignment_id: int = 1,
    roll_no: str = Form(None),
    email: str = Form(None),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
        
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        sub_id = submissions_collection.count_documents({}) + 1
        new_sub = {
            "submission_id": sub_id,
            "student_id": student_id,
            "assignment_id": int(assignment_id),
            "submitted_file": file.filename,
            "submission_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            "status": "submitted",
            "plagiarism_score": 0.0,
            "roll_no": roll_no,
            "email": email
        }
        submissions_collection.insert_one(new_sub)
            
        return {"message": f"Successfully uploaded {file.filename}", "submission_id": sub_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/submissions")
async def list_submissions(roll_no: str = None, email: str = None):
    try:
        if not roll_no or not email:
            raise HTTPException(status_code=400, detail="roll_no and email are required parameters")
            
        query = {"roll_no": roll_no, "email": email}
        return list(submissions_collection.find(query, {"_id": 0}))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/detect")
@app.get("/api/submissions/detect-plagiarism")
async def run_detection():
    try:
        results = compute_similarity()
        users_cache = list(users_collection.find({"role": "student"}))
        
        for res in results.get("results", []):
            similarity_value = res["similarity"]
            
            # Find Student 1 Name
            sub1 = submissions_collection.find_one({"submitted_file": res["file1"]})
            u1_name = "Unknown Student"
            if sub1:
                student1_id = str(sub1.get("student_id", ""))
                u1 = next((u for u in users_cache if str(u.get("user_id", "")) == student1_id or str(u.get("_id", "")) == student1_id), None)
                if u1: u1_name = u1.get("name", "Unknown Student")
            res["student1_name"] = u1_name
            
            # Find Student 2 Name
            sub2 = submissions_collection.find_one({"submitted_file": res["file2"]})
            u2_name = "Unknown Student"
            if sub2:
                student2_id = str(sub2.get("student_id", ""))
                u2 = next((u for u in users_cache if str(u.get("user_id", "")) == student2_id or str(u.get("_id", "")) == student2_id), None)
                if u2: u2_name = u2.get("name", "Unknown Student")
            res["student2_name"] = u2_name
            
            # Safely calculate new scores and conditional flags for File 1
            new_score1 = max(sub1.get("plagiarism_score", 0), similarity_value) if sub1 else similarity_value
            new_status1 = "flagged" if new_score1 >= 90 else (sub1.get("status", "submitted") if sub1 else "submitted")
            submissions_collection.update_many(
                {"submitted_file": res["file1"]},
                {"$set": {"plagiarism_score": new_score1, "status": new_status1}}
            )
            
            # Safely calculate new scores and conditional flags for File 2
            new_score2 = max(sub2.get("plagiarism_score", 0), similarity_value) if sub2 else similarity_value
            new_status2 = "flagged" if new_score2 >= 90 else (sub2.get("status", "submitted") if sub2 else "submitted")
            submissions_collection.update_many(
                {"submitted_file": res["file2"]},
                {"$set": {"plagiarism_score": new_score2, "status": new_status2}}
            )
                    
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import HTMLResponse, FileResponse
import mimetypes

@app.get("/")
async def serve_root():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    full_path = full_path.lstrip("/")
    if not full_path:
        full_path = "index.html"
        
    file_path = os.path.abspath(os.path.join(FRONTEND_DIR, full_path))
    
    if os.path.exists(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        return FileResponse(file_path, media_type=mime_type)
        
    return HTMLResponse("Not Found", status_code=404)

if __name__ == "__main__":
    import uvicorn
    # When run directly from IDE, start the server automatically
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# RESTART MEMORY CACHE
