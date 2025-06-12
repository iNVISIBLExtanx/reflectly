# Intelligent Agent with Memory Map

> **Learning AI System**: An intelligent agent that learns from your emotional experiences and uses A* search to suggest helpful actions

## 🎯 **What Does This Do?**

This is a focused implementation of an intelligent agent that:

1. **📝 Analyzes your emotional text input** (happy, sad, anxious, etc.)
2. **🧠 Learns from positive experiences** by asking what steps led to good feelings
3. **💡 Suggests helpful actions** for negative emotions using A* search through learned experiences
4. **🗺️ Evolves a memory map** that grows smarter with each interaction

## 🤖 **How the Intelligent Agent Works**

### **When you input POSITIVE emotions (happy, excited):**
- 🤔 Agent asks: *"What steps led to this positive feeling?"*
- 💾 Saves your successful actions to memory map
- 🔗 Creates connections between emotions and successful strategies

### **When you input NEGATIVE emotions (sad, anxious, angry):**
- 🔍 Agent uses **A* search** through memory map
- 🎯 Finds optimal path from current emotion to positive emotions
- 💡 Suggests actions that previously worked for similar situations

### **Memory Map Evolution:**
- 🌱 Starts empty, grows with each interaction
- 📈 Learns patterns of successful emotional transitions
- 🧭 Guides future suggestions using past successes

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.7+
- Node.js 16+

### **One-Command Start**
```bash
# Clone and switch to intelligent agent branch
git clone https://github.com/iNVISIBLExtanx/reflectly.git
cd reflectly
git checkout intelligent-agent-memory

# Start the intelligent agent system
chmod +x start-intelligent-agent.sh
./start-intelligent-agent.sh
```

**Access at**: http://localhost:3000

## 🧪 **Try These Examples**

### **1. Teach the Agent (Positive Input)**
**Input**: *"I'm feeling really happy and excited today!"*
**Agent Response**: *"What steps led to this positive feeling?"*
**Your Steps**: 
- "Went for a morning run"
- "Had coffee with a friend" 
- "Listened to my favorite music"

### **2. Get Suggestions (Negative Input)**
**Input**: *"I'm feeling sad and don't know what to do"*
**Agent Response**: *"Based on past experiences, try these actions..."*
**Suggestions**: 
- "Go for a morning run" (learned from previous success)
- "Have coffee with a friend" 
- "Listen to your favorite music"

### **3. Watch Memory Map Evolve**
- Circle sizes grow with more experiences
- Lines connect emotions based on successful transitions
- Numbers show available learned actions

## 🗺️ **Memory Map Visualization**

The interactive memory map shows:
- **🟢 Green circles**: Positive emotions (happy)
- **🔴 Red circles**: Negative emotions (sad, anxious, angry)
- **⚪ Gray circles**: Neutral emotions
- **➡️ Lines**: Learned transitions between emotions
- **📊 Numbers**: Count of available action suggestions

## 🧠 **A* Search Algorithm**

The agent uses A* search to:
1. **Start** from current negative emotion
2. **Search** through memory map for paths to positive emotions
3. **Find optimal route** based on past success rates
4. **Suggest actions** from the most successful transitions

**Example Path**: `sad → neutral → happy`
- Suggests actions that previously helped transition `sad → neutral`
- Then actions that helped transition `neutral → happy`

## 📁 **Simple Architecture**

```
intelligent-agent-memory/
├── backend/
│   └── intelligent_agent.py     # 🤖 Complete agent with A* search
├── frontend/
│   └── src/
│       ├── IntelligentAgentApp.js   # 🗺️ Memory map visualization
│       └── App.js                   # ⚛️ Simple wrapper
├── start-intelligent-agent.sh      # 🚀 One-command startup
└── README.md                       # 📖 This guide
```

## 🔧 **API Endpoints**

### **Process User Input**
```bash
curl -X POST http://localhost:5000/api/process-input \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel really happy today!", "user_id": "user1"}'
```

### **Save Successful Steps**
```bash
curl -X POST http://localhost:5000/api/save-steps \
  -H "Content-Type: application/json" \
  -d '{"experience_id": "abc123", "steps": ["Went for a run", "Called a friend"]}'
```

