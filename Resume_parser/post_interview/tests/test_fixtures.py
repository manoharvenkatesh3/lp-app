"""Test configuration and fixtures for post-interview analytics.

This module provides shared test configuration and synthetic data generation
for comprehensive testing of the analytics system.
"""

from __future__ import annotations

import json
import random
import pytest
from datetime import datetime, timedelta
from typing import Dict, List

from faker import Faker

# Import models with try/except for testing
try:
    from post_interview.models import (
        AnalyticsConfig,
        InterviewSession,
        ScoringAxes,
        StrengthWeakness,
        TranscriptData,
        UserRole,
    )
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False


class SyntheticDataGenerator:
    """Generate synthetic data for testing purposes."""
    
    def __init__(self, seed: int = 42):
        if not MODELS_AVAILABLE:
            raise ImportError("Models not available for testing")
        
        self.fake = Faker()
        Faker.seed(seed)
        random.seed(seed)
    
    def generate_transcript(self, interview_type: str = "technical",
                          duration_minutes: int = 30) -> Dict:
        """Generate synthetic interview transcript."""
        if interview_type == "technical":
            return self._generate_technical_transcript()
        elif interview_type == "behavioral":
            return self._generate_behavioral_transcript()
        else:
            return self._generate_general_transcript()
    
    def _generate_technical_transcript(self) -> Dict:
        """Generate technical interview transcript."""
        technical_questions = [
            "Tell me about your experience with Python.",
            "How do you approach debugging complex issues?",
            "Describe a challenging technical problem you solved.",
            "What's your experience with database design?",
            "How do you ensure code quality in your projects?"
        ]
        
        technical_responses = [
            "I have 5 years of experience with Python, working with Django and Flask frameworks.",
            "I use systematic debugging approaches, starting with reproduction and then isolating variables.",
            "I implemented a distributed caching system that reduced API response time by 40%.",
            "I've designed normalized schemas for e-commerce platforms and optimized query performance.",
            "I implement comprehensive testing, code reviews, and follow SOLID principles."
        ]
        
        messages = []
        for i, (question, answer) in enumerate(zip(technical_questions, technical_responses)):
            messages.append({"speaker": "Interviewer", "text": question})
            messages.append({"speaker": "Candidate", "text": answer})
        
        return {"messages": messages}
    
    def _generate_behavioral_transcript(self) -> Dict:
        """Generate behavioral interview transcript."""
        behavioral_questions = [
            "Describe a time you had to work with a difficult team member.",
            "How do you handle tight deadlines?",
            "Tell me about a time you had to learn a new technology quickly.",
            "How do you approach conflict resolution?",
            "Describe a situation where you took initiative."
        ]
        
        behavioral_responses = [
            "I scheduled a private meeting to understand their perspective and found common ground.",
            "I prioritize tasks, communicate clearly about timelines, and focus on critical path items.",
            "I learned React in two weeks by dedicating evenings to documentation and building projects.",
            "I listen actively to understand all viewpoints and work toward mutually beneficial solutions.",
            "I identified a process inefficiency and proposed a solution that was adopted by the team."
        ]
        
        messages = []
        for i, (question, answer) in enumerate(zip(behavioral_questions, behavioral_responses)):
            messages.append({"speaker": "Interviewer", "text": question})
            messages.append({"speaker": "Candidate", "text": answer})
        
        return {"messages": messages}
    
    def _generate_general_transcript(self) -> Dict:
        """Generate general interview transcript."""
        return {
            "messages": [
                {"speaker": "Interviewer", "text": "Tell me about yourself."},
                {"speaker": "Candidate", "text": "I'm a software developer with 3 years of experience."},
                {"speaker": "Interviewer", "text": "Why are you interested in this position?"},
                {"speaker": "Candidate", "text": "I'm excited about the company's mission and technical challenges."}
            ]
        }
    
    def generate_interview_session(self) -> InterviewSession:
        """Generate synthetic interview session."""
        session_id = f"session_{self.fake.uuid4()}"
        candidate_id = f"candidate_{self.fake.uuid4()}"
        job_id = f"job_{self.fake.uuid4()}"
        interviewer_id = f"interviewer_{self.fake.uuid4()}"
        
        interview_types = ["technical", "behavioral", "mixed", "panel"]
        interview_type = random.choice(interview_types)
        
        return InterviewSession(
            session_id=session_id,
            candidate_id=candidate_id,
            candidate_name=self.fake.name(),
            job_id=job_id,
            job_title=random.choice([
                "Senior Software Engineer",
                "Full Stack Developer",
                "Data Scientist",
                "DevOps Engineer",
                "Product Manager"
            ]),
            interviewer_id=interviewer_id,
            interviewer_name=self.fake.name(),
            interview_date=self.fake.date_time_between(start_date="-1y", end_date="now"),
            interview_type=interview_type,
            duration_minutes=random.randint(30, 90),
            status="completed"
        )
    
    def generate_transcript_data(self, session_id: str, candidate_id: str,
                               job_id: str) -> TranscriptData:
        """Generate synthetic transcript data."""
        interview_type = random.choice(["technical", "behavioral", "mixed"])
        duration_minutes = random.randint(30, 90)
        transcript = self.generate_transcript(interview_type, duration_minutes)
        
        # Mock encryption (in real tests, this would use actual encryption)
        encrypted_content = json.dumps(transcript)
        content_hash = f"hash_{self.fake.sha256()}"
        signature = f"sig_{self.fake.sha256()}"
        
        return TranscriptData(
            session_id=session_id,
            candidate_id=candidate_id,
            job_id=job_id,
            interview_type=interview_type,
            duration_minutes=duration_minutes,
            encrypted_content=encrypted_content,
            content_hash=content_hash,
            signature=signature,
            timestamp=datetime.utcnow()
        )
    
    def generate_job_requirements(self, job_title: str) -> List[str]:
        """Generate job requirements based on job title."""
        requirements_map = {
            "Senior Software Engineer": [
                "Python", "Django", "REST APIs", "Database Design", "System Architecture"
            ],
            "Full Stack Developer": [
                "JavaScript", "React", "Node.js", "CSS", "HTML"
            ],
            "Data Scientist": [
                "Python", "Machine Learning", "Statistics", "Data Analysis", "TensorFlow"
            ],
            "DevOps Engineer": [
                "Docker", "Kubernetes", "AWS", "CI/CD", "Linux"
            ],
            "Product Manager": [
                "Product Strategy", "User Research", "Agile", "Stakeholder Management"
            ]
        }
        
        return requirements_map.get(job_title, [
            "Communication", "Problem Solving", "Teamwork", "Leadership"
        ])
    
    def generate_expected_scorecard(self, session_id: str, candidate_id: str,
                                 job_id: str, job_requirements: List[str]) -> Dict:
        """Generate expected scorecard for deterministic testing."""
        # Use deterministic scoring based on session_id
        seed = hash(session_id) % 1000
        random.seed(seed)
        
        skill_score = 60 + (seed % 40)  # 60-100
        clarity_score = 65 + ((seed * 2) % 35)  # 65-100
        competency_score = 70 + ((seed * 3) % 30)  # 70-100
        
        overall_score = round((skill_score + clarity_score + competency_score) / 3, 2)
        
        # Calculate job match based on requirements
        match_score = min(100, overall_score + (len(job_requirements) % 10))
        
        strengths = [
            "Strong technical communication",
            "Problem-solving abilities",
            "Team collaboration skills"
        ][:2 + (seed % 2)]  # 2-3 strengths
        
        weaknesses = [
            "Could improve in specific technical areas",
            "Needs more experience with advanced concepts"
        ][:1]  # Always 1 weakness
        
        return {
            "session_id": session_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "skill_score": skill_score,
            "clarity_score": clarity_score,
            "competency_score": competency_score,
            "overall_score": overall_score,
            "job_match_percentage": match_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "feedback_narrative": f"Candidate demonstrates {strengths[0].lower()} and shows potential for growth.",
            "scoring_methodology": {
                "skill_weight": 0.4,
                "clarity_weight": 0.3,
                "competency_weight": 0.3,
                "bias_protection": "No demographic or emotion-based analysis performed"
            }
        }


