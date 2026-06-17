# Contributing to System Design Academy

Thank you for your interest in contributing to **System Design Academy**.

This project aims to become a high-quality, peer-reviewed, open-source system design manual for engineers preparing for senior-level architecture discussions, interviews, and real-world design work. Contributions that improve clarity, correctness, diagrams, code examples, or practical system blueprints are very welcome.

---

## How To Contribute

### Reporting Issues

Open an issue if you find:

- Inaccurate architectural theory.
- Missing trade-offs or failure modes.
- Broken links or formatting problems.
- Mermaid diagrams that do not render correctly.
- Code snippets that are incorrect, unclear, or unsafe.
- Quiz question banks with incorrect answers or tier misclassification.
- Practice materials with inaccurate rubrics or sample solutions.
- Capacity estimates that need correction or stronger assumptions.

When reporting an issue, please include:

- The affected file and section.
- What appears incorrect or unclear.
- A suggested correction, if you have one.
- References or reasoning for technical claims where possible.

### Proposing New Modules Or Blueprints

New system design blueprints are encouraged.

Examples:

- Designing a Rate Limiter.
- Designing a Payment Gateway.
- Designing a Notification System.
- Designing a Distributed Lock Service.
- Designing a Search Autocomplete System.
- Designing a Video Streaming Platform.
- Adding quiz question banks for existing or new modules.
- Creating practice interview prompts and sample solutions.
- Writing production-grade code implementations and tests.

For new blueprints, please include:

- Requirements and assumptions.
- Back-of-the-envelope calculations.
- High-level architecture.
- API and schema definitions where relevant.
- Scaling bottlenecks and failure-mode analysis.
- Mermaid diagrams where useful.

### Improving Existing Content

You can also contribute by improving:

- Explanations and examples.
- Production code snippets.
- Mermaid architecture diagrams.
- Comparison tables and matrices.
- Interview checklists and rubrics.
- Quiz question banks and answer explanations.
- Practice materials and mock interview simulations.
- Test coverage for code implementations.
- Formatting, readability, and organization.

---

## Submission Guidelines

Please follow this pull request flow:

1. Fork the repository.
2. Create a new branch:

   ```bash
   git checkout -b feat/add-new-blueprint
   ```

3. Make your changes.
4. Ensure all diagrams use valid Mermaid syntax.
5. Ensure code examples are documented and easy to run or adapt.
6. For Python snippets, follow PEP8 conventions.
7. For quiz submissions, verify the 8/6/6 tier split and `<details>` answer-hiding format.
8. For practice submissions, align rubrics with the 10-point scoring system in `practice/scoring-rubric.md`.
9. For code submissions, ensure all tests pass with `python -m pytest code/`.
10. Keep changes focused and avoid unrelated formatting churn.
11. Commit with a clear message:

    ```bash
    git commit -m "Add rate limiter system design blueprint"
    ```

12. Push your branch and open a pull request.

In your pull request description, include:

- What changed.
- Why the change improves the repository.
- Any assumptions made.
- Any sources, references, or implementation notes.

---

## Style Guide

All content should maintain the **Engineering Manual** tone:

- Professional and precise.
- Scannable with clear headers, tables, and bullets.
- Visually driven with Mermaid diagrams where helpful.
- Focused on trade-offs, bottlenecks, and failure modes.
- Practical enough to use in real design reviews or interview preparation.

When adding technical content:

- Prefer concrete examples over vague claims.
- Include assumptions behind calculations.
- Explain why a design choice was made.
- Call out operational risks and mitigation strategies.
- Avoid hype, filler, and unsupported absolutes.

---

## Code Of Conduct

All contributors are expected to help maintain a respectful, inclusive, and collaborative environment.

Please:

- Be constructive in feedback.
- Assume good intent.
- Disagree respectfully.
- Keep discussions focused on improving the project.
- Avoid harassment, personal attacks, or exclusionary language.

This repository is for learning, teaching, and building better engineering judgment together.
