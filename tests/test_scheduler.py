from src.data_loader import load_courses, load_degree_requirements
from src.scheduler import build_schedule



def test_build_schedule_respects_max_credits():
    courses_df = load_courses()
    requirements = load_degree_requirements()
    student = {
        "name": "Test Student",
        "major": "Computer Science",
        "completed_courses": ["FY100", "UNIV190", "MA131", "MA132", "MA211", "CS141", "CS142", "CS242"],
        "interests": ["AI", "Systems"],
        "target_credits": 12,
    }

    schedule = build_schedule(courses_df, student, requirements, max_credits=12)
    assert int(schedule["credits"].sum()) <= 12
