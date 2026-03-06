from app.db.models import Task


def test_task_model_has_required_fields():
    cols = {column.name for column in Task.__table__.columns}
    assert {"id", "user_id", "title", "deadline", "duration_minutes", "status"}.issubset(cols)
