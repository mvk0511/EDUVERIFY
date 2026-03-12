from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    department = Column(String)
    semester = Column(String)
    registration_date = Column(DateTime, default=datetime.utcnow)

    submissions = relationship("Submission", back_populates="student")
    tasks = relationship("Task", back_populates="student")

class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    subject = Column(String)
    department = Column(String)

    assignments = relationship("Assignment", back_populates="teacher")
    notes = relationship("Note", back_populates="teacher")

class Assignment(Base):
    __tablename__ = "assignments"

    assignment_id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"))
    title = Column(String, index=True)
    description = Column(Text)
    subject = Column(String)
    deadline = Column(DateTime)
    assignment_file = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("Teacher", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")

class Submission(Base):
    __tablename__ = "submissions"

    submission_id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.assignment_id"))
    student_id = Column(Integer, ForeignKey("students.student_id"))
    submitted_file = Column(String)
    submission_date = Column(DateTime, default=datetime.utcnow)
    plagiarism_score = Column(Float, default=0.0)
    status = Column(String, default="submitted")
    marks = Column(Float, nullable=True)
    teacher_feedback = Column(Text, nullable=True)

    student = relationship("Student", back_populates="submissions")
    assignment = relationship("Assignment", back_populates="submissions")
    plagiarism_report = relationship("PlagiarismReport", back_populates="submission", uselist=False)

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"))
    task_name = Column(String)
    task_date = Column(DateTime)
    completion_status = Column(Boolean, default=False)

    student = relationship("Student", back_populates="tasks")

class Note(Base):
    __tablename__ = "notes"

    note_id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"))
    title = Column(String)
    description = Column(Text)
    created_date = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("Teacher", back_populates="notes")

class PlagiarismReport(Base):
    __tablename__ = "plagiarism_reports"

    report_id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.submission_id"), unique=True)
    plagiarism_percentage = Column(Float)
    similarity_sources = Column(Text, nullable=True)
    flagged_content = Column(Text, nullable=True)

    submission = relationship("Submission", back_populates="plagiarism_report")

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    user_type = Column(String) # 'student' or 'teacher'
    message = Column(Text)
    created_time = Column(DateTime, default=datetime.utcnow)
    read_status = Column(Boolean, default=False)
