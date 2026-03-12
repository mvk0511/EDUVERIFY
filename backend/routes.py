from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# --- Pydantic Schemas for Request/Response Validation ---
class UserLogin(BaseModel):
    email: str
    password: str
    role: str # 'student' or 'teacher'

class StudentCreate(BaseModel):
    name: str
    email: str
    password: str
    department: str
    semester: str

class TeacherCreate(BaseModel):
    name: str
    email: str
    password: str
    subject: str
    department: str

class AssignmentCreate(BaseModel):
    teacher_id: int
    title: str
    description: str
    subject: str
    deadline: datetime

class TaskCreate(BaseModel):
    student_id: int
    task_name: str
    task_date: datetime

class NoteCreate(BaseModel):
    teacher_id: int
    title: str
    description: str

class SubmissionCreate(BaseModel):
    student_id: int
    assignment_id: int
    submitted_file: str # In a real app this might be a URL or path

# --- Authentication Routes ---
@router.post("/api/auth/register/student")
def register_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(models.Student).filter(models.Student.email == student.email).first()
    if db_student:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_student = models.Student(
        name=student.name, email=student.email, password=student.password, # Note: Password should be hashed
        department=student.department, semester=student.semester
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return {"message": "Student registered successfully", "id": new_student.student_id}

@router.post("/api/auth/register/teacher")
def register_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    db_teacher = db.query(models.Teacher).filter(models.Teacher.email == teacher.email).first()
    if db_teacher:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_teacher = models.Teacher(
        name=teacher.name, email=teacher.email, password=teacher.password, # Note: Password should be hashed
        subject=teacher.subject, department=teacher.department
    )
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return {"message": "Teacher registered successfully", "id": new_teacher.teacher_id}

@router.post("/api/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    if user.role == 'student':
        db_user = db.query(models.Student).filter(models.Student.email == user.email, models.Student.password == user.password).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        return {"message": "Login successful", "role": "student", "user_id": db_user.student_id, "name": db_user.name}
    elif user.role == 'teacher':
        db_user = db.query(models.Teacher).filter(models.Teacher.email == user.email, models.Teacher.password == user.password).first()
        if not db_user:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        return {"message": "Login successful", "role": "teacher", "user_id": db_user.teacher_id, "name": db_user.name}
    raise HTTPException(status_code=400, detail="Invalid role")

# --- Assignments Routes ---
@router.post("/api/assignments")
def create_assignment(assignment: AssignmentCreate, db: Session = Depends(get_db)):
    new_assignment = models.Assignment(**assignment.dict())
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment

@router.get("/api/assignments")
def get_assignments(db: Session = Depends(get_db)):
    return db.query(models.Assignment).all()

# --- Tasks Routes (Student) ---
@router.post("/api/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = models.Task(**task.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/api/tasks/student/{student_id}")
def get_student_tasks(student_id: int, db: Session = Depends(get_db)):
    return db.query(models.Task).filter(models.Task.student_id == student_id).all()

@router.put("/api/tasks/{task_id}/toggle")
def toggle_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.completion_status = not task.completion_status
    db.commit()
    return {"message": "Task toggled", "status": task.completion_status}

# --- Notes Routes (Teacher) ---
@router.post("/api/notes")
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    new_note = models.Note(**note.dict())
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

@router.get("/api/notes/teacher/{teacher_id}")
def get_teacher_notes(teacher_id: int, db: Session = Depends(get_db)):
    return db.query(models.Note).filter(models.Note.teacher_id == teacher_id).all()

# --- Administrative Routes (Teacher) ---
@router.get("/api/students")
def get_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

@router.get("/api/submissions")
def get_all_submissions(db: Session = Depends(get_db)):
    # Join with Student and Assignment for rich reporting
    results = db.query(models.Submission).join(models.Student).join(models.Assignment).all()
    # Construct results with necessary details
    data = []
    for sub in results:
        data.append({
            "submission_id": sub.submission_id,
            "student": sub.student.name,
            "student_id": sub.student_id,
            "name": sub.assignment.title,
            "date": sub.submission_date.strftime("%Y-%m-%d %H:%M"),
            "status": sub.status,
            "plagiarism_score": sub.plagiarism_score,
            "marks": sub.marks,
            "feedback": sub.teacher_feedback
        })
    return data

@router.post("/api/submissions")
def create_submission(submission: SubmissionCreate, db: Session = Depends(get_db)):
    # Simple check for existing submission could go here
    new_submission = models.Submission(
        student_id=submission.student_id,
        assignment_id=submission.assignment_id,
        submitted_file=submission.submitted_file,
        status="submitted",
        plagiarism_score=15.0 # Mock plagiarism analysis
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    return new_submission

@router.get("/api/submissions/student/{student_id}")
def get_student_submissions(student_id: int, db: Session = Depends(get_db)):
    results = db.query(models.Submission).filter(models.Submission.student_id == student_id).join(models.Assignment).all()
    data = []
    for sub in results:
        data.append({
            "submission_id": sub.submission_id,
            "name": sub.assignment.title,
            "date": sub.submission_date.strftime("%Y-%m-%d"),
            "status": sub.status,
            "plagiarism": f"Safe ({sub.plagiarism_score}%)" if sub.plagiarism_score < 40 else f"High ({sub.plagiarism_score}%)"
        })
    return data

# --- Submissions & Plagiarism (Mock Analytics) ---
@router.get("/api/analytics/teacher/{teacher_id}")
def get_teacher_analytics(teacher_id: int, db: Session = Depends(get_db)):
    # Mock data for analytics
    return {
        "plagiarism_scores": [10, 15, 5, 45, 80, 20, 10], # %
        "safe_vs_flagged": {"safe": 85, "flagged": 15}
    }

@router.get("/api/analytics/student/{student_id}")
def get_student_analytics(student_id: int, db: Session = Depends(get_db)):
    return {
        "gpa_trend": [3.2, 3.4, 3.5, 3.8, 3.9],
        "submission_tracking": {"completed": 12, "pending": 3, "late": 1}
    }
