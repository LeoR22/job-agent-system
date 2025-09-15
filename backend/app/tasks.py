"""
Celery tasks for Job Agent System

This module contains all background tasks that can be executed asynchronously.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.core.celery import celery_app
from app.core.database import get_db
from app.services.ai import AIService
from app.services.mcp import MCPService
from app.agents.job_agent_graph import job_agent_graph
from app.models.database import CV, JobListing, User, JobMatch, SkillRecommendation, AgentExecution
from app.core.logging import get_logger

logger = get_logger(__name__)

# Initialize services
ai_service = AIService()
mcp_service = MCPService()


@celery_app.task(bind=True, name='process_cv')
def process_cv(self, cv_id: str, user_id: str):
    """Process uploaded CV and extract information"""
    try:
        db = next(get_db())
        
        # Get CV from database
        cv = db.query(CV).filter(CV.id == cv_id, CV.user_id == user_id).first()
        if not cv:
            raise ValueError(f"CV not found: {cv_id}")
        
        # Update status to processing
        cv.parsed_data = cv.parsed_data or {}
        cv.parsed_data["processing_status"] = "processing"
        cv.parsed_data["processing_started_at"] = datetime.now().isoformat()
        db.commit()
        
        # Extract text from CV file
        extracted_text = await _extract_cv_text(cv.file_path, cv.mime_type)
        cv.extracted_text = extracted_text
        
        # Analyze CV with AI
        ai_analysis = await ai_service.analyze_cv(extracted_text)
        cv.parsed_data = ai_analysis
        
        # Extract and save skills
        skills = await _extract_and_save_skills(db, cv.id, ai_analysis)
        
        # Update CV status
        cv.parsed_data["processing_status"] = "completed"
        cv.parsed_data["processing_completed_at"] = datetime.now().isoformat()
        cv.parsed_data["extracted_skills_count"] = len(skills)
        
        db.commit()
        
        # Trigger job matching for this CV
        trigger_cv_matching.delay(cv_id, user_id)
        
        return {
            "status": "success",
            "cv_id": cv_id,
            "skills_extracted": len(skills),
            "processing_time": (
                datetime.fromisoformat(cv.parsed_data["processing_completed_at"]) -
                datetime.fromisoformat(cv.parsed_data["processing_started_at"])
            ).total_seconds()
        }
        
    except Exception as e:
        logger.error(f"CV processing failed: {str(e)}")
        
        # Update CV status to failed
        try:
            db = next(get_db())
            cv = db.query(CV).filter(CV.id == cv_id).first()
            if cv:
                cv.parsed_data = cv.parsed_data or {}
                cv.parsed_data["processing_status"] = "failed"
                cv.parsed_data["processing_failed_at"] = datetime.now().isoformat()
                cv.parsed_data["processing_error"] = str(e)
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update CV status: {str(db_error)}")
        
        raise


@celery_app.task(bind=True, name='search_jobs')
def search_jobs(self, user_id: str, keywords: str, location: str = None, limit: int = 20):
    """Search for jobs using MCP service"""
    try:
        # Execute job search through MCP
        result = await mcp_service.execute_tool(
            "aggregate_jobs",
            {
                "keywords": keywords,
                "location": location,
                "sources": ["linkedin", "indeed", "glassdoor"],
                "limit": limit
            }
        )
        
        if not result.get("success"):
            raise ValueError(f"Job search failed: {result.get('error')}")
        
        jobs = result.get("data", {}).get("jobs", [])
        
        # Save jobs to database
        saved_jobs = []
        for job_data in jobs:
            saved_job = await _save_job_to_db(job_data)
            saved_jobs.append(saved_job)
        
        # Trigger matching for user's active CVs
        user_cvs = _get_user_active_cvs(user_id)
        for cv in user_cvs:
            trigger_job_matching.delay(cv.id, [job.id for job in saved_jobs])
        
        return {
            "status": "success",
            "user_id": user_id,
            "keywords": keywords,
            "jobs_found": len(jobs),
            "jobs_saved": len(saved_jobs)
        }
        
    except Exception as e:
        logger.error(f"Job search failed: {str(e)}")
        raise


@celery_app.task(bind=True, name='trigger_cv_matching')
def trigger_cv_matching(self, cv_id: str, user_id: str):
    """Trigger matching for CV against all relevant jobs"""
    try:
        # Get relevant jobs for matching
        relevant_jobs = _get_relevant_jobs_for_cv(cv_id)
        
        if not relevant_jobs:
            return {
                "status": "success",
                "cv_id": cv_id,
                "message": "No relevant jobs found for matching"
            }
        
        # Execute matching through LangGraph
        result = await job_agent_graph.run_workflow(
            user_id=user_id,
            task_type="matching",
            input_data={
                "cv_id": cv_id,
                "job_ids": [job.id for job in relevant_jobs]
            }
        )
        
        # Save matches to database
        matches = result.get("match_results", {}).get("matches", [])
        saved_matches = []
        
        for match_data in matches:
            saved_match = await _save_job_match(
                user_id=user_id,
                cv_id=cv_id,
                job_id=match_data["job_id"],
                match_score=match_data["match_score"],
                analysis=match_data["analysis"]
            )
            saved_matches.append(saved_match)
        
        return {
            "status": "success",
            "cv_id": cv_id,
            "jobs_matched": len(relevant_jobs),
            "matches_created": len(saved_matches),
            "execution_time": result.get("execution_time")
        }
        
    except Exception as e:
        logger.error(f"CV matching failed: {str(e)}")
        raise


@celery_app.task(bind=True, name='trigger_job_matching')
def trigger_job_matching(self, cv_id: str, job_ids: List[str]):
    """Trigger matching for CV against specific jobs"""
    try:
        # Get user ID from CV
        db = next(get_db())
        cv = db.query(CV).filter(CV.id == cv_id).first()
        if not cv:
            raise ValueError(f"CV not found: {cv_id}")
        
        user_id = cv.user_id
        
        # Execute matching through LangGraph
        result = await job_agent_graph.run_workflow(
            user_id=user_id,
            task_type="matching",
            input_data={
                "cv_id": cv_id,
                "job_ids": job_ids
            }
        )
        
        # Save matches to database
        matches = result.get("match_results", {}).get("matches", [])
        saved_matches = []
        
        for match_data in matches:
            saved_match = await _save_job_match(
                user_id=user_id,
                cv_id=cv_id,
                job_id=match_data["job_id"],
                match_score=match_data["match_score"],
                analysis=match_data["analysis"]
            )
            saved_matches.append(saved_match)
        
        return {
            "status": "success",
            "cv_id": cv_id,
            "jobs_matched": len(job_ids),
            "matches_created": len(saved_matches),
            "execution_time": result.get("execution_time")
        }
        
    except Exception as e:
        logger.error(f"Job matching failed: {str(e)}")
        raise


@celery_app.task(bind=True, name='generate_recommendations')
def generate_recommendations(self, user_id: str):
    """Generate skill and career recommendations for user"""
    try:
        # Get user's active CVs
        user_cvs = _get_user_active_cvs(user_id)
        if not user_cvs:
            return {
                "status": "success",
                "user_id": user_id,
                "message": "No active CVs found"
            }
        
        # Get user's job matches
        user_matches = _get_user_job_matches(user_id)
        
        # Generate recommendations through LangGraph
        result = await job_agent_graph.run_workflow(
            user_id=user_id,
            task_type="recommendations",
            input_data={
                "user_id": user_id,
                "cvs": [cv.id for cv in user_cvs],
                "matches": user_matches
            }
        )
        
        # Save recommendations to database
        recommendations = result.get("recommendations", [])
        saved_recommendations = []
        
        for rec_data in recommendations:
            saved_rec = await _save_skill_recommendation(
                user_id=user_id,
                skill_name=rec_data["skill"],
                priority=rec_data["priority"],
                reason=rec_data["reason"],
                resources=rec_data.get("resources", []),
                target_level=rec_data["target_level"]
            )
            saved_recommendations.append(saved_rec)
        
        return {
            "status": "success",
            "user_id": user_id,
            "recommendations_generated": len(saved_recommendations),
            "execution_time": result.get("execution_time")
        }
        
    except Exception as e:
        logger.error(f"Recommendation generation failed: {str(e)}")
        raise


# Periodic tasks
@celery_app.task(bind=True, name='cleanup_old_cvs')
def cleanup_old_cvs(self):
    """Clean up old and inactive CVs"""
    try:
        db = next(get_db())
        
        # Find CVs older than 90 days and inactive
        cutoff_date = datetime.now() - timedelta(days=90)
        old_cvs = db.query(CV).filter(
            CV.created_at < cutoff_date,
            CV.is_active == False
        ).all()
        
        deleted_count = 0
        for cv in old_cvs:
            try:
                # Delete file from disk
                if os.path.exists(cv.file_path):
                    os.remove(cv.file_path)
                
                db.delete(cv)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete CV {cv.id}: {str(e)}")
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old CVs")
        
        return {
            "status": "success",
            "deleted_cvs": deleted_count
        }
        
    except Exception as e:
        logger.error(f"CV cleanup failed: {str(e)}")
        raise


@celery_app.task(bind=True, name='update_job_listings')
def update_job_listings(self):
    """Update job listings from external sources"""
    try:
        # Search for popular keywords
        popular_keywords = [
            "software developer",
            "data scientist",
            "product manager",
            "designer",
            "marketing"
        ]
        
        total_jobs = 0
        
        for keyword in popular_keywords:
            result = await mcp_service.execute_tool(
                "aggregate_jobs",
                {
                    "keywords": keyword,
                    "limit": 50
                }
            )
            
            if result.get("success"):
                jobs = result.get("data", {}).get("jobs", [])
                for job_data in jobs:
                    await _save_job_to_db(job_data)
                total_jobs += len(jobs)
        
        logger.info(f"Updated {total_jobs} job listings")
        
        return {
            "status": "success",
            "total_jobs_updated": total_jobs
        }
        
    except Exception as e:
        logger.error(f"Job listings update failed: {str(e)}")
        raise


@celery_app.task(bind=True, name='generate_user_recommendations')
def generate_user_recommendations(self):
    """Generate recommendations for all active users"""
    try:
        db = next(get_db())
        
        # Get all active users
        active_users = db.query(User).filter(User.is_active == True).all()
        
        total_recommendations = 0
        
        for user in active_users:
            try:
                result = generate_recommendations.delay(user.id)
                total_recommendations += 1
            except Exception as e:
                logger.error(f"Failed to generate recommendations for user {user.id}: {str(e)}")
        
        logger.info(f"Triggered recommendation generation for {total_recommendations} users")
        
        return {
            "status": "success",
            "users_processed": total_recommendations
        }
        
    except Exception as e:
        logger.error(f"User recommendations generation failed: {str(e)}")
        raise


# Helper functions
async def _extract_cv_text(file_path: str, mime_type: str) -> str:
    """Extract text from CV file"""
    # Implementation similar to CV service
    # This would use PDF/DOCX parsing libraries
    return "Sample CV text"


async def _extract_and_save_skills(db: Session, cv_id: str, ai_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract and save skills from AI analysis"""
    # Implementation similar to CV service
    return []


