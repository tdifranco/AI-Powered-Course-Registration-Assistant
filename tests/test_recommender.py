from src.data_loader import load_courses, load_degree_requirements
from src.recommender import recommend_courses



def test_recommend_courses_returns_ranked_results():
    courses_df = load_courses()
    requirements = load_degree_requirements()
    student = {
        "name": "Test Student",
        "major": "Computer Science",
        "completed_courses": ["FY100", "UNIV190", "MA131", "CS141", "CS142"],
        "interests": ["AI", "Systems"],
        "target_credits": 15,
    }

    result = recommend_courses(courses_df, student, requirements, top_n=5)
    assert not result.empty
    assert result.iloc[0]["score"] >= result.iloc[-1]["score"]
