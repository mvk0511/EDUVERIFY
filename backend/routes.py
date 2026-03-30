from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
import shutil
from db import submissions_collection, assignments_collection, users_collection, notifications_collection, certificates_collection

router = APIRouter()
UPLOAD_DIR = "uploads"

# --- In-Memory State ---
mock_assignments = []
mock_submissions = []
mock_tasks = []

# --- Pydantic Schemas ---
class UserLogin(BaseModel):
    email: str; password: str; role: str

class StudentCreate(BaseModel):
    name: str; email: str; password: str; department: str; semester: str

class TeacherCreate(BaseModel):
    name: str; email: str; password: str; subject: str; department: str

class AssignmentCreate(BaseModel):
    teacher_id: int; title: str; description: str; subject: str; deadline: str

class TaskCreate(BaseModel):
    student_id: int; task_name: str; task_date: str

class NoteCreate(BaseModel):
    teacher_id: int; title: str; description: str

class SubmissionCreate(BaseModel):
    student_id: int; assignment_id: int; submitted_file: str

# --- Authentication Routes ---
@router.post("/api/auth/register/student")
def register_student(student: StudentCreate):
    new_user = student.dict()
    new_user['role'] = 'student'
    new_user['user_id'] = users_collection.count_documents({}) + 1
    users_collection.insert_one(new_user)
    return {"message": "Student registered successfully", "id": new_user['user_id']}

@router.post("/api/auth/register/teacher")
def register_teacher(teacher: TeacherCreate):
    new_user = teacher.dict()
    new_user['role'] = 'teacher'
    new_user['user_id'] = users_collection.count_documents({}) + 1
    users_collection.insert_one(new_user)
    return {"message": "Teacher registered successfully", "id": new_user['user_id']}

@router.post("/api/auth/login")
def login(user: UserLogin):
    # Try MongoDB first
    db_user = users_collection.find_one({"email": user.email, "role": user.role, "password": user.password})
    if db_user:
        # Permanently store the last login time
        users_collection.update_one(
            {"_id": db_user["_id"]},
            {"$set": {"last_login": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}}
        )
        return {"message": "Login successful", "role": db_user['role'], "user_id": db_user['user_id'], "name": db_user.get('name', 'User')}
    
    # Fallback for previous mocked states
    if user.role in ['student', 'teacher']:
        # We only allow login for manually created users in DB now.
        pass
    raise HTTPException(status_code=400, detail="Invalid credentials")

