# 🔗 Connect Local Frontend (Cursor) to Colab Backend

This guide shows you how to run the **frontend locally in Cursor** while connecting to the **backend running in Google Colab**.

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Run Backend in Colab

1. Open `Reflectly_Colab.ipynb` in Google Colab
2. Run cells 1-6 (stops at "Start Flask Backend")
3. **Copy the backend URL** from Cell 9 output:
   ```
   🔧 Backend: https://5000-m-s-5kflgygrvmv3-c.us-west4-1.prod.colab.dev
   ```

### Step 2: Configure Frontend in Cursor

1. Open the `reflectly` project in Cursor
2. Navigate to `frontend/` directory
3. Create a `.env` file:

```bash
cd frontend
cp .env.example .env
```

4. Edit `.env` and add your Colab backend URL:

```bash
# Replace with YOUR actual Colab backend URL from Step 1
REACT_APP_BACKEND_URL=https://5000-m-s-5kflgygrvmv3-c.us-west4-1.prod.colab.dev
```

### Step 3: Install and Run Frontend

```bash
# Install dependencies (first time only)
npm install

# Start the development server
npm start
```

The frontend will open at `http://localhost:3000` and connect to your Colab backend!

---

## 📋 Detailed Instructions

### Prerequisites

- ✅ Cursor IDE installed
- ✅ Node.js 14+ installed
- ✅ Google Colab account
- ✅ Backend running in Colab (see Step 1 above)

---

### Configuration Options

#### Option 1: Environment Variable (.env file) - **Recommended**

```bash
# frontend/.env
REACT_APP_BACKEND_URL=https://5000-m-s-xxxxx.prod.colab.dev
```

**Pros:**
- Easy to change
- Doesn't get committed to git
- Works immediately

**Cons:**
- Need to restart frontend when changed
- URL changes every Colab session

#### Option 2: Hard-coded (for testing)

Edit `frontend/src/IntelligentAgentApp.js`:

```javascript
const getBackendBaseUrl = () => {
  // Hard-code your Colab URL here for testing
  return 'https://5000-m-s-xxxxx.prod.colab.dev';
};
```

**Not recommended** - only use for quick testing!

---

## 🔧 Step-by-Step Guide

### 1. Start Backend in Colab

```python
# In Google Colab, run these cells:

# Cell 1: Clone repository
# Cell 2: Install Python deps
# Cell 3: Install Ollama
# Cell 4: Start Ollama
# Cell 5: Download Mistral (wait 5-10 min)
# Cell 6: Start Flask backend ← STOP HERE

# Cell 9: Get the backend URL
```

**Important:** Note the backend URL that looks like:
```
https://5000-m-s-5kflgygrvmv3-c.us-west4-1.prod.colab.dev
```

---

### 2. Clone Repository in Cursor

```bash
# In your terminal
git clone -b colab-integration https://github.com/iNVISIBLExtanx/reflectly.git
cd reflectly/frontend
```

---

### 3. Create .env File

```bash
# Copy the example file
cp .env.example .env

# Edit .env file
# Add your Colab backend URL
```

Your `.env` file should look like:
```bash
REACT_APP_BACKEND_URL=https://5000-m-s-5kflgygrvmv3-c.us-west4-1.prod.colab.dev
```

**Critical:** Use YOUR actual URL from Colab Cell 9!

---

### 4. Install Dependencies

```bash
# In frontend/ directory
npm install
```

**First time only** - this takes 1-2 minutes

---

### 5. Start Frontend

```bash
npm start
```

**Expected output:**
```
Compiled successfully!

You can now view simple-reflectly-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.x:3000
```

The browser should automatically open to `http://localhost:3000`

---

### 6. Verify Connection

Once the frontend loads, check the status bar:

✅ **Success:**
```
✅ Backend connected: https://5000-m-s-xxxxx.prod.colab.dev
```

❌ **Error:**
```
❌ Backend not connected
Check your .env file and make sure REACT_APP_BACKEND_URL is set correctly
```

---

## 🐛 Troubleshooting

### Issue: "Backend not connected"

**Check 1: Is backend running in Colab?**
```python
# In Colab, run this cell to test:
import requests
response = requests.get('http://localhost:5000/api/health')
print(response.json())
```

**Check 2: Is the URL correct in .env?**
```bash
# frontend/.env should have the FULL URL:
REACT_APP_BACKEND_URL=https://5000-m-s-5kflgygrvmv3-c.us-west4-1.prod.colab.dev

# NOT just:
REACT_APP_BACKEND_URL=https://5000-m-s-5kflgygrvmv3-c.us-west4-1.prod.colab.dev/api  # ❌ Wrong
```

**Check 3: Restart frontend after changing .env**
```bash
# Stop frontend (Ctrl+C)
# Then restart:
npm start
```

---

### Issue: CORS Errors

If you see CORS errors in browser console:

**Solution:** The Flask backend already has CORS enabled for all origins. If you still see errors:

1. Check browser console for the actual error
2. Make sure you're using the correct Colab URL
3. Try accessing the backend directly in browser to verify it's accessible

---

### Issue: Colab URL Changed

**Every time you restart Colab**, the URL changes!

