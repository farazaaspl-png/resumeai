from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import shutil
from pathlib import Path

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    """Root endpoint to check if API is running"""
    return {"message": "FastAPI Server is running!", "status": "success"}


@app.post("/analyse")
async def analyse_resume(
    resume: UploadFile = File(...),
    jobDescription: str = Form(...)
):
    """
    Analyze resume against job description
    
    Parameters:
    - resume: Resume file (PDF, DOC, DOCX)
    - jobDescription: Job description text
    """
    try:
        # Save the uploaded resume
        file_path = UPLOAD_DIR / resume.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
        
        # TODO: Add your resume analysis logic here
        # This is where you would:
        # 1. Parse the resume file
        # 2. Compare it with the job description
        # 3. Return analysis results
        
        response_data = {
            "status": "success",
            "message": "Resume analyzed successfully",
            "data": {
                "filename": resume.filename,
                "content_type": resume.content_type,
                "file_size": file_path.stat().st_size,
                "job_description_length": len(jobDescription),
                # Add your analysis results here
                "match_score": 85,
                "key_skills_found": ["Python", "FastAPI", "React"],
                "missing_skills": ["Docker", "Kubernetes"],
                "recommendations": [
                    "Add more details about your FastAPI experience",
                    "Include specific project examples"
                ]
            }
        }
        
        # Delete the file after processing
        if file_path.exists():
            file_path.unlink()
        
        return response_data
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error analyzing resume: {str(e)}"
        }
    finally:
        await resume.close()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "FastAPI File Upload Server"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
