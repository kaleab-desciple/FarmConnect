"""MongoDB infrastructure module for AI Diagnosis and Forum."""
from .entities import (
    AIDiagnosis,
    AIDiagnosisCreate,
    ImageMetadata,
    AIModelPrediction,
    TreatmentRecommendationDetail,
    ForumThread,
    ForumThreadCreate,
    ForumComment,
    ForumCommentCreate,
    KnowledgeBaseArticle,
)
from .repositories import (
    MongoDBClient,
    AIDiagnosisRepository,
    ForumThreadRepository,
    KnowledgeBaseRepository,
)

__all__ = [
    "AIDiagnosis",
    "AIDiagnosisCreate",
    "ImageMetadata",
    "AIModelPrediction",
    "TreatmentRecommendationDetail",
    "ForumThread",
    "ForumThreadCreate",
    "ForumComment",
    "ForumCommentCreate",
    "KnowledgeBaseArticle",
    "MongoDBClient",
    "AIDiagnosisRepository",
    "ForumThreadRepository",
    "KnowledgeBaseRepository",
]