```
Old: https://5000-m-s-OLDID-c.us-west4-1.prod.colab.dev
New: https://5000-m-s-NEWID-c.us-west4-1.prod.colab.dev
                    ^^^^^^ This part changes!
```

**Solution:**
1. Get new URL from Colab Cell 9
2. Update `.env` file
3. Restart frontend (`npm start`)

---

### Issue: 502 Bad Gateway

```
Error: Could not connect to backend. 502 Bad Gateway
```

**Possible causes:**
1. Colab backend crashed - check Colab for errors
2. Colab session expired - restart from Cell 4
3. Network issue - wait a moment and try again

---

## 📊 How It Works

```
┌─────────────────────┐         ┌──────────────────────┐
│   Cursor (Local)    │         │   Google Colab       │
│                     │         │                      │
│  ┌───────────────┐  │         │  ┌────────────────┐ │
│  │  React        │  │         │  │  Flask Backend │ │
│  │  Frontend     │  │  HTTPS  │  │  Port 5000     │ │
│  │  Port 3000    │──┼────────>│  │                │ │
│  └───────────────┘  │         │  └────────┬───────┘ │
│                     │         │           │         │
└─────────────────────┘         │  ┌────────▼───────┐ │
                                │  │  Ollama        │ │
     Your Computer              │  │  Mistral 7B    │ │
                                │  └────────────────┘ │
                                │                      │
                                └──────────────────────┘
                                   Google's Servers
```

**Data Flow:**
1. You type in frontend (localhost:3000)
2. Frontend sends request to Colab backend
3. Backend processes with Ollama/Mistral
4. Response comes back to frontend
5. Frontend displays result

---

## 💡 Development Workflow

### Daily Workflow

```bash
# Morning: Start Colab
1. Open Reflectly_Colab.ipynb
2. Run cells 1-6
3. Copy new backend URL from Cell 9

# Update local frontend
4. Edit frontend/.env with new URL
5. npm start

# Development
6. Edit code in Cursor
7. Frontend auto-reloads on save
8. Test in browser
```

### Making Changes

**Frontend changes:**
- Just edit and save
- Frontend auto-reloads
- No need to restart

**Backend changes:**
- Edit in local repo
- Push to GitHub
- In Colab: Restart runtime
- Re-run cells 4-6

---

## 🎯 Best Practices

### 1. Keep Colab Tab Open
- Colab disconnects after ~90 minutes idle
- Keep the tab open to maintain session

### 2. Save Backend URL
- Create a text file with the URL
- Makes it easy to update `.env` when Colab restarts

### 3. Use .env.local for Personal Settings
```bash
# .env - committed to git (template)
REACT_APP_BACKEND_URL=http://localhost:5000

# .env.local - NOT committed (your settings)
REACT_APP_BACKEND_URL=https://5000-m-s-xxxxx.prod.colab.dev
```

`.env.local` overrides `.env` and won't be committed!

---

## 📝 Environment Variable Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_BACKEND_URL` | `http://localhost:5000` | Full backend URL (no trailing /api) |

**Examples:**

```bash
# Local backend
REACT_APP_BACKEND_URL=http://localhost:5000

# Colab backend
REACT_APP_BACKEND_URL=https://5000-m-s-5kflgygrvmv3-c.us-west4-1.prod.colab.dev

# Different port
REACT_APP_BACKEND_URL=http://localhost:8000
```

**Important:** 
- No trailing slash
- No `/api` at the end
- Must start with `http://` or `https://`

---

## 🚀 Quick Commands Reference

```bash
# First time setup
cd frontend
cp .env.example .env
# Edit .env with your Colab URL
npm install
npm start

# Daily usage
# 1. Get new Colab URL
# 2. Update .env
npm start

# Restart after .env change
Ctrl+C  # Stop
npm start  # Start

# Clean install (if issues)
rm -rf node_modules package-lock.json
npm install
npm start
```

---

## ✅ Checklist

Before starting development:

- [ ] Colab backend is running (cells 1-6 complete)
- [ ] Backend URL copied from Colab Cell 9
- [ ] `.env` file exists in `frontend/`
- [ ] `REACT_APP_BACKEND_URL` is set correctly in `.env`
- [ ] Dependencies installed (`npm install`)
- [ ] Frontend started (`npm start`)
- [ ] Status shows "✅ Backend connected"

---

## 🎉 Success!

Once everything is set up:

1. **Frontend** runs at `http://localhost:3000` in your browser
2. **Backend** runs in Google Colab
3. **Everything works** just like running both locally!

You can now:
- Edit frontend code in Cursor
- See changes instantly
- Full app functionality
- No Colab limitations on frontend

---

## 💰 Cost Comparison

| Setup | Cost | Pros | Cons |
|-------|------|------|------|
| Both Local | Free | Unlimited time | Requires powerful computer |
| Backend in Colab | Free | No local resources needed | 12hr session limit |
| Both in Colab | Free | Zero setup | Can't edit code easily |

**Recommended:** Frontend local + Backend in Colab (this guide!)

---

## 📞 Need Help?

1. Check [Troubleshooting](#troubleshooting) section
2. Verify backend is accessible: Visit the backend URL in browser + `/api/health`
3. Check browser console for errors (F12 → Console tab)
4. Open an issue on GitHub with error details

---

**Happy coding! 🎊**
