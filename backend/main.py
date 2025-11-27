from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import shutil
from pathlib import Path
import httpx
import PyPDF2
import docx
import json
import io

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

# Ollama API configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"  # You can change this to your preferred model


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def extract_text_from_docx(file_path: Path) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from DOCX: {str(e)}")


def extract_text_from_resume(file_path: Path, content_type: str) -> str:
    """Extract text from resume based on file type"""
    if content_type == "application/pdf" or file_path.suffix.lower() == ".pdf":
        return extract_text_from_pdf(file_path)
    elif content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                          "application/msword"] or file_path.suffix.lower() in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    else:
        raise Exception(f"Unsupported file type: {content_type}")


async def analyze_with_ollama(resume_text: str, job_description: str) -> dict:
    """Analyze resume against job description using Ollama"""
    prompt = f"""You are an expert ATS (Applicant Tracking System) and resume analyzer. Analyze the following resume against the job description and provide a detailed assessment.

Job Description:
{job_description}

Resume:
{resume_text}

Please provide a comprehensive analysis in the following JSON format (respond ONLY with valid JSON, no additional text):
{{
    "ats_score": <number between 0-100>,
    "match_percentage": <number between 0-100>,
    "key_skills_found": [<list of skills from JD that are present in resume>],
    "missing_skills": [<list of important skills from JD that are missing>],
    "experience_match": "<brief assessment of experience level match>",
    "education_match": "<brief assessment of education requirements>",
    "strengths": [<list of 3-5 key strengths of the candidate>],
    "weaknesses": [<list of 3-5 areas for improvement>],
    "recommendations": [<list of 3-5 specific recommendations to improve the resume>],
    "keyword_optimization": "<brief note on keyword usage and ATS optimization>",
    "overall_summary": "<2-3 sentence overall assessment>"
}}"""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OLLAMA_API_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            result = response.json()
            analysis_text = result.get("response", "{}")
            
            # Parse the JSON response from Ollama
            try:
                analysis_data = json.loads(analysis_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{[\s\S]*\}', analysis_text)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                else:
                    raise Exception("Could not parse JSON from Ollama response")
            
            return analysis_data
            
    except httpx.TimeoutException:
        raise Exception("Request to Ollama timed out. Please ensure Ollama is running.")
    except httpx.ConnectError:
        raise Exception("Could not connect to Ollama. Please ensure Ollama is running on localhost:11434")
    except Exception as e:
        raise Exception(f"Error analyzing with Ollama: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint to check if API is running"""
    return {"message": "FastAPI Server is running!", "status": "success"}


# @app.post("/analyse")
# async def analyse_resume(
#     resume: UploadFile = File(...),
#     jobDescription: str = Form(...)
# ):
#     """
#     Analyze resume against job description
    
#     Parameters:
#     - resume: Resume file (PDF, DOC, DOCX)
#     - jobDescription: Job description text
#     """
#     try:
#         # Save the uploaded resume
#         file_path = UPLOAD_DIR / resume.filename
#         with file_path.open("wb") as buffer:
#             shutil.copyfileobj(resume.file, buffer)
        
#         # TODO: Add your resume analysis logic here
#         # This is where you would:
#         # 1. Parse the resume file
#         # 2. Compare it with the job description
#         # 3. Return analysis results
        
#         response_data = {
#             "status": "success",
#             "message": "Resume analyzed successfully",
#             "data": {
#                 "filename": resume.filename,
#                 "content_type": resume.content_type,
#                 "file_size": file_path.stat().st_size,
#                 "job_description_length": len(jobDescription),
#                 # Add your analysis results here
#                 "match_score": 85,
#                 "key_skills_found": ["Python", "FastAPI", "React"],
#                 "missing_skills": ["Docker", "Kubernetes"],
#                 "recommendations": [
#                     "Add more details about your FastAPI experience",
#                     "Include specific project examples"
#                 ]
#             }
#         }
        
#         # Delete the file after processing
#         if file_path.exists():
#             file_path.unlink()
        
#         return response_data
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"Error analyzing resume: {str(e)}"
#         }
#     finally:
#         await resume.close()

@app.post("/analyse")
async def analyse_resume(
    resume: UploadFile = File(...),
    jobDescription: str = Form(...)
):
    """
    Analyze resume against job description using Ollama AI
    
    Parameters:
    - resume: Resume file (PDF, DOC, DOCX)
    - jobDescription: Job description text
    """
    file_path = None
    try:
        # Save the uploaded resume
        file_path = UPLOAD_DIR / resume.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
        
        # Extract text from resume
        resume_text = extract_text_from_resume(file_path, resume.content_type)
        
        if not resume_text or len(resume_text.strip()) < 50:
            return {
                "status": "error",
                "message": "Could not extract sufficient text from resume. Please ensure the file is not corrupted or empty."
            }
        
        # Analyze resume with Ollama
        analysis_result = await analyze_with_ollama(resume_text, jobDescription)
        
        response_data = {
            "status": "success",
            "message": "Resume analyzed successfully",
            "data": {
                "filename": resume.filename,
                "content_type": resume.content_type,
                "file_size": file_path.stat().st_size,
                "job_description_length": len(jobDescription),
                "resume_text_length": len(resume_text),
                # Ollama analysis results
                "ats_score": analysis_result.get("ats_score", 0),
                "match_percentage": analysis_result.get("match_percentage", 0),
                "key_skills_found": analysis_result.get("key_skills_found", []),
                "missing_skills": analysis_result.get("missing_skills", []),
                "experience_match": analysis_result.get("experience_match", ""),
                "education_match": analysis_result.get("education_match", ""),
                "strengths": analysis_result.get("strengths", []),
                "weaknesses": analysis_result.get("weaknesses", []),
                "recommendations": analysis_result.get("recommendations", []),
                "keyword_optimization": analysis_result.get("keyword_optimization", ""),
                "overall_summary": analysis_result.get("overall_summary", "")
            }
        }
        
        return response_data
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error analyzing resume: {str(e)}"
        }
    finally:
        # Delete the file after processing
        if file_path and file_path.exists():
            try:
                file_path.unlink()
            except:
                pass
        if resume.file:
            await resume.close()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "FastAPI File Upload Server"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