class TestScenarios:
    """Predefined test scenarios for comprehensive testing."""
    
    @staticmethod
    def get_high_performer_transcript() -> Dict:
        """Transcript for a high-performing candidate."""
        return {
            "messages": [
                {"speaker": "Interviewer", "text": "Describe your technical experience."},
                {"speaker": "Candidate", "text": "I have 7 years of experience developing scalable web applications using Python, Django, and React. I've led teams of 5+ developers and implemented microservices architecture that improved system performance by 60%."},
                {"speaker": "Interviewer", "text": "How do you handle challenges?"},
                {"speaker": "Candidate", "text": "I approach challenges systematically: first, I analyze the problem thoroughly, then I break it down into manageable components, and finally I implement solutions with proper testing and monitoring. I also communicate clearly with stakeholders throughout the process."}
            ]
        }
    
    @staticmethod
    def get_average_performer_transcript() -> Dict:
        """Transcript for an average-performing candidate."""
        return {
            "messages": [
                {"speaker": "Interviewer", "text": "Describe your technical experience."},
                {"speaker": "Candidate", "text": "I have about 3 years of experience with web development. I've worked with Python and some JavaScript frameworks. I think I can handle most tasks."},
                {"speaker": "Interviewer", "text": "How do you handle challenges?"},
                {"speaker": "Candidate", "text": "Um, I usually try to figure things out. Sometimes I ask for help if I'm stuck. I guess I work through problems step by step."}
            ]
        }
    
    @staticmethod
    def get_low_performer_transcript() -> Dict:
        """Transcript for a low-performing candidate."""
        return {
            "messages": [
                {"speaker": "Interviewer", "text": "Describe your technical experience."},
                {"speaker": "Candidate", "text": "I, like, did some coding in school. Maybe some Python? Not sure. It was okay, I guess."},
                {"speaker": "Interviewer", "text": "How do you handle challenges?"},
                {"speaker": "Candidate", "text": "Uh, I don't know. I usually just try stuff until it works, maybe? Or ask someone else to do it."}
            ]
        }
    
    @staticmethod
    def get_edge_case_transcripts() -> List[Dict]:
        """Get edge case transcripts for testing."""
        return [
            # Empty transcript
            {"messages": []},
            
            # Very short transcript
            {"messages": [{"speaker": "Candidate", "text": "Yes"}]},
            
            # Very long transcript
            {
                "messages": [
                    {"speaker": "Interviewer", "text": f"Question {i}"}
                    for i in range(100)
                ] + [
                    {"speaker": "Candidate", "text": f"Answer {i}"}
                    for i in range(100)
                ]
            },
            
            # Transcript with special characters
            {
                "messages": [
                    {"speaker": "Candidate", "text": "I have experience with C++, Java, Python, SQL, NoSQL, REST APIs, GraphQL, Docker, Kubernetes, AWS, GCP, Azure, CI/CD, TDD, BDD, Agile, Scrum, Kanban."}
                ]
            },
            
            # Transcript with only interviewer
            {
                "messages": [
                    {"speaker": "Interviewer", "text": "Question 1"},
                    {"speaker": "Interviewer", "text": "Question 2"},
                    {"speaker": "Interviewer", "text": "Question 3"}
                ]
            }
        ]


