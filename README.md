# Nestor Rivers — Software Engineering Portfolio

A collection of software engineering projects, technical experiments, and case studies covering backend development, data processing, intelligent systems, spatial computing, security, and applied problem solving.

My professional background includes a BSc in Computer Science, an MSc in Intelligent Systems and Robotics, freelance development, programming work within the VCSE sector, and four years as the lead software developer at Chariot Transport Solutions.

This repository brings together selected examples of that work.

---

## Professional Experience

### Chariot Transport Solutions

I spent four years as the company's lead software developer, designing and building a substantial software system for the transport business.

Working as the only developer meant taking responsibility across the development lifecycle, including requirements analysis, system design, database design, application development, integrations, automation, security, testing, debugging, deployment, and ongoing maintenance.

The original system is no longer available as a public project, so this portfolio documents selected aspects of the engineering work through reconstructed case studies and representative implementations.


**Areas demonstrated:**

* Authentication
* Security engineering
* Access control
* Token-based verification
* Geolocation
* Temporal policies
* Human-in-the-loop approval workflows
* Backend architecture
* Security/usability trade-offs

---

## Selected Projects


### Context-Aware MFA & Access Control

A security-focused authentication system developed at Chariot Transport Solutions, combining email-based MFA with contextual access controls based on user location and working hours. Login requests outside a user's expected location or normal working pattern could trigger a manager approval workflow before access was granted.

The project demonstrates practical security engineering beyond basic authentication, including risk-based access decisions, geolocation checks, time-based policies, token-based verification, and human-in-the-loop approval workflows.

**Areas demonstrated:**

* Authentication and access-control design
* Email-based MFA and token verification
* Geolocation and time-based security policies
* Risk-adaptive access decisions
* Backend security engineering and workflow design

[View project](./mfa-implementation/)

### Supplier Allocation Engine

A software project exploring allocation of suppliers against a set of requirements and constraints.

The project focuses on translating a complex allocation problem into explicit business rules and an executable algorithm.

**Areas demonstrated:**

* Algorithm design
* Constraint handling
* Data modelling
* Backend development
* Automated processing

[View project](./supplier-allocation-engine/)

---

### Transport Data Aggregator

A project concerned with collecting, processing, and consolidating transport-related data from multiple sources.

The project explores the engineering problems involved in transforming disparate data into a consistent structure suitable for further processing.

**Areas demonstrated:**

* Data processing
* API/integration work
* Data transformation
* Error handling
* Backend development

[View project](./transport-data-aggregator/)

---

### AR Project

A browser-based augmented-reality project exploring location-aware and spatial interaction on the web.

The project combines web technologies with AR to create an interactive experience tied to the physical environment.

**Areas demonstrated:**

* JavaScript
* Web APIs
* Augmented reality
* Spatial computing
* Interactive web development


[View project](./ar-project/)

---

### RuneCast

A deep learning project exploring multivariate time-series forecasting for complex RuneScape item prices. RuneCast models relationships between crafted items and their precursor materials, using configurable dependency depth to investigate whether information from upstream components can improve price prediction.

The project demonstrates practical machine learning engineering, including data collection and preprocessing, LSTM-based sequence modelling, automated hyperparameter optimisation with Optuna, and experimental comparison against a univariate baseline.

**Areas demonstrated:**

* Deep learning and LSTM time-series modelling
* Multivariate data processing and feature engineering
* Automated hyperparameter optimisation with Optuna
* Python, PyTorch, Pandas and NumPy
* Data collection, caching and reproducible ML workflows

[View project](./RuneCast/)

---

## Technical Interests

My projects tend to sit at the intersection of practical software engineering and technically interesting problems.

Areas of particular interest include:

* Python and Django
* Backend systems
* APIs and integrations
* Data modelling and processing
* Algorithms and optimisation
* Intelligent systems
* Robotics
* Spatial computing
* Security and authentication
* Automation
* Software architecture

I particularly enjoy problems where the difficult part is understanding the system and its constraints before writing the code.

---

## Engineering Approach

I approach software development as a problem-solving discipline rather than simply an exercise in implementing features.

For significant projects, I aim to document:

1. **The problem** — what needed to be solved and why.
2. **The constraints** — technical, operational, or business limitations.
3. **The design** — how the system was structured.
4. **The difficult parts** — where straightforward solutions were insufficient.
5. **The implementation** — how the design was translated into working software.
6. **The trade-offs** — why particular approaches were chosen over alternatives.
7. **The result** — what the implementation achieved.
8. **The lessons** — what I would retain, change, or improve with hindsight.

Where professional work cannot be published directly, I use reconstructed case studies and representative implementations to demonstrate the underlying engineering without exposing proprietary source code, data, or business information.

---

## About Me

**Nestor Rivers**

BSc Computer Science
MSc Intelligent Systems & Robotics

Software developer interested in building systems that solve difficult, real-world problems.

[LinkedIn](https://www.linkedin.com/in/nestor-rivers/) · [GitHub](https://github.com/nestorrivers)
