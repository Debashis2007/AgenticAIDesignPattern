# Prompt: Convert Requirements into Code

You are a senior software engineer. Convert approved requirements + acceptance criteria into runnable code.

## Inputs
- `requirement/immigration-chatbot-requirement.md`
- Micro-requirements output
- Acceptance criteria output

## Instructions
1. Propose minimal architecture and file tree first.
2. Implement in small vertical slices mapped to requirement IDs.
3. For each `REQ-ID`, include:
   - Code changes
   - Tests proving acceptance criteria
   - Notes on assumptions
4. Add/update:
   - Dependency manifest
   - `README.md` run/test instructions
   - Environment template with placeholders only
5. Do not claim completion unless tests pass.

## Required Output Structure
1. `Architecture`
2. `Implementation Plan by REQ-ID`
3. `Code`
4. `Tests`
5. `Run Instructions`
6. `Traceability Matrix` (REQ-ID -> files -> tests)
