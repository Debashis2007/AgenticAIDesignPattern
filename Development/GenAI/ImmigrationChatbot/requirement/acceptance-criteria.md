# Acceptance Criteria (Generated from prompts)

### REQ-002 - Uncertainty-aware status bands
- AC1: Given process type `visa_filing` and waited days less than 30, when guidance is generated, then status is `early`.
- AC2: Given process type `visa_filing` and waited days between 30 and 90, when guidance is generated, then status is `normal`.
- AC3: Given process type `visa_filing` and waited days greater than 90, when guidance is generated, then status is `delayed`.
- AC4: Given unknown process type, when guidance is generated, then default thresholds are used.

### REQ-005 - Compute confidence from agreement
- AC1: Given claims with same recommendation majority, when synthesis is generated, then confidence is `high`.
- AC2: Given claims with split recommendations, when synthesis is generated, then confidence is `medium`.
- AC3: Given empty claims list, when synthesis is generated, then confidence is `low` and summary asks for more evidence.

### REQ-008 - Draft employer message
- AC1: Given audience `employer`, role, and visa need, when draft is generated, then output includes role and visa note.
- AC2: Given missing optional context, when draft is generated, then message remains polite and complete.
- AC3: Given unsupported audience value, when draft is generated, then fallback generic template is used.

### REQ-011 - CLI interaction flow
- AC1: Given command `timeline`, when user provides required args, then CLI prints structured timeline guidance.
- AC2: Given command `clarify`, when user provides claims, then CLI prints summary and confidence.
- AC3: Given command `draft`, when user provides audience and context, then CLI prints drafted message.

### REQ-012 - Smoke/unit tests
- AC1: Given test suite execution, when run locally, then all behavior tests pass.
- AC2: Given modified thresholds/templates, when tests run, then regression failures surface if behavior changes unexpectedly.
