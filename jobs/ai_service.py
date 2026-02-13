"""
AI Service for Job Recommendations and CV Ranking
Enhanced with semantic skill matching and comprehensive profile analysis
"""
import logging
import os
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from pypdf import PdfReader
from sklearn.metrics.pairwise import cosine_similarity

from ProRecruiterAI.utils.resume_ranker import ranker
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q, Sum, Count, Avg

logger = logging.getLogger('jobs')


def normalize_skill(skill):
    """Normalize skill string for comparison"""
    return skill.strip().lower()


def calculate_keyword_similarity(text1, text2):
    """Calculate similarity between two texts based on shared keywords"""
    if not text1 or not text2:
        return 0.0
    
    words1 = set(w.lower().strip() for w in str(text1).split() if len(w) > 2)
    words2 = set(w.lower().strip() for w in str(text2).split() if len(w) > 2)
    
    if not words1 or not words2:
        return 0.0
    
    matching = words1.intersection(words2)
    return (len(matching) / max(len(words1), len(words2))) * 100


def calculate_skill_match(user_skills, job_skills):
    """
    Calculate percentage of matching skills - STRICT MODE
    Only exact matches count. Partial matches are not accepted.
    Returns the percentage of job-required skills that the user has.
    """
    if not user_skills or not job_skills:
        return 0.0
    
    user_skills_list = [normalize_skill(s) for s in user_skills]
    job_skills_list = [normalize_skill(s) for s in job_skills]
    
    if not job_skills_list:
        return 0.0
    
    # STRICT: Only exact matches count
    exact_matches = 0
    for job_skill in job_skills_list:
        if job_skill in user_skills_list:
            exact_matches += 1
    
    # Percentage of required skills matched (not user skills matched)
    score = (exact_matches / len(job_skills_list)) * 100
    logger.info(f"STRICT Skill match - User: {user_skills_list}, Job: {job_skills_list}, Exact: {exact_matches}/{len(job_skills_list)}, Score: {score:.1f}%")
    return score


def _read_text_resume(file_field):
    if not file_field:
        return ""

    try:
        path = file_field.path
    except Exception:
        return ""

    if not path or not os.path.exists(path):
        return ""

    _, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext != ".pdf":
        return ""

    try:
        reader = PdfReader(path)
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        return "\n".join(pages).strip()
    except Exception as exc:
        logger.warning(f"Resume text read failed: {exc}")
        return ""


def _build_resume_text(application):
    resume_text = _read_text_resume(application.resume)
    if resume_text:
        return resume_text, "application resume"

    return "", "none"


def _build_job_text(job, job_description=None):
    parts = []
    if job_description:
        parts.append(job_description)
    if job:
        for field in [job.description, job.requirements, job.skills_required]:
            if field:
                parts.append(str(field))
    return "\n".join(parts).strip()


@lru_cache(maxsize=1)
def _split_skills(skills_text):
    if not skills_text:
        return []
    return [s.strip() for s in skills_text.split(",") if s.strip()]


def _extract_skill_matches(resume_text, job_skills):
    """
    Extract matched and missing skills using simple string matching.
    Compatible with all Python versions, no spaCy dependency.
    """
    if not resume_text or not job_skills:
        return [], list(job_skills)

    # Normalize resume text for case-insensitive matching
    resume_lower = resume_text.lower()
    
    matched = []
    missing = []
    
    for skill in job_skills:
        if not skill:
            continue
        
        # Check for exact match (case-insensitive) with word boundaries
        skill_lower = skill.lower()
        
        # Check if skill appears as whole word or in common variations
        # e.g., "python" matches "Python", "python,", "python.", etc.
        if skill_lower in resume_lower:
            matched.append(skill)
        else:
            missing.append(skill)
    
    return matched, missing


