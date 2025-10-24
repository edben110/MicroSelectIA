"""
Matching endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import logging

from ...schemas.matching import (
    SingleMatchRequest,
    SingleMatchResponse,
    BatchMatchRequest,
    BatchMatchResponse,
    ExplainMatchRequest,
    ExplainMatchResponse,
    CandidateSchema,
    JobSchema
)
from ...services.matching_engine import get_matching_engine

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/single", response_model=SingleMatchResponse)
async def match_single_candidate(request: SingleMatchRequest):
    """
    Match a single candidate against a job posting
    
    Args:
        request: Single match request with candidate and job information
        
    Returns:
        Match result with compatibility score and detailed breakdown
        
    Example:
        ```json
        {
            "candidate": {
                "id": "123",
                "name": "Juan Pérez",
                "skills": ["python", "javascript", "react"],
                "experience_years": 5,
                "summary": "Desarrollador full-stack con experiencia..."
            },
            "job": {
                "id": "456",
                "title": "Desarrollador Full Stack",
                "description": "Buscamos desarrollador con...",
                "skills": ["python", "react", "node.js"]
            }
        }
        ```
    """
    try:
        logger.info(f"Processing single match: candidate={request.candidate.id}, job={request.job.id}")
        
        engine = get_matching_engine()
        result = engine.match_single(request.candidate, request.job)
        
        logger.info(f"Match completed: score={result.compatibility_score:.2f}")
        return result
        
    except Exception as e:
        logger.error(f"Error in single match: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing match: {str(e)}")


@router.post("/batch", response_model=BatchMatchResponse)
async def match_batch_candidates(request: BatchMatchRequest):
    """
    Match multiple candidates against a single job posting
    
    Returns candidates ranked by compatibility (highest to lowest)
    
    Args:
        request: Batch match request with multiple candidates and one job
        
    Returns:
        Batch match response with ranked candidates
        
    Example:
        ```json
        {
            "candidates": [
                {"id": "1", "name": "Juan", "skills": ["python"]},
                {"id": "2", "name": "María", "skills": ["python", "react"]}
            ],
            "job": {
                "id": "456",
                "title": "Desarrollador",
                "skills": ["python", "react"]
            }
        }
        ```
    """
    try:
        logger.info(f"Processing batch match: {len(request.candidates)} candidates, job={request.job.id}")
        
        if len(request.candidates) > 100:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 100 candidates per batch request"
            )
        
        engine = get_matching_engine()
        ranked_results, avg_score, top_skills = engine.match_batch(
            request.candidates, 
            request.job
        )
        
        logger.info(f"Batch match completed: avg_score={avg_score:.2f}")
        
        return BatchMatchResponse(
            job_id=request.job.id,
            job_title=request.job.title,
            total_candidates=len(request.candidates),
            matches=ranked_results,
            average_score=avg_score,
            top_skills_matched=top_skills
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch match: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing batch match: {str(e)}")


@router.post("/explain", response_model=ExplainMatchResponse)
async def explain_match(request: ExplainMatchRequest):
    """
    Get detailed explanation of a candidate-job match
    
    Provides in-depth analysis with strengths, weaknesses, and suggestions
    
    Args:
        request: Explain match request with candidate and job
        
    Returns:
        Detailed match explanation
    """
    try:
        logger.info(f"Processing explain match: candidate={request.candidate.id}, job={request.job.id}")
        
        engine = get_matching_engine()
        match_result = engine.match_single(request.candidate, request.job)
        
        # Build detailed analysis
        detailed_analysis = {
            "skills": f"Coincidencia de habilidades: {match_result.breakdown.skills_match*100:.0f}%. "
                     f"Habilidades coincidentes: {len(match_result.matched_skills)}. "
                     f"Habilidades faltantes: {len(match_result.missing_skills)}.",
            
            "experience": f"Coincidencia de experiencia: {match_result.breakdown.experience_match*100:.0f}%. "
                         f"El candidato tiene {request.candidate.experience_years} años de experiencia.",
            
            "education": f"Coincidencia educativa: {match_result.breakdown.education_match*100:.0f}%. "
                        f"Educación registrada: {len(request.candidate.education)} registros.",
            
            "semantic": f"Similitud semántica: {match_result.breakdown.semantic_match*100:.0f}%. "
                       "Análisis de compatibilidad entre el perfil del candidato y la descripción del trabajo."
        }
        
        # Identify strengths
        strengths = []
        if match_result.breakdown.skills_match >= 0.7:
            strengths.append("Excelente match de habilidades técnicas")
        if match_result.breakdown.experience_match >= 0.8:
            strengths.append("Experiencia superior a los requisitos")
        if match_result.breakdown.semantic_match >= 0.7:
            strengths.append("Alto alineamiento con la descripción del puesto")
        if len(match_result.matched_skills) > 5:
            strengths.append(f"Domina {len(match_result.matched_skills)} habilidades relevantes")
        
        # Identify weaknesses
        weaknesses = []
        if match_result.breakdown.skills_match < 0.5:
            weaknesses.append("Falta de habilidades técnicas clave")
        if match_result.breakdown.experience_match < 0.6:
            weaknesses.append("Experiencia por debajo de los requisitos")
        if len(match_result.missing_skills) > 5:
            weaknesses.append(f"Le faltan {len(match_result.missing_skills)} habilidades requeridas")
        if match_result.breakdown.education_match < 0.5:
            weaknesses.append("Formación académica no alineada con requisitos")
        
        if not strengths:
            strengths.append("Perfil básico adecuado para evaluación")
        if not weaknesses:
            weaknesses.append("No se identificaron debilidades significativas")
        
        # Generate suggestions (if requested)
        suggestions = []
        if request.include_suggestions:
            suggestions = match_result.recommendations
        
        # Decision recommendation
        if match_result.match_quality == "excellent":
            decision = "RECOMENDADO FUERTEMENTE - Agendar entrevista con prioridad alta"
        elif match_result.match_quality == "good":
            decision = "RECOMENDADO - Agendar entrevista"
        elif match_result.match_quality == "medium":
            decision = "CONSIDERAR - Evaluación adicional recomendada"
        else:
            decision = "NO RECOMENDADO - No cumple requisitos mínimos"
        
        return ExplainMatchResponse(
            candidate_id=request.candidate.id,
            job_id=request.job.id,
            compatibility_score=match_result.compatibility_score,
            match_percentage=match_result.match_percentage,
            breakdown=match_result.breakdown,
            detailed_analysis=detailed_analysis,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            decision_recommendation=decision
        )
        
    except Exception as e:
        logger.error(f"Error in explain match: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating explanation: {str(e)}")


@router.post("/test")
async def test_match():
    """
    Test endpoint with sample data for quick verification
    
    Returns a sample match result for testing purposes
    """
    sample_candidate = CandidateSchema(
        id="test-001",
        name="Juan Pérez",
        skills=["python", "javascript", "react", "sql"],
        experience_years=5,
        summary="Desarrollador full-stack con 5 años de experiencia en desarrollo web"
    )
    
    sample_job = JobSchema(
        id="job-001",
        title="Desarrollador Full Stack",
        description="Buscamos desarrollador con experiencia en Python y React",
        skills=["python", "react", "node.js"],
        requirements=["5 años de experiencia", "Inglés intermedio"]
    )
    
    try:
        engine = get_matching_engine()
        result = engine.match_single(sample_candidate, sample_job)
        
        return {
            "message": "Test match successful",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")
