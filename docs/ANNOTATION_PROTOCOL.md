# Annotation Protocol

## Status

Human validation is in progress. The current goal is to validate a stratified pilot
before scaling to the full model-output matrix.

## Human Validation Goals

The human review protocol is designed to answer three questions:

1. Do model-based or automated rubric scores align with legal expert judgments?
2. Which failure modes are missed by reference-based scoring?
3. Do public-exam rankings transfer to real-case, stance-aware legal analysis?

## Sampling Plan

The first public snapshot stages:

- Chinese real-case pilot rows selected from the stance-aware civil judgment split.
- Public-exam pilot rows selected from high-disagreement or high-value legal exam
  instances.

Future iterations should stratify by:

- split;
- jurisdiction/source country;
- law category;
- issue difficulty;
- model family;
- reasoning mode or prompt mode;
- automated-score disagreement.

## Chinese Real-Case Rubric

Each response receives three scores from 0 to 4.

### A. Citation Relevance

Measures whether the response identifies legally responsive authorities and uses them
to support a concrete proposition.

Score anchors:

- 0: no recognizable legal authority or irrelevant authority;
- 1: bare or weak authority mention;
- 2: partially relevant authority with thin linkage;
- 3: mostly relevant authority and support;
- 4: authority is relevant, specific, and well connected to the claim.

### B. Constraint Extraction And Compliance

Measures whether the response follows the stance, avoids invented facts, covers the
required issue, and respects de-identification / closed-book constraints.

Score anchors:

- 0: major violation such as opposite stance or fabricated material facts;
- 1: severe omissions or compliance failures;
- 2: partial compliance;
- 3: mostly compliant with limited gaps;
- 4: fully compliant.

### C. Reasoning Effectiveness

Measures legal conclusion, rule statement, rule-to-fact application, handling of
counterpoints, and internal coherence.

Score anchors:

- 0: no substantive legal reasoning;
- 1: conclusion with minimal analysis;
- 2: rule listing or thin application;
- 3: coherent reasoning with limited gaps;
- 4: strong rule-to-fact analysis and defensible conclusion.

## Public-Exam Rubric

Public-exam answers receive a 0 to 4 answer-match score against the reference answer.

Core units:

- issue/problem object;
- governing rule or legal test;
- key application, exception, or sub-issue;
- final conclusion, remedy, or outcome.

Score anchors:

- 0: nonresponsive or opposite core conclusion;
- 1: roughly one core unit matches;
- 2: roughly two core units match;
- 3: roughly three core units match;
- 4: all core units match without substantive conflict.

## Review Notes

Review notes should be short, specific, and audit-friendly. Preferred tags include:

- weak citation linkage;
- wrong legal domain;
- opposite stance;
- invented facts;
- missed key rule;
- omitted major issue;
- thin rule-to-fact analysis;
- mostly aligned with minor gaps.

## Reliability Plan

For a final release, the project should report:

- number of human reviewers;
- reviewer training procedure;
- double-coded subset size;
- agreement statistics by split and score dimension;
- adjudication procedure for disagreements.

