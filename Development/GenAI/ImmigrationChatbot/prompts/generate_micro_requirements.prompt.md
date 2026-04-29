# Prompt: Generate Small Requirements

You are a product analyst. Read `requirement/immigration-chatbot-requirement.md` and break it into very small, implementable requirements.

## Instructions
- Generate 12-20 micro-requirements.
- Each requirement must be small enough to implement in 0.5 to 1 day.
- Group by feature area: `timeline-support`, `clarity-engine`, `communication-assist`, `safety`, `platform`.
- Use IDs in format `REQ-001`, `REQ-002`, ...
- Each requirement must include:
  - `id`
  - `title`
  - `user_story` (As a ..., I want ..., so that ...)
  - `business_value` (1 sentence)
  - `dependencies` (list of REQ IDs or `none`)

## Output Format (Markdown table)
| id | feature_area | title | user_story | business_value | dependencies |
