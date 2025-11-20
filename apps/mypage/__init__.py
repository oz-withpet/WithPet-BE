from .repository.user_repo import UserRepository
from .repository.post_repo import PostActivityRepository
from .repository.map_repo import MapActivityRepository
from .services import UserService, PostActivityService, MapActivityService

user_service = UserService(user_repo=UserRepository())
post_activity_service = PostActivityService(repo=PostActivityRepository())
map_activity_service = MapActivityService(repo=MapActivityRepository())

__all__ = []