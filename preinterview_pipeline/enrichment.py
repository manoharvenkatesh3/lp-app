"""Profile enrichment modules for LinkedIn and GitHub data extraction."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx

from .models import CandidateProfile, EnrichmentMetadata, GitHubProfile, LinkedInProfile, Skill, SkillLevel

logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMIT_DELAY = 1.0  # seconds between requests
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0  # exponential backoff multiplier


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, delay: float = RATE_LIMIT_DELAY):
        """Initialize rate limiter with delay between calls."""
        self.delay = delay
        self.last_call = 0.0

    async def wait(self) -> None:
        """Wait until enough time has passed since the last call."""
        elapsed = asyncio.get_event_loop().time() - self.last_call
        if elapsed < self.delay:
            await asyncio.sleep(self.delay - elapsed)
        self.last_call = asyncio.get_event_loop().time()


class LinkedInEnricher:
    """Enrich candidate profile with LinkedIn data."""

    # Note: In production, this would use official LinkedIn API with OAuth
    # For demo, we use heuristics and public profile scraping where allowed
    LINKEDIN_BASE_URL = "https://www.linkedin.com/in/"

    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        """Initialize LinkedIn enricher."""
        self.rate_limiter = rate_limiter or RateLimiter()
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> LinkedInEnricher:
        """Async context manager entry."""
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    async def enrich_profile(
        self,
        profile: CandidateProfile,
        linkedin_url: Optional[str] = None,
    ) -> tuple[CandidateProfile, dict]:
        """
        Enrich candidate profile with LinkedIn data.

        Args:
            profile: Candidate profile to enrich
            linkedin_url: Optional LinkedIn profile URL

        Returns:
            Tuple of (updated_profile, enrichment_data)
        """
        if not self.client:
            raise RuntimeError("LinkedInEnricher must be used as async context manager")

        enrichment_data = {
            "source": "linkedin",
            "success": False,
            "data": None,
            "error": None,
        }

        try:
            # If no LinkedIn URL provided, try to construct from name
            if not linkedin_url and profile.full_name:
                linkedin_url = self._construct_linkedin_url(profile.full_name)

            if not linkedin_url:
                enrichment_data["error"] = "No LinkedIn URL available"
                return profile, enrichment_data

            await self.rate_limiter.wait()

            # In production, use official API. For now, we use a heuristic approach
            linkedin_data = await self._fetch_linkedin_data(linkedin_url)

            if linkedin_data:
                profile.linkedin_profile = linkedin_data
                enrichment_data["success"] = True
                enrichment_data["data"] = linkedin_data.model_dump()

                # Track enrichment
                profile.enrichment_metadata.append(
                    EnrichmentMetadata(
                        source="linkedin",
                        confidence=0.8,
                        provenance=f"Enriched from {linkedin_url}",
                    )
                )

        except Exception as e:
            enrichment_data["error"] = str(e)
            logger.warning(f"LinkedIn enrichment failed for {profile.full_name}: {e}")

        return profile, enrichment_data

    def _construct_linkedin_url(self, full_name: str) -> str:
        """Construct likely LinkedIn URL from full name."""
        # Simple heuristic: convert name to LinkedIn URL format
        name_part = full_name.lower().replace(" ", "-")
        name_part = "".join(c for c in name_part if c.isalnum() or c == "-")
        return f"{self.LINKEDIN_BASE_URL}{name_part}"

    async def _fetch_linkedin_data(self, linkedin_url: str) -> Optional[LinkedInProfile]:
        """Fetch LinkedIn profile data. In production, use official API."""
        try:
            # This is a placeholder that would use official LinkedIn API in production
            # For safety and legal compliance, we don't scrape LinkedIn
            # Instead, this demonstrates the structure

            profile = LinkedInProfile(
                profile_url=linkedin_url,
                verified=False,  # Would be True if verified via API
                last_updated=datetime.utcnow(),
            )
            return profile

        except Exception as e:
            logger.error(f"Failed to fetch LinkedIn data from {linkedin_url}: {e}")
            return None


class GitHubEnricher:
    """Enrich candidate profile with GitHub data."""

    GITHUB_API_BASE_URL = "https://api.github.com"

    def __init__(self, rate_limiter: Optional[RateLimiter] = None, github_token: Optional[str] = None):
        """Initialize GitHub enricher."""
        self.rate_limiter = rate_limiter or RateLimiter()
        self.github_token = github_token
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> GitHubEnricher:
        """Async context manager entry."""
        headers = {}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        self.client = httpx.AsyncClient(
            base_url=self.GITHUB_API_BASE_URL,
            headers=headers,
            timeout=30.0,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    async def enrich_profile(
        self,
        profile: CandidateProfile,
        github_username: Optional[str] = None,
    ) -> tuple[CandidateProfile, dict]:
        """
        Enrich candidate profile with GitHub data.

        Args:
            profile: Candidate profile to enrich
            github_username: Optional GitHub username

        Returns:
            Tuple of (updated_profile, enrichment_data)
        """
        if not self.client:
            raise RuntimeError("GitHubEnricher must be used as async context manager")

        enrichment_data = {
            "source": "github",
            "success": False,
            "data": None,
            "error": None,
        }

        try:
            # If no GitHub username provided, try to infer from email domain or elsewhere
            if not github_username:
                github_username = self._infer_github_username(profile)

            if not github_username:
                enrichment_data["error"] = "No GitHub username available"
                return profile, enrichment_data

            await self.rate_limiter.wait()

            github_data = await self._fetch_github_user_data(github_username)

            if github_data:
                profile.github_profile = github_data
                enrichment_data["success"] = True
                enrichment_data["data"] = github_data.model_dump()

                # Extract programming languages/skills from repos
                skills = await self._extract_skills_from_repos(github_username)
                for skill_name in skills:
                    # Add to profile if not already there
                    if not any(s.name.lower() == skill_name.lower() for s in profile.skills):
                        profile.skills.append(
                            Skill(
                                name=skill_name,
                                level=SkillLevel.INTERMEDIATE,
                            )
                        )

                # Track enrichment
                profile.enrichment_metadata.append(
                    EnrichmentMetadata(
                        source="github",
                        confidence=0.9,
                        provenance=f"Enriched from GitHub user {github_username}",
                    )
                )

        except Exception as e:
            enrichment_data["error"] = str(e)
            logger.warning(f"GitHub enrichment failed for {profile.full_name}: {e}")

        return profile, enrichment_data

    def _infer_github_username(self, profile: CandidateProfile) -> Optional[str]:
        """Try to infer GitHub username from profile."""
        if profile.github_profile and profile.github_profile.username:
            return profile.github_profile.username

        # Try to infer from name (simple heuristic)
        if profile.full_name:
            username = profile.full_name.lower().replace(" ", "")
            username = "".join(c for c in username if c.isalnum() or c in "-_")
            return username if username else None

        return None

    async def _fetch_github_user_data(self, username: str) -> Optional[GitHubProfile]:
        """Fetch GitHub user data from public API."""
        if not self.client:
            return None

        try:
            response = await self.client.get(f"/users/{username}")
            response.raise_for_status()
            data = response.json()

            profile = GitHubProfile(
                github_url=data.get("html_url"),
                username=data.get("login"),
                public_repos=data.get("public_repos"),
                followers=data.get("followers"),
                bio=data.get("bio"),
                verified=data.get("verified", False),
                last_updated=datetime.utcnow(),
            )
            return profile

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.debug(f"GitHub user not found: {username}")
            else:
                logger.error(f"GitHub API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch GitHub data for {username}: {e}")
            return None

    async def _extract_skills_from_repos(self, username: str, limit: int = 10) -> list[str]:
        """Extract programming languages from user's repositories."""
        if not self.client:
            return []

        skills = set()

        try:
            await self.rate_limiter.wait()

            response = await self.client.get(
                f"/users/{username}/repos",
                params={"sort": "stars", "per_page": limit},
            )
            response.raise_for_status()
            repos = response.json()

            for repo in repos:
                language = repo.get("language")
                if language:
                    skills.add(language)

        except Exception as e:
            logger.debug(f"Failed to extract skills from GitHub repos for {username}: {e}")

        return sorted(list(skills))


async def enrich_candidate_from_sources(
    profile: CandidateProfile,
    sources: list[str] = None,
    github_token: Optional[str] = None,
) -> tuple[CandidateProfile, dict]:
    """
    Enrich candidate profile from multiple sources.

    Args:
        profile: Candidate profile to enrich
        sources: List of sources to enrich from ('linkedin', 'github')
        github_token: Optional GitHub API token for higher rate limits

    Returns:
        Tuple of (enriched_profile, enrichment_results)
    """
    if sources is None:
        sources = ["linkedin", "github"]

    enrichment_results = {}
    rate_limiter = RateLimiter()

    # Enrich from LinkedIn
    if "linkedin" in sources:
        async with LinkedInEnricher(rate_limiter) as enricher:
            profile, linkedin_results = await enricher.enrich_profile(profile)
            enrichment_results["linkedin"] = linkedin_results

    # Enrich from GitHub
    if "github" in sources:
        async with GitHubEnricher(rate_limiter, github_token) as enricher:
            profile, github_results = await enricher.enrich_profile(profile)
            enrichment_results["github"] = github_results

    profile.updated_at = datetime.utcnow()
    return profile, enrichment_results
