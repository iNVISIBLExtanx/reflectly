# 🚀 Reflectly Enhanced Setup Guide

## LLM + GNN Integration Setup

This guide will help you set up and run the enhanced Reflectly system with LLM-based emotion analysis and GNN-based dynamic graph weights.

---

## 📋 Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL
- **Python**: 3.8 or higher
- **RAM**: Minimum 8GB (16GB recommended for GNN training)
- **Disk Space**: ~10GB for models and data

### Software Dependencies
1. **Python 3.8+** with pip
2. **Node.js 16+** with npm (for frontend)
3. **Ollama** (for local LLM)

---

## ⚡ Quick Start (Recommended)

```bash
# 1. Clone the repository and checkout the branch
git clone https://github.com/iNVISIBLExtanx/reflectly.git
cd reflectly
git checkout feat-upgrade-LLM

# 2. Run the automated setup script
chmod +x setup_enhanced.sh
./setup_enhanced.sh

# 3. Start the application
./start.sh
```

The setup script will:
- ✅ Install Python dependencies
- ✅ Install and configure Ollama
- ✅ Pull the Mistral 7B model
- ✅ Create data directories
- ✅ Verify all components

---

## 🔧 Manual Setup (If automated setup fails)

### Step 1: Install Python Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

pip install --upgrade pip
pip install -r requirements.txt
```

**Key Dependencies:**
- `flask`, `flask-cors` - Backend API
- `ollama` - LLM integration
- `torch`, `torch-geometric` - GNN implementation
- `numpy`, `scipy` - Numerical computing

### Step 2: Install Ollama

**Linux/macOS:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai/download/windows

**Verify Installation:**
```bash
ollama --version
```

### Step 3: Pull LLM Model

```bash
# Primary model (recommended)
ollama pull mistral:7b

# Alternative models (fallback)
ollama pull llama3.2:3b
ollama pull llama2:7b
```

**Model Sizes:**
- Mistral 7B: ~4.1GB
- Llama 3.2 3B: ~2GB
- Llama 2 7B: ~3.8GB

### Step 4: Verify Ollama is Running

```bash
# Start Ollama service (if not already running)
ollama serve

# Test the model
ollama run mistral:7b "Hello, how are you?"
```

### Step 5: Create Data Directory

```bash
mkdir -p backend/data
```

### Step 6: Configure Environment (Optional)

Create `backend/.env` file:

```env
# LLM Configuration
LLM_ENABLED=true
LLM_MODEL=mistral:7b
OLLAMA_HOST=http://localhost:11434

# GNN Configuration
GNN_ENABLED=true

# Application
DEBUG=True
PORT=5000
```

---

## 🚀 Running the Application

### Option 1: Using Start Script (Recommended)

```bash
# From project root
./start.sh
```

This starts:
- Backend API on http://localhost:5000
- Frontend on http://localhost:3000

### Option 2: Manual Start

**Backend:**
```bash
cd backend
source venv/bin/activate
python intelligent_agent.py
```

**Frontend (separate terminal):**
```bash
cd frontend
npm install  # First time only
npm start
```

---

## 🧪 Testing the Setup

### 1. Test Backend Health

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Enhanced Intelligent Agent",
  "features": ["emotion_analysis", "gnn_weights", "llm_enabled"],
  "llm_enabled": true,
  "gnn_enabled": true
}
```

### 2. Test LLM Emotion Analysis

```bash
curl -X POST http://localhost:5000/api/process-input \\
  -H \"Content-Type: application/json\" \\
  -d '{\"text\": \"I am feeling really happy today!\", \"user_id\": \"test\"}'
```

### 3. Test Frontend

Open http://localhost:3000 in your browser and:
1. Enter "I feel sad" → Should get suggestions
2. Enter "I'm excited!" → Should ask for steps
3. View memory map visualization

---

## 🔍 Troubleshooting

### Issue: Ollama Not Found

**Solution:**
```bash
# Check if Ollama is installed
which ollama

# If not found, install:
curl https://ollama.ai/install.sh | sh

# Verify installation
ollama --version
```

### Issue: Model Not Downloaded

**Solution:**
```bash
# List available models
ollama list

# Pull the model if missing
ollama pull mistral:7b

# Verify it's working
ollama run mistral:7b "test"
```

### Issue: PyTorch/PyG Installation Failed

**Solution:**

