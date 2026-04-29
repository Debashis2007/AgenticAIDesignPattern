"""Simple CLI to exercise chatbot MVP behaviors."""

import argparse
import json

from .engine import draft_message, synthesize_conflicting_info, timeline_guidance


def main() -> None:
    parser = argparse.ArgumentParser(description="Immigration chatbot MVP CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    timeline = sub.add_parser("timeline", help="Get timeline guidance")
    timeline.add_argument("--process", required=True, help="visa_filing|job_offer|approval")
    timeline.add_argument("--days", required=True, type=int, help="Days waited")

    clarify = sub.add_parser("clarify", help="Synthesize conflicting claims")
    clarify.add_argument("--topic", required=True)
    clarify.add_argument("--claim", action="append", default=[], help="Repeat for multiple claims")

    draft = sub.add_parser("draft", help="Draft stakeholder message")
    draft.add_argument("--audience", required=True, help="recruiter|employer|institution")
    draft.add_argument("--role", required=True)
    draft.add_argument("--visa", required=True)
    draft.add_argument("--work", default="flexible")

    args = parser.parse_args()

    if args.command == "timeline":
        result = timeline_guidance(args.process, args.days)
    elif args.command == "clarify":
        result = synthesize_conflicting_info(args.topic, args.claim)
    else:
        result = {
            "audience": args.audience,
            "message": draft_message(args.audience, args.role, args.visa, args.work),
        }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
