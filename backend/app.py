from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, get_db
import models
import routes
import chatbot
import uvicorn

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Assignment Submission and Verification System")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router)
app.include_router(chatbot.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Assignment Submission and Verification System API"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
