# 🤖 Reflectly - AI-Powered Emotional Journaling System

> **Integrating LLM + GNN + A* for Personalized Mental Wellness Support**

[![Stage](https://img.shields.io/badge/Stage-3%2F7_Function_Testing_Complete-success)]()
[![Status](https://img.shields.io/badge/Status-Research_Prototype-blue)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()
[![Python](https://img.shields.io/badge/Python-3.11-blue)]()
[![React](https://img.shields.io/badge/React-18.2-61DAFB)]()

---

## 🎯 Project Overview

Reflectly is an AI-powered emotional journaling system that combines three sophisticated AI techniques to provide personalized mental wellness recommendations:

1. **🧠 Large Language Model (Mistral 7B)** - Understands emotional states from natural language
2. **🕸️ Graph Neural Network (GraphSAGE)** - Learns personalized coping patterns with temporal decay
3. **🗺️ A* Pathfinding Algorithm** - Finds optimal emotional transition paths

### The Innovation

**First system to integrate LLM + GNN + A* for mental health support**

While each technique exists individually, their integration for personalized emotional wellness is novel. The system adapts to each user through temporal decay learning (0.95^days), ensuring recent successes influence recommendations more than distant patterns.

---

## 🔬 Research Status

### Current Stage: 3/7 - Function Testing Complete ✅

```
Progress:
├─ Stage 1: Design & Architecture         ████████ 100% ✓
├─ Stage 2: Implementation                ████████ 100% ✓
├─ Stage 3: Function Testing              ████████ 100% ✓ ← YOU ARE HERE
├─ Stage 4: Data Collection               ░░░░░░░░   0%  (Next: 4 weeks)
├─ Stage 5: GNN Training                  ░░░░░░░░   0%  (After data collection)
├─ Stage 6: User Validation               ░░░░░░░░   0%  (8 weeks, IRB pending)
└─ Stage 7: Clinical Trial                ░░░░░░░░   0%  (6 months, future)
```

### What This Means

**✅ We Have Completed:**
- Full system implementation (2,500+ lines of code)
- Function-level testing with controlled inputs
- Mathematical verification of algorithms
- Deployment-ready architecture

**❌ We Have NOT Done:**
- User validation studies
- GNN training (no user data yet)
- Clinical effectiveness trials
- LLM accuracy testing on diverse populations

### Scientific Honesty

We maintain transparency about our testing methodology:

> "We built a system and verified it works technically.  
> We have NOT proven it helps people.  
> That's our next phase."

📖 **Full Details:** See [RESEARCH_METHODOLOGY.md](./RESEARCH_METHODOLOGY.md)

---

## 🧪 Research Documentation

### Core Research Documents

| Document | Purpose | Status |
|----------|---------|--------|
| [**RESEARCH_METHODOLOGY.md**](./RESEARCH_METHODOLOGY.md) | Testing status, validation roadmap, honest limitations | ✅ Complete |
| [**RESEARCH_COMPONENTS.md**](./RESEARCH_COMPONENTS.md) | Detailed AI component documentation (LLM/GNN/A*) | ✅ Complete |
| [**Technical Specification**](./docs/) | Complete system architecture & implementation | 📄 Available |

### Key Code Locations

**Want to verify our claims? Check these exact locations:**

1. **Temporal Decay Formula (Line 238)**
   ```python
   # File: backend/memory_logger.py, Line 238
   score = 0.95 ** days_old  # Exponential decay
   ```
   📊 **Tested:** Produces correct exponential curve  
   ❌ **Not Tested:** Whether 0.95 is optimal rate

2. **Edge Weight Calculation (Lines 353-390)**
   ```python
   # File: backend/gnn_graph_weight_calculator.py, Lines 353-390
   # Calculates difficulty scores from user history with temporal decay
   ```
   📊 **Tested:** Formula computes correctly  
   ❌ **Not Tested:** GNN learning from real users

3. **A* Pathfinding (Lines 240-271)**
   ```python
   # File: backend/intelligent_agent.py, Lines 240-271
   # A* search with emotion hierarchy heuristic
   ```
   📊 **Tested:** 4.3ms execution, 67% efficiency  
   ❌ **Not Tested:** Path quality for real users

---

## 📊 Validated Results

### What We Actually Tested

#### 1. Temporal Decay Formula ✅

**Test:** Apply formula to days 0-90, verify exponential curve

| Day | Weight | Status |
|-----|--------|--------|
| 0 | 1.000 | ✅ Correct |
| 7 | 0.698 | ✅ Correct |
| 14 | 0.488 | ✅ Correct |
| 30 | 0.215 | ✅ Correct |
| 90 | 0.010 | ✅ Correct |

**Conclusion:** Formula mathematically correct, half-life = 13.5 days

#### 2. A* Pathfinding Performance ✅

**Test:** 50 test cases with sample emotion graphs

| Metric | Result | Status |
|--------|--------|--------|
| Mean execution time | 4.3ms | ✅ Pass |
| Nodes explored | 67% (vs 100% exhaustive) | ✅ Efficient |
| Path optimality | 100% optimal | ✅ Guaranteed |
| Real-time capability | <100ms threshold | ✅ Pass |

**Conclusion:** Algorithm executes efficiently and finds optimal paths

#### 3. System Integration ✅

**Test:** End-to-end request processing

| Component | Time | % of Total |
|-----------|------|-----------|
| LLM Analysis | 1,200ms | 91.6% |
| GNN Calculation | 30ms | 2.3% |
| A* Pathfinding | 4ms | 0.3% |
| Other | 75ms | 5.8% |
| **Total** | **1,309ms** | **100%** |

**Conclusion:** All components integrated and functional

---

## 🚫 What We Did NOT Test (Critical Gaps)

### Be Aware of Limitations

1. **❌ LLM Accuracy:** "94% accuracy" is hypothetical, not validated
2. **❌ GNN Learning:** Architecture ready, but no training data collected
3. **❌ Clinical Effectiveness:** No PHQ-9 measurements or user studies
4. **❌ Real-World Performance:** System not tested with diverse users

**Why This Matters:**

Function testing ≠ User validation  
Working code ≠ Helpful recommendations  
Technical correctness ≠ Clinical effectiveness

We're at Stage 3/7. Five more stages needed to prove real-world impact.

---

## ⚡ Quick Start

### Option 1: Google Colab (Recommended - No Installation)

**Perfect for:** Testing, demos, research, quick start

1. **[Open in Colab](https://colab.research.google.com/github/iNVISIBLExtanx/reflectly/blob/colab-integration/Reflectly_Colab.ipynb)**
2. Add GitHub credentials (one-time)
3. Click "Runtime → Run all"
4. Wait 10-15 minutes
5. Click the frontend URL ✓

📖 **Guide:** [COLAB_SETUP.md](./COLAB_SETUP.md)

### Option 2: Local Installation

**Perfect for:** Development, customization, production

**Requirements:**
- Python 3.11+
- Node.js 18+
- Ollama (for local LLM)
- 8GB RAM minimum
- 10GB disk space

**Setup:**

```bash
# 1. Clone repository
git clone https://github.com/iNVISIBLExtanx/reflectly.git
cd reflectly

# 2. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral:7b-instruct

# 3. Backend setup
cd backend
pip install -r requirements.txt
python intelligent_agent.py &

# 4. Frontend setup
cd ../frontend
npm install
npm run dev

# 5. Open http://localhost:3000
```

📖 **Full Guide:** [SETUP_GUIDE.md](./SETUP_GUIDE.md)

---

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                        │
│  • Journal entry interface                                  │
│  • Emotion visualization                                    │
│  • Recommendation display                                   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   API GATEWAY (Node.js)                     │
│  • Request routing                                          │
│  • Authentication                                           │
│  • Response formatting                                      │
└───────┬──────────────┬──────────────┬──────────────────────┘
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ LLM SERVICE  │ │  GNN SERVICE │ │ A* SERVICE   │
│ (Mistral 7B) │ │ (GraphSAGE)  │ │ (Pathfinding)│
│              │ │              │ │              │
│ Emotion      │ │ Weight       │ │ Optimal      │
│ Detection    │ │ Learning     │ │ Path Finding │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
              ┌──────────────────┐
              │  DATABASE        │
              │  (PostgreSQL)    │
              └──────────────────┘
```

### Technology Stack

**Frontend:**
- React 18.2 + Next.js 13
- TypeScript 4.9
- Tailwind CSS
- Recharts (visualization)

**Backend:**
- Python 3.11
- PyTorch 2.1 + PyTorch Geometric
- Ollama (LLM server)
- Flask/FastAPI

**AI/ML:**
- Mistral 7B (emotion detection)
- GraphSAGE (personalization)
- NumPy/SciPy (mathematics)

**Database:**
- PostgreSQL 15 (main storage)
- Redis 7.0 (caching)

---

## 🎯 Key Features

### Current Features (Implemented)

- ✅ **Local LLM Processing** - Privacy-first, no data transmission
- ✅ **Temporal Decay Learning** - Recent patterns weighted more
- ✅ **Optimal Path Finding** - A* with emotion hierarchy
- ✅ **Real-time Analysis** - <1.5s response time
- ✅ **Graph Visualization** - See emotion connections
- ✅ **Action Tracking** - Log what works for you

### Planned Features (Roadmap)

- 🔄 **Multi-language Support** - Beyond English
- 🔄 **Voice Journaling** - Speech-to-text entry
- 🔄 **Wearable Integration** - Physiological data
- 🔄 **Therapist Collaboration** - Professional oversight
- 🔄 **Mobile Apps** - iOS/Android native

---

## 🔬 For Researchers

### Validation Roadmap

**Stage 4: Data Collection (4 weeks)**
- Recruit 10-20 users
- Collect 300+ transitions
- Gather feedback data

**Stage 5: GNN Training (1 week)**
- Train on collected data
- Validate predictions
- Deploy personalized model

**Stage 6: User Validation (8 weeks)**
- RCT with N=60 (3 groups)
- PHQ-9 measurements
- Success rate analysis

**Stage 7: Clinical Trial (6 months)**
- Multi-center RCT, N=300
- Mental health clinics
- Publication in JMIR or npj Digital Medicine

### Collaboration Opportunities

**We're Looking For:**
- ✨ Clinical psychologists for validation
- ✨ ML researchers for algorithm improvement
- ✨ User study participants
- ✨ Mental health clinics for trials

**Want to Collaborate?**
- Open an issue with [RESEARCH] tag
- Check [RESEARCH_METHODOLOGY.md](./RESEARCH_METHODOLOGY.md)
- Email: [Contact via GitHub]

---

## 📖 Documentation Structure

```
reflectly/
├── README.md                          ← You are here
├── RESEARCH_METHODOLOGY.md            ← Testing status & validation
├── RESEARCH_COMPONENTS.md             ← AI component details
├── COLAB_SETUP.md                     ← Google Colab guide
├── SETUP_GUIDE.md                     ← Local installation
├── backend/
│   ├── memory_logger.py               ← Temporal decay (line 238)
│   ├── gnn_graph_weight_calculator.py ← Edge weights (lines 353-390)
│   ├── intelligent_agent.py           ← A* search (lines 240-271)
│   └── llm_emotion_analyzer.py        ← LLM integration
└── frontend/
    └── (React application)
```

---

## 🤝 Contributing

### How to Contribute

1. **Code Improvements**
   - Fork the repository
   - Create feature branch
   - Submit pull request

2. **Research Validation**
   - Participate in user studies
   - Provide feedback on methodology
   - Suggest improvements

3. **Documentation**
   - Fix typos or improve clarity
   - Add examples
   - Translate to other languages

### Contribution Guidelines

- ✅ Maintain scientific honesty
- ✅ Test your changes
- ✅ Follow code style
- ✅ Update documentation
- ✅ Be respectful and constructive

---

## ⚠️ Important Disclaimers

### This System is NOT:

- ❌ A replacement for professional therapy
- ❌ Clinically validated treatment
- ❌ Suitable for crisis situations
- ❌ Medical advice or diagnosis
- ❌ Proven to improve mental health

### This System IS:

- ✅ A research prototype
- ✅ Technically functional
- ✅ Open for validation
- ✅ Privacy-preserving
- ✅ Free and open source

### Crisis Resources

**If you're in crisis, please seek immediate help:**

- 🆘 **National Suicide Prevention Lifeline:** 988
- 💬 **Crisis Text Line:** Text HOME to 741741
- 🚨 **Emergency Services:** 911

This system is for research and support, not crisis intervention.

---

## 📊 Performance Metrics

### System Performance

| Metric | Value | Status |
|--------|-------|--------|
| End-to-end latency | 1.3s | ✅ Acceptable |
| LLM inference time | 1.2s | ⚠️ Optimization needed |
| A* execution time | 4.3ms | ✅ Excellent |
| Memory usage | ~2GB | ✅ Efficient |
| Cold start time | 15s | ✅ Acceptable |

### AI Component Performance

| Component | Metric | Value |
|-----------|--------|-------|
| **LLM** | Target accuracy | 94% (not validated) |
| **LLM** | Inference speed | 1,200ms |
| **GNN** | Training status | Not trained (no data) |
| **GNN** | Architecture | 3-layer GraphSAGE |
| **A*** | Search efficiency | 67% (vs 100% exhaustive) |
| **A*** | Optimality | Guaranteed |

---

## 📜 License

**MIT License** - See [LICENSE](./LICENSE) file

```
Copyright (c) 2024 Manodhya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

**Key Points:**
- ✅ Free to use, modify, distribute
- ✅ Commercial use allowed
- ✅ No warranty provided
- ⚠️ Use at your own risk

---

## 🙏 Acknowledgments

### Technologies Used

- **Mistral AI** - Mistral 7B LLM
- **PyTorch Team** - Deep learning framework
- **PyTorch Geometric** - Graph neural networks
- **Ollama** - Local LLM serving
- **React Team** - Frontend framework

### Inspiration

- Mental health accessibility challenges (264M+ people with depression)
- High cost of therapy ($200+ per session)
- Long wait times (3-6 months)
- Need for personalized support

---

## 📞 Contact & Support

**Researcher:** Manodhya  
**Institution:** Trent University  
**Course:** AMOD 5640Y - Advanced Topics in Data Science

### Get Help

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/iNVISIBLExtanx/reflectly/issues)
- 📖 **Questions:** Check documentation first
- 💬 **Discussions:** [GitHub Discussions](https://github.com/iNVISIBLExtanx/reflectly/discussions)
- ✉️ **Research Inquiries:** Open issue with [RESEARCH] tag

---

## 🗺️ Roadmap

### Q1 2025 (Current)
- ✅ Complete technical implementation
- ✅ Function testing
- 📝 Research documentation
- 🎓 Academic poster presentation

### Q2 2025
- 📊 Data collection (user study)
- 🤖 GNN training
- 📈 Initial validation

### Q3-Q4 2025
- 🔬 User validation study (RCT)
- 📄 First research publication
- 🚀 System improvements

### 2026+
- 🏥 Clinical trial
- 📱 Mobile apps
- 🌍 Multi-language support
- 🤝 Therapist collaboration features

---

## 🌟 Star History

If you find this project interesting or useful for your research:

⭐ **Star this repository** to show support  
🔄 **Fork it** to contribute  
📖 **Cite it** in your research

---

## 📚 Citation

If you use this system in your research, please cite:

```bibtex
@software{reflectly2024,
  title={Reflectly: AI-Powered Emotional Journaling with LLM+GNN+A* Integration},
  author={Manodhya},
  year={2024},
  url={https://github.com/iNVISIBLExtanx/reflectly},
  note={Research prototype - Stage 3/7 complete}
}
```

---

## 🔗 Quick Links

- 📓 [**Open in Colab**](https://colab.research.google.com/github/iNVISIBLExtanx/reflectly/blob/colab-integration/Reflectly_Colab.ipynb) - Try it now!
- 🔬 [**Research Methodology**](./RESEARCH_METHODOLOGY.md) - Testing details
- 🤖 [**AI Components**](./RESEARCH_COMPONENTS.md) - Technical deep dive
- 📖 [**Setup Guide**](./SETUP_GUIDE.md) - Local installation
- 🐛 [**Issues**](https://github.com/iNVISIBLExtanx/reflectly/issues) - Report bugs
- 💬 [**Discussions**](https://github.com/iNVISIBLExtanx/reflectly/discussions) - Ask questions

---

<div align="center">

**Made with ❤️ for Mental Health Research**

*"We test honestly, report transparently, and validate rigorously."*

[⭐ Star](https://github.com/iNVISIBLExtanx/reflectly) • [🔄 Fork](https://github.com/iNVISIBLExtanx/reflectly/fork) • [🐛 Report Bug](https://github.com/iNVISIBLExtanx/reflectly/issues) • [✨ Request Feature](https://github.com/iNVISIBLExtanx/reflectly/issues)

</div>

---

**Last Updated:** December 2024  
**Version:** 1.0  
**Status:** Stage 3/7 - Function Testing Complete
