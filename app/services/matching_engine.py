"""
Main matching engine that combines all scoring components
"""

from typing import List, Tuple, Dict
import logging
from ..schemas.matching import (
    CandidateSchema,
    JobSchema,
    MatchBreakdown,
    SingleMatchResponse,
    RankedMatchResult,
)
from .ai_matcher import get_ai_matcher
from ..core.config import get_settings

logger = logging.getLogger(__name__)


class MatchingEngine:
    """Main engine for candidate-job matching"""
    
    def __init__(self):
        """Initialize the matching engine"""
        self.settings = get_settings()
        self.ai_matcher = get_ai_matcher(self.settings.AI_MODEL)
        logger.info("Matching engine initialized")
    
    def calculate_skills_match(
        self, 
        candidate: CandidateSchema, 
        job: JobSchema
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calculate skills match score
        
        Args:
            candidate: Candidate information
            job: Job information
            
        Returns:
            Tuple of (score, matched_skills, missing_skills)
        """
        if not job.skills:
            return 1.0, [], []
        
        candidate_skills = set(skill.lower().strip() for skill in candidate.skills)
        job_skills = set(skill.lower().strip() for skill in job.skills)
        
        # Exact matches
        matched_skills = list(candidate_skills.intersection(job_skills))
        missing_skills = list(job_skills - candidate_skills)
        
        # Calculate exact match score
        exact_match_score = len(matched_skills) / len(job_skills) if job_skills else 0
        
        # Use AI for semantic matching of remaining skills
        if missing_skills and candidate.skills:
            semantic_score, semantic_matches = self.ai_matcher.match_skills_semantic(
                candidate.skills, 
                missing_skills
            )
            
            # Combine exact and semantic matches
            # Exact matches have higher weight
            final_score = (exact_match_score * 0.7) + (semantic_score * 0.3)
            
            # Add semantic matches to matched skills
            matched_skills.extend(semantic_matches)
            missing_skills = [skill for skill in missing_skills if skill not in semantic_matches]
        else:
            final_score = exact_match_score
        
        return min(1.0, final_score), matched_skills, missing_skills
    
    def calculate_experience_match(self, candidate: CandidateSchema, job: JobSchema) -> float:
        """
        Calculate experience match score
        
        Args:
            candidate: Candidate information
            job: Job information
            
        Returns:
            Experience match score (0-1)
        """
        if job.min_experience_years is None or job.min_experience_years == 0:
            return 1.0
        
        candidate_exp = candidate.experience_years
        required_exp = job.min_experience_years
        
        if candidate_exp >= required_exp:
            # Candidate meets or exceeds requirements
            # Give bonus for more experience, but with diminishing returns
            excess = candidate_exp - required_exp
            bonus = min(0.2, excess / (required_exp * 2))  # Max 20% bonus
            return min(1.0, 1.0 + bonus)
        else:
            # Candidate has less experience
            # Linear penalty based on gap
            ratio = candidate_exp / required_exp
            return max(0.0, ratio)
    
    def calculate_education_match(self, candidate: CandidateSchema, job: JobSchema) -> float:
        """
        Calculate education match score
        
        Args:
            candidate: Candidate information
            job: Job information
            
        Returns:
            Education match score (0-1)
        """
        if not candidate.education or not job.requirements:
            return 0.5  # Neutral score if no education data
        
        # Extract education-related keywords from job requirements
        edu_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'degree',
            'licenciatura', 'maestría', 'doctorado', 'título'
        ]
        
        job_reqs_text = ' '.join(job.requirements).lower()
        has_edu_requirement = any(keyword in job_reqs_text for keyword in edu_keywords)
        
        if not has_edu_requirement:
            return 1.0  # No specific education requirement
        
        # Score based on education level and relevance
        education_texts = []
        for edu in candidate.education:
            edu_text = f"{edu.degree} in {edu.field or ''} from {edu.institution}"
            education_texts.append(edu_text)
        
        if not education_texts:
            return 0.3  # Low score if requirement exists but candidate has no education listed
        
        # Use semantic matching between education and job requirements
        combined_edu = ". ".join(education_texts)
        score = self.ai_matcher.match_text_semantic(combined_edu, job_reqs_text)
        
        return score
    
    def calculate_semantic_match(self, candidate: CandidateSchema, job: JobSchema) -> float:
        """
        Calculate semantic match between candidate profile and job description
        
        Args:
            candidate: Candidate information
            job: Job information
            
        Returns:
            Semantic match score (0-1)
        """
        # Build candidate profile text
        candidate_parts = []
        
        if candidate.summary:
            candidate_parts.append(candidate.summary)
        
        if candidate.experience:
            exp_texts = [
                f"{exp.position} at {exp.company}. {exp.description or ''}"
                for exp in candidate.experience
            ]
            candidate_parts.extend(exp_texts)
        
        candidate_text = " ".join(candidate_parts)
        
        # Build job text
        job_text = f"{job.title}. {job.description}. " + " ".join(job.requirements)
        
        if not candidate_text or not job_text:
            return 0.5  # Neutral score if no text available
        
        # Calculate semantic similarity
        score = self.ai_matcher.match_text_semantic(candidate_text, job_text)
        
        return score
    
    def calculate_location_match(self, candidate: CandidateSchema, job: JobSchema) -> float:
        """
        Calculate location match score
        
        Args:
            candidate: Candidate information
            job: Job information
            
        Returns:
            Location match score (0-1)
        """
        if not job.location:
            return 1.0  # No location requirement
        
        if not candidate.location:
            return 0.5  # Neutral if candidate location unknown
        
        # Simple string matching (can be enhanced with geocoding/distance)
        candidate_loc = candidate.location.lower().strip()
        job_loc = job.location.lower().strip()
        
        # Check for remote work keywords
        remote_keywords = ['remote', 'remoto', 'anywhere', 'cualquier lugar']
        if any(keyword in job_loc for keyword in remote_keywords):
            return 1.0
        
        # Exact match
        if candidate_loc == job_loc:
            return 1.0
        
        # Partial match (e.g., same city or region)
        if candidate_loc in job_loc or job_loc in candidate_loc:
            return 0.8
        
        # Use semantic similarity as fallback
        loc_similarity = self.ai_matcher.calculate_similarity(candidate_loc, job_loc)
        return loc_similarity * 0.6  # Scale down since it's not exact match
    
    def calculate_overall_score(self, breakdown: MatchBreakdown) -> float:
        """
        Calculate weighted overall match score
        
        Args:
            breakdown: Individual component scores
            
        Returns:
            Overall weighted score (0-1)
        """
        score = (
            breakdown.skills_match * self.settings.SKILLS_WEIGHT +
            breakdown.experience_match * self.settings.EXPERIENCE_WEIGHT +
            breakdown.education_match * self.settings.EDUCATION_WEIGHT +
            breakdown.semantic_match * self.settings.SEMANTIC_WEIGHT
        )
        
        # Optional location factor (not part of main weights)
        if breakdown.location_match is not None:
            # Location can boost score slightly
            location_boost = breakdown.location_match * 0.05
            score = min(1.0, score + location_boost)
        
        return score
    
    def determine_match_quality(self, score: float) -> str:
        """
        Determine match quality level based on score
        
        Args:
            score: Overall match score (0-1)
            
        Returns:
            Quality level: 'low', 'medium', 'good', 'excellent'
        """
        if score >= self.settings.EXCELLENT_MATCH_THRESHOLD:
            return "excellent"
        elif score >= self.settings.GOOD_MATCH_THRESHOLD:
            return "good"
        elif score >= self.settings.MIN_MATCH_THRESHOLD:
            return "medium"
        else:
            return "low"
    
    def generate_explanation(
        self,
        candidate: CandidateSchema,
        job: JobSchema,
        breakdown: MatchBreakdown,
        matched_skills: List[str],
        missing_skills: List[str],
        overall_score: float
    ) -> str:
        """
        Generate human-readable explanation of the match
        
        Args:
            candidate: Candidate information
            job: Job information
            breakdown: Score breakdown
            matched_skills: Skills that matched
            missing_skills: Skills that are missing
            overall_score: Overall match score
            
        Returns:
            Explanation text
        """
        quality = self.determine_match_quality(overall_score)
        percentage = int(overall_score * 100)
        
        explanation_parts = [
            f"{candidate.name} tiene un {percentage}% de compatibilidad con el puesto {job.title}."
        ]
        
        # Skills analysis
        if matched_skills:
            explanation_parts.append(
                f"Habilidades coincidentes: {', '.join(matched_skills[:5])}"
                + (" y más" if len(matched_skills) > 5 else "") + "."
            )
        
        if missing_skills:
            explanation_parts.append(
                f"Habilidades por desarrollar: {', '.join(missing_skills[:3])}"
                + (" y otras" if len(missing_skills) > 3 else "") + "."
            )
        
        # Experience analysis
        if breakdown.experience_match >= 0.8:
            explanation_parts.append("La experiencia del candidato supera los requisitos.")
        elif breakdown.experience_match >= 0.6:
            explanation_parts.append("La experiencia del candidato cumple con los requisitos.")
        else:
            explanation_parts.append("El candidato necesita más experiencia para este puesto.")
        
        # Overall recommendation
        if quality == "excellent":
            explanation_parts.append("Candidato altamente recomendado para entrevista.")
        elif quality == "good":
            explanation_parts.append("Candidato recomendado para considerar.")
        elif quality == "medium":
            explanation_parts.append("Candidato con potencial, requiere evaluación adicional.")
        else:
            explanation_parts.append("Candidato no cumple con los requisitos mínimos.")
        
        return " ".join(explanation_parts)
    
    def generate_recommendations(
        self,
        candidate: CandidateSchema,
        job: JobSchema,
        breakdown: MatchBreakdown,
        missing_skills: List[str]
    ) -> List[str]:
        """
        Generate recommendations for the candidate
        
        Args:
            candidate: Candidate information
            job: Job information
            breakdown: Score breakdown
            missing_skills: Skills that are missing
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Skills recommendations
        if missing_skills:
            top_missing = missing_skills[:3]
            recommendations.append(
                f"Desarrollar habilidades en: {', '.join(top_missing)}"
            )
        
        # Experience recommendations
        if breakdown.experience_match < 0.7 and job.min_experience_years:
            recommendations.append(
                f"Ganar más experiencia relevante (ideal: {job.min_experience_years} años)"
            )
        
        # Education recommendations
        if breakdown.education_match < 0.6:
            recommendations.append(
                "Considerar certificaciones o formación adicional relacionada con el puesto"
            )
        
        # Semantic match recommendations
        if breakdown.semantic_match < 0.6:
            recommendations.append(
                "Actualizar perfil profesional para resaltar experiencia relevante al puesto"
            )
        
        if not recommendations:
            recommendations.append("Perfil muy completo, mantener actualizado")
        
        return recommendations
    
    def match_single(self, candidate: CandidateSchema, job: JobSchema) -> SingleMatchResponse:
        """
        Perform matching for a single candidate-job pair
        
        Args:
            candidate: Candidate information
            job: Job information
            
        Returns:
            Match response with scores and details
        """
        logger.info(f"Matching candidate {candidate.id} with job {job.id}")
        
        # Calculate individual scores
        skills_score, matched_skills, missing_skills = self.calculate_skills_match(candidate, job)
        experience_score = self.calculate_experience_match(candidate, job)
        education_score = self.calculate_education_match(candidate, job)
        semantic_score = self.calculate_semantic_match(candidate, job)
        location_score = self.calculate_location_match(candidate, job)
        
        # Create breakdown
        breakdown = MatchBreakdown(
            skills_match=skills_score,
            experience_match=experience_score,
            education_match=education_score,
            semantic_match=semantic_score,
            location_match=location_score
        )
        
        # Calculate overall score
        overall_score = self.calculate_overall_score(breakdown)
        match_percentage = int(overall_score * 100)
        match_quality = self.determine_match_quality(overall_score)
        
        # Generate explanation and recommendations
        explanation = self.generate_explanation(
            candidate, job, breakdown, matched_skills, missing_skills, overall_score
        )
        recommendations = self.generate_recommendations(
            candidate, job, breakdown, missing_skills
        )
        
        return SingleMatchResponse(
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            job_id=job.id,
            compatibility_score=overall_score,
            match_percentage=match_percentage,
            breakdown=breakdown,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            explanation=explanation,
            recommendations=recommendations,
            match_quality=match_quality
        )
    
    def match_batch(
        self, 
        candidates: List[CandidateSchema], 
        job: JobSchema
    ) -> Tuple[List[RankedMatchResult], float, List[str]]:
        """
        Perform matching for multiple candidates against one job
        
        Args:
            candidates: List of candidates
            job: Job information
            
        Returns:
            Tuple of (ranked_results, average_score, top_skills)
        """
        logger.info(f"Batch matching {len(candidates)} candidates with job {job.id}")
        
        # Match each candidate
        matches = []
        all_matched_skills = []
        
        for candidate in candidates:
            match_result = self.match_single(candidate, job)
            matches.append(match_result)
            all_matched_skills.extend(match_result.matched_skills)
        
        # Sort by compatibility score (descending)
        matches.sort(key=lambda x: x.compatibility_score, reverse=True)
        
        # Create ranked results
        ranked_results = []
        for rank, match in enumerate(matches, 1):
            ranked_result = RankedMatchResult(
                candidate_id=match.candidate_id,
                candidate_name=match.candidate_name,
                compatibility_score=match.compatibility_score,
                match_percentage=match.match_percentage,
                rank=rank,
                breakdown=match.breakdown,
                matched_skills=match.matched_skills,
                missing_skills=match.missing_skills,
                explanation=match.explanation,
                recommendations=match.recommendations,
                match_quality=match.match_quality
            )
            ranked_results.append(ranked_result)
        
        # Calculate average score
        average_score = sum(m.compatibility_score for m in matches) / len(matches) if matches else 0.0
        
        # Get top skills
        skill_counts = {}
        for skill in all_matched_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_skills = [skill for skill, _ in top_skills]
        
        return ranked_results, average_score, top_skills


# Singleton instance
_matching_engine_instance = None


def get_matching_engine() -> MatchingEngine:
    """
    Get or create the singleton MatchingEngine instance
    
    Returns:
        MatchingEngine instance
    """
    global _matching_engine_instance
    
    if _matching_engine_instance is None:
        _matching_engine_instance = MatchingEngine()
    
    return _matching_engine_instance
