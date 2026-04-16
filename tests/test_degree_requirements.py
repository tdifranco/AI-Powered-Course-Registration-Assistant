from src.data_loader import load_courses, load_degree_requirements, load_students
from src.degree_requirements import calculate_graduation_progress



def test_computer_science_progress_reports_major_and_blocks():
    courses_df = load_courses()
    requirements = load_degree_requirements()
    students = load_students()

    student = next(s for s in students if s["major"] == "Computer Science")
    progress = calculate_graduation_progress(student, courses_df, requirements)

    assert progress["major"] == "Computer Science"
    assert progress["completed_credits"] > 0
    assert len(progress["blocks"]) >= 5



def test_business_admin_progress_uses_120_credit_target():
    courses_df = load_courses()
    requirements = load_degree_requirements()
    students = load_students()

    student = next(s for s in students if s["major"] == "Business Administration")
    progress = calculate_graduation_progress(student, courses_df, requirements)

    assert progress["credits_remaining"] == 120 - progress["completed_credits"]
