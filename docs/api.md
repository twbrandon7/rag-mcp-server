# Web Content Vectorization Service API

## 📄 Introduction

This API follows resource-oriented design principles for managing web content vectorization processes. It enables users to organize URLs into projects, process those URLs to extract content, generate vector embeddings, and perform semantic similarity searches.

### API Design Principles

- **Resource-Oriented Design**: Resources are named using noun-based collections with unique identifiers.
- **Standard HTTP Methods**: GET, POST, PATCH, DELETE are used for their standard semantics.
- **Consistent Naming**: Resource names follow predictable patterns using collection identifiers and resource IDs.
- **Strong Consistency**: State changes through API operations provide immediate consistency guarantees.
- **Stateless Protocol**: Each request happens in isolation with the server maintaining persistence.

### Resource Hierarchy

The primary resource hierarchy follows this pattern:
- `users/{user_id}`: User accounts
- `projects/{project_id}`: Projects owned by users
  - `urls/{url_id}`: URLs submitted within a project
    - `chunks/{chunk_id}`: Content chunks extracted from URLs
  - `shares/{share_id}`: Sharing permissions for projects

## 📋 Endpoints

### 1. User Management

#### 1.1 Register User

* **Endpoint**: `POST /api/v1/users`
* **Description**: Create a new user account with email and password.
* **Request Body**:

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

* **Response** (201 Created):

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "created_at": "2025-05-28T12:34:56.789Z"
}
```

---

#### 1.2 Login (Email/Password)

* **Endpoint**: `POST /api/v1/auth/token`
* **Description**: Authenticate with email and password to obtain an access token.
* **Request Body**:

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

* **Response** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

#### 1.3 Google OAuth Login

* **Endpoint**: `POST /api/v1/auth/google`
* **Description**: Complete Google OAuth flow by providing a token from Google. If an account with the same email already exists, the accounts will be automatically linked.
* **Request Body**:

```json
{
  "token": "google_oauth_token_here"
}
```

* **Response** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

#### 1.4 Microsoft OAuth Login

* **Endpoint**: `POST /api/v1/auth/microsoft`
* **Description**: Complete Microsoft OAuth flow by providing a token from Microsoft. If an account with the same email already exists, the accounts will be automatically linked.
* **Request Body**:

```json
{
  "token": "microsoft_oauth_token_here"
}
```

* **Response** (200 OK):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

#### 1.5 Get Current User

* **Endpoint**: `GET /api/v1/users/me`
* **Description**: Get information about the currently authenticated user.
* **Authorization**: Bearer Token Required
* **Response** (200 OK):

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "created_at": "2025-05-28T12:34:56.789Z"
}
```

---

### 2. Project Management

#### 2.1 Create Project

* **Endpoint**: `POST /api/v1/projects`
* **Description**: Create a new project for organizing URLs and vectors.
* **Authorization**: Bearer Token Required
* **Request Body**:

```json
{
  "project_name": "Research Project"
}
```

* **Response** (201 Created):

```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_name": "Research Project",
  "created_at": "2025-05-28T12:34:56.789Z"
}
```

---

#### 2.2 List Projects

* **Endpoint**: `GET /api/v1/projects`
* **Description**: Get all projects belonging to the authenticated user.
* **Authorization**: Bearer Token Required
* **Response** (200 OK):

```json
[
  {
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "project_name": "Research Project",
    "created_at": "2025-05-28T12:34:56.789Z"
  },
  {
    "project_id": "661e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "project_name": "Personal Notes",
    "created_at": "2025-05-28T13:45:56.789Z"
  }
]
```

---

#### 2.3 Get Project

* **Endpoint**: `GET /api/v1/projects/{project_id}`
* **Description**: Get details of a specific project.
* **Authorization**: Bearer Token Required
* **Response** (200 OK):

```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_name": "Research Project",
  "created_at": "2025-05-28T12:34:56.789Z"
}
```

---

#### 2.4 Update Project

* **Endpoint**: `PATCH /api/v1/projects/{project_id}`
* **Description**: Update a project's details.
* **Authorization**: Bearer Token Required
* **Request Body**:

```json
{
  "project_name": "Updated Research Project"
}
```

