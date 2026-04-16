from src.prereqs import check_prereqs, parse_prereqs



def test_parse_prereqs_empty():
    assert parse_prereqs("") == []
    assert parse_prereqs("None") == []



def test_check_prereqs_missing():
    result = check_prereqs(["CS141"], "CS141;MA131")
    assert result["eligible"] is False
    assert result["missing"] == ["MA131"]
