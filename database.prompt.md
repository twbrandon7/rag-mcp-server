---
mode: 'agent'
---

## Task
Please execute the following steps to create alembic database migration files.
1. Remove example migration files in `backend/app/alembic/versions`.
2. Create a new migration file with the message "initial migration".
3. Implement the database schema (the database is PostgreSQL)
    ```markdown
    # Database Schema

    ### **1. users Table**

    | **Column Name** | **Data Type** | **Constraints/Description** |
    | --- | --- | --- |
    | user_id | UUID | Primary Key |
    | email | VARCHAR(255) | Unique, Not Null |
    | password_hash | VARCHAR(255) | For email/password accounts (can be NULL if only SSO is used) |
    | google_id | VARCHAR(255) | Unique (for Google SSO, can be NULL) |
    | microsoft_id | VARCHAR(255) | Unique (for Microsoft SSO, can be NULL) |
    | created_at | TIMESTAMP WITH TIME ZONE | Default: Current Timestamp |

    ### **2. projects Table**

    | **Column Name** | **Data Type** | **Constraints/Description** |
    | --- | --- | --- |
    | project_id | UUID | Primary Key |
    | user_id | UUID | Foreign Key referencing users(user_id), ON DELETE CASCADE |
    | project_name | VARCHAR(255) | Not Null, Unique per user (uq_projects_user_id_project_name constraint) |
    | created_at | TIMESTAMP WITH TIME ZONE | Default: Current Timestamp |

    ### **3. shared_projects Table (Optional for explicit sharing)**

    | **Column Name** | **Data Type** | **Constraints/Description** |
    | --- | --- | --- |
    | shared_project_id | UUID | Primary Key |
    | project_id | UUID | Foreign Key referencing projects(project_id), ON DELETE CASCADE |
    | shared_with_user_id | UUID | Foreign Key referencing users(user_id) (can be NULL for public sharing) |
    | share_token | VARCHAR(255) | Unique (for public sharing links) |
    | created_at | TIMESTAMP WITH TIME ZONE | Default: Current Timestamp |

    ### **4. urls Table**

    | **Column Name** | **Data Type** | **Constraints/Description** |
    | --- | --- | --- |
    | url_id | UUID | Primary Key |
    | project_id | UUID | Foreign Key referencing projects(project_id), ON DELETE CASCADE |
    | original_url | TEXT | Not Null, Unique per project (uq_urls_project_id_original_url constraint) |
    | status | VARCHAR(50) | Not Null (e.g., "pending", "crawling", "encoding", "stored", "failed") |
    | failure_reason | TEXT | Stores error message for failed crawls (can be NULL) |
    | submitted_at | TIMESTAMP WITH TIME ZONE | Default: Current Timestamp |
    | last_updated_at | TIMESTAMP WITH TIME ZONE | Default: Current Timestamp |

    ### **5. chunks Table**

    | **Column Name** | **Data Type** | **Constraints/Description** |
    | --- | --- | --- |
    | chunk_id | UUID | Primary Key |
    | url_id | UUID | Foreign Key referencing urls(url_id), ON DELETE CASCADE |
    | project_id | UUID | Foreign Key referencing projects(project_id) (Denormalized for efficient querying) |
    | content | TEXT | Not Null (The original text content of the chunk) |
    | embedding | VECTOR(1536) | The vector embedding (assuming 1536 dimensions), requires pgvector extension |
    | chunk_index | INT | Not Null (Order of the chunk within its original document) |
    | created_at | TIMESTAMP WITH TIME ZONE | Default: Current Timestamp |

    **Indexes and Constraints:**

    - **Unique Constraints:**
    - uq_projects_user_id_project_name on projects(user_id, project_name)
    - uq_urls_project_id_original_url on urls(project_id, original_url)
    - **Indexes:**
    - idx_chunks_embedding on chunks.embedding using HNSW (Hierarchical Navigable Small World) for efficient similarity search: CREATE INDEX idx_chunks_embedding ON chunks USING hnsw (embedding vector_l2_ops);
    ```
4. Revise `backend/app/models.py` to match the schema.

## Note
### How to use alembic
1.  **Initialize Alembic (if not already done)**:
    ```bash
    alembic init alembic
    ```
    This creates an `alembic` directory and an `alembic.ini` configuration file.
    *Note: In this project, this is already set up in the `backend/` directory.*

2.  **Configure `alembic.ini`**:
    Ensure the `sqlalchemy.url` in `alembic.ini` (or your `pyproject.toml` and `env.py` if configured that way) points to your database.
    For this project, the `sqlalchemy.url` is typically set via environment variables, which are read in `backend/alembic/env.py`.

3.  **Create a new migration script**:
    When you make changes to your SQLAlchemy models (e.g., in `backend/app/models.py`), you need to generate a migration script.
    Navigate to the directory containing `alembic.ini` (i.e., `backend/`) and run:
    ```bash
    alembic revision -m "short_description_of_changes"
    ```
    Replace `"short_description_of_changes"` with a meaningful message, like "add_user_email_column". This will create a new file in `backend/alembic/versions/`.

4.  **Edit the new migration script**:
    Open the newly generated file in `backend/alembic/versions/`.
    -   In the `upgrade()` function, add the code to apply your changes (e.g., `op.create_table(...)`, `op.add_column(...)`).
    -   In the `downgrade()` function, add the code to revert your changes (e.g., `op.drop_table(...)`, `op.drop_column(...)`).
    Alembic can sometimes autogenerate migrations based on model changes. See [Auto Generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html) for more details. To attempt autogeneration:
    ```bash
    alembic revision -m "auto_generate_migration_for_models" --autogenerate
    ```
    Always review autogenerated scripts carefully.

5.  **Apply the migration to the database**:
    Run the upgrade command:
    ```bash
    alembic upgrade head
    ```
    This applies all pending migrations up to the latest one (referred to as `head`).

6.  **Downgrade (if necessary)**:
    To revert the last migration:
    ```bash
    alembic downgrade -1
    ```
    To downgrade to a specific revision:
    ```bash
    alembic downgrade <revision_id>
    ```
    To revert all migrations:
    ```bash
    alembic downgrade base
    ```

7.  **View migration status**:
    -   Show current revision: `alembic current`
    -   Show migration history: `alembic history`
    -   Show verbose history: `alembic history --verbose`
