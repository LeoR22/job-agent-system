import json
from typing import Dict, Any, List, Optional
from app.core.config import settings


class AIService:
    """Service for AI-powered operations"""
    
    def __init__(self):
        self.openai_api_key = settings.openai_api_key
        self.openai_org_id = settings.openai_org_id
    
    async def analyze_cv(self, text: str) -> Dict[str, Any]:
        """Analyze CV text using AI"""
        try:
            prompt = f"""
            Analiza el siguiente texto de un currículum vitae y extrae información estructurada en formato JSON:
            
            Texto del CV:
            {text}
            
            Por favor, extrae la siguiente información y devuélvela en formato JSON válido:
            
            {{
                "profile": {{
                    "name": "nombre completo",
                    "title": "título profesional",
                    "location": "ubicación",
                    "experience_years": número de años de experiencia,
                    "summary": "resumen profesional breve",
                    "contact": {{
                        "email": "email",
                        "phone": "teléfono",
                        "linkedin": "perfil de linkedin",
                        "github": "perfil de github"
                    }}
                }},
                "skills": [
                    {{
                        "name": "nombre de la habilidad",
                        "level": nivel de 1 a 5 (1=básico, 5=experto),
                        "years": años de experiencia,
                        "category": "categoría (Technical, Soft, Language, Tool, Framework)"
                    }}
                ],
                "experience": [
                    {{
                        "title": "puesto",
                        "company": "empresa",
                        "location": "ubicación",
                        "duration": "duración",
                        "description": "descripción del puesto",
                        "achievements": ["logro 1", "logro 2"]
                    }}
                ],
                "education": [
                    {{
                        "degree": "título",
                        "institution": "institución",
                        "location": "ubicación",
                        "year": año,
                        "gpa": "promedio si está disponible"
                    }}
                ],
                "certifications": [
                    {{
                        "name": "nombre de la certificación",
                        "issuer": "emisor",
                        "date": "fecha",
                        "expiry": "fecha de expiración si aplica"
                    }}
                ],
                "languages": [
                    {{
                        "name": "idioma",
                        "level": "nivel (Básico, Intermedio, Avanzado, Nativo)"
                    }}
                ],
                "analysis": {{
                    "experience_level": "nivel de experiencia general (Entry, Mid, Senior, Expert)",
                    "strengths": ["fortaleza 1", "fortaleza 2"],
                    "improvement_areas": ["área de mejora 1", "área de mejora 2"],
                    "market_readiness_score": puntuación de 1 a 100,
                    "recommended_roles": ["rol recomendado 1", "rol recomendado 2"],
                    "career_trajectory": "trayectoria profesional sugerida"
                }}
            }}
            
            Por favor, asegúrate de que el JSON sea válido y completo. Si no encuentras información para algún campo, usa null o array vacío según corresponda.
            """
            
            response = await self._call_openai(prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            print(f"Error analyzing CV: {str(e)}")
            return self._get_fallback_cv_analysis()
    
    async def analyze_job_description(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze job description using AI"""
        try:
            prompt = f"""
            Analiza la siguiente descripción de puesto de trabajo y extrae información estructurada en formato JSON:
            
            Título: {job_data.get('title', '')}
            Empresa: {job_data.get('company', '')}
            Ubicación: {job_data.get('location', '')}
            Descripción: {job_data.get('description', '')}
            Requisitos: {job_data.get('requirements', '')}
            
            Por favor, extrae la siguiente información y devuélvela en formato JSON válido:
            
            {{
                "title": "título del puesto normalizado",
                "company": "nombre de la empresa",
                "location": "ubicación",
                "remote": booleano si es remoto,
                "job_type": "tipo de trabajo (Full-time, Part-time, Contract, Internship)",
                "experience_level": "nivel de experiencia requerido (Entry, Mid, Senior, Expert)",
                "salary_range": {{
                    "min": salario mínimo si está disponible,
                    "max": salario máximo si está disponible,
                    "currency": "moneda"
                }},
                "required_skills": [
                    {{
                        "name": "nombre de la habilidad",
                        "level": nivel requerido de 1 a 5,
                        "importance": "importancia (High, Medium, Low)"
                    }}
                ],
                "preferred_skills": [
                    {{
                        "name": "nombre de la habilidad",
                        "level": nivel preferido de 1 a 5,
                        "importance": "importancia (High, Medium, Low)"
                    }}
                ],
                "responsibilities": ["responsabilidad 1", "responsabilidad 2"],
                "qualifications": ["cualificación 1", "cualificación 2"],
                "benefits": ["beneficio 1", "beneficio 2"],
                "company_info": {{
                    "size": "tamaño de la empresa si se menciona",
                    "industry": "industria",
                    "culture": "descripción de la cultura si se menciona"
                }},
                "application_process": {{
                    "method": "método de aplicación",
                    "deadline": "fecha límite si está disponible"
                }},
                "analysis": {{
                    "difficulty_level": "dificultad para llenar el puesto (Easy, Medium, Hard, Very Hard)",
                    "market_demand": "demanda en el mercado (Low, Medium, High)",
                    "growth_potential": "potencial de crecimiento (Low, Medium, High)",
                    "required_experience_years": años de experiencia requeridos,
                    "key_technologies": ["tecnología clave 1", "tecnología clave 2"],
                    "soft_skills_required": ["habilidad blanda 1", "habilidad blanda 2"]
                }}
            }}
            
            Por favor, asegúrate de que el JSON sea válido y completo. Si no encuentras información para algún campo, usa null o array vacío según corresponda.
            """
            
            response = await self._call_openai(prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            print(f"Error analyzing job description: {str(e)}")
            return self._get_fallback_job_analysis()
    
    async def calculate_match_score(self, cv_analysis: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate match score between CV and job using AI"""
        try:
            prompt = f"""
            Analiza el siguiente CV y descripción de puesto para calcular un score de compatibilidad:
            
            CV Analysis:
            {json.dumps(cv_analysis, indent=2, ensure_ascii=False)}
            
            Job Analysis:
            {json.dumps(job_analysis, indent=2, ensure_ascii=False)}
            
            Por favor, calcula la compatibilidad y devuelve un análisis detallado en formato JSON:
            
            {{
                "overall_score": puntuación general de 0 a 100,
                "skill_match_score": puntuación de habilidades de 0 a 100,
                "experience_match_score": puntuación de experiencia de 0 a 100,
                "education_match_score": puntuación de educación de 0 a 100,
                "soft_skills_match_score": puntuación de habilidades blandas de 0 a 100,
                "skill_analysis": [
                    {{
                        "skill": "nombre de la habilidad",
                        "cv_level": nivel en CV de 1 a 5,
                        "required_level": nivel requerido de 1 a 5,
                        "match_score": puntuación de 0 a 100 para esta habilidad,
                        "gap": "diferencia (Exact Match, Close Match, Gap, Significant Gap)"
                    }}
                ],
                "missing_skills": ["habilidad faltante 1", "habilidad faltante 2"],
                "strengths": ["fortaleza 1", "fortaleza 2"],
                "weaknesses": ["debilidad 1", "debilidad 2"],
                "recommendations": [
                    {{
                        "type": "tipo de recomendación (Skill Development, Experience, Education)",
                        "priority": "prioridad (High, Medium, Low)",
                        "description": "descripción detallada",
                        "action_items": ["acción 1", "acción 2"]
                    }}
                ],
                "fit_assessment": {{
                    "level": "nivel de ajuste (Excellent, Good, Fair, Poor)",
                    "confidence": "confianza en el análisis (High, Medium, Low)",
                    "reasoning": "razonamiento detallado del assessment",
                    "interview_readiness": "preparación para entrevista (Ready, Needs Preparation, Not Ready)"
                }},
                "career_progression": {{
                    "current_level": "nivel actual del candidato",
                    "target_level": "nivel del puesto",
                    "feasibility": "factibilidad del salto (High, Medium, Low)",
                    "timeline": "timeline estimado para alcanzar el nivel"
                }}
            }}
            
            Por favor, sé objetivo y detallado en tu análisis. Considera no solo las habilidades técnicas sino también la experiencia, educación y potencial de crecimiento.
            """
            
            response = await self._call_openai(prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            print(f"Error calculating match score: {str(e)}")
            return self._get_fallback_match_analysis()
    
    async def generate_skill_recommendations(self, user_profile: Dict[str, Any], job_matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate skill recommendations based on profile and job matches"""
        try:
            prompt = f"""
            Basado en el siguiente perfil de usuario y análisis de matches con ofertas de trabajo, genera recomendaciones de formación personalizadas:
            
            User Profile:
            {json.dumps(user_profile, indent=2, ensure_ascii=False)}
            
            Job Matches Analysis:
            {json.dumps(job_matches, indent=2, ensure_ascii=False)}
            
            Por favor, genera recomendaciones de formación en formato JSON array:
            
            [
                {{
                    "skill": "nombre de la habilidad a aprender",
                    "category": "categoría (Technical, Soft, Language, Tool)",
                    "priority": "prioridad (1-5, donde 5 es la más alta)",
                    "reason": "razón detallada por qué esta habilidad es importante",
                    "current_level": "nivel actual del usuario (1-5)",
                    "target_level": "nivel objetivo (1-5)",
                    "time_to_achieve": "tiempo estimado para lograr el nivel objetivo",
                    "difficulty": "dificultad (Easy, Medium, Hard)",
                    "market_demand": "demanda en el mercado (Low, Medium, High)",
                    "learning_resources": [
                        {{
                            "type": "tipo de recurso (Course, Book, Tutorial, Certification)",
                            "title": "título del recurso",
                            "provider": "proveedor (Udemy, Coursera, etc.)",
                            "duration": "duración estimada",
                            "cost": "costo aproximado",
                            "url": "URL si está disponible"
                        }}
                    ],
                    "career_impact": {{
                        "description": "impacto en la carrera",
                        "job_opportunities": "oportunidades de trabajo adicionales",
                        "salary_increase_potential": "potencial de aumento de salario"
                    }}
                }}
            ]
            
            Genera máximo 8 recomendaciones, enfocadas en las habilidades con mayor impacto y que sean más relevantes para el perfil del usuario.
            """
            
            response = await self._call_openai(prompt)
            recommendations = self._parse_json_response(response)
            
            return recommendations if isinstance(recommendations, list) else []
            
        except Exception as e:
            print(f"Error generating skill recommendations: {str(e)}")
            return self._get_fallback_recommendations()
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            # Import here to avoid dependency issues if OpenAI is not available
            from openai import OpenAI
            
            client = OpenAI(
                api_key=self.openai_api_key,
                organization=self.openai_org_id
            )
            
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en análisis de currículums, reclutamiento y desarrollo de carrera. Proporciona análisis detallados, objetivos y prácticos."
                    },
                    {
                        "role": "user",
                        content: prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error calling OpenAI: {str(e)}")
            raise e
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from AI"""
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[start:end]
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Error parsing JSON response: {str(e)}")
            print(f"Response: {response}")
            raise e
    
    def _get_fallback_cv_analysis(self) -> Dict[str, Any]:
        """Fallback CV analysis when AI fails"""
        return {
            "profile": {
                "name": "Unknown",
                "title": "Professional",
                "location": "Unknown",
                "experience_years": 0,
                "summary": "No summary available"
            },
            "skills": [
                {"name": "Communication", "level": 3, "years": 2, "category": "Soft"}
            ],
            "experience": [],
            "education": [],
            "certifications": [],
            "languages": [],
            "analysis": {
                "experience_level": "Entry",
                "strengths": ["Communication"],
                "improvement_areas": ["Technical skills"],
                "market_readiness_score": 30,
                "recommended_roles": ["Junior Professional"],
                "career_trajectory": "Early career development"
            }
        }
    
    def _get_fallback_job_analysis(self) -> Dict[str, Any]:
        """Fallback job analysis when AI fails"""
        return {
            "title": "Professional Position",
            "company": "Company",
            "location": "Location",
            "remote": False,
            "job_type": "Full-time",
            "experience_level": "Mid",
            "required_skills": [
                {"name": "Communication", "level": 3, "importance": "High"}
            ],
            "preferred_skills": [],
            "responsibilities": ["Professional responsibilities"],
            "qualifications": ["Professional qualifications"],
            "analysis": {
                "difficulty_level": "Medium",
                "market_demand": "Medium",
                "growth_potential": "Medium"
            }
        }
    
    def _get_fallback_match_analysis(self) -> Dict[str, Any]:
        """Fallback match analysis when AI fails"""
        return {
            "overall_score": 50,
            "skill_match_score": 50,
            "experience_match_score": 50,
            "skill_analysis": [],
            "missing_skills": [],
            "strengths": ["Professional attitude"],
            "weaknesses": ["Specific technical skills"],
            "recommendations": [],
            "fit_assessment": {
                "level": "Fair",
                "confidence": "Medium",
                "reasoning": "Limited analysis available"
            }
        }
    
    def _get_fallback_recommendations(self) -> List[Dict[str, Any]]:
        """Fallback recommendations when AI fails"""
        return [
            {
                "skill": "Communication",
                "category": "Soft",
                "priority": 3,
                "reason": "Important for professional development",
                "current_level": 3,
                "target_level": 4,
                "time_to_achieve": "3-6 months",
                "difficulty": "Medium"
            }
        ]