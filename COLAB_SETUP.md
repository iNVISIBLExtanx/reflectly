# Reflectly - Google Colab Setup

Run Reflectly entirely in Google Colab without ngrok! This setup allows you to run both the backend and frontend locally within Colab, accessing the app directly through Colab's interface.

## 🚀 Quick Start

Copy the cells below into a new Google Colab notebook and run them in order.

---

## 📋 **CELL 1: Clone Repository**

```python
# ================================================================
# Clone Private Repository using Colab Secrets
# ================================================================

from google.colab import userdata
import os

print("🔐 GitHub Private Repository Setup")
print("="*60)

try:
    # Get credentials from Colab secrets
    github_username = userdata.get('GITHUB_USERNAME')
    github_token = userdata.get('GITHUB_TOKEN')
    
    print(f"✅ Found credentials for user: {github_username}")
    
except Exception as e:
    print("❌ Could not find GitHub secrets!")
    print("\n📝 To add secrets:")
    print("   1. Click 🔑 (key icon) in left sidebar")
    print("   2. Add: GITHUB_USERNAME (your GitHub username)")
    print("   3. Add: GITHUB_TOKEN (your GitHub Personal Access Token)")
    print("   4. Enable notebook access for both secrets")
    print()
    raise e

print("\n📦 Cloning repository...")

# Clone with authentication
repo_url = f"https://{github_username}:{github_token}@github.com/iNVISIBLExtanx/reflectly.git"

# Clean up any existing directory
!rm -rf /content/reflectly 2>/dev/null || true

# Clone the repository
%cd /content
!git clone -q {repo_url}

print("✅ Repository cloned!")

# Switch to the colab-integration branch
%cd reflectly
!git checkout colab-integration

print("\n🎉 Repository ready!")
print("\n📁 Project structure:")
!ls -la

# Clear sensitive variables
del github_token
del repo_url

print("\n✅ CELL 1 COMPLETE - Proceed to Cell 2")
```

---

## 📋 **CELL 2: Install Python Dependencies**

```python
# ================================================================
# Install Python Dependencies
# ================================================================

print("📦 Installing Python dependencies...")
print("="*60)

# Install backend requirements
print("\n🔧 Installing backend dependencies...")
!pip install -q flask flask-cors ollama numpy scipy pandas python-dateutil

# Install PyTorch and PyTorch Geometric for GNN
print("\n🔥 Installing PyTorch and PyTorch Geometric...")
!pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
!pip install -q torch-geometric

print("\n✅ All Python dependencies installed!")

# Verify installations
print("\n📋 Verifying installations:")
import flask
import flask_cors
import ollama
import torch
import torch_geometric

print(f"   ✅ Flask: {flask.__version__}")
print(f"   ✅ Flask-CORS: Installed")
print(f"   ✅ PyTorch: {torch.__version__}")
print(f"   ✅ Ollama: Installed")
print(f"   ✅ PyTorch Geometric: Installed")

print("\n✅ CELL 2 COMPLETE - Proceed to Cell 3")
```

---

## 📋 **CELL 3: Install Ollama**

```python
# ================================================================
# Install Ollama
# ================================================================

print("🤖 Installing Ollama...")
print("="*60)

# Install Ollama
!curl -fsSL https://ollama.ai/install.sh | sh

print("\n✅ Ollama installed!")

# Verify installation
!which ollama
!ollama --version

print("\n✅ CELL 3 COMPLETE - Proceed to Cell 4")
```

---

## 📋 **CELL 4: Start Ollama Server**

```python
# ================================================================
# Start Ollama Server in Background
# ================================================================

import subprocess
import time
import os

print("🚀 Starting Ollama service...")
print("="*60)

# Kill any existing Ollama processes
!pkill -9 ollama 2>/dev/null || true
time.sleep(2)

# Start Ollama server in background
ollama_process = subprocess.Popen(
    ['ollama', 'serve'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    preexec_fn=os.setpgrp
)

# Wait for Ollama to start
print("⏳ Waiting for Ollama to start...")
time.sleep(5)

# Verify it's running
result = !ps aux | grep "ollama serve" | grep -v grep
if result:
    print("✅ Ollama service is running!")
    print(f"   Process ID: {ollama_process.pid}")
else:
    print("⚠️  Ollama might not be running. Check errors above.")

print("\n✅ CELL 4 COMPLETE - Proceed to Cell 5")
```

---

## 📋 **CELL 5: Download Mistral Model**

