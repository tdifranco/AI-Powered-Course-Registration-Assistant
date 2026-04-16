# AI-Powered Course Registration Assistant

A Streamlit prototype for course exploration, prerequisite checking, recommendations, semester planning, and graduation progress tracking.

## Features

- top navigation instead of default sidebar page links
- editable student profiles with major, completed courses, interests, and target credits
- course search and course details
- prerequisite checking
- course recommendations that prioritize major requirements and interests
- semester schedule builder
- graduation progress tracker driven by a JSON degree-requirements file

## Project structure

```text
course-registration-assistant/
├── app.py
├── data/
│   ├── courses.csv
│   ├── degree_requirements.json
│   └── sample_students.json
├── src/
│   ├── ai_helper.py
│   ├── data_loader.py
│   ├── degree_requirements.py
│   ├── prereqs.py
│   ├── qa.py
│   ├── recommender.py
│   └── scheduler.py
└── tests/
```

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

## Graduation progress design

The graduation checker reads `data/degree_requirements.json`.

Each major definition can include blocks such as:

- exact required courses
- choose-one requirements
- minimum course counts by prefix and level
- minimum credit counts by prefix
- flagged knowledge-area counts

This keeps the logic easy to extend when you add more Clarkson majors from the undergraduate catalog.

## Next steps

- expand `courses.csv` with more real Clarkson courses
- add more majors to `degree_requirements.json`
- parse catalog data into structured JSON instead of entering it manually
- add export to PDF or advising summary
