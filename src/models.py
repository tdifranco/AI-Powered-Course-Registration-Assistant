from dataclasses import dataclass, field
from typing import List


@dataclass
class StudentProfile:
    name: str
    major: str
    completed_courses: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    target_credits: int = 15


@dataclass
class RecommendationResult:
    course_code: str
    course_name: str
    score: int
    reasons: List[str] = field(default_factory=list)
