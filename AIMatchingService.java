package com.clipers.clipers.service;

import com.clipers.clipers.dto.matching.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.RestClientException;
import lombok.extern.slf4j.Slf4j;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Service for integrating with MicroSelectIA (AI Matching Microservice)
 * 
 * This service communicates with the Python microservice for intelligent candidate-job matching
 */
@Service
@Slf4j
public class AIMatchingService {
    
    private final RestTemplate restTemplate;
    
    @Value("${microselectia.url:http://localhost:8000}")
    private String microServiceUrl;
    
    @Value("${microselectia.enabled:true}")
    private boolean microServiceEnabled;
    
    @Value("${microselectia.fallback-to-local:true}")
    private boolean fallbackToLocal;
    
    public AIMatchingService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    
    /**
     * Match a single candidate against a job using AI
     * 
     * @param candidateId Candidate ID
     * @param jobId Job ID
     * @return Match result with compatibility score
     */
    public MatchResult matchSingleCandidate(String candidateId, String jobId) {
        if (!microServiceEnabled) {
            log.warn("MicroSelectIA is disabled, skipping AI matching");
            return null;
        }
        
        try {
            // Build request
            SingleMatchRequest request = buildSingleMatchRequest(candidateId, jobId);
            
            // Call microservice
            String url = microServiceUrl + "/api/match/single";
            log.info("Calling MicroSelectIA: POST {}", url);
            
            ResponseEntity<SingleMatchResponse> response = restTemplate.postForEntity(
                url, 
                request, 
                SingleMatchResponse.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                log.info("AI matching successful: candidateId={}, jobId={}, score={}", 
                    candidateId, jobId, response.getBody().getCompatibilityScore());
                return convertToMatchResult(response.getBody());
            }
            
            log.warn("AI matching returned no data");
            return null;
            
        } catch (RestClientException e) {
            log.error("Error calling MicroSelectIA: {}", e.getMessage());
            if (fallbackToLocal) {
                log.info("Falling back to local matching");
                return null; // Will trigger fallback in calling method
            }
            throw new RuntimeException("AI matching service unavailable", e);
        }
    }
    
    /**
     * Match multiple candidates against a job using AI
     * Returns candidates ranked by compatibility (highest to lowest)
     * 
     * @param candidateIds List of candidate IDs
     * @param jobId Job ID
     * @return List of ranked match results
     */
    public List<RankedMatchResult> matchBatchCandidates(List<String> candidateIds, String jobId) {
        if (!microServiceEnabled) {
            log.warn("MicroSelectIA is disabled, skipping AI matching");
            return null;
        }
        
        try {
            // Build request
            BatchMatchRequest request = buildBatchMatchRequest(candidateIds, jobId);
            
            // Call microservice
            String url = microServiceUrl + "/api/match/batch";
            log.info("Calling MicroSelectIA batch matching: POST {}, candidates={}", url, candidateIds.size());
            
            ResponseEntity<BatchMatchResponse> response = restTemplate.postForEntity(
                url, 
                request, 
                BatchMatchResponse.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                BatchMatchResponse body = response.getBody();
                log.info("AI batch matching successful: jobId={}, candidates={}, avgScore={}", 
                    jobId, body.getTotalCandidates(), body.getAverageScore());
                return body.getMatches();
            }
            
            log.warn("AI batch matching returned no data");
            return null;
            
        } catch (RestClientException e) {
            log.error("Error calling MicroSelectIA batch matching: {}", e.getMessage());
            if (fallbackToLocal) {
                log.info("Falling back to local matching");
                return null;
            }
            throw new RuntimeException("AI matching service unavailable", e);
        }
    }
    
    /**
     * Get detailed explanation of a match
     * 
     * @param candidateId Candidate ID
     * @param jobId Job ID
     * @return Detailed match explanation
     */
    public ExplainMatchResponse explainMatch(String candidateId, String jobId) {
        if (!microServiceEnabled) {
            log.warn("MicroSelectIA is disabled, skipping AI matching explanation");
            return null;
        }
        
        try {
            ExplainMatchRequest request = buildExplainMatchRequest(candidateId, jobId);
            
            String url = microServiceUrl + "/api/match/explain";
            log.info("Calling MicroSelectIA explain: POST {}", url);
            
            ResponseEntity<ExplainMatchResponse> response = restTemplate.postForEntity(
                url, 
                request, 
                ExplainMatchResponse.class
            );
            
            return response.getBody();
            
        } catch (RestClientException e) {
            log.error("Error calling MicroSelectIA explain: {}", e.getMessage());
            return null;
        }
    }
    
    /**
     * Check if MicroSelectIA is healthy and available
     * 
     * @return true if service is healthy
     */
    public boolean isServiceHealthy() {
        if (!microServiceEnabled) {
            return false;
        }
        
        try {
            String url = microServiceUrl + "/health";
            ResponseEntity<HealthResponse> response = restTemplate.getForEntity(url, HealthResponse.class);
            return response.getStatusCode() == HttpStatus.OK;
        } catch (Exception e) {
            log.warn("MicroSelectIA health check failed: {}", e.getMessage());
            return false;
        }
    }
    
    // ========== Private helper methods ==========
    
    private SingleMatchRequest buildSingleMatchRequest(String candidateId, String jobId) {
        // TODO: Fetch candidate and job from database and convert to DTOs
        // This is a placeholder - implement actual data fetching
        CandidateDTO candidate = fetchCandidateData(candidateId);
        JobDTO job = fetchJobData(jobId);
        
        SingleMatchRequest request = new SingleMatchRequest();
        request.setCandidate(candidate);
        request.setJob(job);
        return request;
    }
    
    private BatchMatchRequest buildBatchMatchRequest(List<String> candidateIds, String jobId) {
        List<CandidateDTO> candidates = candidateIds.stream()
            .map(this::fetchCandidateData)
            .collect(Collectors.toList());
        
        JobDTO job = fetchJobData(jobId);
        
        BatchMatchRequest request = new BatchMatchRequest();
        request.setCandidates(candidates);
        request.setJob(job);
        return request;
    }
    
    private ExplainMatchRequest buildExplainMatchRequest(String candidateId, String jobId) {
        CandidateDTO candidate = fetchCandidateData(candidateId);
        JobDTO job = fetchJobData(jobId);
        
        ExplainMatchRequest request = new ExplainMatchRequest();
        request.setCandidate(candidate);
        request.setJob(job);
        request.setIncludeSuggestions(true);
        return request;
    }
    
    private CandidateDTO fetchCandidateData(String candidateId) {
        // TODO: Implement actual database fetch
        // For now, return placeholder
        log.debug("Fetching candidate data for ID: {}", candidateId);
        return new CandidateDTO(); // Replace with actual implementation
    }
    
    private JobDTO fetchJobData(String jobId) {
        // TODO: Implement actual database fetch
        log.debug("Fetching job data for ID: {}", jobId);
        return new JobDTO(); // Replace with actual implementation
    }
    
    private MatchResult convertToMatchResult(SingleMatchResponse response) {
        // Convert microservice response to internal MatchResult format
        MatchResult result = new MatchResult();
        result.setCandidateId(response.getCandidateId());
        result.setJobId(response.getJobId());
        result.setCompatibilityScore(response.getCompatibilityScore());
        result.setMatchPercentage(response.getMatchPercentage());
        result.setMatchedSkills(response.getMatchedSkills());
        result.setExplanation(response.getExplanation());
        result.setMatchQuality(response.getMatchQuality());
        return result;
    }
}
