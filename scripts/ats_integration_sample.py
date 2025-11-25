"""Sample ATS integration script demonstrating push/pull operations."""
from __future__ import annotations

import asyncio
import os
from datetime import datetime
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")
ATS_API_KEY = os.getenv("ATS_API_KEY", "")


class ATSIntegrationClient:
    """Sample ATS integration client."""

    def __init__(self, api_key: str, base_url: str = API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        }

    async def push_candidate(self, candidate_data: dict[str, Any]) -> dict[str, Any]:
        """
        Push a candidate to the recruiter platform.

        Example candidate_data:
        {
            "external_id": "ATS-12345",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "resume_url": "https://example.com/resume.pdf",
            "skills": ["Python", "React", "AWS"],
            "experience_years": 5.0
        }
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/ats/candidates/sync",
                json=candidate_data,
                headers=self.headers,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def pull_candidates(
        self, updated_since: datetime | None = None, page: int = 1, page_size: int = 50
    ) -> dict[str, Any]:
        """
        Pull candidates from the recruiter platform.

        Returns paginated list of candidates with their latest information.
        """
        params = {"page": page, "page_size": page_size}
        if updated_since:
            params["updated_since"] = updated_since.isoformat()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/ats/candidates",
                params=params,
                headers=self.headers,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def pull_scorecards(
        self,
        candidate_external_id: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """
        Pull interview scorecards for export to ATS.

        Scorecards include bias-filtered feedback and complete scoring details.
        """
        params = {}
        if candidate_external_id:
            params["candidate_external_id"] = candidate_external_id
        if from_date:
            params["from_date"] = from_date.isoformat()
        if to_date:
            params["to_date"] = to_date.isoformat()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/ats/scorecards/export",
                params=params,
                headers=self.headers,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def push_feedback(
        self, candidate_external_id: str, feedback_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Push additional feedback from ATS to the platform.

        Feedback is automatically checked for bias and sanitized if needed.

        Example feedback_data:
        {
            "text": "Great candidate with strong technical skills",
            "source": "ATS",
            "rating": 5
        }
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/ats/feedback/sync",
                params={"candidate_external_id": candidate_external_id},
                json=feedback_data,
                headers=self.headers,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()


async def demo_push_candidate():
    """Demonstrate pushing a candidate to the platform."""
    print("\n=== Demo: Push Candidate ===")

    client = ATSIntegrationClient(ATS_API_KEY)

    candidate = {
        "external_id": f"DEMO-{datetime.now().timestamp()}",
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice.johnson@example.com",
        "phone": "+1234567890",
        "resume_url": "https://example.com/alice-resume.pdf",
        "linkedin_url": "https://linkedin.com/in/alicejohnson",
        "skills": ["Python", "Machine Learning", "Data Science", "SQL"],
        "experience_years": 7.5,
        "education": [
            {
                "degree": "M.S. Computer Science",
                "institution": "MIT",
                "year": 2016,
            }
        ],
        "ats_data": {
            "source": "LinkedIn",
            "application_date": "2024-01-15",
            "status": "screening",
        },
    }

    try:
        result = await client.push_candidate(candidate)
        print(f"✓ Successfully pushed candidate: {result['id']}")
        print(f"  Name: {result['first_name']} {result['last_name']}")
        print(f"  Email: {result['email']}")
        return result["id"]
    except Exception as e:
        print(f"✗ Failed to push candidate: {e}")
        return None


async def demo_pull_candidates():
    """Demonstrate pulling candidates from the platform."""
    print("\n=== Demo: Pull Candidates ===")

    client = ATSIntegrationClient(ATS_API_KEY)

    try:
        result = await client.pull_candidates(page=1, page_size=10)
        print(f"✓ Retrieved {len(result['candidates'])} candidates (Total: {result['total']})")

        for candidate in result["candidates"][:3]:  # Show first 3
            print(f"\n  Candidate: {candidate['first_name']} {candidate['last_name']}")
            print(f"  Email: {candidate['email']}")
            print(f"  Skills: {', '.join(candidate.get('skills', []))}")
    except Exception as e:
        print(f"✗ Failed to pull candidates: {e}")


async def demo_pull_scorecards():
    """Demonstrate pulling scorecards from the platform."""
    print("\n=== Demo: Pull Scorecards ===")

    client = ATSIntegrationClient(ATS_API_KEY)

    try:
        # Pull scorecards from the last 30 days
        from_date = datetime.now().replace(day=1)  # Start of current month
        scorecards = await client.pull_scorecards(from_date=from_date)

        print(f"✓ Retrieved {len(scorecards)} scorecards")

        for scorecard in scorecards[:2]:  # Show first 2
            print(f"\n  Position: {scorecard['position']}")
            print(f"  Overall Score: {scorecard['scores']['overall']}")
            print(f"  Recommendation: {scorecard['recommendation']}")
            print(f"  Recruiter: {scorecard['recruiter_email']}")
    except Exception as e:
        print(f"✗ Failed to pull scorecards: {e}")


async def demo_push_feedback():
    """Demonstrate pushing feedback to the platform."""
    print("\n=== Demo: Push Feedback ===")

    client = ATSIntegrationClient(ATS_API_KEY)

    # First, create a candidate to add feedback to
    candidate_id = await demo_push_candidate()
    if not candidate_id:
        print("✗ Cannot demo feedback without a candidate")
        return

    feedback = {
        "text": "Excellent candidate with strong problem-solving skills. Shows great potential for team collaboration.",
        "source": "Mock ATS",
        "rating": 4.5,
        "reviewer": "Hiring Manager",
    }

    try:
        result = await client.push_feedback(f"DEMO-{candidate_id}", feedback)
        print(f"✓ Successfully pushed feedback")
        print(f"  Bias Filtered: {result.get('bias_filtered', False)}")
    except Exception as e:
        print(f"✗ Failed to push feedback: {e}")


async def main():
    """Run all demo operations."""
    print("=" * 60)
    print("ATS Integration Sample Script")
    print("=" * 60)

    if not ATS_API_KEY:
        print("\n⚠ WARNING: No ATS_API_KEY found in environment")
        print("Please set ATS_API_KEY in your .env file or environment variables")
        print("\nTo register a new integration, run:")
        print("  curl -X POST http://localhost:8000/api/ats/integrations/register \\")
        print('    -H "Content-Type: application/json" \\')
        print('    -d \'{"name": "Mock ATS"}\'')
        return

    try:
        # Run demos
        await demo_push_candidate()
        await demo_pull_candidates()
        await demo_pull_scorecards()
        await demo_push_feedback()

        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
