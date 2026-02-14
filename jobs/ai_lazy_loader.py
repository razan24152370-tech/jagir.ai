"""
Lazy loader for AI dependencies to reduce memory footprint on startup.
Only loads heavy ML libraries when actually needed.
"""
import logging

logger = logging.getLogger('jobs')

# Global cache for loaded models
_ranker = None
_sklearn_loaded = False


def get_ranker():
    """Lazy load the resume ranker model"""
    global _ranker
    if _ranker is None:
        try:
            # Use the getter function instead of direct import
            from ProRecruiterAI.utils.resume_ranker import get_ranker_instance
            _ranker = get_ranker_instance()
            logger.info("Resume ranker model loaded successfully via getter")
        except Exception as e:
            logger.warning(f"Failed to load resume ranker: {e}")
            _ranker = None
    return _ranker


def get_sklearn():
    """Lazy load sklearn modules"""
    global _sklearn_loaded
    if not _sklearn_loaded:
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            _sklearn_loaded = True
            logger.info("Sklearn loaded successfully")
            return cosine_similarity
        except Exception as e:
            logger.warning(f"Failed to load sklearn: {e}")
            return None
    else:
        from sklearn.metrics.pairwise import cosine_similarity
        return cosine_similarity


def is_ai_available():
    """Check if AI features are available without loading them"""
    try:
        import torch
        import sentence_transformers
        import sklearn
        return True
    except ImportError:
        return False