```python
# ================================================================
# Download Mistral 7B Model
# ================================================================

print("📥 Downloading Mistral 7B model...")
print("⏳ This takes 5-10 minutes (4.1 GB download)...")
print("="*60)

# Pull the model
!ollama pull mistral:7b

print("\n✅ Model downloaded successfully!")
print("\n📋 Available models:")
!ollama list

print("\n✅ CELL 5 COMPLETE - Proceed to Cell 6")
```

---

## 📋 **CELL 6: Start Flask Backend**

```python
# ================================================================
# Start Flask Backend Server
# ================================================================

import subprocess
import time
import os
import socket

print("🌐 Starting Flask backend...")
print("="*60)

# Verify backend files exist
backend_path = '/content/reflectly/backend'
if not os.path.exists(f'{backend_path}/intelligent_agent.py'):
    print("❌ ERROR: Backend files not found!")
    !ls -la {backend_path}
    raise FileNotFoundError("Backend files missing")
else:
    print(f"✅ Backend files found at {backend_path}")

# Kill any existing Flask processes
!pkill -9 -f intelligent_agent.py 2>/dev/null || true
time.sleep(2)

print("\n🚀 Starting backend process...")

# Create log file
backend_log = open('/tmp/backend.log', 'w')

# Start backend in background
backend_process = subprocess.Popen(
    ['python', 'intelligent_agent.py'],
    cwd=backend_path,
    stdout=backend_log,
    stderr=subprocess.STDOUT,
    preexec_fn=os.setpgrp
)

# Wait for backend to start
print("⏳ Waiting for backend to initialize...")
time.sleep(8)

# Check if process is running
if backend_process.poll() is None:
    print(f"✅ Backend process running (PID: {backend_process.pid})")
    
    # Check if port is listening
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5000))
    sock.close()
    
    if result == 0:
        print("✅ Backend is listening on port 5000!")
        print("\n🔥 Backend is ready!")
        
        # Quick health check
        import requests
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=5)
            if response.ok:
                print(f"✅ Health check passed: {response.json()}")
        except Exception as e:
            print(f"⚠️  Health check failed: {e}")
    else:
        print("⚠️  Backend started but not responding on port 5000")
        print("\n📋 Checking logs...")
        !tail -30 /tmp/backend.log
else:
    print(f"❌ Backend exited with code: {backend_process.poll()}")
    print("\n📋 Error logs:")
    !cat /tmp/backend.log
    raise RuntimeError("Backend failed to start")

print("\n✅ CELL 6 COMPLETE - Proceed to Cell 7")
```

---

## 📋 **CELL 7: Install Frontend Dependencies**

```python
# ================================================================
# Install Frontend Dependencies (Node.js & npm)
# ================================================================

print("📦 Installing Node.js and npm...")
print("="*60)

# Install Node.js 18.x
!curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
!apt-get install -y nodejs

print("\n✅ Node.js installed!")
!node --version
!npm --version

# Install frontend dependencies
print("\n📦 Installing frontend dependencies...")
%cd /content/reflectly/frontend
!npm install

print("\n✅ Frontend dependencies installed!")
print("\n✅ CELL 7 COMPLETE - Proceed to Cell 8")
```

---

## 📋 **CELL 8: Start Frontend Development Server**

```python
# ================================================================
# Start React Frontend Server
# ================================================================

import subprocess
import time
import socket

print("🎨 Starting React frontend...")
print("="*60)

# Kill any existing npm processes
!pkill -9 -f "npm start" 2>/dev/null || true
!pkill -9 -f "react-scripts" 2>/dev/null || true
time.sleep(2)

print("\n🚀 Starting frontend development server...")
print("⏳ This may take 30-60 seconds to compile...")

# Start frontend in background
frontend_log = open('/tmp/frontend.log', 'w')
frontend_process = subprocess.Popen(
    ['npm', 'start'],
    cwd='/content/reflectly/frontend',
    stdout=frontend_log,
    stderr=subprocess.STDOUT,
    preexec_fn=os.setpgrp,
    env={**os.environ, 'PORT': '3000', 'BROWSER': 'none'}
)

# Wait for frontend to compile and start
print("⏳ Compiling React app...")
time.sleep(45)  # React needs time to compile

# Check if port is listening
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 3000))
sock.close()

if result == 0:
    print("✅ Frontend is running on port 3000!")
    print(f"   Process ID: {frontend_process.pid}")
else:
    print("⚠️  Frontend not responding yet, checking logs...")
    !tail -50 /tmp/frontend.log

print("\n✅ CELL 8 COMPLETE - Proceed to Cell 9")
```

---

## 📋 **CELL 9: Access the Application**

