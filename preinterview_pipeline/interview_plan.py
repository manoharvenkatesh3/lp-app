"""Interview plan generator based on gap analysis and competency assessment."""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from .models import (
    GapAnalysisResult,
    InterviewPlan,
    InterviewQuestion,
    SkillGap,
    SkillLevel,
)

logger = logging.getLogger(__name__)


class InterviewPlanGenerator:
    """Generate structured interview plans based on gap analysis."""

    # Competency categories
    COMPETENCIES = {
        "technical_depth": "Technical depth and specialization",
        "problem_solving": "Problem-solving and analytical thinking",
        "communication": "Communication and collaboration",
        "leadership": "Leadership and ownership",
        "learning_agility": "Learning agility and adaptability",
        "domain_expertise": "Domain expertise and industry knowledge",
    }

    def __init__(self):
        """Initialize interview plan generator."""
        pass

    def generate_plan(
        self,
        candidate_id: str,
        job_id: str,
        gap_analysis: GapAnalysisResult,
        interview_format: str = "full_loop",
    ) -> InterviewPlan:
        """
        Generate interview plan for candidate-job pairing.

        Args:
            candidate_id: Candidate ID
            job_id: Job ID
            gap_analysis: Gap analysis results
            interview_format: Interview format (phone_screen, technical, full_loop, executive)

        Returns:
            Generated interview plan
        """
        plan_id = f"IP-{uuid.uuid4().hex[:12]}"

        # Determine focus based on readiness level
        interview_focus = self._determine_focus(gap_analysis, interview_format)

        # Select competencies to assess
        competency_focus = self._select_competencies(gap_analysis, interview_format)

        # Generate questions for each competency
        questions = self._generate_questions(
            gap_analysis=gap_analysis,
            competencies=competency_focus,
            interview_format=interview_format,
        )

        # Set interview duration based on format
        duration_minutes = {
            "phone_screen": 30,
            "technical": 60,
            "full_loop": 180,  # 3 hours with breaks
            "executive": 45,
        }.get(interview_format, 60)

        # Generate guidance for critical gaps
        critical_gap_exploration = self._guidance_for_critical_gaps(gap_analysis.critical_gaps)
        strength_validation = self._guidance_for_strengths(gap_analysis.strengths)

        # Identify risk indicators
        risk_indicators = self._identify_risk_indicators(gap_analysis)

        plan = InterviewPlan(
            plan_id=plan_id,
            candidate_id=candidate_id,
            job_id=job_id,
            interview_focus=interview_focus,
            interview_duration_minutes=duration_minutes,
            competency_focus=competency_focus,
            questions=questions,
            critical_gap_exploration=critical_gap_exploration,
            strength_validation=strength_validation,
            risk_indicators=risk_indicators,
        )

        return plan

    def _determine_focus(self, gap_analysis: GapAnalysisResult, interview_format: str) -> str:
        """Determine primary focus of interview based on gap analysis and format."""
        readiness = gap_analysis.readiness_level

        if interview_format == "phone_screen":
            return "Screen for basic qualifications and communication skills"

        if interview_format == "technical":
            if gap_analysis.critical_gaps:
                return f"Assess technical depth in {gap_analysis.critical_gaps[0].skill_name}"
            return "Evaluate technical problem-solving abilities"

        if interview_format == "executive":
            return "Evaluate strategic thinking and leadership potential"

        # Full loop
        if readiness == "ready":
            return "Validate expertise and cultural fit"
        elif readiness == "trainable":
            return f"Assess potential to close gaps in {self._gap_summary(gap_analysis)}"
        else:
            return f"Deep dive into {self._gap_summary(gap_analysis)} and learn aspirations"

    def _gap_summary(self, gap_analysis: GapAnalysisResult) -> str:
        """Create a short summary of key gaps."""
        if gap_analysis.critical_gaps:
            return gap_analysis.critical_gaps[0].skill_name
        if gap_analysis.significant_gaps:
            return gap_analysis.significant_gaps[0].skill_name
        return "core competencies"

    def _select_competencies(self, gap_analysis: GapAnalysisResult, interview_format: str) -> list[str]:
        """Select competencies to focus on during interview."""
        selected = []

        if interview_format == "phone_screen":
            selected = ["communication", "learning_agility"]
        elif interview_format == "technical":
            selected = ["technical_depth", "problem_solving"]
        elif interview_format == "executive":
            selected = ["leadership", "domain_expertise"]
        else:  # full_loop
            selected = [
                "technical_depth",
                "problem_solving",
                "communication",
                "domain_expertise",
            ]

        # Add learning_agility if there are significant gaps
        if gap_analysis.significant_gaps or gap_analysis.critical_gaps:
            if "learning_agility" not in selected:
                selected.append("learning_agility")

        return selected

    def _generate_questions(
        self,
        gap_analysis: GapAnalysisResult,
        competencies: list[str],
        interview_format: str,
    ) -> list[InterviewQuestion]:
        """Generate interview questions based on competencies and gaps."""
        questions: list[InterviewQuestion] = []
        question_id_counter = 1

        # Generate questions for each competency
        for competency in competencies:
            comp_questions = self._questions_for_competency(
                competency=competency,
                gap_analysis=gap_analysis,
                interview_format=interview_format,
            )

            for q_text, q_type, difficulty, follow_ups, criteria in comp_questions:
                q_id = f"Q{question_id_counter:02d}"
                question_id_counter += 1

                question = InterviewQuestion(
                    question_id=q_id,
                    question_text=q_text,
                    competency=competency,
                    question_type=q_type,
                    difficulty=difficulty,
                    follow_ups=follow_ups,
                    evaluation_criteria=criteria,
                )
                questions.append(question)

        return questions

    def _questions_for_competency(
        self,
        competency: str,
        gap_analysis: GapAnalysisResult,
        interview_format: str,
    ) -> list[tuple[str, str, str, list[str], str]]:
        """
        Generate questions for a specific competency.

        Returns:
            List of (question_text, type, difficulty, follow_ups, criteria)
        """
        if competency == "technical_depth":
            return [
                (
                    "Can you walk us through a complex technical project you led?",
                    "behavioral",
                    "medium",
                    [
                        "What was your specific technical contribution?",
                        "How did you handle unexpected technical challenges?",
                    ],
                    "Assess depth of technical understanding and problem-solving approach",
                ),
                (
                    "How do you stay current with new technical trends?",
                    "open_ended",
                    "easy",
                    [
                        "Can you share a recent technology you learned?",
                        "How has that technology impacted your work?",
                    ],
                    "Evaluate learning agility and technical curiosity",
                ),
            ]

        elif competency == "problem_solving":
            return [
                (
                    "Tell me about a time you had to debug a critical issue.",
                    "behavioral",
                    "hard",
                    [
                        "What was your systematic approach?",
                        "How did you prioritize when there were many unknowns?",
                    ],
                    "Assess structured problem-solving methodology",
                ),
                (
                    "How would you approach learning a new problem domain?",
                    "scenario",
                    "medium",
                    [
                        "What resources would you consult?",
                        "How would you validate your understanding?",
                    ],
                    "Evaluate learning strategy and domain transfer skills",
                ),
            ]

        elif competency == "communication":
            return [
                (
                    "Describe a time you had to explain a complex technical concept to non-technical stakeholders.",
                    "behavioral",
                    "medium",
                    [
                        "How did you simplify the concept?",
                        "How did you verify they understood?",
                    ],
                    "Assess clarity and empathy in communication",
                ),
                (
                    "How do you handle disagreements within your team?",
                    "behavioral",
                    "medium",
                    [
                        "Can you give a specific example?",
                        "What was the outcome?",
                    ],
                    "Evaluate collaboration and conflict resolution",
                ),
            ]

        elif competency == "leadership":
            return [
                (
                    "Tell us about a time you led a team or project.",
                    "behavioral",
                    "hard",
                    [
                        "What was your leadership style?",
                        "How did you handle underperformance?",
                    ],
                    "Assess leadership capabilities and team dynamics",
                ),
                (
                    "How would you mentor someone struggling with a skill you know well?",
                    "scenario",
                    "medium",
                    [
                        "What would be your first step?",
                        "How would you measure progress?",
                    ],
                    "Evaluate mentoring and development mindset",
                ),
            ]

        elif competency == "learning_agility":
            return [
                (
                    "Tell us about a skill that was completely new to you that you had to master quickly.",
                    "behavioral",
                    "medium",
                    [
                        "How did you approach the learning?",
                        "How quickly did you become productive?",
                    ],
                    "Assess ability to learn under pressure",
                ),
                (
                    "When faced with a technology or approach you disagreed with, how did you respond?",
                    "behavioral",
                    "medium",
                    [
                        "What was your mindset?",
                        "What did you learn?",
                    ],
                    "Evaluate openness to feedback and learning from different perspectives",
                ),
            ]

        elif competency == "domain_expertise":
            return [
                (
                    "What aspects of your domain experience do you consider your superpower?",
                    "open_ended",
                    "easy",
                    [
                        "How did you develop this expertise?",
                        "Can you share a recent application of this expertise?",
                    ],
                    "Assess depth and passion for domain expertise",
                ),
                (
                    "What's a misconception people often have about your domain?",
                    "open_ended",
                    "medium",
                    [
                        "How would you educate someone about this?",
                    ],
                    "Evaluate thought leadership and communication",
                ),
            ]

        return []

    def _guidance_for_critical_gaps(self, critical_gaps: list[SkillGap]) -> Optional[str]:
        """Generate guidance for exploring critical gaps during interview."""
        if not critical_gaps:
            return None

        gap_names = [g.skill_name for g in critical_gaps[:3]]
        gap_str = ", ".join(gap_names)

        return (
            f"This candidate has critical gaps in: {gap_str}. "
            f"Explore: (1) Awareness of the gap, (2) Willingness and ability to learn, "
            f"(3) Similar experiences that show transferable learning. "
            f"Focus on growth potential rather than current lack."
        )

    def _guidance_for_strengths(self, strengths: list[str]) -> Optional[str]:
        """Generate guidance for validating candidate's strengths."""
        if not strengths:
            return None

        strength_str = ", ".join(strengths[:3])
        return (
            f"This candidate demonstrates strength in: {strength_str}. "
            f"Explore: (1) Depth of expertise, (2) Recent applications, "
            f"(3) How they would leverage these strengths in this role. "
            f"Ask for specific examples and metrics."
        )

    def _identify_risk_indicators(self, gap_analysis: GapAnalysisResult) -> list[str]:
        """Identify potential risk indicators to watch for during interview."""
        risks: list[str] = []

        # Risk: Many critical gaps with low trainability
        if len(gap_analysis.critical_gaps) > 2:
            risks.append(
                "Multiple critical skill gaps - assess learning ability and willingness to invest"
            )

        # Risk: Overconfidence in areas where gaps exist
        if gap_analysis.critical_gaps:
            risks.append("Watch for overconfidence about areas where gaps exist")

        # Risk: No strengths despite being considered
        if not gap_analysis.strengths:
            risks.append("Limited identifiable strengths - probe for hidden capabilities")

        # Risk: Poor fit
        if gap_analysis.readiness_level == "not_suitable":
            risks.append("Overall poor fit - assess if this is right career move for candidate")

        # Risk: Lack of domain knowledge
        if "domain_expertise" in [g.skill_name for g in gap_analysis.critical_gaps]:
            risks.append("Domain knowledge gap - assess transferability from previous experience")

        # General risks
        risks.extend(
            [
                "Listen for growth mindset vs fixed mindset indicators",
                "Assess genuine interest in the specific role and company",
            ]
        )

        return risks[:5]  # Limit to top 5 risk indicators
