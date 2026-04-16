from __future__ import annotations

import pandas as pd
import streamlit as st

from src.ai_helper import generate_ai_summary
from src.data_loader import load_courses, load_degree_requirements, load_students
from src.degree_requirements import calculate_graduation_progress, list_available_majors
from src.prereqs import explain_prereqs
from src.qa import answer_course_question, search_courses
from src.recommender import recommend_courses
from src.scheduler import build_schedule

st.set_page_config(
    page_title="Course Registration Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.set_option("client.showSidebarNavigation", False)

COURSES_DF = load_courses()
STUDENTS = load_students()
DEGREE_REQUIREMENTS = load_degree_requirements()

NAV_ITEMS = [
    "Home",
    "Course Search",
    "Recommendations",
    "Prerequisites",
    "Schedule",
    "Graduation Progress",
]


def inject_clarkson_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --clarkson-green: #146959;
            --clarkson-green-dark: #0F5A4D;
            --page-bg: #F7F9FC;
            --card-bg: #FFFFFF;
            --border: #D7DEE7;
            --text: #1F2937;
            --muted: #5F6B7A;
        }

        .stApp {
            background-color: var(--page-bg);
            color: var(--text);
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }

        h1, h2, h3, h4, h5, h6,
        p, span, label {
            color: var(--text) !important;
        }

        small {
            color: var(--muted) !important;
        }

        /* Metrics */
        div[data-testid="stMetric"] {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1rem;
        }

        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] p,
        div[data-testid="stMetric"] div {
            color: var(--text) !important;
        }

        /* Expanders */
        div[data-testid="stExpander"] {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
        }

        /* Inputs and selects */
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        textarea {
            background: #FFFFFF !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
        }

        input, textarea {
            color: var(--text) !important;
            -webkit-text-fill-color: var(--text) !important;
        }

        /* Multiselect pills */
        span[data-baseweb="tag"] {
            background: #E7F3F0 !important;
            color: var(--clarkson-green-dark) !important;
            border: 1px solid #BFD8D1 !important;
            border-radius: 999px !important;
        }

        /* Buttons */
        .stButton > button {
            min-height: 44px;
            border-radius: 10px;
            font-weight: 600;
            border: 1px solid var(--border);
        }

        .stButton > button[kind="primary"] {
            background-color: var(--clarkson-green) !important;
            border-color: var(--clarkson-green) !important;
            color: white !important;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: var(--clarkson-green-dark) !important;
            border-color: var(--clarkson-green-dark) !important;
            color: white !important;
        }

        .stButton > button[kind="secondary"] {
            background-color: #FFFFFF !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
        }

        .stButton > button[kind="secondary"]:hover {
            border-color: var(--clarkson-green) !important;
            color: var(--clarkson-green) !important;
            background-color: #F9FCFB !important;
        }

        /* Tables / dataframe */
        div[data-testid="stDataFrame"] {
            background: #FFFFFF;
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }

        /* Info/warning/success boxes */
        div[data-testid="stAlert"] {
            border-radius: 12px;
        }

        hr {
            border: none;
            height: 1px;
            background: var(--border);
            margin: 1rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_clarkson_theme()


def get_student_from_state() -> dict:
    if "selected_student_name" not in st.session_state:
        st.session_state.selected_student_name = STUDENTS[0]["name"]

    if "student_profile_source" not in st.session_state:
        st.session_state.student_profile_source = st.session_state.selected_student_name

    if (
        "student_profile" not in st.session_state
        or st.session_state.student_profile_source != st.session_state.selected_student_name
    ):
        default_student = next(
            student
            for student in STUDENTS
            if student["name"] == st.session_state.selected_student_name
        )
        st.session_state.student_profile = default_student.copy()
        st.session_state.student_profile_source = st.session_state.selected_student_name

    return st.session_state.student_profile


def render_header() -> tuple[dict, str]:
    st.title("Course Registration Dashboard")
    st.caption(
        "Clarkson-style planning tool for course exploration, prerequisite checks, "
        "semester planning, and graduation progress."
    )

    left, right = st.columns([2, 3])

    with left:
        st.selectbox(
            "Student profile",
            options=[student["name"] for student in STUDENTS],
            key="selected_student_name",
        )

    with right:
        st.info(
            "Choose a student profile, then edit the details below to simulate completed "
            "courses, interests, and major changes."
        )

    student = get_student_from_state()
    available_majors = list_available_majors(DEGREE_REQUIREMENTS)

    default_major = student.get("major", "")
    if available_majors:
        if default_major not in available_majors:
            default_major = available_majors[0]
        default_major_index = available_majors.index(default_major)
    else:
        default_major_index = 0

    with st.expander("Edit selected student profile", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            student["name"] = st.text_input("Name", value=student.get("name", ""))
            if available_majors:
                student["major"] = st.selectbox(
                    "Major",
                    options=available_majors,
                    index=default_major_index,
                )
            student["target_credits"] = st.slider(
                "Target semester credits",
                min_value=6,
                max_value=18,
                value=int(student.get("target_credits", 15)),
            )

        with col2:
            all_codes = COURSES_DF["course_code"].astype(str).tolist()
            categories = sorted(
                 {
                     str(category).strip()
                     for category in COURSES_DF["category"].dropna().tolist()
                     if str(category).strip()
                 }
)

            valid_completed = [
    course for course in student.get("completed_courses", [])
    if course in all_codes
]

            valid_interests = [
    interest for interest in student.get("interests", [])
    if interest in categories
]

            student["completed_courses"] = st.multiselect(
    "Completed courses",
    options=all_codes,
    default=valid_completed,
)

            student["interests"] = st.multiselect(
    "Interests",
    options=categories,
    default=valid_interests,
)

    if "current_view" not in st.session_state:
        st.session_state.current_view = "Home"

    st.markdown("### Navigate")
    nav_cols = st.columns(len(NAV_ITEMS))

    for i, item in enumerate(NAV_ITEMS):
        with nav_cols[i]:
            button_type = (
                "primary" if st.session_state.current_view == item else "secondary"
            )
            if st.button(
                item,
                key=f"nav_{item}",
                type=button_type,
                width="stretch",
            ):
                st.session_state.current_view = item
                st.rerun()

    st.divider()
    return student, st.session_state.current_view


def render_home(student: dict) -> None:
    progress = calculate_graduation_progress(student, COURSES_DF, DEGREE_REQUIREMENTS)
    recommended = recommend_courses(
        COURSES_DF,
        student,
        DEGREE_REQUIREMENTS,
        top_n=5,
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Major", student.get("major", "Not set"))
    m2.metric("Completed credits", progress["completed_credits"])
    m3.metric("Credits remaining", progress["credits_remaining"])

    left, right = st.columns([3, 2])

    with left:
        st.subheader("Student Profile")
        st.write(f"**Name:** {student.get('name', '—')}")
        st.write(f"**Major:** {student.get('major', '—')}")
        st.write(f"**Target credits:** {student.get('target_credits', '—')}")
        st.write(
            f"**Completed courses:** {', '.join(student.get('completed_courses', [])) or 'None yet'}"
        )
        st.write(
            f"**Interests:** {', '.join(student.get('interests', [])) or 'None selected'}"
        )

    with right:
        st.subheader("Next Good Options")
        if recommended.empty:
            st.warning("No recommendations available from the current profile.")
        else:
            preview = recommended[["course_code", "course_name", "score"]].copy()
            st.dataframe(preview, use_container_width=True, hide_index=True)

    st.subheader("Overview")
    st.write(
        "This prototype combines course search, prerequisite logic, recommendations, "
        "schedule building, and major-specific graduation tracking in one advising workflow."
    )


def render_course_search() -> None:
    st.subheader("Course Search")

    query = st.text_input("Search by course code, title, category, department, or keyword")
    results = search_courses(COURSES_DF, query)

    st.write(f"Found **{len(results)}** course(s).")

    display_columns = [
        "course_code",
        "course_name",
        "category",
        "credits",
        "semester",
        "department",
    ]

    if results.empty:
        st.info("No courses matched the current search.")
        return

    st.dataframe(
        results[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Course Details")
    selected_course = st.selectbox(
        "Choose a course",
        results["course_code"].tolist(),
    )

    if selected_course:
        st.text(answer_course_question(COURSES_DF, selected_course))


def render_recommendations(student: dict) -> None:
    st.subheader("Recommendations")

    recommendations = recommend_courses(
        COURSES_DF,
        student,
        DEGREE_REQUIREMENTS,
        top_n=8,
    )

    if recommendations.empty:
        st.warning("No recommendations could be generated from the current profile.")
        return

    st.dataframe(
        recommendations,
        use_container_width=True,
        hide_index=True,
    )

    if st.button("Generate explanation", type="primary"):
        prompt = (
        f"Student profile: {student}\n\n"
        f"Recommendations:\n{recommendations.to_string(index=False)}\n\n"
        "Explain why these are good next courses. Mention prerequisite readiness, "
        "interest match, and major relevance."
    )
        summary = generate_ai_summary(prompt)
        st.write(summary)


def render_prerequisites(student: dict) -> None:
    st.subheader("Prerequisite Checker")

    course_code = st.selectbox(
        "Choose a course",
        COURSES_DF["course_code"].tolist(),
    )

    course_row = COURSES_DF[COURSES_DF["course_code"] == course_code].iloc[0]
    result = explain_prereqs(
        course_code,
        str(course_row.get("prerequisites", "")),
        student.get("completed_courses", []),
    )
    st.write(result)


def render_schedule(student: dict) -> None:
    st.subheader("Schedule Builder")

    max_credits = st.slider(
        "Maximum credits for this semester",
        min_value=6,
        max_value=18,
        value=int(student.get("target_credits", 15)),
    )

    schedule_df = build_schedule(
        COURSES_DF,
        student,
        DEGREE_REQUIREMENTS,
        max_credits=max_credits,
    )

    if schedule_df.empty:
        st.warning(
            "No eligible schedule could be built from the current profile and sample data."
        )
        return

    display_cols = [
        "course_code",
        "course_name",
        "credits",
        "category",
        "difficulty",
        "semester",
        "priority_reason",
    ]

    st.dataframe(
        schedule_df[display_cols],
        use_container_width=True,
        hide_index=True,
    )

    st.success(f"Total credits: {int(schedule_df['credits'].sum())}")


def render_graduation_progress(student: dict) -> None:
    st.subheader("Graduation Progress")

    progress = calculate_graduation_progress(student, COURSES_DF, DEGREE_REQUIREMENTS)

    m1, m2, m3 = st.columns(3)
    m1.metric("Completed credits", progress["completed_credits"])
    m2.metric("Credits remaining", progress["credits_remaining"])
    m3.metric("Credit progress", f"{progress['credit_progress_percent']}%")

    st.write(f"**Major:** {progress['major']}")
    st.write(f"**Catalog source:** {progress['catalog_source']}")

    status_rows = []
    for block in progress["blocks"]:
        status_rows.append(
            {
                "Requirement": block["name"],
                "Status": "Complete" if block["complete"] else "In progress",
                "Progress": block["progress_text"],
                "Matched courses": ", ".join(block["matched_courses"])
                if block["matched_courses"]
                else "—",
                "Missing": ", ".join(block["missing_items"])
                if block["missing_items"]
                else "—",
            }
        )

    status_df = pd.DataFrame(status_rows)

    if status_df.empty:
        st.info("No detailed requirement blocks are loaded for this major yet.")
    else:
        st.dataframe(status_df, use_container_width=True, hide_index=True)

    if progress["notes"]:
        with st.expander("Catalog notes and prototype limitations"):
            for note in progress["notes"]:
                st.write(f"- {note}")


student_profile, selected_view = render_header()

if selected_view == "Home":
    render_home(student_profile)
elif selected_view == "Course Search":
    render_course_search()
elif selected_view == "Recommendations":
    render_recommendations(student_profile)
elif selected_view == "Prerequisites":
    render_prerequisites(student_profile)
elif selected_view == "Schedule":
    render_schedule(student_profile)
elif selected_view == "Graduation Progress":
    render_graduation_progress(student_profile)