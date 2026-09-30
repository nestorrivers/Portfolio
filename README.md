# Nestor Rivers: Software Engineering Portfolio

Django and Python developer with a BSc in Computer Science and an MSc in Intelligent Systems and Robotics. I've spent four years as the sole developer of a production transport management system, and I've written software for community transport providers in the voluntary sector.

I'm looking for roles in **civic tech, mission-driven organisations, and arts and culture technology**, where the difficult part is understanding people, constraints and systems before writing the code.

[LinkedIn](https://www.linkedin.com/in/nestor-rivers/) · [GitHub](https://github.com/nestorrivers)

---

## How to read this repository

My largest project, a production transport management system, is proprietary and can't be published. So this repository holds **extracted and reconstructed components** instead: self-contained pieces of real systems, written to be read or dropped into a host project and adapted, not run as standalone sites.

Every project folder has its own README covering the problem, the design, the decisions and trade-offs, and a **Known limitations** section. I'd rather you see where the edges are than guess.

## Projects

| Project | What it is | Stack | Status |
| --- | --- | --- | --- |
| [challenge-chain-api](./challenge-chain-api/) | An HTTP-only puzzle service: fetch a challenge, solve it in your own code, post the answer, follow the link to the next one | Django REST Framework | Complete, with tests |
| [MFA & Access Control](./mfa-implementation/) | Email MFA plus location and working-hours policies, with manager approval for logins that fail them | Django | Reconstructed excerpt |
| [Supplier Allocation Engine](./supplier-allocation-engine/) | Decides which suppliers are offered a booking and in what order, with a reason code for every placement | Pure Python | Extracted component |
| [Pataverse](./ar-project/) | Browser-based AR: leave content at real-world coordinates and let others find it | Django, AR.js, A-Frame | Extracted, work in progress |
| [Transport Data Aggregator](./transport-data-aggregator/) | Turns UK public RSS feeds (weather, traffic) into typed objects a transport system can use | Python | Alpha: weather done, traffic scaffolded |
| [RuneCast](./RuneCast/) | Tests whether an item's supply-chain prices help predict its own price | PyTorch, Optuna | Pipeline built, evaluation in progress |

---

### challenge-chain-api

A small Django REST service where the API *is* the interface. A player writes a client that fetches a challenge (sort these numbers, compute this checksum), posts a solution, and follows the `next` link until the chain is complete. Challenges are generated deterministically from a seed, so runs are reproducible. Adding a new challenge type is one decorated function.

*Shows:* API design, deterministic generation, authentication and server-side timing, test coverage.

### Context-Aware MFA & Access Control

After the password check, a login is judged against **where** the user is and **when** they're logging in, then passes through an emailed one-time token. Logins that fail the contextual checks aren't simply rejected: they're escalated to a manager, whose approval unlocks the next attempt. A reconstruction of an access-control subsystem I built for Chariot Transport Solutions.

*Shows:* security engineering, risk-based access decisions, human-in-the-loop workflows, security and usability trade-offs.

### Supplier Allocation Engine

A rule-driven engine, extracted from a production booking system where the allocation logic had become tangled up with request handling. It takes a booking and a pool of suppliers and returns an ordered list plus a reason trail: eligibility, passenger preference, price agreements, nearby points of interest, then distance, ETA or price. Zero framework dependencies, no side effects.

*Shows:* turning business rules into an explicit, testable algorithm; explainable output; refactoring for isolation.

### Pataverse

Users create text and image content through an ordinary Django app and place it at real-world coordinates. Anyone walking past with a phone can see it through the browser using AR.js. The interesting engineering is at the edges: location as untrusted input, a bounding-box-then-Haversine discovery query, restricted-area polygons that keep content out of unsafe places, and moderation.

*Shows:* geospatial logic, safety-aware design, user-generated content moderation, browser-based AR.

### Transport Data Aggregator

A framework-agnostic library that fetches public feeds and normalises each domain into frozen, typed dataclasses, so a consuming system never needs to know about feed formats. Strict at the edges (explicit fetch and parse failures), lenient in the middle (an unparseable field becomes `None`, not a failed batch). The weather domain is implemented, and traffic and the CLI are scaffolded.

*Shows:* layered library design, typed Python, pluggable sources, error-handling policy.

### RuneCast

An LSTM forecasting project built around one question: does knowing the prices of an item's *inputs* help predict its price? A configurable "depth" adds successive tiers of the supply chain (1 to 40 features) so the same code can compare a univariate model with progressively deeper ones. The data pipeline, model and tuning are built. The baseline comparison is still to do, and the README says so.

*Shows:* multivariate time-series modelling, an experiment designed around a testable question, and honesty about evaluation status.

---

## Professional background

**Chariot Transport Solutions**: lead (and sole) developer for four years on a substantial transport management system, covering requirements, database and system design, integrations, automation, security, deployment and maintenance.

**Voluntary sector**: development work alongside community transport providers.

The Chariot system itself is private, so the MFA and allocation projects above are reconstructions of parts of it.

## How I write things up

For significant work I try to record the problem, the constraints, the design, the difficult parts, the trade-offs, the result and what I'd change with hindsight. Project READMEs follow that shape, including where the work is unfinished.