from sqlalchemy.orm import Session

from backend.repositories.user_repository import UserRepository
from backend.schemas.user import UserResponse


class UserService:

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def get_user(self) -> UserResponse | None:
        user = self.repository.get_user()

        if user is None:
            return None

        return UserResponse(
            id=user.id,
            name=user.name,
        )

    def save_user(self, name: str) -> UserResponse:
        name = name.strip()

        if not name:
            raise ValueError("Name cannot be empty.")

        user = self.repository.get_user()

        if user is None:
            user = self.repository.create_user(name)
        else:
            user = self.repository.update_user(
                user,
                name,
            )

        return UserResponse(
            id=user.id,
            name=user.name,
        )