def _infer_years_experience(resume_text):
    if not resume_text:
        return None

    patterns = [
        r"(\d{1,2})\+?\s*(?:years|yrs)\s+(?:of\s+)?experience",
        r"(\d{1,2})\+?\s*(?:years|yrs)",
    ]

    years = []
    for pattern in patterns:
        for match in re.findall(pattern, resume_text, flags=re.IGNORECASE):
            try:
                years.append(int(match))
            except ValueError:
                continue

    return max(years) if years else None


def _normalize_title(text):
    if not text:
        return set()
    return {token for token in re.split(r"\W+", text.lower()) if len(token) > 2}


@lru_cache(maxsize=1)
def _load_upskilling_data():
    """Load the Employee Upskilling Dataset for market insights"""
    dataset_path = Path(getattr(settings, "MEDIA_ROOT", "media")) / "models" / "Employee_Upskilling_Dataset.csv"

    if not dataset_path.exists():
        logger.warning(f"Upskilling dataset not found at {dataset_path}; skipping market insights.")
        return None

    try:
        df = pd.read_csv(dataset_path)
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        
        # Ensure success column is numeric
        if "success_in_hiring_process" in df.columns:
            df["success_in_hiring_process"] = pd.to_numeric(df["success_in_hiring_process"], errors="coerce").fillna(0)
        
        logger.info(f"Loaded upskilling dataset: {len(df)} records")
        return df
    except Exception as exc:
        logger.error(f"Failed to load upskilling dataset: {exc}")
        return None


def _get_market_success_rate(job_title, industry=None):
    """Get market success rate for similar roles from upskilling dataset"""
    df = _load_upskilling_data()
    if df is None or "success_in_hiring_process" not in df.columns:
        return None

    title_tokens = _normalize_title(job_title)
    if not title_tokens:
        return None

    # Match by job role or current job title
    role_cols = [col for col in ["job_role", "current_job_title"] if col in df.columns]
    if not role_cols:
        return None

    matched_rows = []
    for col in role_cols:
        for idx, val in df[col].items():
            if pd.isna(val):
                continue
            val_tokens = _normalize_title(str(val))
            overlap = len(title_tokens & val_tokens) / max(len(title_tokens | val_tokens), 1)
            if overlap >= 0.4:
                matched_rows.append(idx)

    if not matched_rows:
        return None

    subset = df.loc[list(set(matched_rows))]
    
    # Filter by industry if provided
    if industry and "industry" in df.columns:
        industry_match = subset[subset["industry"].str.lower() == industry.lower()]
        if not industry_match.empty:
            subset = industry_match

    if subset.empty:
        return None

    success_rate = subset["success_in_hiring_process"].mean() * 100
    total_count = len(subset)

    return {
        "success_rate": success_rate,
        "sample_size": total_count,
        "role_match": True,
    }


def _get_upskilling_recommendations(job_title, current_skills=None):
    """Get AI upskilling recommendations based on market data"""
    df = _load_upskilling_data()
    if df is None:
        return []

    title_tokens = _normalize_title(job_title)
    if not title_tokens:
        return []

    # Match similar roles
    role_cols = [col for col in ["job_role", "current_job_title"] if col in df.columns]
    if not role_cols or "ai_upskilling_type" not in df.columns or "success_in_hiring_process" not in df.columns:
        return []

    matched_rows = []
    for col in role_cols:
        for idx, val in df[col].items():
            if pd.isna(val):
                continue
            val_tokens = _normalize_title(str(val))
            overlap = len(title_tokens & val_tokens) / max(len(title_tokens | val_tokens), 1)
            if overlap >= 0.4:
                matched_rows.append(idx)

    if not matched_rows:
        return []

    subset = df.loc[list(set(matched_rows))]
    if subset.empty:
        return []

    # Get upskilling types with success rates
    upskilling_success = subset.groupby("ai_upskilling_type")["success_in_hiring_process"].agg(["mean", "count"]).reset_index()
    upskilling_success = upskilling_success[upskilling_success["count"] >= 5]  # Min sample size
    upskilling_success = upskilling_success.sort_values("mean", ascending=False)

    recommendations = []
    for _, row in upskilling_success.head(3).iterrows():
        skill_type = row["ai_upskilling_type"]
        success_rate = row["mean"] * 100
        if pd.notna(skill_type) and success_rate > 50:
            recommendations.append({
                "skill": str(skill_type),
                "success_rate": success_rate,
            })

    return recommendations


