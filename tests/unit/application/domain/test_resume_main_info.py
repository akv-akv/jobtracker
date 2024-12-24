from uuid import UUID, uuid4

from src.application.domain.entity.resume_main_info import ResumeMainInfo


def test_create_resume():
    data = {
        "user_id": uuid4(),
        "title": "Main resume",
        "applicant_name": "John Green",
        "skills": ["sql", "python"],
    }
    resume_main_info = ResumeMainInfo.create(**data)
    assert isinstance(resume_main_info, ResumeMainInfo)
    assert isinstance(resume_main_info.user_id, UUID)
    assert isinstance(resume_main_info.skills, list)
    assert len(resume_main_info.skills) == 2
