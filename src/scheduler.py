from __future__ import annotations

import pandas as pd

from src.degree_requirements import get_major_required_courses, normalize_course_code
from src.prereqs import check_prereqs



def build_schedule(courses_df: pd.DataFrame, student: dict, requirements: dict | None = None, max_credits: int = 15) -> pd.DataFrame:
    completed = {normalize_course_code(c) for c in student.get("completed_courses", [])}
    interests = {i.strip().lower() for i in student.get("interests", [])}
    major_required_courses = get_major_required_courses(student.get("major", ""), requirements or {})

    eligible_rows = []
    for _, course in courses_df.iterrows():
        course_code = normalize_course_code(course["course_code"])
        if course_code in completed:
            continue

        credits = int(course.get("credits", 0) or 0)
        if credits <= 0:
            continue

        prereq = check_prereqs(completed, str(course.get("prerequisites", "")))
        if not prereq["eligible"]:
            continue

        reasons = []
        priority = 0
        if course_code in major_required_courses:
            priority += 5
            reasons.append("major requirement")
        if str(course.get("category", "")).strip().lower() in interests:
            priority += 3
            reasons.append("interest match")

        difficulty = int(course.get("difficulty", 2))
        priority -= difficulty
        reasons.append(f"difficulty {difficulty}")

        eligible_rows.append(
            {
                **course.to_dict(),
                "priority": priority,
                "priority_reason": ", ".join(reasons),
            }
        )

    if not eligible_rows:
        return pd.DataFrame(columns=courses_df.columns)

    eligible_df = pd.DataFrame(eligible_rows).sort_values(
        by=["priority", "difficulty", "course_code"],
        ascending=[False, True, True],
    )

    selected = []
    total_credits = 0
    heavy_count = 0

    for _, course in eligible_df.iterrows():
        credits = int(course.get("credits", 3))
        difficulty = int(course.get("difficulty", 2))

        if total_credits + credits > max_credits:
            continue
        if difficulty >= 4 and heavy_count >= 2:
            continue

        selected.append(course.to_dict())
        total_credits += credits
        if difficulty >= 4:
            heavy_count += 1

    return pd.DataFrame(selected)