def _get_market_insights(job_title, industry=None):
    """Get comprehensive market insights for a job"""
    success_data = _get_market_success_rate(job_title, industry)
    upskilling_recs = _get_upskilling_recommendations(job_title)

    if not success_data and not upskilling_recs:
        return None

    return {
        "market_success_rate": success_data.get("success_rate") if success_data else None,
        "sample_size": success_data.get("sample_size") if success_data else 0,
        "upskilling_recommendations": upskilling_recs,
    }


def _build_xai(job, resume_text, candidate_id=None, job_description=None):
    job_skills = _split_skills(job.skills_required if job else "")
    matched_skills, missing_skills = _extract_skill_matches(resume_text, job_skills)
    years = _infer_years_experience(resume_text)
    market_insights = _get_market_insights(job.title if job else "", getattr(job, "company", None))

    lines = []
    if job_skills:
        lines.append(f"{len(matched_skills)}/{len(job_skills)} required skills")
    if years is not None:
        lines.append(f"{years} years relevant experience (resume)")
    
    if market_insights:
        if market_insights["market_success_rate"]:
            lines.append(f"Market success rate for this role: {market_insights['market_success_rate']:.1f}% (from {market_insights['sample_size']} profiles)")
        
        if market_insights["upskilling_recommendations"]:
            top_skill = market_insights["upskilling_recommendations"][0]
            lines.append(f"Top upskilling: {top_skill['skill']} ({top_skill['success_rate']:.0f}% success rate)")
    else:
        lines.append("Market insights: not available")

    explanation = "Matched because:\n- " + "\n- ".join(lines) if lines else "Matched because: resume similarity"

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "experience_years": years,
        "similar_role": market_insights is not None,
        "similar_role_success": market_insights,
        "market_insights": market_insights,
        "explanation": explanation,
    }


def _calculate_feature_importance(features, weights):
    """
    Calculate feature importance percentages based on weighted contributions.
    More reliable than SHAP and compatible with all numpy versions.
    """
    values = np.array(features, dtype=float)
    weight_array = np.array(weights, dtype=float)
    if values.size == 0 or weight_array.size == 0:
        return []

    # Calculate weighted contributions
    contributions = values * weight_array
    total = contributions.sum()
    
    if total == 0:
        return [0.0] * len(features)
    
    # Return percentage contribution of each feature
    return (contributions / total * 100).tolist()


