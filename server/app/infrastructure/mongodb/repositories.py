"""MongoDB repositories for AI Diagnosis and Forum content."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId

from app.infrastructure.mongodb.entities import (
    AIDiagnosis,
    AIDiagnosisCreate,
    ForumThread,
    ForumThreadCreate,
    ForumComment,
    ForumCommentCreate,
    KnowledgeBaseArticle,
)


class MongoDBClient:
    """MongoDB client singleton."""
    _instance: Optional["MongoDBClient"] = None
    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self, mongo_url: str, db_name: str):
        """Connect to MongoDB."""
        self._client = AsyncIOMotorClient(mongo_url)
        self._db = self._client[db_name]
    
    def get_db(self) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if self._db is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self._db
    
    async def close(self):
        """Close MongoDB connection."""
        if self._client:
            self._client.close()


class AIDiagnosisRepository:
    """Repository for AI Diagnosis operations in MongoDB."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.ai_diagnoses
    
    async def create(self, diagnosis: AIDiagnosisCreate) -> str:
        """Create a new AI diagnosis record."""
        doc = {
            "postgres_report_id": diagnosis.postgres_report_id,
            "farm_id": diagnosis.farm_id,
            "field_id": diagnosis.field_id,
            "crop_cycle_id": diagnosis.crop_cycle_id,
            "status": "processing",
            "created_at": datetime.utcnow(),
            "processed_at": None,
            "image_analysis": {},
            "ai_models": [],
            "ensemble_result": None,
            "treatment_recommendations": [],
            "similar_cases": [],
            "farmer_feedback": None,
        }
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)
    
    async def get_by_id(self, diagnosis_id: str) -> Optional[Dict[str, Any]]:
        """Get AI diagnosis by ID."""
        doc = await self.collection.find_one({"_id": ObjectId(diagnosis_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    async def get_by_postgres_report_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get AI diagnosis by PostgreSQL report ID."""
        return await self.collection.find_one({"postgres_report_id": report_id})
    
    async def get_by_field_id(self, field_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Get AI diagnoses for a field."""
        cursor = self.collection.find({"field_id": field_id}).sort("created_at", -1).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results
    
    async def update_status(self, diagnosis_id: str, status: str):
        """Update diagnosis status."""
        await self.collection.update_one(
            {"_id": ObjectId(diagnosis_id)},
            {"$set": {"status": status, "processed_at": datetime.utcnow()}}
        )
    
    async def update_results(self, diagnosis_id: str, results: Dict[str, Any]):
        """Update diagnosis with ML results."""
        update_data = {
            "status": "completed",
            "processed_at": datetime.utcnow(),
        }
        if "image_analysis" in results:
            update_data["image_analysis"] = results["image_analysis"]
        if "ai_models" in results:
            update_data["ai_models"] = results["ai_models"]
        if "ensemble_result" in results:
            update_data["ensemble_result"] = results["ensemble_result"]
        
        await self.collection.update_one(
            {"_id": ObjectId(diagnosis_id)},
            {"$set": update_data}
        )
    
    async def add_treatment_recommendations(self, diagnosis_id: str, recommendations: List[Dict[str, Any]]):
        """Add treatment recommendations to diagnosis."""
        await self.collection.update_one(
            {"_id": ObjectId(diagnosis_id)},
            {"$push": {"treatment_recommendations": {"$each": recommendations}}}
        )
    
    async def add_farmer_feedback(self, diagnosis_id: str, feedback: Dict[str, Any]):
        """Add farmer feedback to diagnosis."""
        await self.collection.update_one(
            {"_id": ObjectId(diagnosis_id)},
            {"$set": {"farmer_feedback": feedback}}
        )
    
    async def create_indexes(self):
        """Create MongoDB indexes for AI diagnoses."""
        await self.collection.create_index("postgres_report_id", unique=True)
        await self.collection.create_index([("field_id", 1), ("created_at", -1)])
        await self.collection.create_index([("ensemble_result.primary_diagnosis", 1), ("created_at", -1)])
        await self.collection.create_index("ai_models.predictions.class_name")
        await self.collection.create_index("ensemble_result.confidence")


class ForumThreadRepository:
    """Repository for Forum Thread operations in MongoDB."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.forum_threads
    
    async def create(self, thread: ForumThreadCreate) -> str:
        """Create a new forum thread."""
        doc = {
            "title": thread.title,
            "slug": thread.title.lower().replace(" ", "-") + "-" + ObjectId().__str__()[:8],
            "author": {
                "user_id": thread.author_id,
                "username": thread.author_username,
                "reputation_score": 0,
                "expertise_badge": None,
            },
            "category": thread.category,
            "subcategory": thread.subcategory,
            "tags": thread.tags or [],
            "content": {
                "body": thread.body,
                "format": "markdown",
                "attachments": thread.attachments or [],
            },
            "context": {
                "related_field_id": thread.related_field_id,
                "related_crop_cycle_id": thread.related_crop_cycle_id,
                "crop_type": thread.crop_type,
                "growth_stage": thread.growth_stage,
            },
            "engagement": {
                "views": 0,
                "upvotes": 0,
                "downvotes": 0,
                "bookmarks": 0,
                "shares": 0,
            },
            "comments": [],
            "status": "open",
            "resolution": None,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "bumped_at": datetime.utcnow(),
        }
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)
    
    async def get_by_id(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get forum thread by ID."""
        doc = await self.collection.find_one({"_id": ObjectId(thread_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    async def get_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get forum thread by slug."""
        doc = await self.collection.find_one({"slug": slug})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    async def get_by_category(self, category: str, limit: int = 30, skip: int = 0) -> List[Dict[str, Any]]:
        """Get forum threads by category."""
        cursor = self.collection.find({"category": category}).sort([("created_at", -1)]).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results
    
    async def get_trending(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending forum threads by engagement."""
        cursor = self.collection.find({"status": "open"}).sort("engagement.views", -1).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results
    
    async def add_comment(self, thread_id: str, comment: ForumCommentCreate):
        """Add a comment to a thread."""
        comment_doc = {
            "_id": ObjectId(),
            "thread_id": thread_id,
            "author": {
                "user_id": comment.author_id,
                "username": comment.author_username,
                "badge": None,
            },
            "content": comment.content,
            "parent_id": comment.parent_id,
            "created_at": datetime.utcnow(),
            "upvotes": 0,
            "is_accepted_answer": False,
            "replies": [],
        }
        
        if comment.parent_id:
            # Reply to a comment
            await self.collection.update_one(
                {"_id": ObjectId(thread_id), "comments._id": ObjectId(comment.parent_id)},
                {"$push": {"comments.$.replies": comment_doc}}
            )
        else:
            # Top-level comment
            await self.collection.update_one(
                {"_id": ObjectId(thread_id)},
                {
                    "$push": {"comments": comment_doc},
                    "$set": {"last_activity": datetime.utcnow(), "bumped_at": datetime.utcnow()}
                }
            )
    
    async def upvote(self, thread_id: str, comment_id: Optional[str] = None):
        """Upvote a thread or comment."""
        if comment_id:
            await self.collection.update_one(
                {"_id": ObjectId(thread_id), "comments._id": ObjectId(comment_id)},
                {"$inc": {"comments.$.upvotes": 1, "engagement.upvotes": 1}}
            )
        else:
            await self.collection.update_one(
                {"_id": ObjectId(thread_id)},
                {"$inc": {"engagement.upvotes": 1}}
            )
    
    async def mark_accepted_answer(self, thread_id: str, comment_id: str):
        """Mark a comment as accepted answer."""
        # Unmark any previously accepted answer
        await self.collection.update_one(
            {"_id": ObjectId(thread_id), "comments.is_accepted_answer": True},
            {"$set": {"comments.$.is_accepted_answer": False}}
        )
        # Mark new accepted answer
        await self.collection.update_one(
            {"_id": ObjectId(thread_id), "comments._id": ObjectId(comment_id)},
            {"$set": {"comments.$.is_accepted_answer": True, "status": "resolved"}}
        )
    
    async def create_indexes(self):
        """Create MongoDB indexes for forum threads."""
        await self.collection.create_index("slug", unique=True)
        await self.collection.create_index([("category", 1), ("created_at", -1)])
        await self.collection.create_index("tags", background=True)
        await self.collection.create_index([("context.crop_type", 1), ("created_at", -1)])
        await self.collection.create_index("engagement.views", -1)
        await self.collection.create_index("last_activity", -1)
        await self.collection.create_index([("status", 1), ("created_at", -1)])


class KnowledgeBaseRepository:
    """Repository for Knowledge Base operations in MongoDB."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.knowledge_articles
    
    async def create(self, article: Dict[str, Any]) -> str:
        """Create a new knowledge article."""
        doc = {
            "title": article["title"],
            "slug": article.get("slug") or article["title"].lower().replace(" ", "-").replace("_", "-"),
            "summary": article.get("summary"),
            "content": article["content"],
            "format": article.get("format", "markdown"),
            "author": article["author"],
            "category": article["category"],
            "subcategory": article.get("subcategory"),
            "tags": article.get("tags", []),
            "metadata": article.get("metadata", {}),
            "views": 0,
            "upvotes": 0,
            "downvotes": 0,
            "status": article.get("status", "draft"),
            "published_at": article.get("published_at"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)
    
    async def get_by_id(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Get knowledge article by ID."""
        doc = await self.collection.find_one({"_id": ObjectId(article_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    async def get_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get knowledge article by slug."""
        doc = await self.collection.find_one({"slug": slug})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    async def get_published(self, category: Optional[str] = None, limit: int = 30) -> List[Dict[str, Any]]:
        """Get published knowledge articles."""
        query = {"status": "published"}
        if category:
            query["category"] = category
        
        cursor = self.collection.find(query).sort("published_at", -1).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results
    
    async def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search knowledge articles."""
        # Simple text search using regex
        cursor = self.collection.find({
            "status": "published",
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}},
                {"tags": {"$in": [query.lower()]}},
            ]
        }).limit(limit)
        
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results
    
    async def increment_views(self, article_id: str):
        """Increment article view count."""
        await self.collection.update_one(
            {"_id": ObjectId(article_id)},
            {"$inc": {"views": 1}}
        )
    
    async def create_indexes(self):
        """Create MongoDB indexes for knowledge articles."""
        await self.collection.create_index("slug", unique=True)
        await self.collection.create_index("category")
        await self.collection.create_index("tags", background=True)
        await self.collection.create_index("status")
        await self.collection.create_index([("published_at", -1)])
