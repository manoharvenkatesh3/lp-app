#!/usr/bin/env python3
"""
Demo script for Post-Interview Analytics System

This script demonstrates the core functionality of the post-interview analytics
system including encryption, scoring, and bias-free evaluation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from Resume_parser.post_interview import (
        AnalyticsConfig,
        InterviewAnalytics,
        TranscriptCrypto,
        TranscriptHasher,
        TranscriptProcessor,
    )
    POST_INTERVIEW_AVAILABLE = True
except ImportError as e:
    print(f"❌ Post-interview analytics not available: {e}")
    print("Please install required dependencies:")
    print("pip install asyncpg cryptography fastapi python-jose passlib")
    POST_INTERVIEW_AVAILABLE = False


def demo_encryption():
    """Demonstrate transcript encryption and integrity verification."""
    print("\n🔐 === Transcript Encryption Demo ===")
    
    if not POST_INTERVIEW_AVAILABLE:
        print("⚠️  Skipping encryption demo - dependencies not available")
        return
    
    # Sample transcript
    transcript = {
        "messages": [
            {"speaker": "Interviewer", "text": "Tell me about your Python experience."},
            {"speaker": "Candidate", "text": "I have 5 years of Python development experience with Django and Flask."}
        ]
    }
    
    print(f"📝 Original transcript: {json.dumps(transcript, indent=2)}")
    
    # Initialize crypto components
    crypto = TranscriptCrypto()
    hasher = TranscriptHasher()
    processor = TranscriptProcessor(crypto, hasher)
    
    # Process transcript
    transcript_data = processor.process_transcript(
        transcript=transcript,
        session_id="demo_session_123",
        candidate_id="demo_candidate_456",
        job_id="demo_job_789",
        interview_type="technical",
        duration_minutes=30
    )
    
    print(f"\n🔒 Encrypted content length: {len(transcript_data.encrypted_content)} characters")
    print(f"🔍 Content hash: {transcript_data.content_hash}")
    print(f"✍️  Signature: {transcript_data.signature}")
    
    # Verify integrity
    is_valid = processor.verify_transcript(transcript_data)
    print(f"✅ Integrity verification: {'PASSED' if is_valid else 'FAILED'}")
    
    # Decrypt and validate
    try:
        decrypted = processor.decrypt_and_validate(transcript_data)
        print(f"🔓 Decryption: SUCCESS")
        print(f"📄 Decrypted matches original: {decrypted == transcript}")
    except Exception as e:
        print(f"❌ Decryption failed: {e}")


def demo_analytics():
    """Demonstrate analytics processing."""
    print("\n📊 === Analytics Processing Demo ===")
    
    if not POST_INTERVIEW_AVAILABLE:
        print("⚠️  Skipping analytics demo - dependencies not available")
        return
    
    # Sample transcripts for different performance levels
    transcripts = {
        "High Performer": {
            "messages": [
                {"speaker": "Interviewer", "text": "Describe your technical experience."},
                {"speaker": "Candidate", "text": "I have 7 years of experience developing scalable web applications using Python and Django. I've led teams of 5+ developers and implemented microservices architecture that improved performance by 60%."}
            ]
        },
        "Average Performer": {
            "messages": [
                {"speaker": "Interviewer", "text": "Describe your technical experience."},
                {"speaker": "Candidate", "text": "I have about 3 years of experience with web development. I've worked with Python and some JavaScript frameworks. I think I can handle most tasks."}
            ]
        },
        "Low Performer": {
            "messages": [
                {"speaker": "Interviewer", "text": "Describe your technical experience."},
                {"speaker": "Candidate", "text": "I, like, did some coding in school. Maybe some Python? Not sure. It was okay, I guess."}
            ]
        }
    }
    
    # Initialize analytics
    config = AnalyticsConfig()
    crypto = TranscriptCrypto()
    hasher = TranscriptHasher()
    processor = TranscriptProcessor(crypto, hasher)
    analytics = InterviewAnalytics(config, processor)
    
    job_requirements = ["Python", "Django", "Web Development", "Communication"]
    
    for performer_type, transcript in transcripts.items():
        print(f"\n🎯 Processing {performer_type}:")
        
        # Process transcript
        transcript_data = processor.process_transcript(
            transcript=transcript,
            session_id=f"session_{performer_type.lower().replace(' ', '_')}",
            candidate_id=f"candidate_{performer_type.lower().replace(' ', '_')}",
            job_id="demo_job_789",
            interview_type="technical",
            duration_minutes=30
        )
        
        # Generate scorecard
        scorecard = analytics.analyze_interview(transcript_data, job_requirements)
        
        # Display results
        print(f"  📈 Overall Score: {scorecard.overall_score:.1f}/100")
        print(f"  🎯 Job Match: {scorecard.job_match_percentage:.1f}%")
        print(f"  🔧 Skills: {scorecard.scoring_axes.skill_score:.1f}/100")
        print(f"  💬 Clarity: {scorecard.scoring_axes.clarity_score:.1f}/100")
        print(f"  🏆 Competency: {scorecard.scoring_axes.competency_score:.1f}/100")
        
        print(f"  💪 Strengths ({len(scorecard.strengths_weaknesses.strengths)}):")
        for strength in scorecard.strengths_weaknesses.strengths:
            print(f"    ✅ {strength}")
        
        print(f"  🎯 Development Areas ({len(scorecard.strengths_weaknesses.weaknesses)}):")
        for weakness in scorecard.strengths_weaknesses.weaknesses:
            print(f"    📈 {weakness}")


def demo_bias_protection():
    """Demonstrate bias-free evaluation."""
    print("\n⚖️  === Bias Protection Demo ===")
    
    if not POST_INTERVIEW_AVAILABLE:
        print("⚠️  Skipping bias protection demo - dependencies not available")
        return
    
    print("✅ Bias Protection Features:")
    print("  🚫 No demographic analysis (age, gender, ethnicity, etc.)")
    print("  🚫 No emotion inference or sentiment analysis")
    print("  🎯 Skills-focused evaluation only")
    print("  🔍 Transparent scoring methodology")
    print("  📊 Evidence-based strengths/weaknesses")
    print("  ⚖️  Consistent scoring algorithms")
    
    # Show scoring methodology
    config = AnalyticsConfig()
    print(f"\n📊 Scoring Configuration:")
    print(f"  🔧 Technical Skills: {config.skill_weight*100:.0f}% weight")
    print(f"  💬 Communication Clarity: {config.clarity_weight*100:.0f}% weight")
    print(f"  🏆 Core Competency: {config.competency_weight*100:.0f}% weight")
    print(f"  📈 Total: {(config.skill_weight + config.clarity_weight + config.competency_weight)*100:.0f}%")


def demo_security_features():
    """Demonstrate security features."""
    print("\n🔒 === Security Features Demo ===")
    
    print("🛡️  Security & Compliance:")
    print("  🔐 AES-256 encryption for transcript storage")
    print("  🔍 SHA-256 hashing for integrity verification")
    print("  ✍️  HMAC signatures for tamper detection")
    print("  🗄️  PostgreSQL database with secure connections")
    print("  📋 Complete audit trail for all operations")
    print("  👥 Role-based access control (RBAC)")
    print("  🔑 JWT authentication with expiration")
    print("  📊 GDPR-compliant data handling")
    print("  🚫 No demographic data storage")


def main():
    """Run the complete demonstration."""
    print("🚀 Eureka Post-Interview Analytics Demo")
    print("=" * 50)
    
    # Check availability
    if not POST_INTERVIEW_AVAILABLE:
        print("\n⚠️  Post-interview analytics module not fully available")
        print("This demo will show limited functionality.")
        print("\nTo install all dependencies:")
        print("pip install asyncpg cryptography fastapi python-jose passlib python-multipart")
    
    # Run demonstrations
    demo_encryption()
    demo_analytics()
    demo_bias_protection()
    demo_security_features()
    
    print("\n" + "=" * 50)
    print("✅ Demo completed!")
    
    if POST_INTERVIEW_AVAILABLE:
        print("\n🎉 Full post-interview analytics system is available!")
        print("📊 Try the new 'Post-Interview Analytics' tab in the Streamlit app")
        print("🔗 Or start the API server: python api_server.py")
    else:
        print("\n📦 Install dependencies to enable full functionality:")
        print("pip install -r requirements.txt")


if __name__ == "__main__":
    main()