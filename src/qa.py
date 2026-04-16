from __future__ import annotations

import pandas as pd


def search_courses(courses_df: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query.strip():
        return courses_df.copy()

    q = query.strip().lower()
    mask = (
        courses_df["course_code"].astype(str).str.lower().str.contains(q)
        | courses_df["course_name"].astype(str).str.lower().str.contains(q)
        | courses_df["description"].astype(str).str.lower().str.contains(q)
        | courses_df["category"].astype(str).str.lower().str.contains(q)
        | courses_df["department"].astype(str).str.lower().str.contains(q)
    )
    return courses_df[mask].copy()


def answer_course_question(courses_df: pd.DataFrame, course_code: str) -> str:
    match = courses_df[
        courses_df["course_code"].astype(str).str.upper() == course_code.strip().upper()
    ]
    if match.empty:
        return f"I could not find {course_code} in the current catalog."

    row = match.iloc[0]
    prereqs = row.get("prerequisites", "None") or "None"

    return (
        f"{row['course_code']}: {row['course_name']}\n"
        f"Description: {row['description']}\n"
        f"Credits: {row['credits']}\n"
        f"Category: {row['category']}\n"
        f"Department: {row['department']}\n"
        f"Semester: {row['semester']}\n"
        f"Prerequisites: {prereqs}"
    )