class DeterministicTestConfig:
    """Configuration for deterministic testing."""
    
    # Fixed test data
    TEST_SESSION_ID = "test_session_123"
    TEST_CANDIDATE_ID = "test_candidate_456"
    TEST_JOB_ID = "test_job_789"
    
    # Fixed configuration
    DEFAULT_ANALYTICS_CONFIG = AnalyticsConfig(
        skill_weight=0.4,
        clarity_weight=0.3,
        competency_weight=0.3
    )
    
    # Expected scores for test transcripts
    HIGH_PERFORMER_EXPECTED_SCORES = {
        "skill_score": 90.0,
        "clarity_score": 85.0,
        "competency_score": 88.0,
        "overall_score": 87.67,
        "job_match_percentage": 88.0
    }
    
    AVERAGE_PERFORMER_EXPECTED_SCORES = {
        "skill_score": 65.0,
        "clarity_score": 55.0,
        "competency_score": 60.0,
        "overall_score": 60.0,
        "job_match_percentage": 60.0
    }
    
    LOW_PERFORMER_EXPECTED_SCORES = {
        "skill_score": 30.0,
        "clarity_score": 25.0,
        "competency_score": 35.0,
        "overall_score": 30.0,
        "job_match_percentage": 30.0
    }


# Test fixtures for pytest
@pytest.fixture
def synthetic_data_generator():
    """Provide synthetic data generator for tests."""
    if not MODELS_AVAILABLE:
        pytest.skip("Models not available for testing")
    return SyntheticDataGenerator()