### **Get Memory Map Data**
```bash
curl http://localhost:5000/api/memory-map
```

## 💻 **Development & Customization**

### **Add New Emotions**
```python
# In EmotionAnalyzer.__init__()
self.emotion_keywords = {
    'happy': ['happy', 'joyful', 'excited'],
    'proud': ['proud', 'accomplished', 'successful'],  # Add new emotion
    # ... existing emotions
}
```

### **Modify A* Search**
```python
# In IntelligentAgent._astar_search_for_actions()
# Customize the search algorithm:
# - Change cost functions
# - Adjust heuristics  
# - Add path preferences
```

### **Enhance Memory Learning**
```python
# In IntelligentAgent.save_successful_steps()
# Modify how steps are stored and weighted:
# - Add success rate tracking
# - Implement step effectiveness scoring
# - Add temporal decay for old experiences
```

## 🎮 **Interactive Features**

### **Conversation Interface**
- 💬 Chat-like interface with the intelligent agent
- 📝 Natural language input processing
- 🤖 Contextual responses based on emotion type
- ⏰ Timestamped conversation history

### **Memory Map Visualization**
- 🎨 Color-coded emotional states
- 📏 Dynamic sizing based on experience count
- 🔗 Visual connections showing learned transitions
- 📊 Real-time learning statistics

### **Learning System**
- 📚 Automatic experience categorization
- 💾 Persistent memory storage (session-based)
- 🔄 Continuous map evolution
- 🎯 Personalized suggestion improvement

## 🔬 **Algorithm Details**

### **Emotion Classification**
- **Method**: Keyword-based analysis with scoring
- **Emotions**: 7 categories (happy, sad, anxious, angry, confused, tired, neutral)
- **Output**: Primary emotion + confidence score

### **A* Search Implementation**
- **Goal**: Find optimal path to positive emotions
- **Heuristic**: Distance to target emotional state
- **Cost**: Inverse of historical success rate
- **Path**: Sequence of emotions and actions

### **Memory Management**
- **Storage**: In-memory dictionary structures
- **Indexing**: By emotion type and transition pairs
- **Retrieval**: O(1) lookup for common patterns
- **Evolution**: Continuous learning from new experiences

## 🎯 **Use Cases**

### **Personal Emotional Learning**
- Track what makes you happy and apply it when sad
- Build personal emotional intelligence
- Discover effective coping strategies

### **AI Research & Development**
- Study human emotional patterns
- Test reinforcement learning approaches
- Develop personalized recommendation systems

### **Educational Demonstrations**
- Show A* search in practical applications
- Demonstrate machine learning concepts
- Illustrate graph theory in psychology

## 📊 **Learning Metrics**

The system tracks:
- **Total Experiences**: Number of emotional inputs processed
- **Emotions Learned**: Unique emotional states encountered  
- **Transitions Learned**: Successful emotional pathways discovered
- **Success Rate**: Effectiveness of suggested actions

## 🛠️ **Troubleshooting**

### **Agent Not Learning**
- Make sure you provide steps when asked after positive emotions
- Check that memory map shows connections between emotions
- Verify backend is saving experiences (check learning stats)

### **No Suggestions for Negative Emotions**
- First input positive emotions and teach successful steps
- The agent needs learned experiences to make suggestions
- Use "Reset Memory" to start fresh if needed

### **Memory Map Not Updating**
- Check browser console for API errors
- Ensure backend is running on port 5000
- Try refreshing the page to reload memory data

## 🔮 **Future Enhancements**

### **Advanced Learning**
- Weight actions by success frequency
- Implement temporal decay for old experiences
- Add user feedback on suggestion effectiveness

### **Improved Search**
- Multi-objective optimization (time, effort, success rate)
- Dynamic cost adjustment based on user feedback
- Context-aware pathfinding (time of day, situation)

### **Enhanced Visualization**
- 3D memory map representation
- Animated transition paths
- Historical timeline view
- Success rate heat maps

---

**This intelligent agent demonstrates how AI can learn from human experiences and use graph algorithms to provide personalized emotional support. The memory map evolves with each interaction, becoming a more effective guide over time.** 🧠✨

**Start learning**: `./start-intelligent-agent.sh` 🚀
