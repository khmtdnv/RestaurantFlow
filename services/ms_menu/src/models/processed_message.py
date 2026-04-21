from db.database import Base, created_at, id_pk
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class ProcessedMessage(Base):
    __tablename__ = "processed_messages"

    id: Mapped[id_pk]
    message_id: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[created_at]
