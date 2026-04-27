# Reflectly
### AI-Powered Emotional Journaling & Mental Wellness Platform

[![Status](https://img.shields.io/badge/Status-Research%20Prototype%20(Not%20Hosted)-orange?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)]()
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)]()

> **Note:** This is a research prototype. The system is not currently hosted publicly. The code, architecture, and research documentation are available in this repository.

---

## The Problem

Mental wellness apps generate journal entries but don’t learn from them. Most platforms offer generic recommendations that ignore the fact that emotional patterns are personal, non-linear, and context-dependent.

A user who journaled about anxiety 6 months ago is not the same person today. Standard CBT-based apps treat every entry in isolation. The result: recommendations that don’t fit, low engagement, and users who abandon the app after a few weeks.

---

## What Reflectly Does

Reflectly is an AI-powered journaling system that learns each user’s emotional patterns over time and delivers personalised wellness recommendations that get more accurate the longer you use it.

Three systems work together:

1. **LLM (Mistral 7B)** — Understands emotional nuance in natural language journal entries
2. **Graph Neural Network (GraphSAGE)** — Maps the relationship between emotional states and coping strategies over time, personalised per user
3. **A* Pathfinding Algorithm** — Finds the most effective emotional transition path based on your personal history

**The result:** Recommendations that improve with every journal entry — not pulled from a generic wellness library.

---

## Why This Is Different

| Standard Wellness App | Reflectly |
|----------------------|----------|
| Generic CBT recommendations | Recommendations based on *your* emotional history |
| Treats each entry in isolation | Learns patterns across entries over time |
| Same advice for all users | Adaptive: adjusts as your patterns change |
| No memory of past successes | Weights recent outcomes more heavily (temporal decay: 0.95^days) |

The temporal decay mechanism means what worked for you last week matters more than what worked 3 months ago — reflecting real psychological change.

---

## Research Foundation

This system is a research prototype. The architecture explores a novel integration of three AI techniques not previously combined for mental wellness applications:

- **GraphSAGE** for personalised emotional pattern learning
- **LLM grounding** for contextual emotional interpretation
- **A\* search** on emotional state graphs for optimal wellness pathway recommendation

Built as a research investigation into AI-driven personalised mental health support. Currently at **3/7 functional testing complete**.

---

## Architecture

```
User Journal Entry (React Frontend)
           |
           v
     LLM Layer (Mistral 7B via Ollama)
     Emotional state extraction + classification
           |
           v
     GNN Layer (GraphSAGE)
     Personalised emotional pattern graph
     (temporal decay weighting: 0.95^days)
           |
           v
     A* Pathfinding
     Optimal emotional transition path
           |
           v
     Personalised Recommendation Output
           |
           v
     Cloudflare Tunnel → Colab Backend (GPU)
```

**Stack:** Python 3.11 · React 18 · FastAPI · Mistral 7B · GraphSAGE · PyTorch · Cloudflare Tunnel

---

## Repository Structure

```
reflectly/
├── backend/          # Python FastAPI + GNN + LLM pipeline
├── frontend/         # React 18 journaling interface
├── docs/             # Architecture and research documentation
└── Reflectly_Colab.ipynb  # GPU-backed GNN training notebook
```

---

## Live Metrics

- **Status:** Research prototype — 3/7 functions tested, not publicly hosted
- **Commits:** 100 across development history
- **Architecture:** Documented in `/docs`

---

## Business Applications

This research architecture has direct commercial applications:

- **Employee wellness platforms** — personalised burnout detection and intervention
- **Digital health companion apps** — supplement to therapy, not replacement
- **Chronic condition support** — mood-condition correlation for patients with long-term health issues
- **Corporate EAP (Employee Assistance Programs)** — data-driven mental health program effectiveness measurement

---

## Built By

Manodhya Opallage — [GitHub](https://github.com/iNVISIBLExtanx) · [LinkedIn](https://linkedin.com/in/manodhya-opallage)

M.Sc. Data Science (Trent University, Canada) · IEEE Published · Patent Pending

---

**Interested in this research or its commercial applications?** Contact: mopallage@gmail.com
