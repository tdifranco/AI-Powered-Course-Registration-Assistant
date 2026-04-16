# Architecture Notes

## Design choice
The recommendation logic is rule-based so the system remains explainable and predictable.
AI is optional and only used to rewrite structured outputs into more natural explanations.

## Main flow
1. Streamlit collects student inputs.
2. `data_loader.py` loads catalog and student data.
3. `prereqs.py` checks eligibility.
4. `recommender.py` ranks courses.
5. `scheduler.py` builds a semester plan.
6. `ai_helper.py` optionally summarizes results in plain language.
