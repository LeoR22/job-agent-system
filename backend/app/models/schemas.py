from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class JobStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    APPLIED = "applied"
    REJECTED = "rejected"


class RecommendationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class MCPStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileBase(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    currency: str = "USD"


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileResponse(UserProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# CV schemas
class CVBase(BaseModel):
    file_name: str
    extracted_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None


class CVCreate(CVBase):
    pass


class CVResponse(CVBase):
    id: str
    user_id: str
    file_path: str
    file_size: int
    mime_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CVWithSkills(CVResponse):
    skills: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True


# Skill schemas
class SkillBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class CVSkillBase(BaseModel):
    skill_id: str
    level: int = Field(..., ge=1, le=5)
    years: Optional[int] = Field(None, ge=0)


class CVSkillCreate(CVSkillBase):
    pass


class CVSkillResponse(CVSkillBase):
    id: str
    cv_id: str
    skill: SkillResponse
    
    class Config:
        from_attributes = True


# Job schemas
class JobListingBase(BaseModel):
    title: str
    company: str
    location: str
    description: str
    requirements: Optional[str] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    currency: str = "USD"
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    remote: bool = False
    url: Optional[str] = None
    source: Optional[str] = None


class JobListingCreate(JobListingBase):
    external_id: Optional[str] = None


class JobListingResponse(JobListingBase):
    id: str
    external_id: Optional[str]
    posted_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobSkillBase(BaseModel):
    skill_id: str
    required: bool = True
    level: Optional[int] = Field(None, ge=1, le=5)


class JobSkillCreate(JobSkillBase):
    pass


class JobSkillResponse(JobSkillBase):
    id: str
    job_id: str
    skill: SkillResponse
    
    class Config:
        from_attributes = True


# Job Search schemas
class JobSearchBase(BaseModel):
    keywords: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience: Optional[str] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    remote: bool = False


class JobSearchCreate(JobSearchBase):
    pass


class JobSearchResponse(JobSearchBase):
    id: str
    user_id: str
    results: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Job Match schemas
class JobMatchBase(BaseModel):
    match_score: float = Field(..., ge=0.0, le=100.0)
    analysis: Optional[Dict[str, Any]] = None
    status: JobStatus = JobStatus.PENDING
    notes: Optional[str] = None


class JobMatchCreate(JobMatchBase):
    cv_id: str
    job_id: str


class JobMatchResponse(JobMatchBase):
    id: str
    user_id: str
    cv_id: str
    job_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobMatchWithDetails(JobMatchResponse):
    cv: CVWithSkills
    job: JobListingResponse
    
    class Config:
        from_attributes = True


# Skill Recommendation schemas
class SkillRecommendationBase(BaseModel):
    priority: int = Field(..., ge=1, le=5)
    reason: str
    resources: Optional[Dict[str, Any]] = None
    target_level: int = Field(..., ge=1, le=5)
    status: RecommendationStatus = RecommendationStatus.PENDING


class SkillRecommendationCreate(SkillRecommendationBase):
    skill_id: str


class SkillRecommendationResponse(SkillRecommendationBase):
    id: str
    user_id: str
    skill_id: str
    created_at: datetime
    updated_at: datetime
    skill: SkillResponse
    
    class Config:
        from_attributes = True


# Agent schemas
class AgentExecutionBase(BaseModel):
    agent_type: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = Field(None, ge=0.0)
    status: AgentStatus = AgentStatus.PENDING
    error_message: Optional[str] = None


class AgentExecutionCreate(AgentExecutionBase):
    user_id: Optional[str] = None


class AgentExecutionResponse(AgentExecutionBase):
    id: str
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# MCP schemas
class MCPToolExecutionBase(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = Field(None, ge=0.0)
    status: MCPStatus = MCPStatus.PENDING
    error_message: Optional[str] = None
    source: Optional[str] = None


class MCPToolExecutionCreate(MCPToolExecutionBase):
    user_id: Optional[str] = None


class MCPToolExecutionResponse(MCPToolExecutionBase):
    id: str
    user_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(UserCreate):
    pass


# Response schemas
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: float


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None


class PaginatedResponse(BaseModel):
    success: bool
    message: str
    data: List[Any]
    pagination: Dict[str, Any]
    total: int