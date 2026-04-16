from __future__ import annotations

from typing import Iterable


EMPTY_VALUES = {"", "none", "n/a", "na"}


def parse_prereqs(prereq_text: str) -> list[str]:
    """
    Parses a simple semicolon-separated prerequisite field.

    Example:
    "CS141;MATH131" -> ["CS141", "MATH131"]

    This starter version assumes all listed prerequisites are required.
    """
    text = (prereq_text or "").strip()
    if text.lower() in EMPTY_VALUES:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def check_prereqs(completed_courses: Iterable[str], prereq_text: str) -> dict:
    completed = {c.strip().upper() for c in completed_courses}
    needed = parse_prereqs(prereq_text)
    missing = [course for course in needed if course.upper() not in completed]
    return {
        "eligible": len(missing) == 0,
        "needed": needed,
        "missing": missing,
    }


def explain_prereqs(course_code: str, prereq_text: str, completed_courses: Iterable[str]) -> str:
    result = check_prereqs(completed_courses, prereq_text)
    if not result["needed"]:
        return f"{course_code} has no prerequisites."
    if result["eligible"]:
        return f"You are eligible for {course_code}. You completed: {', '.join(result['needed'])}."
    return (
        f"You are not yet eligible for {course_code}. Missing prerequisites: "
        f"{', '.join(result['missing'])}."
    )
