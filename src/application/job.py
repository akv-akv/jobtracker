from src.application.base.manage import Manage
from src.domain.entity.job import Job
from src.domain.entity.user import User
from src.repository.base.repository import Repository


class ManageJob(Manage[Job]):
    pass


class JobRepository(Repository[Job]):
    pass


class ManageUser(Manage[User]):
    pass


class UserRepository(Repository[User]):
    pass
