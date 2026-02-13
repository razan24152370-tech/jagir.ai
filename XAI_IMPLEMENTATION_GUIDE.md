# XAI Implementation Guide - Global Market Insights

## What Was Implemented

Your XAI system now uses **global market insights** from the Employee Upskilling Dataset instead of per-candidate history.

### Data Source
- **File:** `media/models/Employee_Upskilling_Dataset.csv`
- **Records:** 3000 employee profiles
- **Key Fields Used:**
  - Job Role / Current Job Title
  - Industry
  - AI Upskilling Type
  - Success in Hiring Process (0/1)
  - Percentage Hike in Salary

### Features

#### 1. Market Success Rate
Shows hiring success percentage for similar roles:
```
"Market success rate for this role: 78.5% (from 147 profiles)"
```

#### 2. AI Upskilling Recommendations
Recommends upskilling based on market data:
```
"Top upskilling: Deep Learning (85% success rate)"
```

#### 3. Personalized Improvement Tips
Job seekers see:
- Missing skills from job requirements
- Recommended AI upskilling types with proven success rates
- Experience gap guidance

### Where XAI Appears

#### For Recruiters
1. **Applications List** (`/jobs/recruiter/applications/`)
   - Match score with explanation per candidate
   - Skills matched/missing breakdown

2. **Rank Modal**
   - Top candidates with detailed explanations
   - Market insights per candidate

3. **Candidate Detail Page**
   - Full XAI breakdown with feature importance
   - SHAP contributions (similarity, skills, experience)

#### For Job Seekers
1. **Job Recommendations** (Dashboard & Browse Jobs)
   - Match score with explanation
   - "Improve by learning:" tips with upskilling suggestions

2. **Job Detail Page**
   - Match score with market insights
   - Upskilling recommendations to increase chances

### How It Works

#### Matching Logic
1. **Resume Analysis:**
   - Extracts skills using spaCy PhraseMatcher
   - Infers years of experience from text patterns
   - PDF-only (strict requirement)

2. **Market Lookup:**
   - Matches job title to dataset roles (40%+ token overlap)
   - Filters by industry if available
   - Computes success rate from similar profiles

3. **Upskilling Recs:**
   - Finds profiles in similar roles
   - Ranks AI upskilling types by success rate
   - Returns top 3 with >50% success rate

#### Scoring Formula
```
Final Score = (
    Resume Similarity × 60% +
    Skill Match % × 30% +
    Experience Match % × 10%
)
```

With SHAP feature importance showing contribution breakdown.

### Example XAI Output

**Recruiter sees:**
```
Matched because:
- 7/10 required skills
- 5 years relevant experience (resume)
- Market success rate for this role: 82.3% (from 234 profiles)
- Top upskilling: Machine Learning (79% success rate)
- Feature importance: similarity 65%, skills 28%, experience 7%
```

**Job seeker sees:**
```
Match Score: 78%

Matched because:
- 8/10 required skills
- 3 years relevant experience (resume)
- Market success rate for this role: 75.0% (from 189 profiles)
- Top upskilling: Natural Language Processing (81% success rate)

Improve by learning:
- Docker, Kubernetes (missing skills)
- Natural Language Processing (AI upskilling)
- Deep Learning (AI upskilling)
```

## Next Steps

### 1. Install Dependencies (if not done)
```bash
pip install -r requirements.txt
```

### 2. Verify Dataset
The system automatically loads from:
```
media/models/Employee_Upskilling_Dataset.csv
```

Check logs for: `"Loaded upskilling dataset: 3000 records"`

### 3. Test the System

#### Test Recruiter XAI
1. Go to Applications page
2. Click "Rank" on any job
3. Check explanations show:
   - Skills breakdown
   - Market success rate
   - Feature importance

#### Test Job Seeker XAI
1. Log in as job seeker
2. Upload PDF resume
3. Browse jobs
4. Check match scores show:
   - Explanation with market insights
   - Upskilling recommendations

### 4. Monitor Logs
```python
logger.info(f"Loaded upskilling dataset: {len(df)} records")
logger.info(f"RESUME AI: {job.title} for {user}: {score:.1f}%")
```

## Customization Options

### Adjust Matching Threshold
In `_get_market_success_rate()`:
```python
if overlap >= 0.4:  # Change this (0.0-1.0)
```

### Minimum Sample Size
In `_get_upskilling_recommendations()`:
```python
upskilling_success = upskilling_success[upskilling_success["count"] >= 5]  # Change min
```

### Success Rate Threshold
In `_get_upskilling_recommendations()`:
```python
if pd.notna(skill_type) and success_rate > 50:  # Change threshold
```

### Scoring Weights
In `get_job_recommendations()` and `rank_applications()`:
```python
weights = {
    "similarity": 0.6,  # Adjust these
    "skills": 0.3,
    "experience": 0.1,
}
```

## Future Enhancements

When you add **email mapping** to the CSV:
1. Set `XAI_DATA_DIR` to use both systems
2. Per-candidate history overrides market data
3. More personalized recommendations

### To Add Email Mapping
1. Populate `email` column in CSV with Django user emails
2. System will automatically detect and use per-candidate data
3. Falls back to market insights when no history exists

## Troubleshooting

### No Market Insights Shown
- Check CSV path: `media/models/Employee_Upskilling_Dataset.csv`
- Verify columns: `job_role`, `current_job_title`, `ai_upskilling_type`
- Check logs for loading errors

### Low Match Rates
- Reduce overlap threshold in `_get_market_success_rate()`
- Check job titles in dataset match your job postings
- Consider adding more role synonyms

### Empty Upskilling Recommendations
- Check dataset has `ai_upskilling_type` populated
- Lower success rate threshold (currently 50%)
- Reduce minimum sample size (currently 5)

## Technical Details

### Dependencies Added
- `spacy>=3.7.5` - Skill extraction
- `shap>=0.45.0` - Feature importance
- `pypdf>=4.2.0` - PDF parsing

### Key Functions
- `_load_upskilling_data()` - Loads and caches dataset
- `_get_market_success_rate()` - Computes role success rate
- `_get_upskilling_recommendations()` - Returns AI upskilling tips
- `_build_xai()` - Generates full explanation
- `_shap_feature_importance()` - Computes SHAP values

### Performance
- Dataset cached in memory (LRU cache)
- Fast lookups via pandas groupby
- No per-request CSV reads

---

**Status:** ✅ Fully implemented and ready to test
**Dataset:** ✅ Employee_Upskilling_Dataset.csv loaded
**XAI:** ✅ Global market insights active
**Mapping:** ⚠️ Email column empty (using global insights only)
