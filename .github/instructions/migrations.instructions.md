---
applyTo: 'backend/alembic/versions/**'
---
## Migrations. Alembic
1. Migrations must be static and revertable.
If your migrations depend on dynamically generated data, then 
make sure the only thing that is dynamic is the data itself, not its structure.
2. Generate migrations with descriptive names & slugs. Slug is required and should explain the changes.
3. Set human-readable file template for new migrations. We use `*date*_*slug*.py` pattern, e.g. `2022-08-24_post_content_idx.py`
```
# alembic.ini
file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(slug)s
```