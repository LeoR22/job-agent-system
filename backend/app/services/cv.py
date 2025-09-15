import os
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.database import CV, Skill, CVSkill, User
from app.models.schemas import CVCreate, CVUpdate, CVSkillCreate
from app.services.ai import AIService


class CVService:
    """Service for CV operations"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def get_user_cvs(self, db: Session, user_id: str, skip: int = 0, limit: int = 10) -> List[CV]:
        """Get user's CVs"""
        return db.query(CV).filter(CV.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_cv(self, db: Session, cv_id: str, user_id: str) -> Optional[CV]:
        """Get specific CV for user"""
        return db.query(CV).filter(CV.id == cv_id, CV.user_id == user_id).first()
    
    def create_cv(self, db: Session, user_id: str, cv_data: CVCreate) -> CV:
        """Create new CV"""
        db_cv = CV(
            user_id=user_id,
            **cv_data.dict()
        )
        db.add(db_cv)
        db.commit()
        db.refresh(db_cv)
        return db_cv
    
    def update_cv(self, db: Session, cv_id: str, user_id: str, cv_data: CVUpdate) -> Optional[CV]:
        """Update CV"""
        cv = self.get_cv(db, cv_id, user_id)
        if not cv:
            return None
        
        update_data = cv_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cv, field, value)
        
        db.commit()
        db.refresh(cv)
        return cv
    
    def delete_cv(self, db: Session, cv_id: str, user_id: str) -> bool:
        """Delete CV"""
        cv = self.get_cv(db, cv_id, user_id)
        if not cv:
            return False
        
        # Delete file from disk
        if cv.file_path and os.path.exists(cv.file_path):
            try:
                os.remove(cv.file_path)
            except OSError:
                pass  # Continue even if file deletion fails
        
        db.delete(cv)
        db.commit()
        return True
    
    def activate_cv(self, db: Session, cv_id: str, user_id: str) -> Optional[CV]:
        """Activate CV"""
        cv = self.get_cv(db, cv_id, user_id)
        if not cv:
            return None
        
        cv.is_active = True
        db.commit()
        db.refresh(cv)
        return cv
    
    def deactivate_cv(self, db: Session, cv_id: str, user_id: str) -> Optional[CV]:
        """Deactivate CV"""
        cv = self.get_cv(db, cv_id, user_id)
        if not cv:
            return None
        
        cv.is_active = False
        db.commit()
        db.refresh(cv)
        return cv
    
    def count_user_cvs(self, db: Session, user_id: str) -> int:
        """Count user's CVs"""
        return db.query(CV).filter(CV.user_id == user_id).count()
    
    def get_active_cv(self, db: Session, user_id: str) -> Optional[CV]:
        """Get user's active CV"""
        return db.query(CV).filter(CV.user_id == user_id, CV.is_active == True).first()
    
    async def process_cv(self, db: Session, user_id: str, file_path: str, filename: str, file_size: int, mime_type: str) -> Dict[str, Any]:
        """Process uploaded CV: extract text, analyze with AI, and save to database"""
        try:
            # Extract text from CV
            extracted_text = await self.extract_text_from_cv(file_path, mime_type)
            
            # Analyze CV with AI
            ai_analysis = await self.ai_service.analyze_cv(extracted_text)
            
            # Create CV record
            cv_data = CVCreate(
                file_name=filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                extracted_text=extracted_text,
                parsed_data=ai_analysis
            )
            
            cv = self.create_cv(db, user_id, cv_data)
            
            # Extract and save skills
            skills = await self.extract_and_save_skills(db, cv.id, ai_analysis)
            
            # Deactivate other CVs for this user
            db.query(CV).filter(CV.user_id == user_id, CV.id != cv.id).update({"is_active": False})
            db.commit()
            
            return {
                "id": cv.id,
                "file_name": cv.file_name,
                "extracted_text": cv.extracted_text,
                "parsed_data": cv.parsed_data,
                "skills": skills,
                "is_active": cv.is_active,
                "created_at": cv.created_at
            }
        
        except Exception as e:
            # Clean up uploaded file if processing fails
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            raise e
    
    async def extract_text_from_cv(self, file_path: str, mime_type: str) -> str:
        """Extract text from CV file"""
        try:
            if mime_type == "application/pdf":
                return await self.extract_text_from_pdf(file_path)
            elif mime_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                return await self.extract_text_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {mime_type}")
        except Exception as e:
            raise Exception(f"Text extraction failed: {str(e)}")
    
    async def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import pypdf
            
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"PDF text extraction failed: {str(e)}")
    
    async def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"DOCX text extraction failed: {str(e)}")
    
    async def extract_and_save_skills(self, db: Session, cv_id: str, ai_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract skills from AI analysis and save to database"""
        skills = []
        
        try:
            # Get skills from AI analysis
            ai_skills = ai_analysis.get("skills", [])
            
            for skill_data in ai_skills:
                skill_name = skill_data.get("name", "").lower().strip()
                if not skill_name:
                    continue
                
                # Find or create skill
                skill = db.query(Skill).filter(Skill.name == skill_name).first()
                if not skill:
                    skill = Skill(
                        name=skill_name,
                        category=skill_data.get("category", "Technical"),
                        description=f"Skill: {skill_name}"
                    )
                    db.add(skill)
                    db.commit()
                    db.refresh(skill)
                
                # Create CV skill relationship
                cv_skill = CVSkill(
                    cv_id=cv_id,
                    skill_id=skill.id,
                    level=skill_data.get("level", 1),
                    years=skill_data.get("years")
                )
                db.add(cv_skill)
                db.commit()
                db.refresh(cv_skill)
                
                skills.append({
                    "id": cv_skill.id,
                    "skill_id": skill.id,
                    "name": skill.name,
                    "category": skill.category,
                    "level": cv_skill.level,
                    "years": cv_skill.years
                })
        
        except Exception as e:
            print(f"Error extracting skills: {str(e)}")
        
        return skills
    
    def add_cv_skill(self, db: Session, cv_id: str, user_id: str, skill_data: CVSkillCreate) -> Optional[CVSkill]:
        """Add skill to CV"""
        # Verify CV belongs to user
        cv = self.get_cv(db, cv_id, user_id)
        if not cv:
            return None
        
        # Find or create skill
        skill = db.query(Skill).filter(Skill.id == skill_data.skill_id).first()
        if not skill:
            return None
        
        # Check if skill already exists for CV
        existing_cv_skill = db.query(CVSkill).filter(
            CVSkill.cv_id == cv_id,
            CVSkill.skill_id == skill_data.skill_id
        ).first()
        
        if existing_cv_skill:
            # Update existing skill
            existing_cv_skill.level = skill_data.level
            existing_cv_skill.years = skill_data.years
            db.commit()
            db.refresh(existing_cv_skill)
            return existing_cv_skill
        
        # Create new CV skill
        cv_skill = CVSkill(
            cv_id=cv_id,
            skill_id=skill_data.skill_id,
            level=skill_data.level,
            years=skill_data.years
        )
        db.add(cv_skill)
        db.commit()
        db.refresh(cv_skill)
        
        return cv_skill
    
    def get_cv_skills(self, db: Session, cv_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get CV skills"""
        cv = self.get_cv(db, cv_id, user_id)
        if not cv:
            return []
        
        skills = db.query(CVSkill).filter(CVSkill.cv_id == cv_id).all()
        
        return [
            {
                "id": skill.id,
                "skill_id": skill.skill_id,
                "name": skill.skill.name,
                "category": skill.skill.category,
                "level": skill.level,
                "years": skill.years
            }
            for skill in skills
        ]
    
    def remove_cv_skill(self, db: Session, cv_id: str, user_id: str, skill_id: str) -> bool:
        """Remove skill from CV"""
        cv = self.get_cv(db, cv_id, user_id)
        if not cv:
            return False
        
        cv_skill = db.query(CVSkill).filter(
            CVSkill.cv_id == cv_id,
            CVSkill.skill_id == skill_id
        ).first()
        
        if not cv_skill:
            return False
        
        db.delete(cv_skill)
        db.commit()
        return True