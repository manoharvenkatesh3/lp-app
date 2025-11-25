# ATS Integration Scripts

Sample scripts demonstrating integration with the Recruiter Dashboard API.

## Setup

1. Install dependencies:
```bash
pip install httpx python-dotenv
```

2. Configure API key:
```bash
# Register an integration to get an API key
curl -X POST http://localhost:8000/api/ats/integrations/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Your ATS Name"}'

# Set the API key in your environment
export ATS_API_KEY="ats_xxx..."
export API_BASE_URL="http://localhost:8000/api"
```

3. Run the sample script:
```bash
python ats_integration_sample.py
```

## Sample Script

The `ats_integration_sample.py` script demonstrates:

### Push Candidate
Upload candidate data from your ATS to the recruiter platform:
```python
candidate = {
    "external_id": "ATS-12345",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "skills": ["Python", "React"],
    "experience_years": 5.0
}
result = await client.push_candidate(candidate)
```

### Pull Candidates
Retrieve updated candidate information (incremental sync):
```python
# Get candidates updated since last sync
from_date = datetime(2024, 1, 1)
result = await client.pull_candidates(updated_since=from_date)
```

### Pull Scorecards
Export interview scorecards with bias-filtered feedback:
```python
scorecards = await client.pull_scorecards(
    candidate_external_id="ATS-12345",
    from_date=datetime(2024, 1, 1)
)
```

### Push Feedback
Send additional feedback from your ATS:
```python
feedback = {
    "text": "Excellent problem-solving skills",
    "rating": 4.5,
    "reviewer": "Hiring Manager"
}
result = await client.push_feedback("ATS-12345", feedback)
```

## Rate Limiting

The API enforces rate limits:
- **1000 requests per hour** per API key
- Rate limit headers are included in responses
- Exceeded limits return 429 status with retry-after header

## Error Handling

All methods raise `httpx.HTTPStatusError` on API errors:
```python
try:
    result = await client.push_candidate(candidate)
except httpx.HTTPStatusError as e:
    print(f"API error: {e.response.status_code}")
    print(f"Details: {e.response.json()}")
```

## Bias Detection

All feedback and scorecard data is automatically checked for bias:
- Age-related language
- Gender-specific terms
- Race/ethnicity references
- Disability mentions
- Appearance-based comments
- Family status references

The API will return `bias_filtered: true` if content was sanitized.

## Custom Integration

Use the `ATSIntegrationClient` class as a base for your own integration:

```python
from ats_integration_sample import ATSIntegrationClient

class MyATSClient(ATSIntegrationClient):
    async def sync_all_candidates(self):
        """Sync all candidates from your ATS."""
        # Your custom logic here
        pass
```

## Support

For questions or issues:
- API Documentation: [../API_DOCUMENTATION.md](../API_DOCUMENTATION.md)
- Dashboard Documentation: [../DASHBOARD_README.md](../DASHBOARD_README.md)
