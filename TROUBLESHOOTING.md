# 🔧 Troubleshooting Guide - 403 Forbidden Error

## 🚨 **Problem: 403 Forbidden Error**

When you type input, you see:
```
POST http://localhost:3000/api/process-input 403 (Forbidden)
```

## 🎯 **Quick Fix (Most Common)**

### **Step 1: Make sure backend is running**
```bash
# Option 1: Run backend only
./start-agent.sh

# Option 2: Run both frontend and backend
./start-intelligent-agent.sh

# Option 3: Manual backend start
cd backend
python3 intelligent_agent.py
```

### **Step 2: Test backend directly**
```bash
# Make test script executable and run it
chmod +x test-backend.sh
./test-backend.sh
```

**Expected output:**
```json
{
  "status": "healthy",
  "service": "Intelligent Agent with Memory Map"
}
```

### **Step 3: Check frontend connection**
Open browser console (F12) and look for:
- ✅ "Backend connected" message
- ✅ Green status indicator in the UI

## 🔍 **Detailed Diagnosis**

### **Check 1: Is backend running?**
```bash
curl http://localhost:5000/api/health
```

**If this fails:**
- Backend is not running
- **Solution**: Start backend with `./start-agent.sh`

### **Check 2: CORS issues?**
```bash
curl -X POST http://localhost:5000/api/process-input \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "user_id": "test"}'
```

**If this works but browser fails:**
- CORS configuration issue
- **Solution**: Check backend CORS settings

### **Check 3: Port conflicts?**
```bash
# Check what's running on port 5000
lsof -i :5000

# Check what's running on port 3000  
lsof -i :3000
```

**If wrong services are running:**
- Kill conflicting processes
- Restart with correct scripts

## 🛠️ **Step-by-Step Solution**

### **1. Stop everything**
```bash
# Kill any running processes
pkill -f "intelligent_agent.py"
pkill -f "npm start"
pkill -f "react-scripts"
```

### **2. Start backend first**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install Flask Flask-CORS
python3 intelligent_agent.py
```

**Wait for this message:**
```
🤖 Starting Intelligent Agent with Memory Map
📡 API: http://localhost:5000
```

### **3. Test backend works**
```bash
# In new terminal
curl http://localhost:5000/api/health
```

**Should see:**
```json
{
  "status": "healthy",
  "service": "Intelligent Agent with Memory Map"
}
```

### **4. Start frontend**
```bash
# In new terminal
cd frontend
npm start
```

### **5. Check browser**
- Go to http://localhost:3000
- Look for **green "Backend connected"** status
- Try typing: "I'm feeling happy today!"

## ⚠️ **Common Issues & Solutions**

### **Issue 1: Backend won't start**
```bash
# Error: ModuleNotFoundError: No module named 'flask'
pip install Flask Flask-CORS

# Error: Permission denied
chmod +x start-agent.sh

# Error: Port already in use
lsof -i :5000
kill -9 <PID>
```

### **Issue 2: Frontend shows red status**
- Check browser console for exact error
- Make sure backend is running first
- Try refreshing the page

### **Issue 3: CORS still blocked**
- Make sure you're using the updated frontend code
- Clear browser cache (Ctrl+Shift+R)
- Check backend console for CORS messages

### **Issue 4: Proxy not working**
The updated frontend tries direct connection first, so proxy issues are avoided.

## 🧪 **Test Commands**

### **Test 1: Backend Health**
```bash
curl http://localhost:5000/api/health
```

### **Test 2: Emotion Processing**
```bash
curl -X POST http://localhost:5000/api/process-input \
  -H "Content-Type: application/json" \
  -d '{"text": "I am happy", "user_id": "test"}'
```

### **Test 3: Memory Map**
```bash
curl http://localhost:5000/api/memory-map
```

## 📋 **Checklist for Working System**

- [ ] Backend running on port 5000
- [ ] Frontend running on port 3000  
- [ ] Green "Backend connected" status in UI
- [ ] Can type text and get response
- [ ] Memory map shows in right panel
- [ ] No 403 or CORS errors in console

## 🚀 **Quick Reset (Nuclear Option)**

If nothing works, start completely fresh:

```bash
# 1. Kill everything
pkill -f python
pkill -f node
pkill -f react

# 2. Clean start backend
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install Flask Flask-CORS
python3 intelligent_agent.py

# 3. Clean start frontend (new terminal)
cd frontend
rm -rf node_modules
npm install
npm start

# 4. Test
curl http://localhost:5000/api/health
```

## 🆘 **Still Not Working?**

### **Check browser console (F12) for:**
- Network errors
- CORS errors  
- JavaScript errors

### **Check backend console for:**
- Flask startup messages
- CORS configuration
- Request logs

### **Common error messages:**
- `EADDRINUSE`: Port already in use
- `Connection refused`: Backend not running
- `CORS error`: CORS misconfiguration
- `403 Forbidden`: Permission/routing issue

## ✅ **Success Indicators**

**Backend console should show:**
```
🤖 Starting Intelligent Agent with Memory Map
🧠 Features: Emotion Analysis + A* Search + Learning
📡 API: http://localhost:5000
✅ CORS enabled for http://localhost:3000
```

**Frontend should show:**
- ✅ Green "Backend connected" status
- 🗺️ Memory map visualization (even if empty)
- 💬 Conversation interface ready for input

**Browser console should show:**
```
✅ Backend connected: {status: "healthy", service: "Intelligent Agent with Memory Map"}
```

---

**After following this guide, your intelligent agent should work correctly! The 403 error is almost always caused by the backend not running or CORS misconfiguration.** 🔧✨
