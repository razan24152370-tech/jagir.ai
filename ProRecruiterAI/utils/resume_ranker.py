import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
import pickle
import logging
import sys

# NumPy 2.x compatibility bridge for loading older pickles
import numpy
import numpy.core.numeric
import numpy.core.multiarray
sys.modules['numpy._core'] = numpy.core
sys.modules['numpy._core.numeric'] = numpy.core.numeric
sys.modules['numpy._core.multiarray'] = numpy.core.multiarray

logger = logging.getLogger(__name__)

class ResumeRanker:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResumeRanker, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Paths - adjust if different
        self.model_path = os.path.join(settings.MEDIA_ROOT, 'models/resume_ranking_model')
        self.data_path = os.path.join(settings.MEDIA_ROOT, 'models/processed_resumes.pkl')
        
        self.model = None
        self.df = None
        self._load_model()
        self._initialized = True
    
    def _load_model(self):
        """Load model and data ONCE at startup"""
        try:
            self.model = SentenceTransformer(self.model_path)
            self.df = pd.read_pickle(self.data_path)
            logger.info(f"✅ Loaded {len(self.df)} resumes and model")
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            raise
    
    def rank_candidates(self, job_description, top_k=10):
        """Main ranking function"""
        if self.model is None or self.df is None:
            raise ValueError("Model not loaded")
        
        # Encode job description
        jd_emb = self.model.encode(job_description)
        
        # Compute similarity scores
        resume_embs = np.stack(self.df['resume_embedding'].values)
        scores = cosine_similarity(resume_embs, [jd_emb]).flatten() * 100
        
        # Create results
        self.df['rank_score'] = scores
        results = self.df.nlargest(top_k, 'rank_score')
        
        return results[['rank_score', 'skills_list', 'full_resume_text']].to_dict('records')

# Helper for true lazy loading
_ranker_instance = None

def get_ranker_instance():
    """Get or create the singleton ResumeRanker instance"""
    global _ranker_instance
    if _ranker_instance is None:
        _ranker_instance = ResumeRanker()
    return _ranker_instance