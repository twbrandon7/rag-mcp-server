---
applyTo: 'backend/src/**/exceptions.py'
---
## ValueErrors might become Pydantic ValidationError
If you raise a `ValueError` in a Pydantic schema that is directly faced by the client, it will return a nice detailed response to users.
```python
# src.profiles.schemas
from pydantic import BaseModel, field_validator

class ProfileCreate(BaseModel):
    username: str
    
    @field_validator("password", mode="after")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit or "
                "special symbol"
            )

        return password


# src.profiles.routes
from fastapi import APIRouter

router = APIRouter()


@router.post("/profiles")
async def get_creator_posts(profile_data: ProfileCreate):
   pass
```
**Response Example:**

<img src="images/value_error_response.png" width="400" height="auto">
