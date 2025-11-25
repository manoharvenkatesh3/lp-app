"""Unit tests for post-interview analytics.

This module contains comprehensive tests for the post-interview analytics
system including encryption, scoring, and audit logging.
"""

from __future__ import annotations

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

try:
    from post_interview.analytics import (
        InterviewAnalytics,
        PostInterviewProcessor,
        ScoreCard,
        TranscriptAnalyzer,
    )
    from post_interview.auth import RBACManager, UserRole
    from post_interview.background import BackgroundTaskManager, TaskStatus
    from post_interview.crypto import TranscriptCrypto, TranscriptHasher, TranscriptProcessor
    from post_interview.database import AnalyticsDatabase, AuditLogger
    from post_interview.models import (
        AnalyticsConfig,
        InterviewSession,
        ScoringAxes,
        StrengthWeakness,
        TranscriptData,
    )
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False


class TestTranscriptCrypto:
    """Test transcript encryption and decryption."""
    
    @pytest.fixture(autouse=True)
    def check_analytics_available(self):
        if not ANALYTICS_AVAILABLE:
            pytest.skip("Post-interview analytics not available")
    
    def test_encrypt_decrypt_transcript(self):
        """Test basic encrypt/decrypt functionality."""
        crypto = TranscriptCrypto()
        
        transcript = {
            "messages": [
                {"speaker": "Interviewer", "text": "Tell me about your experience."},
                {"speaker": "Candidate", "text": "I have 5 years of experience in Python development."}
            ]
        }
        
        # Encrypt
        encrypted_content, _ = crypto.encrypt_transcript(transcript)
        
        # Verify encryption
        assert encrypted_content != str(transcript)
        assert len(encrypted_content) > 0
        
        # Decrypt
        decrypted = crypto.decrypt_transcript(encrypted_content)
        
        # Verify decryption
        assert decrypted == transcript
    
    def test_rsa_key_generation(self):
        """Test RSA key pair generation."""
        private_key, public_key = TranscriptCrypto.generate_rsa_keypair()
        
        assert "-----BEGIN PRIVATE KEY-----" in private_key
        assert "-----END PRIVATE KEY-----" in private_key
        assert "-----BEGIN PUBLIC KEY-----" in public_key
        assert "-----END PUBLIC KEY-----" in public_key


class TestTranscriptHasher:
    """Test transcript hashing and integrity verification."""
    
    def test_content_hash(self):
        """Test content hash computation."""
        content = "This is test content"
        hash1 = TranscriptHasher.compute_content_hash(content)
        hash2 = TranscriptHasher.compute_content_hash(content)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length
    
    def test_integrity_verification(self):
        """Test integrity verification."""
        content = "Original content"
        hash_value = TranscriptHasher.compute_content_hash(content)
        
        # Verify with correct content
        assert TranscriptHasher.verify_integrity(content, hash_value) is True
        
        # Verify with modified content
        assert TranscriptHasher.verify_integrity("Modified content", hash_value) is False
    
    def test_hmac_signature(self):
        """Test HMAC signature creation and verification."""
        content = "Test message"
        secret_key = "test_secret"
        
        signature = TranscriptHasher.create_hmac_signature(content, secret_key)
        
        # Verify correct signature
        assert TranscriptHasher.verify_hmac_signature(content, signature, secret_key) is True
        
        # Verify with wrong content
        assert TranscriptHasher.verify_hmac_signature("Wrong content", signature, secret_key) is False
        
        # Verify with wrong key
        assert TranscriptHasher.verify_hmac_signature(content, signature, "wrong_key") is False


