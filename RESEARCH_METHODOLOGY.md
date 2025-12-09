# 🔬 Research Methodology & Testing Framework

**Reflectly - AI-Powered Emotional Journaling System**  
**Research Status:** Technical Implementation & Function Testing Phase  
**Current Stage:** Stage 3/7 - Function Testing Complete  
**Next Phase:** User Data Collection & GNN Training

---

## 📊 Table of Contents

1. [Research Overview](#research-overview)
2. [Current Testing Status](#current-testing-status)
3. [What We Tested](#what-we-tested)
4. [What We Did NOT Test](#what-we-did-not-test)
5. [Testing Methodology](#testing-methodology)
6. [Results & Validation](#results--validation)
7. [Next Steps](#next-steps)
8. [Project Timeline](#project-timeline)

---

## 🎯 Research Overview

Reflectly is an AI-powered emotional journaling system that integrates three sophisticated AI techniques:

1. **Large Language Model (LLM)** - Emotion detection from natural language (Mistral 7B)
2. **Graph Neural Network (GNN)** - Personalized learning of coping strategy effectiveness
3. **A* Pathfinding Algorithm** - Optimal emotional transition path discovery

### Research Question

> Can AI integration (LLM + GNN + A*) provide personalized mental wellness support that adapts to individual user patterns through temporal decay learning?

### Hypothesis

The system will demonstrate:
- Technical feasibility through function testing
- Readiness for user validation studies
- Foundation for clinical effectiveness trials

---

## ✅ Current Testing Status

### Stage 3: Function Testing (COMPLETE)

**What This Means:**
- We tested individual mathematical functions with controlled inputs
- We verified code correctness and algorithmic performance
- We did NOT test with real users or measure clinical effectiveness

### Testing Philosophy: Honest & Transparent

```
We believe in rigorous science:
1. Build correctly (Stage 1-3) ✓
2. Test functions (Stage 3) ✓
3. Validate with users (Stage 4-5) ← NEXT
4. Prove effectiveness (Stage 6-7) ← FUTURE
```

---

## ✅ What We Tested

### 1. Temporal Decay Formula (Mathematical Correctness)

**File:** `backend/memory_logger.py`, **Line 238**

**Formula:**
```python
score = 0.95 ** days_old  # Exponential decay
```

**Test Method:**
- Generated mathematical inputs (days 0-90)
- Applied formula to each input
- Verified output matches exponential decay theory

**Results:**
| Day | Expected | Actual | Match |
|-----|----------|--------|-------|
| 0 | 1.000 | 1.000 | ✓ |
| 7 | 0.698 | 0.698 | ✓ |
| 14 | 0.488 | 0.488 | ✓ |
| 30 | 0.215 | 0.215 | ✓ |
| 60 | 0.046 | 0.046 | ✓ |
| 90 | 0.010 | 0.010 | ✓ |

**Conclusion:** ✅ Formula implemented correctly, produces expected exponential decay curve

**Limitation:** ❌ Did not validate whether 0.95 is optimal rate for real users

---

### 2. A* Pathfinding Performance (Algorithmic Efficiency)

**File:** `backend/intelligent_agent.py`, **Lines 240-271**

**Test Method:**
- Created 50 test graphs with sample edge weights
- Ran A* algorithm on each test case
- Measured execution time and nodes explored

**Results:**

**Execution Time:**
- Mean: 4.3ms
- Range: 3.0ms - 6.2ms
- 95th percentile: 5.6ms
- All executions < 100ms threshold ✓

**Search Efficiency:**
- Mean nodes explored: 4.7 out of 7 (67%)
- Comparison: Exhaustive search = 100%
- Improvement: 33% reduction in search space
- Optimality: All paths provably optimal ✓

**Conclusion:** ✅ Algorithm executes efficiently, reduces search space while maintaining optimality

**Limitation:** ❌ Did not test whether recommended paths help real users

---

### 3. Edge Weight Calculation (Formula Verification)

**File:** `backend/gnn_graph_weight_calculator.py`, **Lines 353-390**

**Test Method:**
- Created simulated user histories with known patterns
- Applied edge weight calculation function
- Verified temporal decay integration

**Test Input (Example):**
```python
sample_history = [
    {'success': 1, 'days_ago': 0},   # Recent success
    {'success': 1, 'days_ago': 1},   # 1 day ago
    {'success': 1, 'days_ago': 3},   # 3 days ago
    {'success': 1, 'days_ago': 7},   # 7 days ago
    {'success': 1, 'days_ago': 9}    # 9 days ago
]
```

**Calculation Process:**
```
Step 1: Apply temporal decay
  Day 0: 1 × 0.95^0 = 1.000
  Day 1: 1 × 0.95^1 = 0.950
  Day 3: 1 × 0.95^3 = 0.857
  Day 7: 1 × 0.95^7 = 0.698
  Day 9: 1 × 0.95^9 = 0.630

Step 2: Average = (1.0 + 0.95 + 0.86 + 0.70 + 0.63) / 5 = 0.827

Step 3: Scale to [0.1, 10.0] range
  High success (0.827) → Low weight (2.38)

Result: Edge weight = 2.38 (easy transition)
```

**Conclusion:** ✅ Formula computes correctly with temporal decay integration

**Limitation:** ❌ Did not train GNN on real user feedback data

---

## ❌ What We Did NOT Test

### Critical Gaps (Requiring Future Work)

#### 1. LLM Emotion Detection Accuracy
**Status:** NOT TESTED

**What we need:**
- 200+ manually labeled journal entries
- Balanced across 7 emotion categories
- Expert consensus labels (3 raters, κ ≥ 0.70)

**Current claim:** "94% accuracy target"  
**Reality:** Hypothetical based on Mistral 7B literature, not validated

---

#### 2. GNN Personalization Learning
**Status:** NOT TESTED (No Training Data)

**What we need:**
- 10+ users with 10+ transitions each
- Real action success/failure feedback
- Sufficient data to train neural network

**Current status:** 
- ✅ GNN architecture complete
- ✅ Training code written
- ❌ No training data collected
- ❌ No trained model exists

---

#### 3. Clinical Effectiveness
**Status:** NOT TESTED

**What we need:**
- IRB-approved user studies
- PHQ-9 measurements (depression scale)
- Randomized controlled trial design
- 60+ participants over 8 weeks

**Current status:**
- ✅ Study designed (Phase 1-3)
- ❌ IRB approval pending
- ❌ No participants recruited
- ❌ No effectiveness data

---

#### 4. Real-World System Performance
**Status:** NOT TESTED

**What we need:**
- Real user journal entries (diverse)
- End-to-end system latency with real LLM
- Recommendation quality feedback
- Long-term engagement metrics

---

## 🧪 Testing Methodology

### Our Approach: Function-Level Testing

**Philosophy:**
```
"Test that the car engine works before testing if the car drives safely"
```

**What This Means:**
- We test individual components with known inputs
- We verify mathematical correctness
- We measure algorithmic performance
- We do NOT claim user effectiveness

### Why This Approach?

1. **Scientific Rigor:** Build correctly before testing effectiveness
2. **Honest Reporting:** Clear about what is/isn't validated
3. **Foundation:** Necessary step before user studies
4. **Reproducibility:** Anyone can verify our function tests

### Test Data Generation

**Temporal Decay Test:**
```python
# Mathematical test data (NOT user data)
days = np.arange(0, 91)  # Days 0 to 90
weights = 0.95 ** days    # Apply formula

# This tests: "Does the formula work mathematically?"
# This does NOT test: "Does this improve recommendations?"
```

**A* Performance Test:**
```python
# Create sample emotion graphs
test_graphs = []
for i in range(50):
    # Generate random edge weights
    weights = {
        ('anxious', 'neutral'): random.uniform(0.5, 8.0),
        ('sad', 'neutral'): random.uniform(0.5, 8.0),
        # ... more edges
    }
    test_graphs.append(weights)

# Run A* on each graph, measure time and nodes explored
# This tests: "Does A* execute efficiently?"
# This does NOT test: "Do the paths help users?"
```

---

## 📈 Results & Validation

### Function Testing Results Summary

| Component | Test Type | Result | Status |
|-----------|-----------|--------|--------|
| Temporal Decay | Mathematical | Correct formula | ✅ PASS |
| A* Pathfinding | Performance | 4.3ms, 67% efficiency | ✅ PASS |
| Edge Calculation | Formula | Correct integration | ✅ PASS |
| System Integration | Code execution | All components work | ✅ PASS |

### What These Results Mean

**✅ We can claim:**
- Technical implementation is complete
- Mathematical functions work correctly
- Algorithms perform efficiently
- System is ready for validation

**❌ We cannot claim:**
- LLM accurately detects emotions (not tested)
- GNN learns user patterns (no training data)
- System helps people (no user studies)
- Recommendations are effective (no validation)

---

## 🚀 Next Steps

### Stage 4: Data Collection (4 weeks)

**Goal:** Collect real user data for GNN training

**Plan:**
1. **Recruit 10-20 users** (volunteers, Reddit, university)
2. **Users journal daily** (1-2 entries/day target)
3. **Users try recommendations** and provide feedback
4. **Collect 300+ transitions** (10-15 per user)

**Timeline:** 4 weeks  
**Status:** Ready to begin (system deployed)

---

### Stage 5: GNN Training (1 week)

**Goal:** Train GNN on collected data

**Plan:**
1. **Prepare training data** from collected histories
2. **Train GNN model** (50 epochs, early stopping)
3. **Validate predictions** on held-out test set (30%)
4. **Deploy trained model** for personalized recommendations

**Metrics:**
- Mean Squared Error (MSE) < 0.5
- Prediction accuracy on test set
- Improvement over hierarchy defaults

**Timeline:** 1 week after data collection  
**Status:** Code ready, waiting for data

---

### Stage 6: User Validation (8 weeks)

**Goal:** Validate recommendation quality

**Design:** Randomized Controlled Trial (RCT)
- **N = 60** participants (20 per group)
- **Groups:**
  1. Reflectly (AI-powered)
  2. Traditional journaling
  3. Wait-list control
- **Duration:** 8 weeks
- **Primary Outcome:** PHQ-9 score change
- **Secondary:** GAD-7, WHO-5, engagement, usability

**Expected Results (Hypothesized):**
- Reflectly: -6.5 PHQ-9 reduction
- Traditional: -3.2 PHQ-9 reduction
- Control: -1.2 PHQ-9 reduction

**Timeline:** 8 weeks (pending IRB approval)  
**Status:** Study designed, IRB submission ready

---

### Stage 7: Clinical Trial (6 months)

**Goal:** Prove clinical effectiveness

**Design:** Multi-center RCT
- **N = 300** participants
- **Collaboration:** 3 mental health clinics
- **Groups:** Reflectly + TAU vs TAU only
- **Duration:** 6 months
- **Publication:** JMIR Mental Health or npj Digital Medicine

**Timeline:** 6 months (after Stage 6 success)  
**Status:** Protocol drafted

---

## 📅 Project Timeline

### Completed Stages

```
Stage 1: Design & Architecture         ████████ 100% ✓
Stage 2: Implementation                ████████ 100% ✓
Stage 3: Function Testing              ████████ 100% ✓ ← YOU ARE HERE
```

### Upcoming Stages

```
Stage 4: Data Collection               ░░░░░░░░   0%  (4 weeks)
Stage 5: GNN Training                  ░░░░░░░░   0%  (1 week)
Stage 6: User Validation               ░░░░░░░░   0%  (8 weeks)
Stage 7: Clinical Trial                ░░░░░░░░   0%  (6 months)
```

**Total Time to Full Validation:** ~8-9 months from now

---

## 🎓 Academic Integrity Statement

### Our Commitment to Honest Research

We believe scientific integrity requires:

1. **Clear Boundaries:** Distinguish function testing from user validation
2. **No Overclaiming:** Only claim what we've actually tested
3. **Transparent Limitations:** State what we haven't done
4. **Designed Validation:** Plan rigorous studies for future work

### What This Means

**We say:** "We built a system and verified it works technically"  
**We don't say:** "We proved it helps people"

**We say:** "GNN architecture is ready to train"  
**We don't say:** "GNN has learned personalization"

**We say:** "We designed validation studies"  
**We don't say:** "We conducted validation studies"

---

## 📚 References & Citations

### Key Code Locations

1. **Temporal Decay Formula**
   - File: `backend/memory_logger.py`
   - Line: 238
   - Function: `_calculate_temporal_score()`

2. **Edge Weight Calculation**
   - File: `backend/gnn_graph_weight_calculator.py`
   - Lines: 353-390
   - Function: `_calculate_true_edge_weight()`

3. **A* Pathfinding**
   - File: `backend/intelligent_agent.py`
   - Lines: 240-271
   - Function: `astar_search()`

### Related Documentation

- [RESEARCH_COMPONENTS.md](./RESEARCH_COMPONENTS.md) - Detailed AI component explanations
- [Technical Specification](./docs/TECHNICAL_SPECIFICATION.md) - Complete system documentation
- [Testing Scripts](./backend/test_reflectly_functionality.py) - Function test implementations

---

## 📧 Contact & Collaboration

**Researcher:** Manodhya  
**Institution:** Trent University  
**Course:** AMOD 5640Y - Advanced Topics in Data Science

**For Research Inquiries:**
- Open an issue on GitHub
- Suggest improvements to methodology
- Collaborate on validation studies
- Contribute to open-source development

---

## ⚖️ Ethical Considerations

### Privacy & Safety

- ✅ Local LLM processing (no data transmission)
- ✅ Crisis detection with professional resource routing
- ✅ User controls all data (export, delete)
- ✅ Transparent processing (open source)

### Research Ethics

- IRB approval required before user studies
- Informed consent for all participants
- Right to withdraw at any time
- Data anonymization for any publications

### Limitations & Warnings

⚠️ **This system is NOT:**
- A replacement for professional therapy
- Clinically validated treatment
- Suitable for crisis situations
- Proven to improve mental health

✅ **This system IS:**
- A research prototype
- Technically functional
- Ready for validation
- Open for peer review

---

**Last Updated:** December 2024  
**Version:** 1.0  
**Status:** Stage 3 Complete - Function Testing Verified

---

*"We test honestly, report transparently, and validate rigorously."*