def _build_user_embedding(user, resume_text):
    """
    Build personalized user embedding based on:
    - Resume/profile (base signal)
    - Applied jobs (positive signal)
    - Rejected implicit preferences (negative signal)
    - Viewed jobs weighted by engagement time
    
    Returns weighted embedding vector
    """
    if not resume_text or not hasattr(ranker, "model") or ranker.model is None:
        return None
    
    # Import here to avoid circular dependency
    from jobs.models import JobApplication, JobPreference, JobView
    
    # Base embedding from resume
    base_embedding = ranker.model.encode(resume_text)
    weighted_embeddings = [base_embedding * 1.0]  # Base weight 1.0
    
    # Get behavioral data (last 90 days)
    cutoff_date = timezone.now() - timedelta(days=90)
    
    # Positive signals: Applied jobs (weight: 0.5 per job)
    applied_jobs = JobApplication.objects.filter(
        applicant=user,
        applied_at__gte=cutoff_date
    ).select_related('job')[:20]
    
    for app in applied_jobs:
        job_text = _build_job_text(app.job)
        if job_text:
            job_emb = ranker.model.encode(job_text)
            weighted_embeddings.append(job_emb * 0.5)  # Strong positive signal
    
    # Negative signals: Rejected preferences (weight: -0.3)
    rejected_prefs = JobPreference.objects.filter(
        user=user,
        preference_type='rejected',
        created_at__gte=cutoff_date
    ).select_related('job')[:10]
    
    for pref in rejected_prefs:
        job_text = _build_job_text(pref.job)
        if job_text:
            job_emb = ranker.model.encode(job_text)
            weighted_embeddings.append(job_emb * -0.3)  # Negative signal
    
    # Engagement signals: Viewed jobs (weight based on time spent)
    viewed_jobs = JobView.objects.filter(
        user=user,
        viewed_at__gte=cutoff_date,
        time_spent_seconds__gte=10  # At least 10 seconds
    ).select_related('job').order_by('-time_spent_seconds')[:15]
    
    for view in viewed_jobs:
        job_text = _build_job_text(view.job)
        if job_text:
            job_emb = ranker.model.encode(job_text)
            # Weight by engagement: 0.1 to 0.4 based on time spent
            engagement_weight = min(0.4, view.time_spent_seconds / 300)  # Max at 5 minutes
            weighted_embeddings.append(job_emb * engagement_weight)
    
    # Saved jobs (weight: 0.4)
    saved_prefs = JobPreference.objects.filter(
        user=user,
        preference_type='saved',
        created_at__gte=cutoff_date
    ).select_related('job')[:10]
    
    for pref in saved_prefs:
        job_text = _build_job_text(pref.job)
        if job_text:
            job_emb = ranker.model.encode(job_text)
            weighted_embeddings.append(job_emb * 0.4)
    
    # Compute weighted average
    if len(weighted_embeddings) == 1:
        return base_embedding  # No behavioral data, use base only
    
    user_embedding = np.mean(weighted_embeddings, axis=0)
    return user_embedding


def _get_collaborative_boost(user, job, max_boost=10.0):
    """
    Collaborative filtering: boost score based on similar users' behavior
    If users with similar profiles applied to this job, boost its score
    """
    from jobs.models import JobApplication, JobView
    from accounts.models import Profile
    
    try:
        user_profile = user.profile
        user_skills = set(user_profile.get_skills_list())
        
        if not user_skills:
            return 0.0
        
        # Find users with similar skills who applied to this job
        similar_applicants = JobApplication.objects.filter(
            job=job
        ).select_related('applicant__profile')[:50]
        
        similarity_scores = []
        for app in similar_applicants:
            try:
                other_skills = set(app.applicant.profile.get_skills_list())
                if other_skills:
                    overlap = len(user_skills & other_skills)
                    union = len(user_skills | other_skills)
                    if union > 0:
                        jaccard = overlap / union
                        similarity_scores.append(jaccard)
            except:
                continue
        
        if similarity_scores:
            avg_similarity = np.mean(similarity_scores)
            boost = avg_similarity * max_boost
            return boost
        
    except Exception as e:
        logger.debug(f"Collaborative boost failed: {e}")
    
    return 0.0


