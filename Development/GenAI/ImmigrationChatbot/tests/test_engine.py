import pytest

from immigration_chatbot.engine import (
    draft_message,
    synthesize_conflicting_info,
    timeline_guidance,
)


@pytest.fixture(autouse=True)
def disable_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_ENABLED", "false")


def test_timeline_guidance_status_bands_for_visa_filing() -> None:
    assert timeline_guidance("visa_filing", 10)["status"] == "early"
    assert timeline_guidance("visa_filing", 45)["status"] == "normal"
    assert timeline_guidance("visa_filing", 120)["status"] == "delayed"


def test_timeline_guidance_marks_rule_based_source_when_ollama_disabled() -> None:
    result = timeline_guidance("visa_filing", 45)
    assert result["response_source"] == "rule_based"


def test_timeline_guidance_uses_default_threshold_for_unknown_process() -> None:
    assert timeline_guidance("unknown", 20)["status"] == "early"


def test_confidence_high_with_clear_majority() -> None:
    result = synthesize_conflicting_info(
        "h1b transfer",
        ["Likely 4-8 weeks", "Likely 4-8 weeks", "Likely 4-8 weeks", "Can exceed 12 weeks"],
    )
    assert result["confidence"] == "high"


def test_confidence_low_for_empty_claims() -> None:
    result = synthesize_conflicting_info("salary benchmark", [])
    assert result["confidence"] == "low"


def test_employer_message_contains_role_and_visa() -> None:
    message = draft_message("employer", "Software Engineer", "H-1B sponsorship")
    assert "Software Engineer" in message
    assert "H-1B sponsorship" in message


def test_fallback_template_for_unknown_audience() -> None:
    message = draft_message("partner", "Data Analyst", "OPT extension")
    assert "Data Analyst" in message
    assert "OPT extension" in message
