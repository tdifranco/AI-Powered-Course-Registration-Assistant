from __future__ import annotations

import re
from typing import Iterable

import pandas as pd


COURSE_CODE_PATTERN = re.compile(r"^([A-Z]+)\s*([0-9]+)")


def normalize_course_code(course_code: str) -> str:
    return str(course_code).strip().upper().replace(" ", "")


def list_available_majors(requirements: dict) -> list[str]:
    return sorted(requirements.get("majors", {}).keys())


def get_major_definition(major: str, requirements: dict) -> dict | None:
    return requirements.get("majors", {}).get(major)


def parse_course_prefix_and_level(course_code: str) -> tuple[str, int | None]:
    normalized = normalize_course_code(course_code)
    match = COURSE_CODE_PATTERN.match(normalized)
    if not match:
        return normalized, None
    prefix, level = match.groups()
    return prefix, int(level)


def course_matches_filters(course_code: str, prefixes: Iterable[str], min_level: int | None = None) -> bool:
    prefix, level = parse_course_prefix_and_level(course_code)
    valid_prefixes = {p.strip().upper() for p in prefixes}
    if prefix not in valid_prefixes:
        return False
    if min_level is not None and level is not None and level < min_level:
        return False
    return True


def completed_courses_lookup(student: dict) -> set[str]:
    return {normalize_course_code(code) for code in student.get("completed_courses", [])}


def _block_result(name: str, complete: bool, progress_text: str, matched_courses: list[str], missing_items: list[str]) -> dict:
    return {
        "name": name,
        "complete": complete,
        "progress_text": progress_text,
        "matched_courses": matched_courses,
        "missing_items": missing_items,
    }


def evaluate_block(block: dict, student: dict, courses_df: pd.DataFrame) -> dict:
    completed = completed_courses_lookup(student)
    block_type = block["type"]
    name = block["name"]

    if block_type == "exact_courses":
        required = [normalize_course_code(code) for code in block.get("courses", [])]
        matched = [code for code in required if code in completed]
        missing = [code for code in required if code not in completed]
        return _block_result(name, not missing, f"{len(matched)}/{len(required)} courses", matched, missing)

    if block_type == "select_n_courses":
        options = [normalize_course_code(code) for code in block.get("options", [])]
        min_count = int(block.get("min_count", 1))
        matched = [code for code in options if code in completed]
        missing_needed = max(0, min_count - len(matched))
        missing = [f"Select {missing_needed} more from: {', '.join(options)}"] if missing_needed else []
        return _block_result(name, len(matched) >= min_count, f"{len(matched)}/{min_count} courses", matched, missing)

    if block_type == "flag_count":
        flag_column = block["flag_column"]
        min_count = int(block["min_count"])
        if flag_column not in courses_df.columns:
            return _block_result(name, False, f"0/{min_count}", [], [f"Missing course metadata column: {flag_column}"])
        flagged = courses_df[courses_df[flag_column].astype(str).str.lower() == "true"]
        matched = [normalize_course_code(code) for code in flagged["course_code"].tolist() if normalize_course_code(code) in completed]
        return _block_result(name, len(matched) >= min_count, f"{len(matched)}/{min_count} courses", matched, [] if len(matched) >= min_count else [f"Complete {min_count - len(matched)} more flagged courses"])

    if block_type in {"course_count_from_prefixes", "credit_count_from_prefixes"}:
        prefixes = block.get("prefixes", [])
        min_level = block.get("min_level")
        exclude_courses = {normalize_course_code(code) for code in block.get("exclude_courses", [])}
        matched_df = []
        for _, course in courses_df.iterrows():
            course_code = normalize_course_code(course["course_code"])
            if course_code not in completed or course_code in exclude_courses:
                continue
            if course_matches_filters(course_code, prefixes, min_level=min_level):
                matched_df.append(course)
        matched_df = pd.DataFrame(matched_df)
        matched_codes = [] if matched_df.empty else [normalize_course_code(code) for code in matched_df["course_code"].tolist()]

        if block_type == "course_count_from_prefixes":
            min_count = int(block["min_count"])
            return _block_result(name, len(matched_codes) >= min_count, f"{len(matched_codes)}/{min_count} courses", matched_codes, [] if len(matched_codes) >= min_count else [f"Complete {min_count - len(matched_codes)} more course(s) in this group"])

        min_credits = int(block["min_credits"])
        credits = 0 if matched_df.empty else int(matched_df["credits"].fillna(0).astype(int).sum())
        return _block_result(name, credits >= min_credits, f"{credits}/{min_credits} credits", matched_codes, [] if credits >= min_credits else [f"Earn {min_credits - credits} more credit(s) in this group"])

    return _block_result(name, False, "Unsupported block type", [], [block_type])


def calculate_completed_credits(student: dict, courses_df: pd.DataFrame) -> int:
    completed = completed_courses_lookup(student)
    if not completed:
        return 0
    matched = courses_df[courses_df["course_code"].astype(str).map(normalize_course_code).isin(completed)].copy()
    if matched.empty:
        return 0
    return int(matched["credits"].fillna(0).astype(int).sum())


def calculate_graduation_progress(student: dict, courses_df: pd.DataFrame, requirements: dict) -> dict:
    major = student.get("major", "")
    major_definition = get_major_definition(major, requirements)
    if not major_definition:
        return {
            "major": major,
            "catalog_source": "No matching degree requirements loaded",
            "completed_credits": calculate_completed_credits(student, courses_df),
            "credits_remaining": None,
            "credit_progress_percent": 0,
            "blocks": [],
            "notes": ["Add this major to data/degree_requirements.json to enable graduation tracking."],
        }

    total_required = int(major_definition.get("total_credits_required", 120))
    completed_credits = calculate_completed_credits(student, courses_df)
    credits_remaining = max(0, total_required - completed_credits)
    percent = round((completed_credits / total_required) * 100) if total_required else 0

    blocks = [evaluate_block(block, student, courses_df) for block in major_definition.get("blocks", [])]

    return {
        "major": major,
        "catalog_source": major_definition.get("catalog_source", "Degree requirements file"),
        "completed_credits": completed_credits,
        "credits_remaining": credits_remaining,
        "credit_progress_percent": percent,
        "blocks": blocks,
        "notes": major_definition.get("notes", []),
    }


def get_major_required_courses(major: str, requirements: dict) -> set[str]:
    major_definition = get_major_definition(major, requirements)
    if not major_definition:
        return set()
    required_courses: set[str] = set()
    for block in major_definition.get("blocks", []):
        if block.get("type") == "exact_courses":
            required_courses.update({normalize_course_code(code) for code in block.get("courses", [])})
        elif block.get("type") == "select_n_courses":
            required_courses.update({normalize_course_code(code) for code in block.get("options", [])})
    return required_courses
