---
applyTo: 'backend/**'
---
## Example of the Project Structure
The project is structured as follows:

```
backend/
├── alembic/
├── src
│   ├── auth
│   │   ├── router.py
│   │   ├── schemas.py  # pydantic models
│   │   ├── models.py  # db models
│   │   ├── dependencies.py
│   │   ├── config.py  # local configs
│   │   ├── constants.py  # module specific constants and error codes
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── users
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── ...
│   ├── projects
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── ...
│   ├── urls
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── ...
│   ├── chunks
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── ...
│   ├── shares
│   │   ├── router.py
│   │   ├── ...
│   ├── vectorization
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── ...
│   ├── system
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── ...
│   ├── aws
│   │   ├── client.py  # client model for external service communication
│   │   ├── schemas.py
│   │   ├── ...
│   ├── config.py  # global configs
│   ├── models.py  # global models
│   ├── exceptions.py  # global exceptions
│   ├── pagination.py  # global module e.g. pagination
│   ├── database.py  # db connection related stuff
│   └── main.py
├── tests/
│   ├── auth
│   ├── users
│   ├── projects
│   ├── urls
│   ├── chunks
│   ├── shares
│   ├── vectorization
│   ├── system
│   └── aws
├── scripts/
│   ├── format.sh
│   ├── lint.sh
│   └── test.sh
├── .env
├── .gitignore
├── .dockerignore
├── logging.ini
├── Dockerfile
├── pyproject.toml
├── README.md
├── uv.lock
└── alembic.ini
```
1. Store all domain directories inside `src` folder
   1. `src/` - highest level of an app, contains common models, configs, and constants, etc.
   2. `src/main.py` - root of the project, which inits the FastAPI app
2. Each package has its own router, schemas, models, etc.
   1. `router.py` - is a core of each module with all the endpoints
   2. `schemas.py` - for pydantic models
   3. `models.py` - for db models
   4. `service.py` - module specific business logic  
   5. `dependencies.py` - router dependencies
   6. `constants.py` - module specific constants and error codes
   7. `config.py` - e.g. env vars
   8. `utils.py` - non-business logic functions, e.g. response normalization, data enrichment, etc.
   9. `exceptions.py` - module specific exceptions, e.g. `ProjectNotFound`, `InvalidUserData`
3. When package requires services or dependencies or constants from other packages - import them with an explicit module name
```python
from src.auth import constants as auth_constants
from src.projects import service as projects_service
from src.urls.constants import ErrorCode as UrlsErrorCode  # in case we have Standard ErrorCode in constants module of each package
```
