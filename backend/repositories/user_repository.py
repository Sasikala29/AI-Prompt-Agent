from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.user import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_user(self) -> User | None:
        statement = (
            select(User)
            .order_by(User.id.asc())
            .limit(1)
        )

        return self.db.scalar(statement)

    def create_user(self, name: str) -> User:
        user = User(name=name.strip())

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def update_user(
        self,
        user: User,
        name: str,
    ) -> User:
        user.name = name.strip()

        self.db.commit()
        self.db.refresh(user)

        return user