```python
# ================================================================
# Access Application via Colab Port Forwarding
# ================================================================

from google.colab.output import eval_js

print("╔══════════════════════════════════════════════════════════╗")
print("║          🎉 Reflectly is Running in Colab!              ║")
print("╚══════════════════════════════════════════════════════════╝")
print()

# Get the Colab URLs for port forwarding
print("🌐 Access your application:")
print()

# Frontend (React app)
frontend_url = eval_js("google.colab.kernel.proxyPort(3000)")
print(f"📱 Frontend (React UI): {frontend_url}")
print()

# Backend API
backend_url = eval_js("google.colab.kernel.proxyPort(5000)")
print(f"🔧 Backend API: {backend_url}/api/health")
print()

print("="*60)
print("\n💡 HOW TO USE:")
print("   1. Click the Frontend URL above to open the app")
print("   2. The app will load in a new tab")
print("   3. Start chatting with Reflectly!")
print()
print("⚠️  IMPORTANT:")
print("   • Keep this Colab tab open while using the app")
print("   • If you refresh Colab, you'll need to restart from Cell 4")
print("   • URLs expire when you close this notebook")
print()

# Test backend
import requests
try:
    response = requests.get('http://localhost:5000/api/health', timeout=5)
    if response.ok:
        print("✅ Backend Status:", response.json())
except Exception as e:
    print(f"❌ Backend Error: {e}")

print("\n🎊 ALL SETUP COMPLETE! Enjoy using Reflectly!")
```

---

## 📋 **OPTIONAL: Monitor Logs**

```python
# ================================================================
# Monitor Application Logs (Optional)
# ================================================================

import time

print("📋 Monitoring application logs...")
print("="*60)
print("\n🔧 BACKEND LOGS:")
!tail -30 /tmp/backend.log

print("\n" + "="*60)
print("\n🎨 FRONTEND LOGS:")
!tail -30 /tmp/frontend.log

print("\n" + "="*60)
print("\n💡 To see live logs, run:")
print("   !tail -f /tmp/backend.log    # Backend")
print("   !tail -f /tmp/frontend.log   # Frontend")
```

---

## 📋 **OPTIONAL: Test Backend API**

```python
# ================================================================
# Test Backend API Endpoints
# ================================================================

import requests
import json

print("🧪 Testing Backend API...")
print("="*60)

BASE_URL = "http://localhost:5000/api"

# Test 1: Health Check
print("\n1️⃣ Health Check:")
try:
    response = requests.get(f'{BASE_URL}/health', timeout=5)
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Emotion Analysis
print("\n2️⃣ Emotion Analysis:")
try:
    test_data = {
        "text": "I'm feeling really happy and excited about my new project!",
        "user_id": "colab_test_user"
    }
    response = requests.post(
        f'{BASE_URL}/process-input',
        json=test_data,
        timeout=30
    )
    result = response.json()
    print(f"   Emotion: {result.get('emotion')}")
    print(f"   Type: {result.get('type')}")
    print(f"   Algorithm: {result.get('algorithm_used')}")
    print(f"   Message: {result.get('message')[:100]}...")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Memory Stats
print("\n3️⃣ Memory Statistics:")
try:
    response = requests.get(f'{BASE_URL}/memory-stats', timeout=5)
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ All tests complete!")
```

---

## 🔧 Troubleshooting

### Backend won't start?
```python
# Check backend logs
!cat /tmp/backend.log

# Restart backend
!pkill -9 -f intelligent_agent.py
# Then re-run Cell 6
```

### Frontend won't start?
```python
# Check frontend logs
!cat /tmp/frontend.log

# Clear and reinstall
%cd /content/reflectly/frontend
!rm -rf node_modules package-lock.json
!npm install
# Then re-run Cell 8
```

### Can't connect to Ollama?
```python
# Check if Ollama is running
!ps aux | grep ollama

# Restart Ollama
!pkill -9 ollama
# Then re-run Cell 4
```

---

## 📝 Notes

- **Session Duration**: Colab free tier sessions last ~12 hours or ~90 minutes idle
- **Model Persistence**: The Mistral model will be cached if you reconnect within a few hours
- **Data Persistence**: All data is lost when the runtime disconnects
- **Port Forwarding**: Colab automatically handles port forwarding for you
- **No ngrok needed**: Everything runs locally within Colab's environment

---

## 🎯 After Setup

Once all cells are running:

1. ✅ Backend running on port 5000
2. ✅ Frontend running on port 3000  
3. ✅ Ollama with Mistral model loaded
4. ✅ Access via Colab's port forwarding URLs

**You can now use Reflectly directly in your browser!**
