# Scoring Rubric

This document summarizes the current scoring protocol. The final paper should include a
more formal version with examples and inter-annotator agreement.

## Chinese Real-Case Split

The real-case split uses three 0-4 dimensions.

### A. Citation Relevance

Checks whether the answer cites or identifies a legally responsive authority and links
that authority to a concrete legal proposition.

- 0: no recognizable citation or irrelevant authority;
- 1: citation is present but generic or weak;
- 2: authority is partially relevant but linkage is thin;
- 3: relevant authority supports the claim with limited gaps;
- 4: authority is specific, relevant, and well applied.

### B. Constraint Extraction

Checks stance obedience, closed-book compliance, no invented material facts, coverage of
the requested issue, and de-identification compliance.

- 0: major violation;
- 1: severe compliance failure;
- 2: partial compliance;
- 3: mostly compliant;
- 4: all major constraints satisfied.

### C. Reasoning Effectiveness

Checks conclusion clarity, rule statement, rule-to-fact linkage, counterpoint handling,
and coherence.

- 0: no substantive reasoning;
- 1: minimal bottom-line answer;
- 2: thin rule listing or partial application;
- 3: coherent analysis with limited gaps;
- 4: strong and defensible legal reasoning.

## Public-Exam Split

The public-exam split uses one 0-4 answer-match score against reference answers.

Core units:

- issue match;
- rule/test match;
- application or exception match;
- conclusion/remedy match.

Score anchors:

- 0: nonresponsive or opposite conclusion;
- 1: roughly one unit matches;
- 2: roughly two units match;
- 3: roughly three units match;
- 4: all core units match without substantive conflict.

