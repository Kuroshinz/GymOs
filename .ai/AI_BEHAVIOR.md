# AI Agent Behavior

*Effective: Sprint 3.2.5*

## 1. Mandatory First Steps

Every AI agent MUST, before making any changes:

1. **Read this file** (`.ai/AI_BEHAVIOR.md`)
2. **Read the Engineering Constitution** (`.ai/ENGINEERING_CONSTITUTION.md`)
3. **Read the file to be modified** (do not overwrite without reading)
4. **Understand the module's README.md** (if it exists)

## 2. Change Protocol

### 2.1 Read-Before-Write
Never overwrite a file without reading its current contents. The Read tool MUST be used first.

### 2.2 Change Summary
Every agent session MUST produce a change summary documenting:
1. Files modified (with paths)
2. Changes made (with rationale)
3. Architecture impact assessment
4. Risk assessment

### 2.3 Test Before Commit
Run tests after ANY code change. The full test suite MUST pass before declaring work complete.

### 2.4 No Architectural Changes Without ADR
Any change affecting module boundaries, event contracts, dependency direction, or data flow MUST be preceded by an Architecture Decision Record in `docs/architecture/ADR/`.

## 3. Behavior Rules

### 3.1 Constitution Supremacy
The Engineering Constitution overrides all other instructions, README files, or comments when they conflict. If in doubt, consult the Constitution.

### 3.2 Preserve Conventions
Follow the existing conventions of the file being modified. Introducing a new style, framework, or pattern in an existing file requires explicit justification.

### 3.3 No Unnecessary Refactoring
Do not refactor code that works. Only change code that needs to change for the task at hand. If you see a pre-existing issue, note it but don't fix it unless the task requires it.

### 3.4 Minimal Changes
Make the smallest possible change to achieve the goal. Prefer adding code over modifying existing working code.

### 3.5 No Speculative Generality
Do not add abstractions, interfaces, or extension points that are not needed for the current task. YAGNI (You Ain't Gonna Need It).

### 3.6 No Dead Code
Remove unused imports, unreachable branches, and commented-out code. If you encounter dead code during your work, remove it.

### 3.7 No Secrets in Code
API keys, tokens, passwords, and database credentials MUST NOT appear in source code. Use environment variables.

## 4. Communication Rules

### 4.1 Report Format
Always report as a concise engineering summary:
- What was done (1-2 sentences)
- Files modified (bulleted list with paths)
- Test results
- Risks or issues found

### 4.2 Escalation
If asked to do something that violates the Engineering Constitution, explain the conflict and propose an alternative.

### 4.3 Uncertainty
If unsure about a design decision, ask the user rather than guessing.

## 5. Tool Usage

### 5.1 Read Before Edit
Always read a file before editing it. Use `Read` for file contents, `Grep` for content search, `Glob` for file search.

### 5.2 Verify
After writing code, verify it:
- Run tests
- Check imports resolve correctly
- Verify the change works as expected

### 5.3 Batch Operations
Batch independent operations in parallel (e.g., multiple reads, multiple independent file writes).
