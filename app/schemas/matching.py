"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict
from enum import Enum


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase"""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class JobType(str, Enum):
    """Job type enumeration"""
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERNSHIP = "INTERNSHIP"


class EducationSchema(BaseModel):
    """Education information"""
    degree: str = Field(..., description="Título obtenido")
    institution: str = Field(..., description="Institución educativa")
    field: Optional[str] = Field(None, description="Campo de estudio")
    start_year: Optional[int] = Field(None, description="Año de inicio")
    end_year: Optional[int] = Field(None, description="Año de finalización")


class ExperienceSchema(BaseModel):
    """Work experience information"""
    company: str = Field(..., description="Nombre de la empresa")
    position: str = Field(..., description="Cargo/Posición")
    description: Optional[str] = Field(None, description="Descripción del rol")
    start_date: Optional[str] = Field(None, description="Fecha de inicio")
    end_date: Optional[str] = Field(None, description="Fecha de finalización (None si es actual)")
    years: Optional[float] = Field(None, description="Años de experiencia en este rol")


class CandidateSchema(BaseModel):
    """Candidate information for matching"""
    id: str = Field(..., description="ID único del candidato")
    name: str = Field(..., description="Nombre completo del candidato")
    skills: List[str] = Field(default_factory=list, description="Lista de habilidades")
    experience_years: float = Field(0, ge=0, description="Años totales de experiencia")
    experience: List[ExperienceSchema] = Field(default_factory=list, description="Experiencia laboral detallada")
    education: List[EducationSchema] = Field(default_factory=list, description="Educación")
    languages: List[str] = Field(default_factory=list, description="Idiomas")
    summary: Optional[str] = Field(None, description="Resumen profesional")
    location: Optional[str] = Field(None, description="Ubicación del candidato")
    
    @field_validator('skills', mode='before')
    @classmethod
    def normalize_skills(cls, v):
        """Normalize skills to lowercase"""
        if isinstance(v, list):
            return [skill.strip().lower() if isinstance(skill, str) else skill for skill in v]
        return v


class JobSchema(BaseModel):
    """Job posting information"""
    id: str = Field(..., description="ID único del trabajo")
    title: str = Field(..., description="Título del puesto")
    description: str = Field(..., description="Descripción completa del trabajo")
    skills: List[str] = Field(default_factory=list, description="Habilidades requeridas")
    requirements: List[str] = Field(default_factory=list, description="Requisitos del puesto")
    location: Optional[str] = Field(None, description="Ubicación del trabajo")
    type: JobType = Field(JobType.FULL_TIME, description="Tipo de contrato")
    salary_min: Optional[int] = Field(None, description="Salario mínimo")
    salary_max: Optional[int] = Field(None, description="Salario máximo")
    min_experience_years: Optional[float] = Field(None, description="Años mínimos de experiencia")
    
    @field_validator('skills', mode='before')
    @classmethod
    def normalize_skills(cls, v):
        """Normalize skills to lowercase"""
        if isinstance(v, list):
            return [skill.strip().lower() if isinstance(skill, str) else skill for skill in v]
        return v


class MatchBreakdown(BaseModel):
    """Detailed breakdown of match scores"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    skills_match: float = Field(..., ge=0, le=1, description="Score de coincidencia de habilidades")
    experience_match: float = Field(..., ge=0, le=1, description="Score de coincidencia de experiencia")
    education_match: float = Field(..., ge=0, le=1, description="Score de coincidencia de educación")
    semantic_match: float = Field(..., ge=0, le=1, description="Score de similitud semántica")
    location_match: Optional[float] = Field(None, ge=0, le=1, description="Score de ubicación")


class SingleMatchRequest(BaseModel):
    """Request for single candidate-job matching"""
    candidate: CandidateSchema
    job: JobSchema


class SingleMatchResponse(BaseModel):
    """Response for single candidate-job matching"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    candidate_id: str
    candidate_name: str
    job_id: str
    compatibility_score: float = Field(..., ge=0, le=1, description="Score total de compatibilidad (0-1)")
    match_percentage: int = Field(..., ge=0, le=100, description="Porcentaje de compatibilidad (0-100)")
    breakdown: MatchBreakdown
    matched_skills: List[str] = Field(default_factory=list, description="Habilidades que coinciden")
    missing_skills: List[str] = Field(default_factory=list, description="Habilidades faltantes")
    explanation: str = Field(..., description="Explicación del match")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones para el candidato")
    match_quality: str = Field(..., description="Calidad del match: 'low', 'medium', 'good', 'excellent'")


class BatchMatchRequest(BaseModel):
    """Request for batch matching (multiple candidates, one job)"""
    candidates: List[CandidateSchema] = Field(..., min_length=1, description="Lista de candidatos")
    job: JobSchema
    
    @field_validator('candidates')
    @classmethod
    def validate_candidates(cls, v):
        """Validate that candidate IDs are unique"""
        ids = [c.id for c in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Candidate IDs must be unique")
        return v


class RankedMatchResult(BaseModel):
    """Individual match result with ranking"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    candidate_id: str
    candidate_name: str
    compatibility_score: float = Field(..., ge=0, le=1)
    match_percentage: int = Field(..., ge=0, le=100)
    rank: int = Field(..., ge=1, description="Posición en el ranking (1 = mejor)")
    breakdown: MatchBreakdown
    matched_skills: List[str]
    missing_skills: List[str]
    explanation: str
    recommendations: List[str]
    match_quality: str


class BatchMatchResponse(BaseModel):
    """Response for batch matching with ranked results"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    job_id: str
    job_title: str
    total_candidates: int
    matches: List[RankedMatchResult] = Field(..., description="Candidatos ordenados por compatibilidad (mayor a menor)")
    average_score: float = Field(..., ge=0, le=1, description="Score promedio de todos los candidatos")
    top_skills_matched: List[str] = Field(default_factory=list, description="Habilidades más comunes entre matches")


class ExplainMatchRequest(BaseModel):
    """Request for detailed match explanation"""
    candidate: CandidateSchema
    job: JobSchema
    include_suggestions: bool = Field(True, description="Incluir sugerencias de mejora")


class ExplainMatchResponse(BaseModel):
    """Detailed explanation of match"""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    candidate_id: str
    job_id: str
    compatibility_score: float
    match_percentage: int
    breakdown: MatchBreakdown
    detailed_analysis: Dict[str, str] = Field(..., description="Análisis detallado por categoría")
    strengths: List[str] = Field(default_factory=list, description="Fortalezas del candidato")
    weaknesses: List[str] = Field(default_factory=list, description="Áreas de mejora")
    suggestions: List[str] = Field(default_factory=list, description="Sugerencias específicas")
    decision_recommendation: str = Field(..., description="Recomendación de decisión")