**For CPU only:**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install torch-geometric
```

**For CUDA (GPU):**
```bash
# Replace cu118 with your CUDA version (e.g., cu117, cu121)
pip install torch --index-url https://download.pytorch.org/whl/cu118
pip install torch-geometric
```

### Issue: LLM Responses are Slow

**Solutions:**
1. Use smaller model: `llama3.2:3b` instead of `mistral:7b`
2. Increase timeout in `backend/config.py`:
   ```python
   REQUEST_TIMEOUT = 60  # Increase from 30
   ```
3. Disable LLM temporarily:
   ```bash
   export LLM_ENABLED=false
   ```

### Issue: GNN Training Fails

**Solutions:**
1. Check if enough data:
   - Need at least 10 transitions for GNN training
2. Disable GNN temporarily:
   ```python
   # In backend/config.py
   GNN_ENABLED = False
   ```
3. Check PyTorch installation:
   ```bash
   python -c "import torch; print(torch.__version__)"
   ```

### Issue: Frontend Can't Connect to Backend

**Solutions:**
1. Check backend is running:
   ```bash
   curl http://localhost:5000/api/health
   ```
2. Check CORS settings in `backend/intelligent_agent.py`
3. Verify frontend proxy settings in `frontend/package.json`

### Issue: Memory Map Not Persisting

**Solution:**
```bash
# Check data directory exists
ls -la backend/data/

# Check file permissions
chmod 755 backend/data

# Manually trigger save
curl -X POST http://localhost:5000/api/save-memory
```

---

## 📊 Verifying LLM vs Regex Performance

```bash
# Get performance stats
curl http://localhost:5000/api/llm-stats
```

Expected metrics:
- `llm_success_rate`: Should be >80% if Ollama is working
- `avg_llm_time_ms`: Typical 500-2000ms depending on hardware
- `regex_fallbacks`: Should be low if LLM is working

---

## 🎛️ Configuration Options

Edit `backend/config.py` to customize:

### LLM Settings
```python
# In LLMConfig class
PRIMARY_MODEL = 'mistral:7b'  # Change model
TEMPERATURE = 0.3  # Lower = more consistent
LLM_ENABLED = True  # Disable to use regex only
```

### GNN Settings
```python
# In GNNConfig class
HIDDEN_DIM = 64  # Increase for more capacity
NUM_EPOCHS = 50  # Increase for better training
MIN_TRANSITIONS_FOR_TRAINING = 10  # Lower to train sooner
GNN_ENABLED = True  # Disable to use hardcoded weights
```

### Memory Settings
```python
# In MemoryConfig class
AUTO_SAVE = True  # Enable/disable auto-save
SAVE_INTERVAL_SECONDS = 300  # Save frequency
MAX_TRANSITION_AGE_DAYS = 90  # Data retention
```

---

## 🔄 Updating the System

```bash
# Pull latest changes
git pull origin feat-upgrade-LLM

# Update Python dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Update Ollama models
ollama pull mistral:7b

# Restart the application
./start.sh
```

---

## 📈 Performance Optimization

### For Better LLM Performance
1. **Use GPU if available:**
   - Ollama automatically uses GPU if CUDA is installed
   - Check: `nvidia-smi` (for NVIDIA GPUs)

2. **Use smaller models for faster responses:**
   ```python
   PRIMARY_MODEL = 'llama3.2:3b'  # Faster than mistral:7b
   ```

3. **Reduce token limit:**
   ```python
   MAX_TOKENS = 100  # Reduce from 150
   ```

### For Better GNN Performance
1. **Use GPU for training:**
   ```python
   # In gnn_graph_weight_calculator.py
   device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
   ```

2. **Reduce training epochs for faster iteration:**
   ```python
   NUM_EPOCHS = 30  # Reduce from 50
   ```

---

## 🛡️ Security Considerations

1. **Local LLM**: Data never leaves your machine
2. **Data Storage**: All data stored locally in `backend/data/`
3. **No API Keys**: No external API calls required
4. **Privacy**: User conversations stored locally only

---

## 📚 Additional Resources

- **Ollama Documentation**: https://github.com/jmorganca/ollama
- **PyTorch Geometric**: https://pytorch-geometric.readthedocs.io/
- **Mistral AI**: https://mistral.ai/
- **Flask Documentation**: https://flask.palletsprojects.com/

---

## ❓ Getting Help

1. **Check logs:**
   ```bash
   # Backend logs in terminal running intelligent_agent.py
   # Or check: backend/logs/
   ```

2. **Reset everything:**
   ```bash
   curl -X POST http://localhost:5000/api/reset-memory
   rm -rf backend/data/*
   ```

3. **Disable advanced features:**
   ```bash
   # Use only regex + hardcoded weights
   export LLM_ENABLED=false
   export GNN_ENABLED=false
   ```

4. **Open an issue:**
   - GitHub: https://github.com/iNVISIBLExtanx/reflectly/issues

---

## ✅ Success Checklist

- [ ] Ollama installed and running
- [ ] Mistral 7B model downloaded
- [ ] Python dependencies installed
- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] LLM emotion analysis working (check /api/llm-stats)
- [ ] GNN training working (after 10+ transitions)
- [ ] Memory persistence working
- [ ] Frontend visualization working

---

**You're all set! 🎉** 

Start chatting with Reflectly and watch it learn from your emotions using state-of-the-art LLM and GNN technology!
