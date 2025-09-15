from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

# Association table for many-to-many relationship between CVs and Skills
cv_skill_association = Table(
    'cv_skills',
    Base.metadata,
    Column('cv_id', String, ForeignKey('cvs.id'), primary_key=True),
    Column('skill_id', String, ForeignKey('skills.id'), primary_key=True),
    Column('level', Integer, default=1),  # 1-5 proficiency level
    Column('years', Integer, nullable=True)  # Years of experience
)

# Association table for many-to-many relationship between Jobs and Skills
job_skill_association = Table(
    'job_skills',
    Base.metadata,
    Column('job_id', String, ForeignKey('job_listings.id'), primary_key=True),
    Column('skill_id', String, ForeignKey('skills.id'), primary_key=True),
    Column('required', Boolean, default=True),
    Column('level', Integer, nullable=True)  # Required proficiency level
)


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    cvs = relationship("CV", back_populates="user")
    searches = relationship("JobSearch", back_populates="user")
    matches = relationship("JobMatch", back_populates="user")
    recommendations = relationship("SkillRecommendation", back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    title = Column(String, nullable=True)
    location = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    github = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    experience_years = Column(Integer, nullable=True)  # Years of experience
    salary_min = Column(Integer, nullable=True)  # Minimum salary expectation
    salary_max = Column(Integer, nullable=True)  # Maximum salary expectation
    currency = Column(String, default="USD")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")


class CV(Base):
    __tablename__ = "cvs"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True)  # Parsed CV data in JSON format
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cvs")
    skills = relationship("Skill", secondary=cv_skill_association, back_populates="cvs")
    matches = relationship("JobMatch", back_populates="cv")


class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=False)  # Technical, Soft, Language, etc.
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    cvs = relationship("CV", secondary=cv_skill_association, back_populates="skills")
    jobs = relationship("JobListing", secondary=job_skill_association, back_populates="skills")
    recommendations = relationship("SkillRecommendation", back_populates="skill")


class JobListing(Base):
    __tablename__ = "job_listings"
    
    id = Column(String, primary_key=True, index=True)
    external_id = Column(String, nullable=True)  # External job board ID
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    currency = Column(String, default="USD")
    job_type = Column(String, nullable=True)  # Full-time, Part-time, Contract, etc.
    experience_level = Column(String, nullable=True)  # Entry, Mid, Senior, etc.
    remote = Column(Boolean, default=False)
    url = Column(String, nullable=True)  # Original job posting URL
    source = Column(String, nullable=True)  # LinkedIn, Indeed, etc.
    posted_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    skills = relationship("Skill", secondary=job_skill_association, back_populates="jobs")
    matches = relationship("JobMatch", back_populates="job")


class JobSearch(Base):
    __tablename__ = "job_searches"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    keywords = Column(String, nullable=False)
    location = Column(String, nullable=True)
    job_type = Column(String, nullable=True)
    experience = Column(String, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    remote = Column(Boolean, default=False)
    results = Column(JSON, nullable=True)  # Search results
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="searches")


class JobMatch(Base):
    __tablename__ = "job_matches"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    cv_id = Column(String, ForeignKey("cvs.id"), nullable=False)
    job_id = Column(String, ForeignKey("job_listings.id"), nullable=False)
    match_score = Column(Float, nullable=False)  # 0-100 match percentage
    analysis = Column(JSON, nullable=True)  # Detailed analysis
    status = Column(String, default="pending")  # pending, reviewed, applied, rejected
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="matches")
    cv = relationship("CV", back_populates="matches")
    job = relationship("JobListing", back_populates="matches")
    
    # Ensure unique combination
    __table_args__ = (
        {'extend_existing': True}
    )


class SkillRecommendation(Base):
    __tablename__ = "skill_recommendations"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    skill_id = Column(String, ForeignKey("skills.id"), nullable=False)
    priority = Column(Integer, nullable=False)  # 1-5 priority level
    reason = Column(Text, nullable=False)  # Why this skill is recommended
    resources = Column(JSON, nullable=True)  # Learning resources
    target_level = Column(Integer, nullable=False)  # Target proficiency level
    status = Column(String, default="pending")  # pending, in_progress, completed
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    skill = relationship("Skill", back_populates="recommendations")
    
    # Ensure unique combination
    __table_args__ = (
        {'extend_existing': True}
    )


class AgentExecution(Base):
    __tablename__ = "agent_executions"
    
    id = Column(String, primary_key=True, index=True)
    agent_type = Column(String, nullable=False)  # cv_analysis, job_search, matching, recommendation
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    execution_time = Column(Float, nullable=True)  # Execution time in seconds
    status = Column(String, default="pending")  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")


class MCPToolExecution(Base):
    __tablename__ = "mcp_tool_executions"
    
    id = Column(String, primary_key=True, index=True)
    tool_name = Column(String, nullable=False)
    parameters = Column(JSON, nullable=False)
    result = Column(JSON, nullable=True)
    execution_time = Column(Float, nullable=True)
    status = Column(String, default="pending")  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)
    source = Column(String, nullable=True)  # External source
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    user = relationship("User")