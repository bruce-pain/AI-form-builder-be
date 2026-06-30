"""LLM conversation data model"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base.model import BaseTableModel


class ConversationPrompt(BaseTableModel):
    __tablename__ = "conversation_prompts"

    conversation_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    prompt: Mapped[str] = mapped_column(nullable=False)

    # immutable log — no updated_at column
    updated_at = None
