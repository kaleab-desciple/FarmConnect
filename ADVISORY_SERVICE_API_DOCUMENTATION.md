# Advisory Service API Documentation
## Farm Connect - AgriManagement System

**Service Port:** 8004  
**Database:** MongoDB (Knowledge Base) + PostgreSQL (Forums)  
**Version:** 1.0.0  
**Last Updated:** February 2024

---

## Table of Contents
1. [Overview](#1-overview)
2. [Forums API](#2-forums-api)
3. [Knowledge Base API](#3-knowledge-base-api)
4. [Moderation API](#4-moderation-api)
5. [Notification System](#5-notification-system)
6. [Rate Limiting & Spam Prevention](#6-rate-limiting--spam-prevention)
7. [Error Handling](#7-error-handling)
8. [Authentication & Authorization](#8-authentication--authorization)

---

## 1. Overview

The Advisory Service provides farmers with access to agricultural expertise through:

- **Forums**: Discussion platform for questions, experiences, and community engagement
- **Knowledge Base**: Searchable repository of agricultural information
- **Moderation**: Content moderation and spam prevention
- **Notifications**: Real-time alerts for forum interactions

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      ADVISORY SERVICE                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │     Forums       │  │  Knowledge Base  │                │
│  │   (PostgreSQL)   │  │    (MongoDB)      │                │
│  └──────────────────┘  └──────────────────┘                │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │   Moderation     │  │  Notifications   │                │
│  │   (PostgreSQL)   │  │   (PostgreSQL)   │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Forums API

### Base URL
```
/api/v1/advisory/forums
```

### Endpoints

#### 2.1 Create Thread

**POST** `/threads`

Create a new forum discussion thread.

**Request Body:**
```json
{
  "title": "Early blight in tomatoes - treatment advice needed",
  "content_body": "I'm seeing early blight symptoms on my Roma tomatoes...",
  "content_format": "markdown",
  "category": "pest_disease",
  "subcategory": "fungal_diseases",
  "tags": ["tomato", "early_blight", "fungicide"],
  "context_field_id": "FLD-2024-001",
  "context_crop_type": "tomato",
  "context_growth_stage": "fruiting"
}
```

**Field Descriptions:**

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `title` | string | Yes | 10-200 chars | Thread title |
| `content_body` | string | Yes | 20-10000 chars | Main content |
| `content_format` | string | No | markdown/html | Content format |
| `category` | string | Yes | Valid category | Thread category |
| `subcategory` | string | No | - | Subcategory |
| `tags` | array | No | Max 10 tags | Tag list |
| `context_field_id` | string | No | Valid field ID | Linked field |
| `context_crop_type` | string | No | - | Crop type |
| `context_growth_stage` | string | No | - | Growth stage |

**Categories:**

| Category | Description |
|----------|-------------|
| `pest_disease` | Pest and disease discussions |
| `irrigation` | Irrigation techniques |
| `fertilization` | Fertilizer use |
| `soil_health` | Soil management |
| `weather` | Weather impact |
| `harvest_storage` | Harvest and storage |
| `market_prices` | Market discussions |
| `equipment` | Equipment topics |
| `organic_farming` | Organic methods |
| `livestock` | Livestock topics |
| `general` | General discussion |

**Response (201 Created):**
```json
{
  "id": "thread-uuid-abc123",
  "title": "Early blight in tomatoes - treatment advice needed",
  "slug": "early-blight-tomatoes-treatment-advice",
  "status": "open",
  "view_count": 0,
  "comment_count": 0,
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

#### 2.2 List Threads

**GET** `/threads`

List forum threads with filtering and pagination.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | string | - | Filter by category |
| `status` | string | - | open, resolved, closed |
| `author_id` | string | - | Filter by author |
| `tags` | array | - | Filter by tags |
| `sort_by` | string | bumped_at | Sort field |
| `sort_order` | string | desc | asc or desc |
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page |

**Response (200 OK):**
```json
{
  "threads": [
    {
      "id": "thread-uuid-abc123",
      "title": "Early blight in tomatoes",
      "slug": "early-blight-tomatoes",
      "author_username": "JohnFarmer",
      "author_reputation": 150,
      "category": "pest_disease",
      "status": "open",
      "view_count": 125,
      "comment_count": 8,
      "upvote_count": 5,
      "created_at": "2024-01-15T10:00:00Z",
      "bumped_at": "2024-01-15T12:00:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

#### 2.3 Get Thread

**GET** `/threads/{thread_id}`

Get detailed thread information including comments.

**Response (200 OK):**
```json
{
  "id": "thread-uuid-abc123",
  "title": "Early blight in tomatoes",
  "slug": "early-blight-tomatoes",
  "content_body": "Full thread content...",
  "author_id": "user-uuid",
  "author_username": "JohnFarmer",
  "author_badge": "experienced_farmer",
  "author_reputation": 150,
  "category": "pest_disease",
  "tags": ["tomato", "early_blight"],
  "status": "open",
  "view_count": 125,
  "comment_count": 8,
  "comments": [
    {
      "id": "comment-uuid-1",
      "content": "Try copper fungicide...",
      "author_username": "DrAgronomist",
      "upvote_count": 3,
      "is_accepted_answer": true,
      "created_at": "2024-01-15T11:00:00Z"
    }
  ],
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

---

#### 2.4 Create Comment

**POST** `/threads/{thread_id}/comments`

Add a reply to a thread.

**Request Body:**
```json
{
  "content": "Apply copper-based fungicide every 7-10 days...",
  "parent_id": null,
  "attachments": [
    {
      "type": "image",
      "url": "https://s3.example.com/photos/treatment.jpg"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": "comment-uuid-xyz789",
  "thread_id": "thread-uuid-abc123",
  "content": "Apply copper-based fungicide...",
  "author_id": "user-uuid",
  "author_username": "DrAgronomist",
  "upvote_count": 0,
  "is_accepted_answer": false,
  "created_at": "2024-01-15T11:00:00Z"
}
```

---

#### 2.5 Vote on Content

**POST** `/threads/{thread_id}/vote`  
**POST** `/comments/{comment_id}/vote`

Vote on threads or comments.

**Request Body:**
```json
{
  "vote_type": "up"
}
```

**Response (200 OK):**
```json
{
  "thread_id": "thread-uuid-abc123",
  "vote_type": "up",
  "upvote_count": 6,
  "downvote_count": 1,
  "user_vote": "up"
}
```

---

#### 2.6 Resolve Thread

**POST** `/threads/{thread_id}/resolve`

Mark thread as resolved (author only).

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `accepted_answer_id` | string | ID of best answer |
| `resolution_summary` | string | Summary of solution |

**Response (200 OK):**
```json
{
  "thread_id": "thread-uuid-abc123",
  "status": "resolved",
  "accepted_answer_id": "comment-uuid-1",
  "resolved_at": "2024-01-15T14:00:00Z"
}
```

---

#### 2.7 Bookmark Thread

**POST** `/threads/{thread_id}/bookmark`

Save thread to bookmarks.

**Response (200 OK):**
```json
{
  "thread_id": "thread-uuid-abc123",
  "bookmarked": true,
  "message": "Thread bookmarked"
}
```

---

## 3. Knowledge Base API

### Base URL
```
/api/v1/advisory/knowledge
```

### Endpoints

#### 3.1 Create Article

**POST** `/articles`

Create a new knowledge article.

**Request Body:**
```json
{
  "title": "Early Blight in Tomatoes: Identification and Treatment",
  "summary": "A comprehensive guide to identifying and treating early blight in tomato crops.",
  "content": "Full article content in markdown...",
  "article_type": "disease_guide",
  "category": "disease_management",
  "subcategory": "fungal_diseases",
  "tags": ["tomato", "early_blight", "fungus", "disease"],
  "keywords": ["alternaria solani", "target spot", "tomato disease"],
  "related_crop_types": ["tomato", "potato", "pepper"],
  "linked_treatments": ["treatment-uuid-1", "treatment-uuid-2"]
}
```

**Article Types:**

| Type | Description |
|------|-------------|
| `pest_guide` | Pest identification and control |
| `disease_guide` | Disease identification and treatment |
| `treatment_protocol` | Step-by-step treatments |
| `best_practice` | Agricultural best practices |
| `faq` | Frequently asked questions |
| `tutorial` | How-to guides |
| `regional_guide` | Region-specific information |
| `crop_guide` | Crop-specific guides |

**Response (201 Created):**
```json
{
  "id": "article-uuid-def456",
  "title": "Early Blight in Tomatoes",
  "slug": "early-blight-tomatoes",
  "status": "draft",
  "version": 1,
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

#### 3.2 List Articles

**GET** `/articles`

List knowledge articles with filtering.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter by category |
| `article_type` | string | Filter by type |
| `crop_type` | string | Filter by crop |
| `status` | string | draft, published, archived |
| `sort_by` | string | created_at, view_count |
| `page` | integer | Page number |
| `page_size` | integer | Items per page |

**Response (200 OK):**
```json
{
  "articles": [
    {
      "id": "article-uuid-def456",
      "title": "Early Blight in Tomatoes",
      "slug": "early-blight-tomatoes",
      "summary": "A comprehensive guide...",
      "article_type": "disease_guide",
      "category": "disease_management",
      "tags": ["tomato", "disease"],
      "view_count": 1250,
      "helpful_count": 89,
      "status": "published",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 156,
  "page": 1,
  "page_size": 20
}
```

---

#### 3.3 Search Articles

**POST** `/search`

Search knowledge base with relevance ranking.

**Request Body:**
```json
{
  "query": "tomato early blight treatment",
  "categories": ["disease_management"],
  "crop_types": ["tomato"],
  "page": 1,
  "page_size": 20
}
```

**Response (200 OK):**
```json
{
  "query": "tomato early blight treatment",
  "total_results": 5,
  "results": [
    {
      "id": "article-uuid-def456",
      "title": "Early Blight in Tomatoes",
      "slug": "early-blight-tomatoes",
      "summary": "A comprehensive guide...",
      "article_type": "disease_guide",
      "category": "disease_management",
      "relevance_score": 0.95,
      "matched_terms": ["tomato", "early blight", "treatment"],
      "view_count": 1250,
      "helpful_count": 89
    }
  ],
  "suggestions": ["copper fungicide", "crop rotation"]
}
```

---

#### 3.4 Get Article

**GET** `/articles/{article_id}`

Get**Response (200 full article content.

 OK):**
```json
{
  "id": "article-uuid-def456",
  "title": "Early Blight in Tomatoes",
  "slug": "early-blight-tomatoes",
  "summary": "A comprehensive guide...",
  "content": "Full article content...",
  "article_type": "disease_guide",
  "category": "disease_management",
  "tags": ["tomato", "disease"],
  "author_username": "DrAgronomist",
  "author_badge": "certified_expert",
  "version": 3,
  "view_count": 1250,
  "helpful_count": 89,
  "related_articles": [
    {
      "id": "article-uuid-2",
      "title": "Late Blight in Potatoes",
      "slug": "late-blight-potatoes"
    }
  ],
  "published_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-02-01T14:00:00Z"
}
```

---

#### 3.5 Rate Article

**POST** `/articles/{article_id}/rate`

Rate article helpfulness.

**Request Body:**
```json
{
  "helpful": true
}
```

**Response (200 OK):**
```json
{
  "article_id": "article-uuid-def456",
  "helpful": true,
  "helpful_count": 90,
  "not_helpful_count": 5
}
```

---

## 4. Moderation API

### Base URL
```
/api/v1/advisory/forums/moderation
```

Requires `moderator` or `admin` role.

### Endpoints

#### 4.1 Get Pending Reports

**GET** `/reports/pending`

Get moderation reports awaiting action.

**Response (200 OK):**
```json
{
  "reports": [
    {
      "id": "report-uuid-123",
      "thread_id": "thread-uuid-abc",
      "report_type": "spam",
      "report_reason": "Promotional content detected",
      "moderation_status": "pending",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

---

#### 4.2 Process Report

**POST** `/reports/{report_id}/decision`

Take action on a moderation report.

**Request Body:**
```json
{
  "decision": "approve",
  "notes": "Content is acceptable agricultural advice"
}
```

**Response (200 OK):**
```json
{
  "report_id": "report-uuid-123",
  "decision": "approve",
  "status": "resolved",
  "moderator_id": "admin-uuid",
  "resolved_at": "2024-01-15T12:00:00Z"
}
```

---

#### 4.3 Moderate Thread

**POST** `/threads/{thread_id}/moderate`

Directly moderate a thread.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `action` | string | approve, reject, hide, delete |
| `reason` | string | Moderation reason |

---

#### 4.4 Moderation Stats

**GET** `/moderator/stats`

Get moderation statistics.

**Response (200 OK):**
```json
{
  "pending_reports": 5,
  "resolved_today": 12,
  "resolved_this_week": 45,
  "average_resolution_time_hours": 2.5,
  "top_report_types": [
    {"type": "spam", "count": 25},
    {"type": "inappropriate", "count": 15}
  ]
}
```

---

## 5. Notification System

### 5.1 Notification Types

| Type | Description | Channels |
|------|-------------|----------|
| `thread_reply` | New reply to thread | in_app, email |
| `answer_accepted` | Answer was accepted | in_app |
| `comment_upvote` | Comment received upvote | in_app |
| `mention` | User mentioned | in_app, email |
| `moderation_action` | Content moderated | in_app, email |

### 5.2 Get Notifications

**GET** `/api/v1/notifications`

Get user notifications.

**Response (200 OK):**
```json
{
  "notifications": [
    {
      "id": "notif-uuid-123",
      "type": "thread_reply",
      "title": "New reply to your thread",
      "message": "DrAgronomist replied to 'Early Blight...'",
      "action_url": "/threads/thread-uuid",
      "is_read": false,
      "created_at": "2024-01-15T12:00:00Z"
    }
  ],
  "unread_count": 3
}
```

---

## 6. Rate Limiting & Spam Prevention

### 6.1 Rate Limits

| Endpoint Type | Limit |
|--------------|-------|
| Read operations | 100/hour |
| Write operations | 20/minute |
| Search queries | 30/minute |
| File uploads | 10/hour |

### 6.2 Spam Detection

Content is automatically checked for:

- Excessive links (max 2)
- All caps content
- Repeated characters
- Promotional language
- Suspicious domains

**Spam Response (400 Bad Request):**
```json
{
  "detail": "Content contains prohibited patterns",
  "reasons": [
    {
      "type": "excessive_links",
      "message": "Too many links in content"
    }
  ]
}
```

---

## 7. Error Handling

### Standard Error Response

```json
{
  "detail": "Error message describing the issue"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | Success | Request completed |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Validation | Invalid data |
| 429 | Rate Limited | Too many requests |
| 500 | Server Error | Internal error |

---

## 8. Authentication & Authorization

### Required Roles

| Endpoint | Required Role |
|----------|---------------|
| Create thread/comment | authenticated |
| Vote, bookmark | authenticated |
| Create article | authenticated |
| Publish article | admin |
| Moderate content | moderator |
| View moderation stats | moderator |

### JWT Token

Include token in header:
```
Authorization: Bearer <jwt_token>
```

---

## Appendix A: Ethiopian Agriculture Reference

### Common Crops

| Crop | Amharic | Regions |
|------|---------|---------|
| Teff | ጤፍ | Highlands |
| Wheat | ስንዴ | Oromia, Amhara |
| Maize | ድንች | Lowlands |
| Coffee | ቡና | SNNPR |

### Forum Categories by Context

| Category | Use For |
|----------|---------|
| `pest_disease` | Disease identification, pest control |
| `irrigation` | Water management, irrigation systems |
| `fertilization` | Fertilizer recommendations |
| `soil_health` | Soil testing, improvement |
| `weather` | Weather alerts, seasonal advice |

---

## Appendix B: Sample Requests

### Complete Thread Flow

```bash
# 1. Create thread
curl -X POST "http://localhost:8004/api/v1/advisory/forums/threads" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Early blight in tomatoes",
    "content_body": "I need help with early blight...",
    "category": "pest_disease",
    "tags": ["tomato", "disease"]
  }'

# 2. Get thread details
curl "http://localhost:8004/api/v1/advisory/forums/threads/<thread_id>"

# 3. Add comment
curl -X POST "http://localhost:8004/api/v1/advisory/forums/threads/<thread_id>/comments" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Try copper fungicide..."}'

# 4. Search knowledge base
curl -X POST "http://localhost:8004/api/v1/advisory/knowledge/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "tomato disease treatment"}'
```

---

**Document Version:** 1.0.0  
**Last Updated:** February 2024  
**Support:** support@farmconnect.et
