from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from pathlib import Path
import aiofiles

from app.core.database import get_db
from app.core.config import settings
from app.models.schemas import (
    CVResponse, CVWithSkills, ApiResponse, PaginatedResponse,
    CVSkillCreate, CVSkillResponse
)
from app.services.cv import CVService
from app.services.auth import get_current_active_user
from app.models.database import User

router = APIRouter()
cv_service = CVService()


@router.post("/upload", response_model=ApiResponse)
async def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and analyze CV"""
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in [".pdf", ".doc", ".docx"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only PDF, DOC, and DOCX files are allowed."
            )
        
        # Validate file size
        if file.size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {settings.max_file_size / (1024*1024):.1f}MB"
            )
        
        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Process CV
        cv_result = await cv_service.process_cv(
            db=db,
            user_id=current_user.id,
            file_path=str(file_path),
            filename=file.filename,
            file_size=file.size,
            mime_type=file.content_type or "application/octet-stream"
        )
        
        return ApiResponse(
            success=True,
            message="CV uploaded and analyzed successfully",
            data=cv_result
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CV upload failed: {str(e)}"
        )


@router.get("/", response_model=ApiResponse)
async def get_user_cvs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """Get user's CVs"""
    try:
        cvs = cv_service.get_user_cvs(db, current_user.id, skip, limit)
        total = cv_service.count_user_cvs(db, current_user.id)
        
        cv_responses = [CVWithSkills.from_orm(cv) for cv in cvs]
        
        return ApiResponse(
            success=True,
            message="CVs retrieved successfully",
            data=cv_responses,
            pagination={
                "skip": skip,
                "limit": limit,
                "total": total
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve CVs: {str(e)}"
        )


@router.get("/{cv_id}", response_model=ApiResponse)
async def get_cv(
    cv_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific CV"""
    try:
        cv = cv_service.get_cv(db, cv_id, current_user.id)
        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        return ApiResponse(
            success=True,
            message="CV retrieved successfully",
            data=CVWithSkills.from_orm(cv)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve CV: {str(e)}"
        )


@router.put("/{cv_id}/activate", response_model=ApiResponse)
async def activate_cv(
    cv_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Activate CV for job matching"""
    try:
        cv = cv_service.activate_cv(db, cv_id, current_user.id)
        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        return ApiResponse(
            success=True,
            message="CV activated successfully",
            data=CVResponse.from_orm(cv)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate CV: {str(e)}"
        )


@router.put("/{cv_id}/deactivate", response_model=ApiResponse)
async def deactivate_cv(
    cv_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deactivate CV"""
    try:
        cv = cv_service.deactivate_cv(db, cv_id, current_user.id)
        if not cv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        return ApiResponse(
            success=True,
            message="CV deactivated successfully",
            data=CVResponse.from_orm(cv)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate CV: {str(e)}"
        )


@router.delete("/{cv_id}", response_model=ApiResponse)
async def delete_cv(
    cv_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete CV"""
    try:
        success = cv_service.delete_cv(db, cv_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        return ApiResponse(
            success=True,
            message="CV deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete CV: {str(e)}"
        )


@router.post("/{cv_id}/skills", response_model=ApiResponse)
async def add_cv_skill(
    cv_id: str,
    skill_data: CVSkillCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add skill to CV"""
    try:
        cv_skill = cv_service.add_cv_skill(db, cv_id, current_user.id, skill_data)
        if not cv_skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CV not found"
            )
        
        return ApiResponse(
            success=True,
            message="Skill added to CV successfully",
            data=CVSkillResponse.from_orm(cv_skill)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add skill to CV: {str(e)}"
        )


@router.get("/{cv_id}/skills", response_model=ApiResponse)
async def get_cv_skills(
    cv_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get CV skills"""
    try:
        skills = cv_service.get_cv_skills(db, cv_id, current_user.id)
        return ApiResponse(
            success=True,
            message="CV skills retrieved successfully",
            data=skills
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve CV skills: {str(e)}"
        )