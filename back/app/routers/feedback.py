from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import auth, models
from ..database import get_db
from ..schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter(
    prefix="/api/v1/feedback",
    tags=["Feedback"],
)


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    feedback = models.Feedback(
        username=current_user.username,
        category=feedback_in.category,
        comment=feedback_in.comment,
        page_url=feedback_in.page_url,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
