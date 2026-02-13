# API Specification - Candidate Ranking System

## Endpoints

### 1. Rank Candidates API

**Endpoint:** `POST /jobs/api/rank/{job_id}/`

**Description:** 
Ranks all candidates for a specific job based on their match to the provided job description using AI-powered semantic analysis.

---

## Request

### Method
```
POST
```

### URL Parameters
```
job_id (integer, required) - The ID of the job position
```

### Headers
```
Content-Type: application/json
Authorization: (automatic via Django session)
X-CSRFToken: (required, Django CSRF token)
```

### Body
```json
{
    "job_description": "Senior Python developer with 5+ years experience..."
}
```

### Body Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_description` | string | Yes | The job description to rank candidates against |

### Example Request
```bash
curl -X POST http://127.0.0.1:8000/jobs/api/rank/1/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN" \
  -d '{
    "job_description": "Python backend developer with Django, PostgreSQL, and AWS expertise. 3+ years experience required."
  }'
```

### Example Python Request
```python
import requests
import json

response = requests.post(
    'http://127.0.0.1:8000/jobs/api/rank/1/',
    headers={
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,
    },
    json={
        'job_description': 'Senior Python developer with Django and AWS experience'
    }
)
result = response.json()
```

---

## Response

### Success Response (200 OK)
```json
{
    "success": true,
    "total": 5,
    "candidates": [
        {
            "id": 42,
            "name": "John Doe",
            "email": "john@example.com",
            "rank_score": 94.5,
            "skills_list": [
                "Python",
                "Django",
                "PostgreSQL",
                "AWS",
                "Docker"
            ],
            "experience_years": 5,
            "headline": "Senior Full Stack Developer"
        },
        {
            "id": 38,
            "name": "Jane Smith",
            "email": "jane@example.com",
            "rank_score": 87.3,
            "skills_list": [
                "Python",
                "Flask",
                "SQL",
                "AWS"
            ],
            "experience_years": 4,
            "headline": "Backend Engineer"
        },
        {
            "id": 35,
            "name": "Mike Johnson",
            "email": "mike@example.com",
            "rank_score": 76.8,
            "skills_list": [
                "Python",
                "Django",
                "MySQL"
            ],
            "experience_years": 2,
            "headline": "Junior Python Developer"
        }
    ]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the request was successful |
| `total` | integer | Number of candidates returned (max 10) |
| `candidates` | array | List of ranked candidates |

### Candidate Object
| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique application ID |
| `name` | string | Candidate's full name |
| `email` | string | Candidate's email address |
| `rank_score` | float | Match score (0-100%) |
| `skills_list` | array | List of candidate's skills |
| `experience_years` | integer | Years of experience |
| `headline` | string | Professional headline |

---

## Error Responses

### 400 Bad Request
Missing or invalid job description:
```json
{
    "error": "Job description required"
}
```

### 403 Forbidden
User is not a recruiter:
```json
{
    "error": "Recruiter access required"
}
```

### 404 Not Found
Job doesn't exist or doesn't belong to user:
```json
{
    "error": "Not found"
}
```

### 500 Internal Server Error
Server error during ranking:
```json
{
    "error": "Error ranking applications: <error_details>"
}
```

---

## Authentication

### Required
- User must be logged in (Django session)
- User must have a recruiter profile
- User must own the job posting

### How to Get CSRF Token

**In Django Template:**
```html
<input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">
```

**In JavaScript:**
```javascript
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
```

---

## Rate Limiting

Currently: **No rate limiting** (can be added via middleware)

Recommended for production:
- 100 requests per hour per recruiter
- Prevents abuse of AI ranking service

---

## Data Validation

### Input Validation
```python
# Job description must be:
- Non-empty string
- Max length: No limit (but recommended <5000 chars)
- Must be UTF-8 encoded
```

### Output Validation
```python
# All candidate data is:
- HTML-escaped (XSS protection)
- Rounded to 1 decimal place (scores)
- Strings properly encoded
```

---

## Performance

| Metric | Value |
|--------|-------|
| Response Time | <500ms (avg) |
| Max Candidates | 10 (top ranked) |
| Model Load Time | 10-15s (first call) |
| Memory Usage | ~1.5GB |
| Timeout | 30 seconds |

---

## Usage Examples

### Example 1: Frontend (JavaScript)
```javascript
async function rankCandidates() {
    const jobDescription = document.getElementById('jobDesc').value;
    
    const response = await fetch('/jobs/api/rank/1/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            job_description: jobDescription
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        displayCandidates(data.candidates);
    } else {
        showError(data.error);
    }
}
```

### Example 2: Python Backend
```python
import requests
from django.contrib.auth.models import User

user = User.objects.first()
client = requests.Session()

# Login (in real scenario, get session from authenticated request)
response = client.post(
    'http://127.0.0.1:8000/jobs/api/rank/1/',
    json={'job_description': 'Senior Python Developer'},
    headers={'X-CSRFToken': csrf_token}
)

candidates = response.json()['candidates']
for candidate in candidates:
    print(f"{candidate['name']}: {candidate['rank_score']}%")
```

### Example 3: React Component
```jsx
import axios from 'axios';

export function CandidateRanker({ jobId }) {
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const rankCandidates = async (jobDescription) => {
        setLoading(true);
        try {
            const response = await axios.post(`/jobs/api/rank/${jobId}/`, {
                job_description: jobDescription
            });
            setResults(response.data.candidates);
        } catch (error) {
            console.error('Ranking failed:', error);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div>
            <textarea onChange={(e) => rankCandidates(e.target.value)} />
            {loading && <p>Ranking...</p>}
            {results && <CandidateTable candidates={results} />}
        </div>
    );
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (missing data) |
| 403 | Forbidden (not recruiter) |
| 404 | Not Found (job doesn't exist) |
| 500 | Server Error |

---

## Webhook/Event Logging

All API calls are logged:

```
INFO jobs 2024-02-05 22:35:10 Ranked 5 candidates for job 1
ERROR jobs 2024-02-05 22:36:00 Error ranking applications for job 2: <error>
```

Log file: `debug.log` in project root

---

## Integration with Dashboard

The ranking API is integrated with the HTML dashboard at:
```
GET /jobs/recruiter/jobs/{job_id}/applications/
```

This page includes:
- Interactive ranking UI
- Real-time results
- Candidate profile links
- Statistics summary

---

## Migration Notes

### From Direct View to API
**Before:**
```python
# Access view directly
/jobs/recruiter/applications/1/
```

**Now:**
```python
# Use dedicated API
POST /jobs/api/rank/1/
GET /jobs/recruiter/jobs/1/applications/
```

---

## Future Enhancements

1. **Filtering:**
   ```json
   {
       "job_description": "...",
       "filters": {
           "min_score": 75,
           "max_experience": 10,
           "skills_required": ["Python", "Django"]
       }
   }
   ```

2. **Batch Processing:**
   ```json
   {
       "job_ids": [1, 2, 3],
       "job_description": "..."
   }
   ```

3. **Custom Weights:**
   ```json
   {
       "job_description": "...",
       "weights": {
           "skills": 0.5,
           "experience": 0.3,
           "education": 0.2
       }
   }
   ```

---

## Support

For issues or questions:
1. Check `debug.log` for errors
2. Verify user is recruiter: `user.profile.user_type == 'recruiter'`
3. Ensure job exists and belongs to recruiter
4. Check that candidates exist for the job

---

**API Version:** 1.0
**Last Updated:** February 2024
**Status:** Production Ready ✅