def get_job_recommendations(user_profile, jobs, use_personalization=True):
    """
    Netflix-style personalized job feed.
    
    Uses:
    - User embedding vector (profile + behavioral history)
    - Job embedding vectors
    - Cosine similarity
    - Collaborative filtering
    
    Feed evolves based on:
    - Applied jobs (positive signal)
    - Rejected jobs (negative signal)
    - Time spent on job posts (engagement signal)
    - Saved jobs (interest signal)
    
    Returns ranked list of jobs personalized to the user.
    """
    from jobs.models import JobApplication, JobPreference, JobView
    
    recommendations = []
    resume_text = _read_text_resume(user_profile.resume)

    if not resume_text or not hasattr(ranker, "model") or ranker.model is None:
        for job in jobs:
            recommendations.append({
                "job": job,
                "score": 0,
                "reason": "Upload a PDF resume to enable AI matching.",
                "improvements": [],
            })
        return recommendations

    # Build personalized user embedding (Netflix-style)
    if use_personalization:
        user_embedding = _build_user_embedding(user_profile.user, resume_text)
        if user_embedding is None:
            user_embedding = ranker.model.encode(resume_text)
    else:
        user_embedding = ranker.model.encode(resume_text)
    
    # Get jobs user already interacted with to filter out
    applied_job_ids = set(
        JobApplication.objects.filter(applicant=user_profile.user)
        .values_list('job_id', flat=True)
    )
    rejected_job_ids = set(
        JobPreference.objects.filter(user=user_profile.user, preference_type='rejected')
        .values_list('job_id', flat=True)
    )
    ignored_job_ids = set(
        JobPreference.objects.filter(user=user_profile.user, preference_type='ignored')
        .values_list('job_id', flat=True)
    )

    for job in jobs:
        # Skip already applied/rejected/ignored jobs
        if job.id in applied_job_ids or job.id in rejected_job_ids or job.id in ignored_job_ids:
            continue
        
        job_text = _build_job_text(job)
        if not job_text:
            continue

        job_emb = ranker.model.encode(job_text)
        similarity = cosine_similarity([user_embedding], [job_emb]).flatten()[0] * 100
        
        # Apply collaborative filtering boost
        if use_personalization:
            collab_boost = _get_collaborative_boost(user_profile.user, job)
            similarity = min(100, similarity + collab_boost)

        xai = _build_xai(job, resume_text, candidate_id=user_profile.user.id)
        job_skills = _split_skills(job.skills_required)
        skill_pct = 0.0
        if job_skills:
            skill_pct = (len(xai["matched_skills"]) / len(job_skills)) * 100

        exp_score = 0.0
        if job.experience_required and xai["experience_years"] is not None:
            exp_score = min(100.0, (xai["experience_years"] / job.experience_required) * 100)

        weights = {
            "similarity": 0.6,
            "skills": 0.3 if job_skills else 0.0,
            "experience": 0.1 if exp_score else 0.0,
        }
        total_weight = sum(weights.values()) or 1.0
        score = (
            similarity * weights["similarity"]
            + skill_pct * weights["skills"]
            + exp_score * weights["experience"]
        ) / total_weight

        importance = _calculate_feature_importance(
            [similarity, skill_pct, exp_score],
            [weights["similarity"], weights["skills"], weights["experience"]],
        )
        if importance:
            xai["explanation"] += (
                "\n- Feature importance: similarity "
                f"{importance[0]:.0f}%, skills {importance[1]:.0f}%, experience {importance[2]:.0f}%"
            )

        improvements = []
        if xai["missing_skills"]:
            improvements.extend(xai["missing_skills"][:3])
        if job.experience_required and (xai["experience_years"] or 0) < job.experience_required:
            improvements.append(f"Gain {job.experience_required - (xai['experience_years'] or 0)} more years experience")
        
        # Add upskilling recommendations from market data
        if xai.get("market_insights") and xai["market_insights"].get("upskilling_recommendations"):
            for rec in xai["market_insights"]["upskilling_recommendations"][:2]:
                improvements.append(f"{rec['skill']} (AI upskilling)")

        recommendations.append({
            "job": job,
            "score": round(min(100, max(0, score))),
            "reason": xai["explanation"],
            "improvements": improvements,
            "personalized": use_personalization,
        })

        logger.info(f"PERSONALIZED AI: {job.title} for {user_profile.user.username}: {score:.1f}%")

    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations


