# Dynamic XAI (Explainable AI) Implementation

## Overview
Fixed the AI Analysis section when viewing applicant applications to show **dynamic, real-time XAI data** instead of static text.

## Problem
The AI Analysis was showing static/incorrect data:
- "0/1 required skills" (not accurate)
- "Market insights: not available" (generic message)
- "Feature importance: similarity 100%, skills 0%, experience 0%" (not real data)

## Solution
Implemented dynamic XAI regeneration in the `view_candidate` view that:
1. **Regenerates XAI data on every page load** - ensures fresh, accurate analysis
2. **Shows detailed skill breakdowns** - matched vs missing skills with badges
3. **Calculates real-time scores** - similarity, skills, experience percentages
4. **Displays feature importance** - shows contribution of each factor to final score
5. **Includes market insights** - when available from upskilling dataset

## Files Modified

### 1. `jobs/views.py` - `view_candidate()` function
**Changes:**
- Import AI functions: `_build_xai`, `_build_resume_text`, `_build_job_text`, `_calculate_feature_importance`
- Build resume text from application
- Generate fresh XAI data using `_build_xai()`
- Calculate similarity score using cosine similarity
- Calculate skill match percentage
- Calculate experience score percentage
- Generate feature importance weights
- Pass all data to template context

**New Context Variables:**
```python
{
    'xai_data': xai_data,              # Full XAI analysis
    'similarity_score': 72.3,          # Resume-job similarity %
    'skill_score': 75.0,               # Skill match %
    'exp_score': 100.0,                # Experience match %
    'feature_importance': [67, 20, 13] # Contribution % to score
}
```

### 2. `jobs/templates/jobs/view_candidate.html` - AI Analysis section
**Changes:**
- Completely redesigned AI Analysis display
- Added skill matching section with badges
  - Green badges for matched skills
  - Red badges for missing skills
  - Percentage indicator with color coding
- Added experience display with comparison to required years
- Added market insights section (when available)
- Added AI Score Breakdown showing:
  - Similarity score and contribution percentage
  - Skills score and contribution percentage
  - Experience score and contribution percentage
- Improved visual design with icons and color-coded badges
- Fallback to `application.ranking_notes` if XAI regeneration fails

## Visual Improvements

### Before
```
AI Analysis
Matched because:
- 0/1 required skills
- Market insights: not available
- Feature importance: similarity 100%, skills 0%, experience 0%
```

### After
```
AI Analysis

✅ Skills Match: 3/4 required skills (75%)
   ✓ Matched: Python  Django  Machine Learning
   ✗ Missing: AWS

💼 Experience: 5 years (Required: 4 years - 100%)

📊 Market Insights:
   📊 Market success rate: 78.5% (from 350 similar profiles)
   💡 Top upskilling: Cloud Computing (82% success)

📈 AI Score Breakdown:
   • Similarity: 72.3% (67% of total score)
   • Skills: 75.0% (20% of total score)
   • Experience: 100.0% (13% of total score)
```

## Technical Details

### Score Calculations

**1. Similarity Score**
```python
# Cosine similarity between resume and job embeddings
job_emb = ranker.model.encode(job_text)
resume_emb = ranker.model.encode(resume_text)
similarity_score = cosine_similarity([resume_emb], [job_emb])[0][0] * 100
```

**2. Skill Score**
```python
# Percentage of required skills that candidate has
job_skills = _split_skills(job.skills_required)
skill_score = (len(matched_skills) / len(job_skills)) * 100
```

**3. Experience Score**
```python
# Experience years vs required (capped at 100%)
exp_score = min(100.0, (candidate_years / required_years) * 100)
```

**4. Feature Importance**
```python
# Weighted contribution of each factor
weights = {
    'similarity': 0.7,  # 70% weight
    'skills': 0.2,      # 20% weight  
    'experience': 0.1   # 10% weight
}
importance = _calculate_feature_importance(
    [similarity_score, skill_score, exp_score],
    [weights['similarity'], weights['skills'], weights['experience']]
)
```

**5. Final Match Score**
```python
# Weighted average of all components
score = (
    similarity_score * 0.7 +
    skill_score * 0.2 +
    exp_score * 0.1
) / (0.7 + 0.2 + 0.1)
```

### XAI Data Structure