* **Response** (200 OK):

```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_name": "Updated Research Project",
  "created_at": "2025-05-28T12:34:56.789Z"
}
```

---

#### 2.5 Delete Project

* **Endpoint**: `DELETE /api/v1/projects/{project_id}`
* **Description**: Delete a project and all its associated data.
* **Authorization**: Bearer Token Required
* **Response** (204 No Content)

---

### 3. URL Management

#### 3.1 Submit Single URL

* **Endpoint**: `POST /api/v1/projects/{project_id}/urls`
* **Description**: Submit a single URL for processing within a project. If the URL is already processed in this project, a 409 Conflict response will be returned with details of the existing URL entry.
* **Authorization**: Bearer Token Required
* **Request Body**:

```json
{
  "original_url": "https://example.com/article"
}
```

* **Response** (202 Accepted):

```json
{
  "url_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "original_url": "https://example.com/article",
  "status": "pending",
  "failure_reason": null,
  "submitted_at": "2025-05-28T12:34:56.789Z",
  "last_updated_at": "2025-05-28T12:34:56.789Z"
}
```

* **Response** (409 Conflict - Duplicate URL):

```json
{
  "message": "URL already exists in this project",
  "existing_url": {
    "url_id": "550e8400-e29b-41d4-a716-446655440000",
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "original_url": "https://example.com/article",
    "status": "stored", // Current status of the existing URL
    "failure_reason": null,
    "submitted_at": "2025-05-28T10:34:56.789Z",
    "last_updated_at": "2025-05-28T10:45:56.789Z"
  }
}
```

---

#### 3.2 Submit Multiple URLs

* **Endpoint**: `POST /api/v1/projects/{project_id}/urls:batch`
* **Description**: Submit multiple URLs for processing within a project. Duplicate URLs will be filtered out and returned separately in the response.
* **Authorization**: Bearer Token Required
* **Request Body**:

```json
{
  "urls": [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://example.com/article3"
  ]
}
```

* **Response** (202 Accepted):

```json
{
  "submitted_urls": [
    {
      "url_id": "550e8400-e29b-41d4-a716-446655440000",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "original_url": "https://example.com/article1",
      "status": "pending",
      "failure_reason": null,
      "submitted_at": "2025-05-28T12:34:56.789Z",
      "last_updated_at": "2025-05-28T12:34:56.789Z"
    },
    {
      "url_id": "661e8400-e29b-41d4-a716-446655440000",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "original_url": "https://example.com/article2",
      "status": "pending",
      "failure_reason": null,
      "submitted_at": "2025-05-28T12:34:56.789Z",
      "last_updated_at": "2025-05-28T12:34:56.789Z"
    },
    {
      "url_id": "772e8400-e29b-41d4-a716-446655440000",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "original_url": "https://example.com/article3",
      "status": "pending",
      "failure_reason": null,
      "submitted_at": "2025-05-28T12:34:56.789Z",
      "last_updated_at": "2025-05-28T12:34:56.789Z"
    }
  ],
  "duplicate_urls": [
    {
      "url_id": "883e8400-e29b-41d4-a716-446655440000",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "original_url": "https://example.com/article4",
      "status": "stored",
      "failure_reason": null,
      "submitted_at": "2025-05-28T10:34:56.789Z",
      "last_updated_at": "2025-05-28T10:45:56.789Z"
    }
  ]
}
```

---

#### 3.3 Get URLs in Project

* **Endpoint**: `GET /api/v1/projects/{project_id}/urls`
* **Description**: Get all URLs associated with a project.
* **Authorization**: Bearer Token Required
* **Query Parameters**:
  * `status` (optional): Filter URLs by status (pending, crawling, encoding, stored, failed)
* **Response** (200 OK):

```json
[
  {
    "url_id": "550e8400-e29b-41d4-a716-446655440000",
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "original_url": "https://example.com/article1",
    "status": "stored",
    "failure_reason": null,
    "submitted_at": "2025-05-28T12:34:56.789Z",
    "last_updated_at": "2025-05-28T12:45:56.789Z"
  },
  {
    "url_id": "661e8400-e29b-41d4-a716-446655440000",
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "original_url": "https://example.com/article2",
    "status": "failed",
    "failure_reason": "Page not found (404)",
    "submitted_at": "2025-05-28T12:34:56.789Z",
    "last_updated_at": "2025-05-28T12:36:56.789Z"
  }
]
```

