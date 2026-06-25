"""LLM conversation repository"""

from typing import List

from sqlalchemy.orm import Session

from app.core.base.repository import BaseRepository
from app.features.llm.models import ConversationPrompt


class ConversationRepository(BaseRepository[ConversationPrompt]):
    def __init__(self, db: Session):
        super().__init__(ConversationPrompt, db)

    def get_prompts(self, conversation_id: str) -> List[str]:
        entries = (
            self.db.query(self.model)
            .filter(self.model.conversation_id == conversation_id)
            .order_by(self.model.created_at)
            .all()
        )
        return [e.prompt for e in entries]

    def delete_conversation(self, conversation_id: str) -> None:
        self.db.query(self.model).filter(
            self.model.conversation_id == conversation_id
        ).delete()
        self.db.commit()