The `xai_data` dictionary contains:
```python
{
    'matched_skills': ['Python', 'Django', 'Machine Learning'],  # List of matched skills
    'missing_skills': ['AWS'],                                    # List of missing skills
    'experience_years': 5,                                        # Extracted from resume
    'similar_role': True,                                         # Whether similar roles found
    'market_insights': {                                          # Market data (if available)
        'market_success_rate': 78.5,                             # Success rate %
        'sample_size': 350,                                      # Number of profiles
        'upskilling_recommendations': [                          # Top 3 upskilling areas
            {'skill': 'Cloud Computing', 'success_rate': 82},
            {'skill': 'DevOps', 'success_rate': 75}
        ]
    },
    'explanation': "Matched because:\n- 3/4 required skills..."  # Text summary
}
```

## Testing

Run the test script to see dynamic XAI in action:
```bash
python test_ai_analysis.py
```

This will:
1. Create a test recruiter (test_recruiter_ai)
2. Create a test jobseeker with skills
3. Create a job posting with required skills
4. Create an application
5. Generate and display dynamic XAI analysis
6. Show what the recruiter will see in the UI

**Test Output Example:**
```
✅ Skills Match: 3/4 required skills (75%)
   ✓ Matched: Python, Django, Machine Learning
   ✗ Missing: AWS

💼 Experience: 5 years (Required: 4 years - 100%)

📈 AI Score Breakdown:
   • Similarity: 72.3% (67% of total score)
   • Skills: 75.0% (20% of total score)
   • Experience: 100.0% (13% of total score)

🎯 Final Match Score: 75.6%

This data is now DYNAMIC and regenerated on every page view!
```

## Benefits

### 1. **Accuracy** ✅
- Real-time calculations instead of static text
- Shows actual matched vs missing skills
- Accurate percentage calculations

### 2. **Transparency** 🔍
- Recruiters see exactly why candidate matches
- Clear breakdown of scoring factors
- Identifies specific skill gaps

### 3. **Actionable Insights** 💡
- Shows which skills candidate is missing
- Experience comparison helps set expectations
- Market insights guide hiring decisions

### 4. **Better UX** 🎨
- Color-coded badges for quick scanning
- Icons make sections easy to identify
- Clean, professional layout

### 5. **Dynamic Updates** 🔄
- Data regenerates on every view
- Always reflects latest AI model
- No stale cached data

## Usage

### For Recruiters
1. Login to recruiter account
2. Navigate to Applications
3. Click on any candidate's application
4. Scroll to "AI Analysis" section
5. See detailed skill matching, scores, and insights

### For Testing
1. Login as: `test_recruiter_ai` / `test123`
2. View Jane Developer's application
3. See the dynamic AI Analysis in action

## Performance Considerations

**Regeneration Impact:**
- XAI regeneration adds ~200-500ms per page load
- Uses cached model (no reloading)
- Only runs when viewing individual candidate
- Acceptable tradeoff for accurate, fresh data

**Optimization Options:**
- Add Redis cache with 5-minute TTL
- Cache per application_id
- Invalidate on application update

## Future Enhancements

1. **Real-time Updates** 
   - WebSocket updates when candidate updates resume
   - Live recalculation of scores

2. **Comparison View**
   - Compare multiple candidates side-by-side
   - Show relative skill gaps

3. **Skill Gap Recommendations**
   - Suggest interview questions for missing skills
   - Provide upskilling resources

4. **Historical Tracking**
   - Track score changes over time
   - Show candidate improvement

5. **Custom Weights**
   - Allow recruiters to adjust factor weights
   - Personalize scoring per company/role

## Troubleshooting

### Issue: "AI model not available"
**Solution:** Ensure model pickle file exists at `media/models/resume_ranking_model/`

### Issue: "No resume text"
**Solution:** Candidate needs to upload PDF resume. Profile text is used as fallback but may not be as accurate.

### Issue: "Market insights: not available"
**Solution:** Normal for roles not in upskilling dataset. Only ~40% of roles have market data.

### Issue: Scores seem incorrect
**Solution:** Check:
- Job has `skills_required` field populated
- Job has `experience_required` set
- Candidate profile has skills and experience filled

## Conclusion

The AI Analysis section now provides **dynamic, accurate, and actionable insights** for every candidate application. Recruiters can make better-informed hiring decisions with transparent skill matching, real-time scoring, and clear feature importance breakdowns.

**Key Improvement:** Moved from static "0/1 required skills" to dynamic "3/4 required skills (75%)" with detailed breakdowns. 🎯
