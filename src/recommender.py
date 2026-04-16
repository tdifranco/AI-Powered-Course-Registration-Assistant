from __future__ import annotations

from typing import Iterable

import pandas as pd

from src.degree_requirements import get_major_required_courses, normalize_course_code
from src.prereqs import check_prereqs



def _normalize_list(values: Iterable[str]) -> set[str]:
    return {str(v).strip().lower() for v in values if str(v).strip()}


def score_course(course: pd.Series, student: dict, requirements: dict | None = None) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    completed = {normalize_course_code(c) for c in student.get("completed_courses", [])}
    interests = _normalize_list(student.get("interests", []))
    major = str(student.get("major", "")).strip().lower()
    major_required_courses = get_major_required_courses(student.get("major", ""), requirements or {})

    course_code = normalize_course_code(course["course_code"])
    category = str(course.get("category", "")).strip().lower()
    department = str(course.get("department", "")).strip().lower()
    credits = int(course.get("credits", 0) or 0)

    if credits <= 0:
        score -= 100
        reasons.append("non-credit milestone")
        return score, reasons

    if course_code in completed:
        score -= 100
        reasons.append("already completed")
        return score, reasons

    prereq_result = check_prereqs(completed, str(course.get("prerequisites", "")))
    if prereq_result["eligible"]:
        score += 4
        reasons.append("eligible now")
    else:
        score -= 12
        reasons.append(f"missing prerequisites: {', '.join(prereq_result['missing'])}")

    if course_code in major_required_courses:
        score += 5
        reasons.append("counts toward current major")

    if category in interests:
        score += 4
        reasons.append("matches stated interests")

    if department and major and department in major:
        score += 3
        reasons.append("aligned with major department")

    difficulty = int(course.get("difficulty", 2))
    if difficulty <= 2:
        score += 1
        reasons.append("lighter workload option")
    elif difficulty >= 4:
        score -= 1
        reasons.append("heavier workload")

    return score, reasons


def recommend_courses(courses_df: pd.DataFrame, student: dict, requirements: dict | None = None, top_n: int = 5) -> pd.DataFrame:
    rows = []
    for _, course in courses_df.iterrows():
        score, reasons = score_course(course, student, requirements=requirements)
        rows.append(
            {
                "course_code": course["course_code"],
                "course_name": course["course_name"],
                "category": course.get("category", ""),
                "credits": course.get("credits", 0),
                "score": score,
                "reasons": "; ".join(reasons),
            }
        )

    result = pd.DataFrame(rows)
    result = result[result["score"] > -100].sort_values(by=["score", "course_code"], ascending=[False, True])
    return result.head(top_n).reset_index(drop=True)
