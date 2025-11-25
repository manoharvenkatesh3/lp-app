"""Core analytics engine for post-interview processing.

This module provides the main analytics functionality including
strength/weakness extraction, scoring algorithms, and feedback generation.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from .models import (
    AnalyticsConfig,
    ScoreCard,
    ScoringAxes,
    StrengthWeakness,
    TranscriptData,
)
from .crypto import TranscriptProcessor


class TranscriptAnalyzer:
    """Analyzes interview transcripts for insights and scoring."""
    
    def __init__(self, config: AnalyticsConfig):
        self.config = config
        # Skill-related keywords for technical assessment
        self.technical_indicators = {
            'problem_solving': ['solve', 'solution', 'approach', 'method', 'algorithm', 'strategy'],
            'technical_knowledge': ['implement', 'develop', 'code', 'programming', 'framework', 'library'],
            'experience': ['worked', 'built', 'created', 'developed', 'implemented', 'designed'],
            'collaboration': ['team', 'collaborate', 'communicate', 'coordinate', 'work together'],
        }
        
        # Clarity indicators
        self.clarity_indicators = {
            'clear_explanation': ['explain', 'describe', 'clarify', 'elaborate', 'specifically'],
            'structured_response': ['first', 'second', 'finally', 'in conclusion', 'therefore'],
            'concise': ['briefly', 'in short', 'to summarize', 'essentially'],
        }
        
        # Competency indicators
        self.competency_indicators = {
            'leadership': ['lead', 'manage', 'guide', 'mentor', 'supervise'],
            'initiative': ['initiated', 'proposed', 'suggested', 'volunteered', 'took ownership'],
            'adaptability': ['adapted', 'learned', 'adjusted', 'flexible', 'pivot'],
            'problem_solving': ['identified', 'resolved', 'fixed', 'addressed', 'overcame'],
        }
    
    def extract_strengths_weaknesses(self, transcript_text: str) -> StrengthWeakness:
        """Extract strengths and weaknesses from transcript."""
        strengths = []
        weaknesses = []
        evidence = {'strengths': [], 'weaknesses': []}
        
        # Analyze for strengths
        for category, keywords in self.technical_indicators.items():
            matches = self._find_keyword_context(transcript_text, keywords)
            if matches:
                strengths.append(f"Strong {category.replace('_', ' ')} skills")
                evidence['strengths'].extend(matches)
        
        for category, keywords in self.competency_indicators.items():
            matches = self._find_keyword_context(transcript_text, keywords)
            if matches:
                strengths.append(f"Demonstrated {category.replace('_', ' ')}")
                evidence['strengths'].extend(matches)
        
        # Analyze for weaknesses (negative indicators or missing competencies)
        weakness_indicators = {
            'unclear_communication': ['um', 'uh', 'like', 'you know', 'I guess', 'maybe'],
            'lack_of_detail': ['just', 'simply', 'basic', 'nothing special', 'regular'],
            'uncertainty': ['not sure', 'maybe', 'perhaps', 'I think', 'probably'],
        }
        
        for category, keywords in weakness_indicators.items():
            matches = self._find_keyword_context(transcript_text, keywords)
            if len(matches) > 3:  # Threshold for weakness identification
                weaknesses.append(f"Areas for improvement in {category.replace('_', ' ')}")
                evidence['weaknesses'].extend(matches)
        
        # Check for missing key competencies
        all_competency_keywords = []
        for keywords in self.competency_indicators.values():
            all_competency_keywords.extend(keywords)
        
        if not any(keyword in transcript_text.lower() for keyword in all_competency_keywords):
            weaknesses.append("Limited demonstration of core competencies")
            evidence['weaknesses'].append("Few competency-related keywords found in responses")
        
        return StrengthWeakness(
            strengths=strengths[:5],  # Limit to top 5
            weaknesses=weaknesses[:3],  # Limit to top 3
            evidence=evidence
        )
    
    def _find_keyword_context(self, text: str, keywords: List[str], 
                            context_window: int = 50) -> List[str]:
        """Find keywords and return surrounding context."""
        text_lower = text.lower()
        contexts = []
        
        for keyword in keywords:
            start = 0
            while True:
                pos = text_lower.find(keyword, start)
                if pos == -1:
                    break
                
                # Extract context
                start_context = max(0, pos - context_window)
                end_context = min(len(text), pos + len(keyword) + context_window)
                context = text[start_context:end_context].strip()
                
                if context and context not in contexts:
                    contexts.append(context)
                
                start = pos + 1
        
        return contexts
    
    def calculate_skill_score(self, transcript_text: str, job_requirements: List[str]) -> float:
        """Calculate technical skill score based on transcript and job requirements."""
        if not job_requirements:
            return 50.0  # Default score if no requirements
        
        # Extract technical terms from transcript
        technical_terms = []
        for category, keywords in self.technical_indicators.items():
            technical_terms.extend(keywords)
        
        # Add job requirements to technical terms
        technical_terms.extend([req.lower() for req in job_requirements])
        
        # Count matches
        transcript_lower = transcript_text.lower()
        matches = sum(1 for term in technical_terms if term in transcript_lower)
        
        # Calculate score (0-100)
        max_possible = len(technical_terms)
        if max_possible == 0:
            return 50.0
        
        raw_score = (matches / max_possible) * 100
        return min(100.0, max(0.0, raw_score))
    
    def calculate_clarity_score(self, transcript_text: str) -> float:
        """Calculate communication clarity score."""
        clarity_score = 50.0  # Base score
        
        # Positive indicators
        for category, keywords in self.clarity_indicators.items():
            matches = self._find_keyword_context(transcript_text, keywords)
            clarity_score += len(matches) * 2  # Add points for clarity indicators
        
        # Negative indicators (filler words, uncertainty)
        negative_indicators = ['um', 'uh', 'like', 'you know', 'not sure', 'maybe']
        negative_count = sum(transcript_text.lower().count(indicator) 
                           for indicator in negative_indicators)
        clarity_score -= negative_count * 1  # Subtract points for negative indicators
        
        return min(100.0, max(0.0, clarity_score))
    
    def calculate_competency_score(self, transcript_text: str) -> float:
        """Calculate overall competency score."""
        competency_score = 50.0  # Base score
        
        # Positive indicators
        for category, keywords in self.competency_indicators.items():
            matches = self._find_keyword_context(transcript_text, keywords)
            competency_score += len(matches) * 3  # Add points for competency indicators
        
        return min(100.0, max(0.0, competency_score))
    
    def calculate_job_match_percentage(self, skill_score: float, clarity_score: float,
                                     competency_score: float) -> float:
        """Calculate overall job match percentage using configured weights."""
        weighted_score = (
            skill_score * self.config.skill_weight +
            clarity_score * self.config.clarity_weight +
            competency_score * self.config.competency_weight
        )
        return round(weighted_score, 2)


class PostInterviewProcessor:
    """Main processor for post-interview analytics."""
    
    def __init__(self, analyzer: TranscriptAnalyzer, 
                 transcript_processor: TranscriptProcessor):
        self.analyzer = analyzer
        self.transcript_processor = transcript_processor
    
    def process_interview(self, transcript_data: TranscriptData,
                         job_requirements: List[str]) -> ScoreCard:
        """Process complete interview and generate scorecard."""
        # Decrypt and validate transcript
        transcript_dict = self.transcript_processor.decrypt_and_validate(transcript_data)
        
        # Convert to text for analysis
        transcript_text = self._transcript_to_text(transcript_dict)
        
        # Extract strengths and weaknesses
        strengths_weaknesses = self.analyzer.extract_strengths_weaknesses(transcript_text)
        
        # Calculate scores
        skill_score = self.analyzer.calculate_skill_score(transcript_text, job_requirements)
        clarity_score = self.analyzer.calculate_clarity_score(transcript_text)
        competency_score = self.analyzer.calculate_competency_score(transcript_text)
        
        # Create scoring axes
        scoring_axes = ScoringAxes(
            skill_score=skill_score,
            clarity_score=clarity_score,
            competency_score=competency_score
        )
        
        # Calculate job match percentage
        job_match = self.analyzer.calculate_job_match_percentage(
            skill_score, clarity_score, competency_score
        )
        
        # Generate feedback narrative
        feedback_narrative = self._generate_feedback_narrative(
            scoring_axes, strengths_weaknesses, job_match
        )
        
        # Create scoring methodology documentation
        scoring_methodology = self._create_scoring_methodology(
            scoring_axes, strengths_weaknesses, job_requirements
        )
        
        # Calculate overall score
        overall_score = round((skill_score + clarity_score + competency_score) / 3, 2)
        
        return ScoreCard(
            session_id=transcript_data.session_id,
            candidate_id=transcript_data.candidate_id,
            job_id=transcript_data.job_id,
            scoring_axes=scoring_axes,
            overall_score=overall_score,
            job_match_percentage=job_match,
            strengths_weaknesses=strengths_weaknesses,
            feedback_narrative=feedback_narrative,
            scoring_methodology=scoring_methodology
        )
    
    def _transcript_to_text(self, transcript_dict: Dict) -> str:
        """Convert transcript dictionary to analyzable text."""
        text_parts = []
        
        # Handle different transcript formats
        if 'messages' in transcript_dict:
            # Format: [{"speaker": "Interviewer", "text": "..."}, ...]
            for message in transcript_dict['messages']:
                if isinstance(message, dict) and 'text' in message:
                    text_parts.append(message['text'])
        
        elif 'exchanges' in transcript_dict:
            # Format: [{"question": "...", "answer": "..."}, ...]
            for exchange in transcript_dict['exchanges']:
                if isinstance(exchange, dict):
                    if 'answer' in exchange:
                        text_parts.append(exchange['answer'])
                    if 'question' in exchange:
                        text_parts.append(exchange['question'])
        
        elif 'raw_text' in transcript_dict:
            # Raw text format
            text_parts.append(transcript_dict['raw_text'])
        
        else:
            # Assume it's a simple string or dict that can be converted
            text_parts.append(str(transcript_dict))
        
        return ' '.join(text_parts)
    
    def _generate_feedback_narrative(self, scoring_axes: ScoringAxes,
                                    strengths_weaknesses: StrengthWeakness,
                                    job_match_percentage: float) -> str:
        """Generate comprehensive feedback narrative."""
        narrative_parts = []
        
        # Overall assessment
        if job_match_percentage >= 80:
            narrative_parts.append("The candidate demonstrates strong alignment with the position requirements.")
        elif job_match_percentage >= 60:
            narrative_parts.append("The candidate shows moderate alignment with the position requirements.")
        else:
            narrative_parts.append("The candidate may require additional development for this position.")
        
        # Skill assessment
        if scoring_axes.skill_score >= 80:
            narrative_parts.append("Technical skills are well-developed and relevant to the role.")
        elif scoring_axes.skill_score >= 60:
            narrative_parts.append("Technical skills are adequate with room for growth.")
        else:
            narrative_parts.append("Technical skills require further development.")
        
        # Communication assessment
        if scoring_axes.clarity_score >= 80:
            narrative_parts.append("Communication is clear, structured, and effective.")
        elif scoring_axes.clarity_score >= 60:
            narrative_parts.append("Communication is generally clear with occasional ambiguity.")
        else:
            narrative_parts.append("Communication clarity needs improvement.")
        
        # Competency assessment
        if scoring_axes.competency_score >= 80:
            narrative_parts.append("Core competencies are strongly demonstrated.")
        elif scoring_axes.competency_score >= 60:
            narrative_parts.append("Core competencies are adequately demonstrated.")
        else:
            narrative_parts.append("Core competencies require further development.")
        
        # Strengths
        if strengths_weaknesses.strengths:
            narrative_parts.append(f"Key strengths include: {', '.join(strengths_weaknesses.strengths)}.")
        
        # Areas for improvement
        if strengths_weaknesses.weaknesses:
            narrative_parts.append(f"Areas for development include: {', '.join(strengths_weaknesses.weaknesses)}.")
        
        return ' '.join(narrative_parts)
    
    def _create_scoring_methodology(self, scoring_axes: ScoringAxes,
                                  strengths_weaknesses: StrengthWeakness,
                                  job_requirements: List[str]) -> Dict:
        """Create transparent scoring methodology documentation."""
        return {
            "scoring_model": "Bias-free multi-axis evaluation",
            "skill_weight": self.analyzer.config.skill_weight,
            "clarity_weight": self.analyzer.config.clarity_weight,
            "competency_weight": self.analyzer.config.competency_weight,
            "skill_score": scoring_axes.skill_score,
            "clarity_score": scoring_axes.clarity_score,
            "competency_score": scoring_axes.competency_score,
            "job_requirements": job_requirements,
            "strengths_identified": len(strengths_weaknesses.strengths),
            "weaknesses_identified": len(strengths_weaknesses.weaknesses),
            "evidence_sources": len(strengths_weaknesses.evidence.get('strengths', [])) + 
                               len(strengths_weaknesses.evidence.get('weaknesses', [])),
            "bias_protection": "No demographic or emotion-based analysis performed",
            "technical_indicators": list(self.analyzer.technical_indicators.keys()),
            "clarity_indicators": list(self.analyzer.clarity_indicators.keys()),
            "competency_indicators": list(self.analyzer.competency_indicators.keys())
        }


class InterviewAnalytics:
    """High-level interface for interview analytics operations."""
    
    def __init__(self, config: AnalyticsConfig,
                 transcript_processor: TranscriptProcessor):
        self.config = config
        self.transcript_processor = transcript_processor
        self.analyzer = TranscriptAnalyzer(config)
        self.processor = PostInterviewProcessor(self.analyzer, transcript_processor)
    
    def analyze_interview(self, transcript_data: TranscriptData,
                         job_requirements: List[str]) -> ScoreCard:
        """Analyze interview and return comprehensive scorecard."""
        return self.processor.process_interview(transcript_data, job_requirements)
    
    def batch_analyze(self, transcripts_data: List[TranscriptData],
                     job_requirements: List[str]) -> List[ScoreCard]:
        """Analyze multiple interviews in batch."""
        scorecards = []
        for transcript_data in transcripts_data:
            try:
                scorecard = self.analyze_interview(transcript_data, job_requirements)
                scorecards.append(scorecard)
            except Exception as e:
                # Log error and continue with next transcript
                print(f"Error analyzing transcript {transcript_data.session_id}: {e}")
                continue
        
        return scorecards