@pytest.fixture
def high_performer_transcript():
    """Provide high performer transcript for testing."""
    return TestScenarios.get_high_performer_transcript()


@pytest.fixture
def average_performer_transcript():
    """Provide average performer transcript for testing."""
    return TestScenarios.get_average_performer_transcript()


@pytest.fixture
def low_performer_transcript():
    """Provide low performer transcript for testing."""
    return TestScenarios.get_low_performer_transcript()


@pytest.fixture
def edge_case_transcripts():
    """Provide edge case transcripts for testing."""
    return TestScenarios.get_edge_case_transcripts()


@pytest.fixture
def deterministic_config():
    """Provide deterministic configuration for testing."""
    if not MODELS_AVAILABLE:
        pytest.skip("Models not available for testing")
    return DeterministicTestConfig()


@pytest.fixture
def sample_job_requirements():
    """Provide sample job requirements for testing."""
    return [
        "Python",
        "Django",
        "REST APIs",
        "Database Design",
        "Communication Skills",
        "Problem Solving"
    ]


# Performance testing utilities
class PerformanceTestUtils:
    """Utilities for performance testing."""
    
    @staticmethod
    def generate_large_dataset(num_sessions: int = 1000) -> List[Dict]:
        """Generate large dataset for performance testing."""
        if not MODELS_AVAILABLE:
            raise ImportError("Models not available for testing")
        
        generator = SyntheticDataGenerator()
        dataset = []
        
        for i in range(num_sessions):
            session = generator.generate_interview_session()
            transcript_data = generator.generate_transcript_data(
                session.session_id, session.candidate_id, session.job_id
            )
            job_requirements = generator.generate_job_requirements(session.job_title)
            
            dataset.append({
                "session": session,
                "transcript": transcript_data,
                "job_requirements": job_requirements
            })
        
        return dataset
    
    @staticmethod
    def measure_processing_time(func, *args, **kwargs):
        """Measure processing time for a function."""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time


# Integration test utilities
class IntegrationTestUtils:
    """Utilities for integration testing."""
    
    @staticmethod
    def create_test_database_config():
        """Create test database configuration."""
        return {
            "host": "localhost",
            "port": 5432,
            "database": "test_eureka_analytics",
            "username": "test_user",
            "password": "test_password"
        }
    
    @staticmethod
    def setup_test_rbac():
        """Setup test RBAC with known users."""
        try:
            from post_interview.auth import RBACManager, UserRole
            rbac = RBACManager("test_secret_key")
            
            # Create test users with known credentials
            rbac.create_user("test_admin", "admin@test.com", "admin123", UserRole.ADMIN)
            rbac.create_user("test_recruiter", "recruiter@test.com", "rec123", UserRole.RECRUITER)
            rbac.create_user("test_interviewer", "interviewer@test.com", "int123", UserRole.INTERVIEWER)
            rbac.create_user("test_viewer", "viewer@test.com", "view123", UserRole.VIEWER)
            
            return rbac
        except ImportError:
            pytest.skip("Auth module not available for testing")
    
    @staticmethod
    def create_mock_fastapi_app():
        """Create mock FastAPI app for testing."""
        from fastapi import FastAPI
        app = FastAPI()
        return app


# Conditional import for pytest
if __name__ == "__main__":
    pytest.main([__file__])