# Test task using FastApi and SQLAlchemy

-   Python (3.11.7) was used
-   Mysql (5.7) was used

**TO run web app:**
1. `cd` into directory: `cd test-task-odoo`
2. Build docker container:  `docker build -t your_image_name .`
3. Run docker container: `docker run -p 8000:8000 your_image_name`
4. Visit `docs` page: `localhost:8000/docs`

This will automatically run both cron job and fastapi web app.
Don't forget to change db uri in `db.py`
