# System Design Mock Interview Practice

Materials for solo or paired system design interview practice modeled on FAANG bar-raiser standards.

## Session Formats

### Solo Practice (60 min)

| Time | Phase | Activity |
|------|-------|----------|
| 5 min | Prompt & Clarify | Read a prompt card. Write down clarifying questions, functional/non-functional requirements, and traffic estimates. |
| 10 min | High-Level Design | Draw the full architecture: client → CDN → LB → app tier → cache → DB → queue → workers. Label every component. |
| 15 min | Deep Dive | Pick one bottleneck component. SQL schema, shard key, cache strategy, async pipeline. Write it out. |
| 10 min | Trade-offs | List 3 architectural decisions. For each: benefit, cost, mitigation. Stress-test with "What If" scenarios. |
| 5 min | Recap | Summarize your design in 60 seconds. State the top 3 risks and how you'd mitigate them. |
| 15 min | Debrief | Score yourself against the rubric. Note where you hesitated or went blank. Re-do those sections. |

### Paired Practice (90 min)

| Time | Activity |
|------|----------|
| 45 min | Candidate session (one person drives the whiteboard, partner plays interviewer using interview-simulator.md) |
| 15 min | Interviewer scores using scoring-rubric.md, prepares verbal feedback |
| 30 min | Debrief: read scores, discuss weak areas, re-do one section cold |

### Drill-Only Sessions (20 min)

Pick one phase and repeat it 3 times with different prompts:

- **Estimations only:** Do traffic math for 3 prompt cards in a row.
- **Schema only:** Write schemas + shard keys for 3 prompts.
- **Deep dive only:** Pick a bottleneck and go deep. Trade-offs only.
- **Recap only:** 60-second summary + top 3 risks for 5 prompts back-to-back.

## Materials

| File | Use |
|------|-----|
| `interview-simulator.md` | Timer-based script with interviewer lines, probe drills, anti-pattern alerts |
| `scoring-rubric.md` | 10-point rubric aligned to FAANG master evaluation checklist |
| `prompt-cards.md` | 15 design prompts sorted by difficulty |
| `sample-solution-url-shortener.md` | Worked solution at expected quality bar |
| `sample-solution-chat-system.md` | Worked solution for WhatsApp-like chat |
| `sample-solution-rate-limiter.md` | Worked solution for distributed rate limiting |