def _get_user_active_cvs(user_id: str) -> List[CV]:
    """Get user's active CVs"""
    db = next(get_db())
    return db.query(CV).filter(CV.user_id == user_id, CV.is_active == True).all()


def _get_relevant_jobs_for_cv(cv_id: str) -> List[JobListing]:
    """Get relevant jobs for CV matching"""
    db = next(get_db())
    # Get recent active jobs
    return db.query(JobListing).filter(
        JobListing.is_active == True,
        JobListing.posted_at >= datetime.now() - timedelta(days=30)
    ).limit(50).all()


def _get_user_job_matches(user_id: str) -> List[JobMatch]:
    """Get user's job matches"""
    db = next(get_db())
    return db.query(JobMatch).filter(JobMatch.user_id == user_id).all()


async def _save_job_to_db(job_data: Dict[str, Any]) -> JobListing:
    """Save job to database"""
    db = next(get_db())
    
    # Check if job already exists
    existing_job = db.query(JobListing).filter(
        JobListing.external_id == job_data.get("id")
    ).first()
    
    if existing_job:
        return existing_job
    
    # Create new job
    job = JobListing(
        external_id=job_data.get("id"),
        title=job_data.get("title"),
        company=job_data.get("company"),
        location=job_data.get("location"),
        description=job_data.get("description"),
        requirements=job_data.get("requirements", ""),
        url=job_data.get("url"),
        source=job_data.get("source"),
        posted_at=datetime.fromisoformat(job_data.get("posted_at", datetime.now().isoformat())),
        is_active=True
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return job


async def _save_job_match(user_id: str, cv_id: str, job_id: str, match_score: float, analysis: Dict[str, Any]) -> JobMatch:
    """Save job match to database"""
    db = next(get_db())
    
    # Check if match already exists
    existing_match = db.query(JobMatch).filter(
        JobMatch.user_id == user_id,
        JobMatch.cv_id == cv_id,
        JobMatch.job_id == job_id
    ).first()
    
    if existing_match:
        # Update existing match
        existing_match.match_score = match_score
        existing_match.analysis = analysis
        existing_match.updated_at = datetime.now()
        db.commit()
        db.refresh(existing_match)
        return existing_match
    
    # Create new match
    match = JobMatch(
        user_id=user_id,
        cv_id=cv_id,
        job_id=job_id,
        match_score=match_score,
        analysis=analysis,
        status="pending"
    )
    
    db.add(match)
    db.commit()
    db.refresh(match)
    
    return match


async def _save_skill_recommendation(user_id: str, skill_name: str, priority: int, reason: str, resources: List[Dict[str, Any]], target_level: int) -> SkillRecommendation:
    """Save skill recommendation to database"""
    db = next(get_db())
    
    # Find or create skill
    from app.models.database import Skill
    skill = db.query(Skill).filter(Skill.name == skill_name.lower()).first()
    if not skill:
        skill = Skill(
            name=skill_name.lower(),
            category="Technical",
            description=f"Skill: {skill_name}"
        )
        db.add(skill)
        db.commit()
        db.refresh(skill)
    
    # Check if recommendation already exists
    existing_rec = db.query(SkillRecommendation).filter(
        SkillRecommendation.user_id == user_id,
        SkillRecommendation.skill_id == skill.id
    ).first()
    
    if existing_rec:
        # Update existing recommendation
        existing_rec.priority = priority
        existing_rec.reason = reason
        existing_rec.resources = resources
        existing_rec.target_level = target_level
        existing_rec.updated_at = datetime.now()
        db.commit()
        db.refresh(existing_rec)
        return existing_rec
    
    # Create new recommendation
    rec = SkillRecommendation(
        user_id=user_id,
        skill_id=skill.id,
        priority=priority,
        reason=reason,
        resources=resources,
        target_level=target_level,
        status="pending"
    )
    
    db.add(rec)
    db.commit()
    db.refresh(rec)
    
    return rec