# --- Assignments Routes ---
@router.post("/api/assignments")
async def create_assignment(
    teacher_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    subject: str = Form(...),
    deadline: str = Form(...),
    question_pdf: UploadFile = File(None)
):
    ass_id = assignments_collection.count_documents({}) + 1
    file_name = None
    
    if question_pdf:
        file_path = os.path.join(UPLOAD_DIR, question_pdf.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(question_pdf.file, buffer)
        file_name = question_pdf.filename

    new_ass = {
        "assignment_id": ass_id,
        "teacher_id": teacher_id,
        "title": title,
        "subject": subject,
        "description": description,
        "deadline": deadline,
        "question_pdf": file_name
    }
    assignments_collection.insert_one(new_ass)
    new_ass.pop("_id", None)
    return new_ass

@router.get("/api/assignments")
def get_assignments():
    # Return from DB directly
    db_assignments = list(assignments_collection.find({}, {"_id": 0}))
    return db_assignments

# --- Tasks Routes (Student) ---
@router.post("/api/tasks")
def create_task(task: TaskCreate):
    task_id = len(mock_tasks) + 1
    new_task = {"task_id": task_id, "task_name": task.task_name, "task_date": task.task_date, "completion_status": False}
    mock_tasks.append(new_task)
    return new_task

@router.get("/api/tasks/student/{student_id}")
def get_student_tasks(student_id: int):
    return mock_tasks

@router.put("/api/tasks/{task_id}/toggle")
def toggle_task(task_id: int):
    for t in mock_tasks:
        if t["task_id"] == task_id:
            t["completion_status"] = not t["completion_status"]
            return {"message": "Task toggled", "status": t["completion_status"]}
    raise HTTPException(status_code=404, detail="Task not found")

# --- Administrative Routes (Teacher) ---
@router.get("/api/students")
def get_students():
    db_students = list(users_collection.find({"role": "student"}, {"_id": 0, "password": 0}))
    for s in db_students:
        s["student_id"] = s.get("user_id", s.get("_id", 1))
        s["registration_date"] = s.get("registration_date", "Registered via App")
        s["last_login"] = s.get("last_login", "Never")
    return db_students

@router.get("/api/submissions")
def get_all_submissions():
    # Return the dynamic array for teacher
    data = []
    assignments = list(assignments_collection.find({}, {"_id": 0}))
    users = list(users_collection.find({"role": "student"}))
    
    for sub in submissions_collection.find({}, {"_id": 0}):
        ass_name = next((a["title"] for a in assignments if a["assignment_id"] == sub["assignment_id"]), "Unknown")
        
        # Robust ID lookup: try matching as int or str
        sub_student_id = sub.get("student_id")
        student_obj = next((u for u in users if u.get("user_id") == sub_student_id or str(u.get("user_id")) == str(sub_student_id)), None)
        
        # Fallback to f-string if user not found, instead of static 'Student User'
        real_student_name = student_obj.get("name") if student_obj else f"User {sub_student_id}"
        
        data.append({
            "submission_id": sub["submission_id"],
            "student": real_student_name,
            "student_id": sub["student_id"],
            "name": ass_name,
            "file_name": sub["submitted_file"],
            "date": sub["submission_date"],
            "status": sub["status"],
            "plagiarism_score": sub["plagiarism_score"],
            "marks": 0.0,
            "feedback": ""
        })
    return data

@router.get("/api/submissions/student/{student_id}")
def get_student_submissions(student_id: int):
    data = []
    assignments = list(assignments_collection.find({}, {"_id": 0}))
    for sub in submissions_collection.find({}, {"_id": 0}):
        if sub["student_id"] == student_id:
            ass_name = next((a["title"] for a in assignments if a["assignment_id"] == sub["assignment_id"]), "Unknown")
            data.append({
                "submission_id": sub["submission_id"],
                "name": ass_name,
                "date": sub["submission_date"],
                "status": sub["status"],
                "plagiarism": "Checked ({}%)".format(sub.get("plagiarism_score", 0)),
                "file_name": sub.get("submitted_file", "")
            })
    return data

# --- Notifications API ---
@router.get("/api/notifications/student/{student_id}")
def get_student_notifications(student_id: int):
    now = datetime.utcnow()
    deadline_threshold = now + timedelta(hours=48)
    
    notifications = []
    
    # Get student submissions to filter out completed assignments
    submitted_assignment_ids = []
    for sub in submissions_collection.find({"student_id": student_id}, {"_id": 0}):
        submitted_assignment_ids.append(sub.get("assignment_id"))
        
    assignments = list(assignments_collection.find({}, {"_id": 0}))
    for ass in assignments:
        if ass.get("assignment_id") in submitted_assignment_ids:
            continue
            
        try:
            # Frontend sends new Date(deadline).toISOString() which ends in 'Z'
            ass_deadline = datetime.fromisoformat(ass['deadline'].replace('Z', '+00:00')).replace(tzinfo=None)
            if now <= ass_deadline <= deadline_threshold:
                notifications.append({
                    "id": ass['assignment_id'],
                    "title": f"Deadline Approaching: {ass['title']}",
                    "message": f"Assignment '{ass['title']}' is due on {ass_deadline.strftime('%Y-%m-%d %H:%M')}.",
                    "type": "warning"
                })
        except Exception:
            pass
            
    return notifications

@router.get("/api/certificates/all")
def get_all_certificates():
    # Return all certificates for the teacher side
    # We will fetch user info to append student name
    users = list(users_collection.find({"role": "student"}))
    certs = list(certificates_collection.find({}, {"_id": 0}))
    for c in certs:
        student_id = c.get("user_id")
        student_obj = next((u for u in users if u.get("user_id") == student_id or str(u.get("user_id")) == str(student_id)), None)
        c["student_name"] = student_obj.get("name") if student_obj else f"Student {student_id}"
    return certs

@router.get("/api/certificates/{student_id}")
def get_student_certificates(student_id: int):
    # Retrieve certificates per user prompt schema
    certs = list(certificates_collection.find({"user_id": str(student_id)}, {"_id": 0}))
    # Also fallback string logic
    if not certs:
        certs = list(certificates_collection.find({"user_id": student_id}, {"_id": 0}))
    return certs

@router.post("/api/certificates/upload")
async def upload_certificate(
    student_id: int = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...)
):
    cert_dir = os.path.join(UPLOAD_DIR, "certificates")
    os.makedirs(cert_dir, exist_ok=True)
    
    # Save the file
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join(cert_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    date_issued = datetime.now().strftime("%Y-%m-%d")
    
    new_cert = {
        "user_id": student_id,
        "name": name,
        "filename": unique_filename,
        "date_issued": date_issued,
        "status": "Review Pending"
    }
    
    certificates_collection.insert_one(new_cert)
    new_cert.pop("_id", None)
    return new_cert