---

#### 3.4 Get URL Status

* **Endpoint**: `GET /api/v1/projects/{project_id}/urls/{url_id}`
* **Description**: Get details and processing status of a specific URL.
* **Authorization**: Bearer Token Required
* **Response** (200 OK):

```json
{
  "url_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "original_url": "https://example.com/article",
  "status": "stored",
  "failure_reason": null,
  "submitted_at": "2025-05-28T12:34:56.789Z",
  "last_updated_at": "2025-05-28T12:45:56.789Z"
}
```

---

### 4. Content Chunks & Vectors

#### 4.1 Get Content Chunks for URL

* **Endpoint**: `GET /api/v1/projects/{project_id}/urls/{url_id}/chunks`
* **Description**: Retrieve the content chunks associated with a processed URL.
* **Authorization**: Bearer Token Required
* **Query Parameters**:
  * `include_vectors` (optional): Boolean to include vector embeddings in the response (default: false)
* **Response** (200 OK):

```json
[
  {
    "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
    "url_id": "550e8400-e29b-41d4-a716-446655440000",
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "This is the first chunk of content from the webpage...",
    "chunk_index": 0,
    "created_at": "2025-05-28T12:45:56.789Z",
    "embedding": [0.123, -0.456, 0.789, ...] // Only included if include_vectors=true
  },
  {
    "chunk_id": "661e8400-e29b-41d4-a716-446655440000",
    "url_id": "550e8400-e29b-41d4-a716-446655440000",
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "This is the second chunk of content from the webpage...",
    "chunk_index": 1,
    "created_at": "2025-05-28T12:45:56.789Z",
    "embedding": [0.234, -0.567, 0.890, ...] // Only included if include_vectors=true
  }
]
```

---

#### 4.2 Get Transformer Model Information

* **Endpoint**: `GET /api/v1/system/transformer-model`
* **Description**: Retrieve information about the transformer model used for vectorization.
* **Authorization**: Bearer Token Required
* **Response** (200 OK):

```json
{
  "model_name": "all-MiniLM-L6-v2",
  "embedding_size": 384,
  "max_sequence_length": 256,
  "chunking_strategy": "text_splitting",
  "chunk_size": 512,
  "chunk_overlap": 50,
  "configuration": {
    "normalize_embeddings": true
  },
  "version": "1.0.0"
}
```

---

### 5. Project Sharing

#### 5.1 Create Project Share

* **Endpoint**: `POST /api/v1/projects/{project_id}/shares`
* **Description**: Share a project with another user or generate a sharing token.
* **Authorization**: Bearer Token Required

##### Option A: Share with Specific User

* **Request Body**:

```json
{
  "shared_with_user_id": "661e8400-e29b-41d4-a716-446655440000"
}
```

* **Response** (201 Created):

```json
{
  "name": "projects/550e8400-e29b-41d4-a716-446655440000/shares/550e8400-e29b-41d4-a716-446655440000",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "shared_with_user_id": "661e8400-e29b-41d4-a716-446655440000",
  "share_token": null,
  "created_at": "2025-05-28T12:34:56.789Z"
}
```

##### Option B: Generate Share Token

* **Request Body**:
```json
{}
```

* **Response** (201 Created):
```json
{
  "name": "projects/550e8400-e29b-41d4-a716-446655440000/shares/550e8400-e29b-41d4-a716-446655440000",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "shared_with_user_id": null,
  "share_token": "abc123def456",
  "created_at": "2025-05-28T12:34:56.789Z"
}
```

---

#### 5.2 List Project Shares

* **Endpoint**: `GET /api/v1/projects/{project_id}/shares`
* **Description**: List all shares for a specific project.
* **Authorization**: Bearer Token Required
* **Response** (200 OK):

