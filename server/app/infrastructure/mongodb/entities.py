"""MongoDB entities for AI Diagnosis and Forum content."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v, handler=None):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


class AIDiagnosis(BaseModel):
    """AI Diagnosis entity stored in MongoDB."""
    id: Optional[str] = Field(None, alias="_id")
    postgres_report_id: str
    farm_id: str
    field_id: str
    crop_cycle_id: Optional[str] = None
    
    image_analysis: Dict[str, Any] = {}
    ai_models: List[Dict[str, Any]] = []
    ensemble_result: Optional[Dict[str, Any]] = None
    
    treatment_recommendations: List[Dict[str, Any]] = []
    similar_cases: List[Dict[str, Any]] = []
    farmer_feedback: Optional[Dict[str, Any]] = None
    
    status: str = "processing"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AIDiagnosisCreate(BaseModel):
    """AI Diagnosis creation entity."""
    postgres_report_id: str
    farm_id: str
    field_id: str
    crop_cycle_id: Optional[str] = None


class ImageMetadata(BaseModel):
    """Image metadata entity."""
    width: int
    height: int
    format: str
    exif: Optional[Dict[str, Any]] = None


class AIModelPrediction(BaseModel):
    """AI Model prediction entity."""
    model_id: str
    model_version: str
    framework: str
    inference_time_ms: int
    predictions: List[Dict[str, Any]] = []
    ensemble_weight: float = 0.0


class TreatmentRecommendationDetail(BaseModel):
    """Treatment recommendation detail entity."""
    treatment_id: str
    type: str
    name: str
    active_ingredient: Optional[str] = None
    confidence: float
    dosage: Dict[str, str] = {}
    application: Dict[str, Any] = {}
    safety: Dict[str, Any] = {}
    estimated_cost_per_ha_usd: float = 0.0
    effectiveness_rating: float = 0.0
    expected_results_days: int = 0


# Forum/Community Entities
class ForumThread(BaseModel):
    """Forum Thread entity for MongoDB."""
    id: Optional[str] = Field(None, alias="_id")
    
    author: Dict[str, Any] = {}
    title: str
    slug: Optional[str] = None
    
    category: str
    subcategory: Optional[str] = None
    tags: List[str] = []
    
    content: Dict[str, Any] = {}
    context: Dict[str, Any] = {}
    
    engagement: Dict[str, int] = {}
    comments: List[Dict[str, Any]] = []
    
    status: str = "open"
    resolution: Optional[Dict[str, Any]] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    bumped_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ForumThreadCreate(BaseModel):
    """Forum Thread creation entity."""
    author_id: str
    author_username: str
    title: str
    category: str
    subcategory: Optional[str] = None
    tags: List[str] = []
    body: str
    attachments: Optional[List[Dict[str, Any]]] = None
    related_field_id: Optional[str] = None
    related_crop_cycle_id: Optional[str] = None
    crop_type: Optional[str] = None
    growth_stage: Optional[str] = None


class ForumComment(BaseModel):
    """Forum Comment entity."""
    id: Optional[str] = Field(None, alias="_id")
    
    thread_id: str
    author: Dict[str, Any] = {}
    content: str
    parent_id: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    upvotes: int = 0
    is_accepted_answer: bool = False
    replies: List[Dict[str, Any]] = []
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ForumCommentCreate(BaseModel):
    """Forum Comment creation entity."""
    thread_id: str
    author_id: str
    author_username: str
    content: str
    parent_id: Optional[str] = None


# Knowledge Base Entities
class KnowledgeBaseArticle(BaseModel):
    """Knowledge Base Article entity."""
    id: Optional[str] = Field(None, alias="_id")
    
    title: str
    slug: Optional[str] = None
    summary: Optional[str] = None
    content: str
    format: str = "markdown"
    
    author: Dict[str, Any] = {}
    category: str
    subcategory: Optional[str] = None
    tags: List[str] = []
    
    metadata: Dict[str, Any] = {}
    
    views: int = 0
    upvotes: int = 0
    downvotes: int = 0
    
    status: str = "draft"
    published_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