def _rank_applications_strict(job, applications):
    """Fallback ranking based on profile skills and experience."""
    job_skills = job.get_skills_list()
    ranked = []

    for application in applications:
        try:
            profile = application.applicant.profile
        except Exception:
            application.match_score = 0.0
            application.ranking_notes = "No profile"
            application.save()
            ranked.append(application)
            continue

        user_skills = profile.get_skills_list()
        score = 0.0
        notes = []

        skill_score = calculate_skill_match(user_skills, job_skills)
        score += skill_score * 0.5
        notes.append(f"Skills: {skill_score:.0f}%")

        experience_gap = profile.experience_years - job.experience_required

        if experience_gap >= 0:
            exp_score = 100
            notes.append(f"Exp: ✓ ({profile.experience_years}y)")
        elif experience_gap >= -2:
            exp_score = max(0, 50 + (experience_gap * 25))
            notes.append(f"Exp: {profile.experience_years}y (need {job.experience_required}y)")
        else:
            exp_score = 0
            notes.append(f"Exp: {abs(experience_gap)}y below")

        score += exp_score * 0.35

        if profile.education:
            edu_score = 10
            notes.append("Edu: ✓")
        else:
            edu_score = 0
        score += edu_score

        if application.resume or profile.resume:
            score += 5
            notes.append("Resume: ✓")

        score = min(100, max(0, score))
        application.match_score = round(score, 1)
        application.ranking_notes = " | ".join(notes)
        application.save()

        ranked.append(application)
        logger.info(
            f"STRICT RANK: {application.applicant.get_full_name()} for {job.title}: {score:.1f}%"
            f" (S:{skill_score:.0f}% E:{exp_score:.0f}%)"
        )

    ranked.sort(key=lambda x: x.match_score, reverse=True)
    return ranked


def rank_applications(job, applications, job_description=None):
    """
    Rank job applications using the resume AI model.
    Falls back to strict profile scoring if resume text or model is unavailable.
    """
    applications = list(applications)
    if not applications:
        return []

    job_text = _build_job_text(job, job_description)
    if not job_text or not hasattr(ranker, "model") or ranker.model is None:
        for application in applications:
            application.match_score = 0.0
            application.ranking_notes = "AI model unavailable"
            application.save()
        return applications

    ai_apps = []
    resume_texts = []
    ranked = []
    sources = {}

    for application in applications:
        resume_text, source = _build_resume_text(application)

        if resume_text:
            ai_apps.append(application)
            resume_texts.append(resume_text)
            sources[application.id] = source
        else:
            application.match_score = 0.0
            application.ranking_notes = "PDF resume required"
            application.save()
            ranked.append(application)

    if not ai_apps:
        return ranked

    try:
        job_emb = ranker.model.encode(job_text)
        resume_embs = ranker.model.encode(resume_texts)
        similarity_scores = cosine_similarity(resume_embs, [job_emb]).flatten() * 100

        for application, similarity, resume_text in zip(ai_apps, similarity_scores, resume_texts):
            xai = _build_xai(
                job,
                resume_text,
                candidate_id=application.applicant.id,
                job_description=job_description,
            )
            job_skills = _split_skills(job.skills_required)
            skill_pct = 0.0
            if job_skills:
                skill_pct = (len(xai["matched_skills"]) / len(job_skills)) * 100

            exp_score = 0.0
            if job.experience_required and xai["experience_years"] is not None:
                exp_score = min(100.0, (xai["experience_years"] / job.experience_required) * 100)

            weights = {
                "similarity": 0.7,
                "skills": 0.2 if job_skills else 0.0,
                "experience": 0.1 if exp_score else 0.0,
            }
            total_weight = sum(weights.values()) or 1.0
            score = (
                similarity * weights["similarity"]
                + skill_pct * weights["skills"]
                + exp_score * weights["experience"]
            ) / total_weight

            importance = _calculate_feature_importance(
                [similarity, skill_pct, exp_score],
                [weights["similarity"], weights["skills"], weights["experience"]],
            )
            if importance:
                xai["explanation"] += (
                    "\n- Feature importance: similarity "
                    f"{importance[0]:.0f}%, skills {importance[1]:.0f}%, experience {importance[2]:.0f}%"
                )

            application.match_score = round(float(score), 1)
            application.ranking_notes = xai["explanation"]
            application.xai_data = xai
            application.save()
            ranked.append(application)

        logger.info(f"AI resume ranking complete for {len(ai_apps)} candidates")
    except Exception as exc:
        logger.error(f"AI resume ranking failed: {exc}")
        for application in ai_apps:
            application.match_score = 0.0
            application.ranking_notes = "AI ranking failed"
            application.save()
        return applications

    ranked.sort(key=lambda x: x.match_score, reverse=True)
    return ranked