```json
{
  "shares": [
    {
      "name": "projects/550e8400-e29b-41d4-a716-446655440000/shares/550e8400-e29b-41d4-a716-446655440000",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "shared_with_user_id": "661e8400-e29b-41d4-a716-446655440000",
      "share_token": null,
      "created_at": "2025-05-28T12:34:56.789Z"
    },
    {
      "name": "projects/550e8400-e29b-41d4-a716-446655440000/shares/661e8400-e29b-41d4-a716-446655440000",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "shared_with_user_id": null,
      "share_token": "def456ghi789",
      "created_at": "2025-05-28T13:45:56.789Z"
    }
  ]
}
```

---

#### 5.3 Delete Project Share

* **Endpoint**: `DELETE /api/v1/projects/{project_id}/shares/{share_id}`
* **Description**: Remove a specific share from a project.
* **Authorization**: Bearer Token Required
* **Response** (204 No Content)

---

#### 5.4 Access Shared Project

* **Endpoint**: `GET /api/v1/shared-projects/{token}`
* **Description**: Access a project using a share token.
* **Response** (200 OK):

```json
{
  "name": "projects/550e8400-e29b-41d4-a716-446655440000",
  "project_name": "Research Project",
  "created_at": "2025-05-28T12:34:56.789Z"
}
```

---

#### 5.5 List Shared Projects

* **Endpoint**: `GET /api/v1/users/me/shared-projects`
* **Description**: List all projects shared with the authenticated user.
* **Authorization**: Bearer Token Required
* **Response** (200 OK):

```json
{
  "shared_projects": [
    {
      "name": "projects/550e8400-e29b-41d4-a716-446655440000",
      "project_name": "Research Project",
      "owner_email": "other.user@example.com",
      "shared_at": "2025-05-28T12:34:56.789Z"
    }
  ]
}
```

---

### 6. MCP Server API for LLM Queries

#### 6.1 Query Content (MCP Endpoint)

* **Endpoint**: `POST /api/v1/projects:query`
* **Description**: Query content from one or more projects using semantic similarity.
* **Authorization**: Bearer Token Required
* **Request Body**:

```json
{
  "query": "What are the main advantages of vector databases?",
  "project_ids": ["550e8400-e29b-41d4-a716-446655440000", "661e8400-e29b-41d4-a716-446655440000"],
  "top_k": 5
}
```

* **Response** (200 OK):

```json
{
  "results": [
    {
      "content": "Vector databases offer several advantages over traditional databases. First, they enable similarity search, allowing you to find content that is semantically similar rather than just exact matches. Second, they are optimized for the high-dimensional vectors produced by modern embedding models...",
      "url": "https://example.com/article1",
      "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "similarity_score": 0.92
    },
    {
      "content": "One of the key benefits of vector databases is their performance when dealing with large-scale similarity searches. Traditional databases struggle with the 'curse of dimensionality', but specialized vector databases implement algorithms like HNSW or IVF that make these searches practical...",
      "url": "https://example.com/article2",
      "chunk_id": "661e8400-e29b-41d4-a716-446655440000",
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "similarity_score": 0.87
    }
    // Additional results...
  ]
}
```

---

### 7. System Status & Operations

#### 7.1 Get System Status

* **Endpoint**: `GET /api/v1/system/status`
* **Description**: Retrieve the current system status including processing queue information.
* **Authorization**: Bearer Token Required
* **Response** (200 OK):

```json
{
  "status": "healthy",
  "processing_queue": {
    "pending_urls": 12,
    "crawling_urls": 3,
    "encoding_urls": 5
  },
  "system_load": {
    "cpu_usage": 45,
    "memory_usage": 62,
    "disk_usage": 38
  },
  "embedding_model_status": "operational"
}
```

---

#### 7.2 Reprocess URL

* **Endpoint**: `POST /api/v1/projects/{project_id}/urls/{url_id}:reprocess`
* **Description**: Request reprocessing of a previously processed URL.
* **Authorization**: Bearer Token Required
* **Request Body**: Empty
* **Response** (202 Accepted):

```json
{
  "url_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "original_url": "https://example.com/article",
  "status": "pending", // Reset to pending
  "failure_reason": null,
  "submitted_at": "2025-05-28T12:34:56.789Z",
  "last_updated_at": "2025-05-28T14:23:45.678Z" // Updated timestamp
}
```

---
