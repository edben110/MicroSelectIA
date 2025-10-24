"""
Test script for MicroSelectIA
Run this to verify the microservice is working correctly
"""

import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def test_health_check():
    """Test health check endpoint"""
    print_header("Testing Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_single_match():
    """Test single candidate matching"""
    print_header("Testing Single Match")
    
    # Sample data
    candidate = {
        "id": "cand-001",
        "name": "Juan Pérez",
        "skills": ["python", "javascript", "react", "sql", "docker"],
        "experience_years": 5,
        "summary": "Desarrollador full-stack con 5 años de experiencia en desarrollo web. Experto en Python, React y bases de datos.",
        "experience": [
            {
                "company": "Tech Solutions",
                "position": "Full Stack Developer",
                "description": "Desarrollo de aplicaciones web con Python y React",
                "years": 3
            },
            {
                "company": "StartupXYZ",
                "position": "Backend Developer",
                "description": "Desarrollo de APIs REST con Python",
                "years": 2
            }
        ],
        "education": [
            {
                "degree": "Ingeniería en Sistemas",
                "institution": "Universidad Nacional",
                "field": "Computer Science"
            }
        ],
        "location": "Ciudad de México"
    }
    
    job = {
        "id": "job-001",
        "title": "Desarrollador Full Stack Senior",
        "description": "Buscamos desarrollador con experiencia en Python y React para proyecto de alto impacto",
        "skills": ["python", "react", "postgresql", "docker", "aws"],
        "requirements": [
            "5+ años de experiencia",
            "Inglés intermedio",
            "Título universitario"
        ],
        "location": "Ciudad de México",
        "type": "FULL_TIME",
        "min_experience_years": 5
    }
    
    payload = {
        "candidate": candidate,
        "job": job
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/match/single", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Match Result:")
            print(f"   Candidate: {result['candidate_name']}")
            print(f"   Job: {result['job_id']}")
            print(f"   Compatibility: {result['match_percentage']}%")
            print(f"   Quality: {result['match_quality'].upper()}")
            print(f"\n   Breakdown:")
            print(f"      Skills: {result['breakdown']['skills_match']*100:.1f}%")
            print(f"      Experience: {result['breakdown']['experience_match']*100:.1f}%")
            print(f"      Education: {result['breakdown']['education_match']*100:.1f}%")
            print(f"      Semantic: {result['breakdown']['semantic_match']*100:.1f}%")
            print(f"\n   Matched Skills: {', '.join(result['matched_skills'])}")
            print(f"   Missing Skills: {', '.join(result['missing_skills'])}")
            print(f"\n   {result['explanation']}")
            print(f"\n   Recommendations:")
            for rec in result['recommendations']:
                print(f"      - {rec}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_batch_match():
    """Test batch matching"""
    print_header("Testing Batch Match")
    
    candidates = [
        {
            "id": "cand-001",
            "name": "Juan Pérez",
            "skills": ["python", "react", "sql"],
            "experience_years": 5,
            "summary": "Desarrollador full-stack senior"
        },
        {
            "id": "cand-002",
            "name": "María García",
            "skills": ["python", "django", "postgresql", "aws"],
            "experience_years": 7,
            "summary": "Desarrolladora backend con experiencia en cloud"
        },
        {
            "id": "cand-003",
            "name": "Carlos López",
            "skills": ["javascript", "react", "node.js"],
            "experience_years": 3,
            "summary": "Desarrollador frontend especializado en React"
        }
    ]
    
    job = {
        "id": "job-001",
        "title": "Desarrollador Full Stack",
        "description": "Buscamos desarrollador con experiencia en Python y React",
        "skills": ["python", "react", "postgresql"],
        "requirements": ["5 años de experiencia"],
        "min_experience_years": 5
    }
    
    payload = {
        "candidates": candidates,
        "job": job
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/match/batch", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Batch Match Results:")
            print(f"   Job: {result['job_title']}")
            print(f"   Total Candidates: {result['total_candidates']}")
            print(f"   Average Score: {result['average_score']*100:.1f}%")
            print(f"\n   Ranking:")
            
            for match in result['matches']:
                print(f"\n   #{match['rank']} - {match['candidate_name']}")
                print(f"      Score: {match['match_percentage']}% ({match['match_quality'].upper()})")
                print(f"      Skills: {', '.join(match['matched_skills'][:3])}")
                
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_explain_match():
    """Test detailed match explanation"""
    print_header("Testing Explain Match")
    
    candidate = {
        "id": "cand-001",
        "name": "Juan Pérez",
        "skills": ["python", "javascript"],
        "experience_years": 3,
        "summary": "Desarrollador con 3 años de experiencia"
    }
    
    job = {
        "id": "job-001",
        "title": "Desarrollador Senior",
        "description": "Buscamos desarrollador senior",
        "skills": ["python", "react", "aws", "docker"],
        "requirements": ["5 años de experiencia", "Título universitario"],
        "min_experience_years": 5
    }
    
    payload = {
        "candidate": candidate,
        "job": job,
        "include_suggestions": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/match/explain", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Detailed Analysis:")
            print(f"   Candidate: {result['candidate_id']}")
            print(f"   Compatibility: {result['match_percentage']}%")
            
            print(f"\n   Detailed Analysis:")
            for key, value in result['detailed_analysis'].items():
                print(f"      {key.title()}: {value}")
            
            print(f"\n   Strengths:")
            for strength in result['strengths']:
                print(f"      ✓ {strength}")
            
            print(f"\n   Weaknesses:")
            for weakness in result['weaknesses']:
                print(f"      ✗ {weakness}")
            
            print(f"\n   Suggestions:")
            for suggestion in result['suggestions']:
                print(f"      → {suggestion}")
            
            print(f"\n   Decision: {result['decision_recommendation']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  MicroSelectIA - Test Suite")
    print(f"  Testing: {BASE_URL}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {
        "Health Check": test_health_check(),
        "Single Match": test_single_match(),
        "Batch Match": test_batch_match(),
        "Explain Match": test_explain_match()
    }
    
    print_header("Test Summary")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n   Total: {passed}/{total} tests passed")
    
    return all(results.values())


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
