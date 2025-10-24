"""
AI-powered semantic matching using Sentence Transformers
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class AIMatcherService:
    """AI service for semantic text matching"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the AI matcher with a Sentence Transformer model
        
        Args:
            model_name: Name of the Sentence Transformer model to use
        """
        self.model_name = model_name
        self.model = None
        logger.info(f"Initializing AI Matcher with model: {model_name}")
    
    def load_model(self):
        """Load the Sentence Transformer model"""
        if self.model is None:
            logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
    
    def ensure_model_loaded(self):
        """Ensure the model is loaded before use"""
        if self.model is None:
            self.load_model()
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode a single text string into embeddings
        
        Args:
            text: Text to encode
            
        Returns:
            Embedding vector
        """
        self.ensure_model_loaded()
        return self.model.encode([text])[0]
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode multiple texts into embeddings
        
        Args:
            texts: List of texts to encode
            
        Returns:
            Array of embedding vectors
        """
        self.ensure_model_loaded()
        return self.model.encode(texts)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        self.ensure_model_loaded()
        
        # Encode texts
        embeddings = self.model.encode([text1, text2])
        
        # Calculate cosine similarity
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        
        # Ensure score is between 0 and 1
        return float(max(0, min(1, similarity)))
    
    def calculate_batch_similarity(self, text: str, texts: List[str]) -> List[float]:
        """
        Calculate similarity between one text and multiple texts
        
        Args:
            text: Query text
            texts: List of texts to compare against
            
        Returns:
            List of similarity scores
        """
        self.ensure_model_loaded()
        
        if not texts:
            return []
        
        # Encode all texts
        query_embedding = self.model.encode([text])[0]
        text_embeddings = self.model.encode(texts)
        
        # Calculate similarities
        similarities = cosine_similarity([query_embedding], text_embeddings)[0]
        
        # Ensure scores are between 0 and 1
        return [float(max(0, min(1, sim))) for sim in similarities]
    
    def match_skills_semantic(self, candidate_skills: List[str], job_skills: List[str]) -> Tuple[float, List[str]]:
        """
        Match skills using semantic similarity
        
        Args:
            candidate_skills: List of candidate skills
            job_skills: List of required job skills
            
        Returns:
            Tuple of (average_similarity_score, matched_skills)
        """
        self.ensure_model_loaded()
        
        if not candidate_skills or not job_skills:
            return 0.0, []
        
        # Normalize skills to lowercase
        candidate_skills = [skill.lower().strip() for skill in candidate_skills]
        job_skills = [skill.lower().strip() for skill in job_skills]
        
        # Encode all skills
        candidate_embeddings = self.model.encode(candidate_skills)
        job_embeddings = self.model.encode(job_skills)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(job_embeddings, candidate_embeddings)
        
        # For each job skill, find the best matching candidate skill
        matched_skills = []
        match_scores = []
        
        threshold = 0.7  # Threshold for considering a match
        
        for idx, job_skill in enumerate(job_skills):
            max_similarity = similarity_matrix[idx].max()
            max_idx = similarity_matrix[idx].argmax()
            
            if max_similarity >= threshold:
                matched_skills.append(job_skill)
                match_scores.append(max_similarity)
        
        # Calculate average score
        avg_score = np.mean(match_scores) if match_scores else 0.0
        
        return float(avg_score), matched_skills
    
    def match_text_semantic(self, candidate_text: str, job_text: str) -> float:
        """
        Match two text descriptions using semantic similarity
        
        Args:
            candidate_text: Candidate's text (summary, experience, etc.)
            job_text: Job description/requirements
            
        Returns:
            Similarity score between 0 and 1
        """
        if not candidate_text or not job_text:
            return 0.0
        
        return self.calculate_similarity(candidate_text, job_text)
    
    def extract_key_phrases(self, text: str, top_k: int = 10) -> List[str]:
        """
        Extract key phrases from text using embeddings
        (Simplified version - can be enhanced with proper keyword extraction)
        
        Args:
            text: Text to extract phrases from
            top_k: Number of top phrases to extract
            
        Returns:
            List of key phrases
        """
        # Simple implementation: split into sentences and rank by length/relevance
        # In production, use proper keyword extraction libraries like KeyBERT
        sentences = text.split('.')
        phrases = [s.strip() for s in sentences if s.strip()]
        
        # Return top_k phrases
        return phrases[:top_k]
    
    def get_model_info(self) -> dict:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary with model information
        """
        self.ensure_model_loaded()
        
        return {
            "model_name": self.model_name,
            "max_seq_length": self.model.max_seq_length,
            "embedding_dimension": self.model.get_sentence_embedding_dimension(),
        }


# Singleton instance
_ai_matcher_instance = None


def get_ai_matcher(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> AIMatcherService:
    """
    Get or create the singleton AIMatcherService instance
    
    Args:
        model_name: Name of the model to use
        
    Returns:
        AIMatcherService instance
    """
    global _ai_matcher_instance
    
    if _ai_matcher_instance is None:
        _ai_matcher_instance = AIMatcherService(model_name)
        _ai_matcher_instance.load_model()
    
    return _ai_matcher_instance
