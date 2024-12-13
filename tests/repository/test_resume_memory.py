from datetime import date
from uuid import uuid4

import pytest

from src.domain.entity.resume import Experience, Resume
from src.repository.resume_memory import InMemoryResumeRepository


@pytest.fixture
def repository():
    """Fixture to provide a fresh repository for each test."""
    return InMemoryResumeRepository()


@pytest.fixture
def sample_resume():
    """Fixture to provide a sample resume instance."""
    return Resume(
        id=uuid4(),
        candidate_name="John Doe",
        summary="Experienced software engineer with expertise in scalable systems.",
        skills=["Python", "SQL", "Data Engineering"],
        location="New York, USA",
        phone="123-456-7890",
        email="johndoe@example.com",
        linkedin="linkedin.com/in/johndoe",
        version=1,
        experiences=[
            Experience(
                id=uuid4(),
                employer="Tech Corp",
                position="Software Engineer",
                start_date=date(2020, 5, 1),
                end_date=date(2022, 8, 31),
                description=[
                    "Developed scalable microservices.",
                    "Implemented CI/CD pipelines.",
                    "Collaborated with cross-functional teams.",
                ],
                employer_details="Leading tech company specializing in AI solutions.",
                employer_website="https://www.techcorp.com",
                job_location="San Francisco, CA",
            ),
            Experience(
                id=uuid4(),
                employer="Startup Inc",
                position="Backend Engineer",
                start_date=date(2018, 3, 1),
                end_date=date(2020, 4, 30),
                description=[
                    "Designed and maintained RESTful APIs.",
                    "Improved system reliability by 30%.",
                    "Optimized database queries for performance.",
                ],
                employer_details="Innovative startup focused on IoT solutions.",
                employer_website="https://www.startupinc.com",
                job_location="New York, NY",
            ),
        ],
    )


def test_create_resume(repository, sample_resume):
    """Test creating a resume."""
    repository.create(sample_resume)
    assert repository.read(sample_resume.id) == sample_resume


def test_create_duplicate_resume(repository, sample_resume):
    """Test creating a duplicate resume raises an error."""
    repository.create(sample_resume)
    with pytest.raises(ValueError, match="Resume with id .* already exists."):
        repository.create(sample_resume)


def test_read_resume(repository, sample_resume):
    """Test reading a resume by ID."""
    repository.create(sample_resume)
    resume = repository.read(sample_resume.id)
    assert resume == sample_resume


def test_read_nonexistent_resume(repository):
    """Test reading a non-existent resume returns None."""
    resume = repository.read(uuid4())
    assert resume is None


def test_update_resume(repository, sample_resume):
    """Test updating an existing resume."""
    repository.create(sample_resume)
    data = {"resume_name": "Some resume name"}
    repository.update(resume_id=sample_resume.id, data=data)
    resume = repository.read(sample_resume.id)
    assert resume.resume_name == data["resume_name"]


def test_update_nonexistent_resume(repository, sample_resume):
    """Test updating a non-existent resume raises an error."""
    with pytest.raises(ValueError, match="Resume with id .* does not exist."):
        repository.update(sample_resume.id, {})


def test_delete_resume(repository, sample_resume):
    """Test deleting a resume."""
    repository.create(sample_resume)
    repository.delete(sample_resume.id)
    assert repository.read(sample_resume.id) is None


def test_delete_nonexistent_resume(repository):
    """Test deleting a non-existent resume raises an error."""
    with pytest.raises(ValueError, match="Resume with id .* does not exist."):
        repository.delete(uuid4())


def test_list_resumes(repository, sample_resume):
    """Test listing all resumes."""
    repository.create(sample_resume)
    resumes = repository.list()
    assert len(resumes) == 1
    assert resumes[0] == sample_resume


def test_list_resumes_empty(repository):
    """Test listing resumes when repository is empty."""
    resumes = repository.list()
    assert resumes == []


@pytest.fixture
def repository_with_resumes():
    """Fixture to populate the repository with sample resumes."""
    repo = InMemoryResumeRepository()
    repo.create(
        Resume(
            id=uuid4(),
            candidate_name="John Doe",
            summary="Experienced software engineer.",
            skills=["Python", "SQL", "Data Engineering"],
            location="New York, USA",
            phone="123-456-7890",
            email="johndoe@example.com",
            linkedin="linkedin.com/in/johndoe",
            version=1,
            experiences=[
                Experience(
                    id=uuid4(),
                    employer="TechCorp",
                    position="Software Engineer",
                    start_date=date(2020, 5, 1),
                    end_date=date(2022, 8, 31),
                    description=[
                        "Developed scalable microservices.",
                        "Implemented CI/CD pipelines.",
                    ],
                    employer_details="Leading tech company.",
                    employer_website="https://www.techcorp.com",
                    job_location="San Francisco, CA",
                )
            ],
        )
    )
    repo.create(
        Resume(
            id=uuid4(),
            candidate_name="Jane Smith",
            summary="Product manager with strong leadership skills.",
            skills=["Product Management", "Agile", "Scrum"],
            location="San Francisco, USA",
            phone="234-567-8901",
            email="janesmith@example.com",
            linkedin="linkedin.com/in/janesmith",
            version=2,
            resume_name="resume_1",
            experiences=[
                Experience(
                    id=uuid4(),
                    employer="BizCorp",
                    position="Product Manager",
                    start_date=date(2019, 3, 1),
                    end_date=date(2021, 12, 31),
                    description=[
                        "Led cross-functional teams.",
                        "Increased product revenue by 20%.",
                    ],
                    employer_details="Global business solutions company.",
                    employer_website="https://www.bizcorp.com",
                    job_location="San Francisco, CA",
                )
            ],
        )
    )
    return repo


def test_list_all_resumes(repository_with_resumes):
    """Test listing all resumes without filters."""
    result = repository_with_resumes.list()
    assert len(result) == 2


@pytest.mark.parametrize(
    "filters,expected_names",
    [
        ({"resume_name": "resume_1"}, ["resume_1"]),
        ({}, [None, "resume_1"]),
        ({"version": 2}, ["resume_1"]),
    ],
)
def test_list_resumes_by_skills(repository_with_resumes, filters, expected_names):
    """Test listing resumes filtered by skills."""
    result = repository_with_resumes.list(filters)
    names = [resume.resume_name for resume in result]
    assert names == expected_names
