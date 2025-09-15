"""
LangGraph Agents for Job Agent System

This module contains the implementation of LangGraph agents for various tasks:
- CV Analysis Agent
- Job Search Agent  
- Matching Agent
- Recommendation Agent
- MCP Integration Agent
"""

from typing import Dict, Any, List, Optional, TypedDict
import asyncio
import json
from datetime import datetime
from langgraph.graph import Graph, END, START
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.services.ai import AIService
from app.models.database import User, CV, JobListing, Skill
from app.services.mcp import MCPService


class AgentState(TypedDict):
    """State for LangGraph agents"""
    user_id: str
    task_type: str
    input_data: Dict[str, Any]
    cv_data: Optional[Dict[str, Any]]
    job_data: Optional[Dict[str, Any]]
    analysis_results: Optional[Dict[str, Any]]
    match_results: Optional[Dict[str, Any]]
    recommendations: Optional[List[Dict[str, Any]]]
    mcp_results: Optional[Dict[str, Any]]
    final_output: Optional[Dict[str, Any]]
    error: Optional[str]
    execution_time: Optional[float]


class JobAgentGraph:
    """Main LangGraph orchestration for job agent system"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.mcp_service = MCPService()
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            organization=settings.openai_org_id,
            model="gpt-4",
            temperature=0.3
        )
        
        # Initialize the graph
        self.graph = self._build_graph()
        
    def _build_graph(self) -> Graph:
        """Build the LangGraph workflow"""
        workflow = Graph()
        
        # Add nodes
        workflow.add_node("input_validation", self._validate_input)
        workflow.add_node("cv_analysis", self._analyze_cv)
        workflow.add_node("job_search", self._search_jobs)
        workflow.add_node("job_analysis", self._analyze_jobs)
        workflow.add_node("matching", self._calculate_matches)
        workflow.add_node("recommendation_generation", self._generate_recommendations)
        workflow.add_node("mcp_integration", self._integrate_mcp)
        workflow.add_node("output_formatting", self._format_output)
        workflow.add_node("error_handling", self._handle_error)
        
        # Add edges
        workflow.add_edge(START, "input_validation")
        
        # Conditional routing based on task type
        workflow.add_conditional_edges(
            "input_validation",
            self._route_by_task_type,
            {
                "cv_analysis": "cv_analysis",
                "job_search": "job_search",
                "matching": "matching",
                "recommendations": "recommendation_generation",
                "mcp_search": "mcp_integration",
                "error": "error_handling"
            }
        )
        
        # CV Analysis flow
        workflow.add_edge("cv_analysis", "output_formatting")
        
        # Job Search flow
        workflow.add_edge("job_search", "job_analysis")
        workflow.add_edge("job_analysis", "output_formatting")
        
        # Matching flow
        workflow.add_edge("matching", "recommendation_generation")
        workflow.add_edge("recommendation_generation", "output_formatting")
        
        # MCP Integration flow
        workflow.add_edge("mcp_integration", "output_formatting")
        
        # Recommendation flow
        workflow.add_edge("recommendation_generation", "output_formatting")
        
        # Final edges
        workflow.add_edge("output_formatting", END)
        workflow.add_edge("error_handling", END)
        
        return workflow.compile()
    
    async def run_workflow(self, user_id: str, task_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the LangGraph workflow"""
        start_time = datetime.now()
        
        try:
            # Initialize state
            initial_state: AgentState = {
                "user_id": user_id,
                "task_type": task_type,
                "input_data": input_data,
                "cv_data": None,
                "job_data": None,
                "analysis_results": None,
                "match_results": None,
                "recommendations": None,
                "mcp_results": None,
                "final_output": None,
                "error": None,
                "execution_time": None
            }
            
            # Execute the graph
            result = await self.graph.ainvoke(initial_state)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            result["execution_time"] = execution_time
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "task_type": task_type,
                "user_id": user_id
            }
    
    async def _validate_input(self, state: AgentState) -> AgentState:
        """Validate input data and determine task type"""
        try:
            task_type = state["task_type"]
            input_data = state["input_data"]
            
            # Validate based on task type
            if task_type == "cv_analysis":
                if "cv_id" not in input_data:
                    raise ValueError("CV ID is required for CV analysis")
                    
            elif task_type == "job_search":
                if "keywords" not in input_data:
                    raise ValueError("Keywords are required for job search")
                    
            elif task_type == "matching":
                if "cv_id" not in input_data or "job_ids" not in input_data:
                    raise ValueError("CV ID and Job IDs are required for matching")
                    
            elif task_type == "recommendations":
                if "user_id" not in input_data:
                    raise ValueError("User ID is required for recommendations")
                    
            elif task_type == "mcp_search":
                if "tool_name" not in input_data or "parameters" not in input_data:
                    raise ValueError("Tool name and parameters are required for MCP search")
            
            return state
            
        except Exception as e:
            state["error"] = str(e)
            return state
    
    def _route_by_task_type(self, state: AgentState) -> str:
        """Route to appropriate node based on task type"""
        if state.get("error"):
            return "error"
        
        task_type = state["task_type"]
        
        if task_type == "cv_analysis":
            return "cv_analysis"
        elif task_type == "job_search":
            return "job_search"
        elif task_type == "matching":
            return "matching"
        elif task_type == "recommendations":
            return "recommendation_generation"
        elif task_type == "mcp_search":
            return "mcp_integration"
        else:
            return "error"
    
    async def _analyze_cv(self, state: AgentState) -> AgentState:
        """Analyze CV using AI"""
        try:
            cv_id = state["input_data"]["cv_id"]
            
            # Get CV from database (in real implementation)
            # For now, use mock data
            cv_text = "Sample CV text for analysis..."
            
            # Analyze CV with AI
            analysis = await self.ai_service.analyze_cv(cv_text)
            
            state["cv_data"] = analysis
            state["analysis_results"] = {
                "cv_analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            return state
            
        except Exception as e:
            state["error"] = f"CV analysis failed: {str(e)}"
            return state
    
    async def _search_jobs(self, state: AgentState) -> AgentState:
        """Search for jobs using MCP and internal database"""
        try:
            keywords = state["input_data"]["keywords"]
            location = state["input_data"].get("location")
            
            # Search using MCP service
            mcp_result = await self.mcp_service.execute_tool(
                "aggregate_jobs",
                {
                    "keywords": keywords,
                    "location": location,
                    "sources": ["linkedin", "indeed", "glassdoor"],
                    "limit": 20
                }
            )
            
            state["job_data"] = mcp_result.get("data", {}).get("jobs", [])
            state["mcp_results"] = mcp_result
            
            return state
            
        except Exception as e:
            state["error"] = f"Job search failed: {str(e)}"
            return state
    
    async def _analyze_jobs(self, state: AgentState) -> AgentState:
        """Analyze job descriptions"""
        try:
            jobs = state["job_data"]
            
            analyzed_jobs = []
            
            for job in jobs:
                # Analyze each job with AI
                job_analysis = await self.ai_service.analyze_job_description(job)
                analyzed_jobs.append({
                    **job,
                    "analysis": job_analysis
                })
            
            state["job_data"] = analyzed_jobs
            state["analysis_results"] = {
                "job_analysis": analyzed_jobs,
                "timestamp": datetime.now().isoformat()
            }
            
            return state
            
        except Exception as e:
            state["error"] = f"Job analysis failed: {str(e)}"
            return state
    
    async def _calculate_matches(self, state: AgentState) -> AgentState:
        """Calculate matches between CV and jobs"""
        try:
            cv_id = state["input_data"]["cv_id"]
            job_ids = state["input_data"]["job_ids"]
            
            # Get CV analysis (mock for now)
            cv_analysis = state.get("cv_data") or {
                "skills": [{"name": "JavaScript", "level": 4}],
                "experience": {"experience_years": 5}
            }
            
            # Get job analyses (mock for now)
            job_analyses = state.get("job_data") or []
            
            matches = []
            
            for job in job_analyses:
                # Calculate match score
                match_result = await self.ai_service.calculate_match_score(
                    cv_analysis, 
                    job.get("analysis", {})
                )
                
                matches.append({
                    "job_id": job.get("id"),
                    "match_score": match_result.get("overall_score", 0),
                    "analysis": match_result
                })
            
            # Sort by match score
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            
            state["match_results"] = {
                "matches": matches,
                "cv_id": cv_id,
                "job_ids": job_ids,
                "timestamp": datetime.now().isoformat()
            }
            
            return state
            
        except Exception as e:
            state["error"] = f"Matching calculation failed: {str(e)}"
            return state
    
    async def _generate_recommendations(self, state: AgentState) -> AgentState:
        """Generate skill and career recommendations"""
        try:
            user_id = state["user_id"]
            
            # Get user profile and matches (mock for now)
            user_profile = {
                "skills": [{"name": "JavaScript", "level": 4}],
                "experience": {"experience_years": 5}
            }
            
            job_matches = state.get("match_results", {}).get("matches", [])
            
            # Generate recommendations
            recommendations = await self.ai_service.generate_skill_recommendations(
                user_profile,
                job_matches
            )
            
            state["recommendations"] = recommendations
            
            return state
            
        except Exception as e:
            state["error"] = f"Recommendation generation failed: {str(e)}"
            return state
    
    async def _integrate_mcp(self, state: AgentState) -> AgentState:
        """Integrate with MCP tools"""
        try:
            tool_name = state["input_data"]["tool_name"]
            parameters = state["input_data"]["parameters"]
            
            # Execute MCP tool
            result = await self.mcp_service.execute_tool(tool_name, parameters)
            
            state["mcp_results"] = result
            
            return state
            
        except Exception as e:
            state["error"] = f"MCP integration failed: {str(e)}"
            return state
    
    async def _format_output(self, state: AgentState) -> AgentState:
        """Format the final output"""
        try:
            task_type = state["task_type"]
            
            output = {
                "task_type": task_type,
                "user_id": state["user_id"],
                "timestamp": datetime.now().isoformat(),
                "execution_time": state.get("execution_time"),
                "status": "completed" if not state.get("error") else "failed"
            }
            
            # Add task-specific results
            if task_type == "cv_analysis":
                output["cv_analysis"] = state.get("cv_data")
                output["analysis"] = state.get("analysis_results")
                
            elif task_type == "job_search":
                output["jobs"] = state.get("job_data")
                output["search_results"] = state.get("mcp_results")
                
            elif task_type == "matching":
                output["matches"] = state.get("match_results")
                
            elif task_type == "recommendations":
                output["recommendations"] = state.get("recommendations")
                
            elif task_type == "mcp_search":
                output["mcp_results"] = state.get("mcp_results")
            
            if state.get("error"):
                output["error"] = state["error"]
            
            state["final_output"] = output
            
            return state
            
        except Exception as e:
            state["error"] = f"Output formatting failed: {str(e)}"
            return state
    
    async def _handle_error(self, state: AgentState) -> AgentState:
        """Handle errors"""
        error = state.get("error", "Unknown error")
        
        state["final_output"] = {
            "task_type": state["task_type"],
            "user_id": state["user_id"],
            "timestamp": datetime.now().isoformat(),
            "execution_time": state.get("execution_time"),
            "status": "failed",
            "error": error
        }
        
        return state


# Global instance
job_agent_graph = JobAgentGraph()