class TestTranscriptProcessor:
    """Test high-level transcript processing."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.crypto = TranscriptCrypto()
        self.hasher = TranscriptHasher()
        self.processor = TranscriptProcessor(self.crypto, self.hasher)
    
    def test_process_transcript(self):
        """Test complete transcript processing."""
        transcript = {
            "messages": [
                {"speaker": "Interviewer", "text": "What's your experience with Python?"},
                {"speaker": "Candidate", "text": "I've worked with Python for 5 years."}
            ]
        }
        
        transcript_data = self.processor.process_transcript(
            transcript=transcript,
            session_id="session_123",
            candidate_id="candidate_456",
            job_id="job_789",
            interview_type="technical",
            duration_minutes=45
        )
        
        assert transcript_data.session_id == "session_123"
        assert transcript_data.candidate_id == "candidate_456"
        assert transcript_data.job_id == "job_789"
        assert transcript_data.interview_type == "technical"
        assert transcript_data.duration_minutes == 45
        assert len(transcript_data.encrypted_content) > 0
        assert len(transcript_data.content_hash) == 64
        assert transcript_data.signature is not None
    
    def test_verify_transcript(self):
        """Test transcript verification."""
        transcript = {"test": "data"}
        transcript_data = self.processor.process_transcript(
            transcript=transcript,
            session_id="session_123",
            candidate_id="candidate_456",
            job_id="job_789",
            interview_type="technical",
            duration_minutes=30
        )
        
        # Verify valid transcript
        assert self.processor.verify_transcript(transcript_data) is True
        
        # Tamper with encrypted content
        transcript_data.encrypted_content = "tampered_content"
        assert self.processor.verify_transcript(transcript_data) is False
    
    def test_decrypt_and_validate(self):
        """Test decryption and validation."""
        original_transcript = {"messages": [{"text": "Test message"}]}
        transcript_data = self.processor.process_transcript(
            transcript=original_transcript,
            session_id="session_123",
            candidate_id="candidate_456",
            job_id="job_789",
            interview_type="technical",
            duration_minutes=30
        )
        
        # Successful decryption and validation
        decrypted = self.processor.decrypt_and_validate(transcript_data)
        assert decrypted == original_transcript
        
        # Tampered transcript should raise error
        transcript_data.encrypted_content = "invalid"
        with pytest.raises(ValueError, match="integrity verification failed"):
            self.processor.decrypt_and_validate(transcript_data)


class TestTranscriptAnalyzer:
    """Test transcript analysis functionality."""
    
    def setup_method(self):
        """Setup test configuration."""
        self.config = AnalyticsConfig()
        self.analyzer = TranscriptAnalyzer(self.config)
    
    def test_extract_strengths_weaknesses(self):
        """Test strengths and weaknesses extraction."""
        transcript_text = """
        I have extensive experience developing web applications using Python and Django.
        I've led a team of 5 developers and successfully delivered multiple projects.
        I implemented a solution that improved performance by 40%.
        I can solve complex problems and work well with my team.
        Um, uh, I think I can handle the requirements, maybe.
        """
        
        result = self.analyzer.extract_strengths_weaknesses(transcript_text)
        
        assert isinstance(result, StrengthWeakness)
        assert len(result.strengths) > 0
        assert len(result.weaknesses) >= 0
        assert 'strengths' in result.evidence
        assert 'weaknesses' in result.evidence
    
    def test_calculate_skill_score(self):
        """Test technical skill score calculation."""
        transcript_text = """
        I have experience with Python, Django, and PostgreSQL.
        I've implemented RESTful APIs and worked with microservices.
        I developed a machine learning model using scikit-learn.
        """
        job_requirements = ["Python", "Django", "REST APIs", "Machine Learning"]
        
        score = self.analyzer.calculate_skill_score(transcript_text, job_requirements)
        
        assert 0 <= score <= 100
        assert score > 50  # Should be relatively high for this transcript
    
    def test_calculate_clarity_score(self):
        """Test communication clarity score calculation."""
        # Clear transcript
        clear_text = """
        First, I analyzed the requirements. Second, I designed the solution.
        Finally, I implemented the system with proper error handling.
        """
        
        # Unclear transcript
        unclear_text = """
        Um, uh, like, I think I did, you know, the thing, maybe.
        I guess it worked, I'm not sure, probably.
        """
        
        clear_score = self.analyzer.calculate_clarity_score(clear_text)
        unclear_score = self.analyzer.calculate_clarity_score(unclear_text)
        
        assert 0 <= clear_score <= 100
        assert 0 <= unclear_score <= 100
        assert clear_score > unclear_score
    
    def test_calculate_competency_score(self):
        """Test competency score calculation."""
        competency_text = """
        I led a team of 5 developers on a major project.
        I initiated a new process that improved efficiency by 30%.
        I adapted to changing requirements and delivered on time.
        I identified and resolved critical issues in the system.
        """
        
        score = self.analyzer.calculate_competency_score(competency_text)
        
        assert 0 <= score <= 100
        assert score > 50  # Should be high for this transcript
    
    def test_calculate_job_match_percentage(self):
        """Test job match percentage calculation."""
        skill_score = 85.0
        clarity_score = 75.0
        competency_score = 80.0
        
        match_percentage = self.analyzer.calculate_job_match_percentage(
            skill_score, clarity_score, competency_score
        )
        
        assert 0 <= match_percentage <= 100
        
        # Should be weighted average based on config
        expected = (
            skill_score * self.config.skill_weight +
            clarity_score * self.config.clarity_weight +
            competency_score * self.config.competency_weight
        )
        assert abs(match_percentage - expected) < 0.01


class TestPostInterviewProcessor:
    """Test post-interview processing pipeline."""
    
    def setup_method(self):
        """Setup test dependencies."""
        self.config = AnalyticsConfig()
        self.crypto = TranscriptCrypto()
        self.hasher = TranscriptHasher()
        self.transcript_processor = TranscriptProcessor(self.crypto, self.hasher)
        self.analyzer = TranscriptAnalyzer(self.config)
        self.processor = PostInterviewProcessor(self.analyzer, self.transcript_processor)
    
    def test_process_interview(self):
        """Test complete interview processing."""
        # Create test transcript data
        transcript_dict = {
            "messages": [
                {"speaker": "Interviewer", "text": "Tell me about your Python experience."},
                {"speaker": "Candidate", "text": "I've worked with Python for 5 years, developing web applications with Django."}
            ]
        }
        
        transcript_data = self.transcript_processor.process_transcript(
            transcript=transcript_dict,
            session_id="session_123",
            candidate_id="candidate_456",
            job_id="job_789",
            interview_type="technical",
            duration_minutes=45
        )
        
        job_requirements = ["Python", "Django", "Web Development"]
        
        # Process interview
        scorecard = self.processor.process_interview(transcript_data, job_requirements)
        
        # Verify scorecard
        assert isinstance(scorecard, ScoreCard)
        assert scorecard.session_id == "session_123"
        assert scorecard.candidate_id == "candidate_456"
        assert scorecard.job_id == "job_789"
        assert 0 <= scorecard.overall_score <= 100
        assert 0 <= scorecard.job_match_percentage <= 100
        assert len(scorecard.feedback_narrative) > 0
        assert len(scorecard.scoring_methodology) > 0
    
    def test_transcript_to_text_conversion(self):
        """Test transcript to text conversion."""
        # Test messages format
        transcript_dict = {
            "messages": [
                {"speaker": "Interviewer", "text": "Question 1"},
                {"speaker": "Candidate", "text": "Answer 1"}
            ]
        }
        
        text = self.processor._transcript_to_text(transcript_dict)
        assert "Question 1" in text
        assert "Answer 1" in text
        
        # Test exchanges format
        transcript_dict = {
            "exchanges": [
                {"question": "Question 2", "answer": "Answer 2"}
            ]
        }
        
        text = self.processor._transcript_to_text(transcript_dict)
        assert "Question 2" in text
        assert "Answer 2" in text
        
        # Test raw text format
        transcript_dict = {
            "raw_text": "Raw transcript content"
        }
        
        text = self.processor._transcript_to_text(transcript_dict)
        assert text == "Raw transcript content"


class TestRBACManager:
    """Test role-based access control."""
    
    def setup_method(self):
        """Setup RBAC manager."""
        self.rbac = RBACManager("test_secret_key")
    
    def test_user_creation_and_authentication(self):
        """Test user creation and authentication."""
        # Create user
        user = self.rbac.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role=UserRole.RECRUITER
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.RECRUITER
        
        # Test successful authentication
        auth_user = self.rbac.authenticate_user("testuser", "testpass123")
        assert auth_user is not None
        assert auth_user.user_id == user.user_id
        
        # Test failed authentication
        auth_user = self.rbac.authenticate_user("testuser", "wrongpass")
        assert auth_user is None
    
    def test_token_generation_and_verification(self):
        """Test JWT token generation and verification."""
        user = self.rbac.create_user(
            username="tokenuser",
            email="token@example.com",
            password="tokenpass123",
            role=UserRole.ADMIN
        )
        
        # Generate token
        token = self.rbac.generate_token(user)
        assert len(token) > 0
        
        # Verify token
        payload = self.rbac.verify_token(token)
        assert payload is not None
        assert payload["user_id"] == user.user_id
        assert payload["username"] == user.username
        assert payload["role"] == UserRole.ADMIN.value
    
    def test_permission_checking(self):
        """Test permission checking."""
        # Test admin permissions
        admin_user = self.rbac.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            role=UserRole.ADMIN
        )
        
        assert self.rbac.has_permission(admin_user, "read", "all") is True
        assert self.rbac.has_permission(admin_user, "write", "all") is True
        assert self.rbac.has_permission(admin_user, "delete", "all") is True
        
        # Test recruiter permissions
        recruiter_user = self.rbac.create_user(
            username="recruiter",
            email="recruiter@example.com",
            password="recruiterpass",
            role=UserRole.RECRUITER
        )
        
        assert self.rbac.has_permission(recruiter_user, "read", "scorecards") is True
        assert self.rbac.has_permission(recruiter_user, "write", "scorecards") is True
        assert self.rbac.has_permission(recruiter_user, "delete", "scorecards") is False
        assert self.rbac.has_permission(recruiter_user, "manage_users", "all") is False


@pytest.mark.asyncio
class TestBackgroundTaskManager:
    """Test background task management."""
    
    async def test_task_submission_and_execution(self):
        """Test task submission and execution."""
        # Mock database
        mock_db = AsyncMock()
        mock_db.pool = AsyncMock()
        
        # Create task manager
        task_manager = BackgroundTaskManager(mock_db)
        
        # Register test handler
        async def test_handler(task_id: str, task_data: dict):
            return {"status": "completed", "task_id": task_id}
        
        task_manager.register_task_handler("test_task", test_handler)
        
        # Submit task
        task_id = await task_manager.submit_task(
            task_type="test_task",
            session_id="session_123",
            task_data={"test": "data"}
        )
        
        assert task_id is not None
        assert len(task_id) > 0
        
        # Get task status
        task = await task_manager.get_task_status(task_id)
        assert task is not None
        assert task.task_id == task_id
        assert task.task_type == "test_task"
    
    async def test_task_statistics(self):
        """Test task statistics."""
        mock_db = AsyncMock()
        mock_db.pool = AsyncMock()
        
        task_manager = BackgroundTaskManager(mock_db)
        
        # Get initial statistics
        stats = task_manager.get_task_statistics()
        assert "total_tasks" in stats
        assert "completed_tasks" in stats
        assert "failed_tasks" in stats
        assert "success_rate" in stats
        assert "active_tasks" in stats
        assert "queued_tasks" in stats


@pytest.mark.asyncio
class TestAuditLogger:
    """Test audit logging functionality."""
    
    async def test_audit_log_creation(self):
        """Test audit log entry creation."""
        # Mock database
        mock_db = AsyncMock()
        mock_db.pool = AsyncMock()
        
        # Create audit logger
        audit_logger = AuditLogger(mock_db)
        
        # Create audit table
        await audit_logger.create_audit_table()
        
        # Log access
        await audit_logger.log_access(
            user_id="user_123",
            user_role=UserRole.RECRUITER,
            resource_type="scorecards",
            resource_id="scorecard_456",
            session_id="session_789"
        )
        
        # Verify database call was made
        mock_db.pool.acquire.assert_called()
    
    async def test_audit_trail_retrieval(self):
        """Test audit trail retrieval."""
        mock_db = AsyncMock()
        mock_db.pool = AsyncMock()
        
        # Setup mock response
        mock_rows = [
            {
                "log_id": "audit_1",
                "user_id": "user_123",
                "action": "ACCESS",
                "resource_type": "scorecards",
                "resource_id": "scorecard_456",
                "timestamp": datetime.utcnow()
            }
        ]
        
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = mock_rows
        mock_db.pool.acquire.return_value.__aenter__.return_value = mock_conn
        
        audit_logger = AuditLogger(mock_db)
        
        # Get audit trail
        trail = await audit_logger.get_audit_trail("scorecards", "scorecard_456")
        
        assert len(trail) == 1
        assert trail[0]["log_id"] == "audit_1"
        assert trail[0]["user_id"] == "user_123"


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_full_analytics_pipeline(self):
        """Test the complete analytics pipeline."""
        # Setup components
        config = AnalyticsConfig()
        crypto = TranscriptCrypto()
        hasher = TranscriptHasher()
        transcript_processor = TranscriptProcessor(crypto, hasher)
        analytics = InterviewAnalytics(config, transcript_processor)
        
        # Create test transcript
        transcript_dict = {
            "messages": [
                {"speaker": "Interviewer", "text": "What's your experience with Python?"},
                {"speaker": "Candidate", "text": "I have 5 years of Python experience, working with Django and Flask."}
            ]
        }
        
        transcript_data = transcript_processor.process_transcript(
            transcript=transcript_dict,
            session_id="session_integration",
            candidate_id="candidate_integration",
            job_id="job_integration",
            interview_type="technical",
            duration_minutes=30
        )
        
        job_requirements = ["Python", "Django", "Web Development"]
        
        # Process analytics
        scorecard = analytics.analyze_interview(transcript_data, job_requirements)
        
        # Verify complete pipeline
        assert isinstance(scorecard, ScoreCard)
        assert scorecard.session_id == "session_integration"
        assert 0 <= scorecard.overall_score <= 100
        assert 0 <= scorecard.job_match_percentage <= 100
        assert len(scorecard.feedback_narrative) > 0
        assert "bias_protection" in scorecard.scoring_methodology
    
    def test_synthetic_transcript_scoring(self):
        """Test scoring with synthetic transcripts for deterministic results."""
        config = AnalyticsConfig()
        crypto = TranscriptCrypto()
        hasher = TranscriptHasher()
        transcript_processor = TranscriptProcessor(crypto, hasher)
        analytics = InterviewAnalytics(config, transcript_processor)
        
        # Create deterministic synthetic transcript
        synthetic_transcript = {
            "messages": [
                {"speaker": "Interviewer", "text": "Describe your technical skills."},
                {"speaker": "Candidate", "text": "I have strong Python skills with Django framework experience."},
                {"speaker": "Interviewer", "text": "How do you handle team collaboration?"},
                {"speaker": "Candidate", "text": "I communicate clearly and work well with my team members."}
            ]
        }
        
        transcript_data = transcript_processor.process_transcript(
            transcript=synthetic_transcript,
            session_id="synthetic_session",
            candidate_id="synthetic_candidate",
            job_id="synthetic_job",
            interview_type="technical",
            duration_minutes=25
        )
        
        job_requirements = ["Python", "Django", "Communication"]
        
        # Process multiple times to ensure deterministic results
        scorecards = []
        for _ in range(3):
            scorecard = analytics.analyze_interview(transcript_data, job_requirements)
            scorecards.append(scorecard)
        
        # Verify deterministic scoring
        first_score = scorecards[0].overall_score
        for scorecard in scorecards[1:]:
            assert scorecard.overall_score == first_score
            assert scorecard.job_match_percentage == scorecards[0].job_match_percentage


if __name__ == "__main__":
    pytest.main([__file__])