"""Core business logic mapped from requirements and acceptance criteria."""

from collections import Counter
import os
from typing import Dict, List

from .llm import try_llm_prompt

PROCESS_THRESHOLDS: Dict[str, tuple[int, int]] = {
    "visa_filing": (30, 90),
    "job_offer": (14, 45),
    "approval": (21, 60),
}


def timeline_guidance(process_type: str, days_waited: int) -> Dict[str, str]:
    """Return uncertainty-aware status and next actions.

    Status bands:
    - early: days_waited < lower threshold
    - normal: lower <= days_waited <= upper
    - delayed: days_waited > upper threshold
    """
    if days_waited < 0:
        raise ValueError("days_waited must be >= 0")

    low, high = PROCESS_THRESHOLDS.get(process_type, (30, 90))

    if days_waited < low:
        status = "early"
        action = "Continue monitoring weekly and keep documents ready."
    elif days_waited <= high:
        status = "normal"
        action = "Track updates and prepare follow-up questions in advance."
    else:
        status = "delayed"
        action = "Send a formal follow-up and gather escalation options."

    result = {
        "process_type": process_type,
        "days_waited": str(days_waited),
        "status": status,
        "next_action": action,
        "disclaimer": "This is guidance, not legal advice.",
    }

    llm_prompt = (
        "You are an immigration and career planning assistant. "
        "Given JSON input, write a concise supportive summary in 2-3 sentences. "
        "Do not provide legal advice and do not invent facts.\n\n"
        f"Input: {result}"
    )
    llm_summary = try_llm_prompt(llm_prompt)
    if llm_summary:
        result["llm_summary"] = llm_summary
        result["response_source"] = os.getenv("LLM_PROVIDER", "openai")
    else:
        result["response_source"] = "rule_based"

    return result


def synthesize_conflicting_info(topic: str, claims: List[str]) -> Dict[str, str]:
    """Synthesize conflicting claims into a concise summary with confidence."""
    normalized = [c.strip() for c in claims if c and c.strip()]
    if not normalized:
        result = {
            "topic": topic,
            "summary": "Insufficient evidence. Please add reliable sources.",
            "confidence": "low",
        }
        result["response_source"] = "rule_based"
        return result

    counts = Counter(normalized)
    winner, winner_count = counts.most_common(1)[0]
    ratio = winner_count / len(normalized)

    if ratio >= 0.7:
        confidence = "high"
    elif ratio >= 0.5:
        confidence = "medium"
    else:
        confidence = "low"

    summary = f"Most sources suggest: '{winner}'."
    result = {"topic": topic, "summary": summary, "confidence": confidence}

    llm_prompt = (
        "You are a clarity assistant helping users with conflicting information. "
        "Summarize the likely conclusion in 2 short sentences and mention uncertainty. "
        "Do not provide legal advice.\n\n"
        f"Topic: {topic}\n"
        f"Claims: {normalized}\n"
        f"Winning claim: {winner}\n"
        f"Confidence: {confidence}"
    )
    llm_summary = try_llm_prompt(llm_prompt)
    if llm_summary:
        result["summary"] = llm_summary
        result["response_source"] = os.getenv("LLM_PROVIDER", "openai")
    else:
        result["response_source"] = "rule_based"

    return result


def draft_message(
    audience: str,
    role: str,
    visa_requirement: str,
    work_arrangement: str = "flexible",
) -> str:
    """Draft context-aware communication text for key stakeholder audiences."""
    templates = {
        "recruiter": (
            "Hi, I am interested in the {role} opportunity. "
            "I currently require {visa_requirement}. "
            "I am open to a {work_arrangement} work setup and happy to discuss next steps."
        ),
        "employer": (
            "Hello, thank you for considering me for the {role} role. "
            "I want to proactively share that I require {visa_requirement}. "
            "I can support a {work_arrangement} arrangement and can provide needed documents promptly."
        ),
        "institution": (
            "Dear Team, I am writing regarding my {role} situation. "
            "I currently require {visa_requirement} and request guidance on available options. "
            "My preferred arrangement is {work_arrangement}."
        ),
    }

    template = templates.get(
        audience,
        (
            "Hello, I am reaching out regarding a {role} discussion. "
            "I currently require {visa_requirement} and prefer a {work_arrangement} arrangement."
        ),
    )

    fallback_message = template.format(
        role=role,
        visa_requirement=visa_requirement,
        work_arrangement=work_arrangement,
    )

    llm_prompt = (
        "You draft concise professional messages for immigration and work arrangement communication. "
        "Keep it polite, clear, and practical in 4-6 sentences. "
        "Do not provide legal claims.\n\n"
        f"Audience: {audience}\n"
        f"Role: {role}\n"
        f"Visa Requirement: {visa_requirement}\n"
        f"Work Arrangement: {work_arrangement}\n"
    )
    llm_message = try_llm_prompt(llm_prompt)
    return llm_message or fallback_message


def fallback_chat_response(message: str) -> str:
    """Rule-based fallback for free-form chat conversations."""
    text = message.strip().lower()
    if any(word in text for word in ["wait", "timeline", "delay", "processing"]):
        return (
            "I hear the uncertainty is stressful. Share your process type and days waited, "
            "and I can suggest whether it looks early, normal, or delayed with practical next steps."
        )
    if any(word in text for word in ["conflict", "different", "source", "unclear", "confused"]):
        return (
            "Let's reduce the noise. Paste 2-5 claims or sources, and I will synthesize them "
            "with a confidence level and highlight what to verify next."
        )
    if any(word in text for word in ["email", "recruiter", "employer", "message", "communicate"]):
        return (
            "I can draft a clear message for recruiter, employer, or institution. "
            "Tell me audience, role, visa requirement, and preferred work arrangement."
        )
    return (
        "I can help with three things: timeline uncertainty, conflicting information, "
        "and communication drafts. Tell me which one you want to tackle first."
    )
