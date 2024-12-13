from datetime import date
from uuid import uuid4

from src.domain.entity.resume import Experience, Resume


def test_experience_creation():
    """Test Experience instantiation with all fields."""
    exp = Experience(
        id=uuid4(),
        employer="ExampleCorp",
        position="Data Engineer",
        description=["Built ETL pipelines", "Led migrations"],
        start_date=date(2021, 5, 1),
        end_date=date(2023, 5, 1),
        employer_details="Global tech company specializing in data solutions.",
        employer_website="https://example.com",
        job_location="New York, NY",
    )

    assert exp.employer == "ExampleCorp"
    assert exp.position == "Data Engineer"
    assert "Built ETL pipelines" in exp.description
    assert exp.start_date == date(2021, 5, 1)
    assert exp.end_date == date(2023, 5, 1)
    assert exp.employer_details == "Global tech company specializing in data solutions."
    assert exp.employer_website == "https://example.com"
    assert exp.job_location == "New York, NY"


def test_experience_optional_fields():
    """Test Experience instantiation with optional fields omitted."""
    exp = Experience(
        id=uuid4(),
        employer="ExampleCorp",
        position="Data Engineer",
        description=["Built ETL pipelines", "Led migrations"],
        start_date=date(2021, 5, 1),
    )

    assert exp.employer == "ExampleCorp"
    assert exp.employer_website is None
    assert exp.job_location is None
    assert exp.end_date is None


def test_resume_creation():
    """Test Resume instantiation with all fields."""
    resume = Resume(
        id=uuid4(),
        candidate_name="John Doe",
        summary="Experienced Data Engineer skilled in "
        "Python, SQL, and Cloud Solutions.",
        skills="Python, SQL, ETL, AWS",
        location="San Francisco, CA",
        phone="+1 123-456-7890",
        email="john.doe@example.com",
        linkedin="https://linkedin.com/in/johndoe",
    )

    assert resume.candidate_name == "John Doe"
    assert resume.summary.startswith("Experienced Data Engineer")
    assert "Python" in resume.skills
    assert resume.version == 1  # Default version
    assert resume.parent_id is None  # Default parent_id
    assert len(resume.experiences) == 0  # No experiences by default


def test_resume_add_experience():
    """Test adding experiences to a resume."""
    resume = Resume(
        id=uuid4(),
        candidate_name="John Doe",
        summary="Experienced Data Engineer skilled in "
        "Python, SQL, and Cloud Solutions.",
        skills="Python, SQL, ETL, AWS",
    )

    experience = Experience(
        id=uuid4(),
        employer="ExampleCorp",
        position="Data Engineer",
        description=["Built ETL pipelines", "Led migrations"],
        start_date=date(2021, 5, 1),
    )

    resume.experiences.append(experience)

    assert len(resume.experiences) == 1
    assert resume.experiences[0].employer == "ExampleCorp"
