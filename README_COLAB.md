# Reflectly - Google Colab Integration

Run Reflectly entirely in Google Colab without needing to install anything locally! No ngrok required.

## 🚀 Quick Start

### Option 1: Use the Ready-Made Notebook

1. **Download the notebook:**
   - Go to: [Reflectly_Colab.ipynb](https://github.com/iNVISIBLExtanx/reflectly/blob/colab-integration/Reflectly_Colab.ipynb)
   - Click "Raw" button
   - Save the file to your computer

2. **Upload to Google Colab:**
   - Go to [Google Colab](https://colab.research.google.com/)
   - Click "File" → "Upload notebook"
   - Upload the `Reflectly_Colab.ipynb` file

3. **Add GitHub credentials:**
   - Click the 🔑 key icon in Colab's left sidebar
   - Add `GITHUB_USERNAME` (your GitHub username)
   - Add `GITHUB_TOKEN` (your [GitHub Personal Access Token](https://github.com/settings/tokens))
   - Enable notebook access for both secrets

4. **Run it:**
   - Click "Runtime" → "Run all"
   - Wait 10-15 minutes for initial setup
   - Click the frontend URL when it appears!

### Option 2: Copy-Paste Cells

See [COLAB_SETUP.md](./COLAB_SETUP.md) for detailed cell-by-cell instructions.

## 📖 How It Works

### Architecture

```
┌─────────────────────────────────────────┐
│         Google Colab VM                 │
│                                         │
│  ┌─────────────┐    ┌───────────────┐  │
│  │   Ollama    │◄───┤ Flask Backend │  │
│  │  (Mistral)  │    │   Port 5000   │  │
│  └─────────────┘    └───────┬───────┘  │
│                             │          │
│                     ┌───────▼───────┐  │
│                     │ React Frontend│  │
│                     │   Port 3000   │  │
│                     └───────────────┘  │
└─────────────────────────────────────────┘
                     │
                     ▼
           Colab Port Forwarding
                     │
                     ▼
              Your Browser
```

### What Happens When You Run

1. **Cell 1-3**: Sets up the environment
   - Clones the repository
   - Installs Python dependencies
   - Installs Ollama

2. **Cell 4-5**: Prepares the AI model
   - Starts Ollama server
   - Downloads Mistral 7B (4.1 GB, takes 5-10 min)

3. **Cell 6**: Starts the backend
   - Flask API server on port 5000
   - Handles emotion analysis and memory

4. **Cell 7-8**: Starts the frontend
   - Installs Node.js
   - Builds and runs React app on port 3000

5. **Cell 9**: Provides access URLs
   - Uses Colab's built-in port forwarding
   - No ngrok needed!

## 🔧 Technical Details

### Port Forwarding

Google Colab automatically forwards ports to public URLs:

```python
from google.colab.output import eval_js

# Get public URL for frontend (port 3000)
frontend_url = eval_js("google.colab.kernel.proxyPort(3000)")

# Get public URL for backend (port 5000)
backend_url = eval_js("google.colab.kernel.proxyPort(5000)")
```

These URLs are temporary and expire when you close the notebook.

### Running Without Interruption

- **Session Duration**: ~12 hours (or 90 min idle on free tier)
- **Model Caching**: Mistral model persists if you reconnect quickly
- **Data Persistence**: All app data is lost when runtime disconnects

### Resource Usage

- **RAM**: ~6-8 GB (Colab free tier has 12 GB)
- **Disk**: ~5 GB (mostly for Mistral model)
- **CPU**: Moderate (no GPU needed)

## 🐛 Troubleshooting

### Backend won't start

```python
# Check logs
!cat /tmp/backend.log

# Restart
!pkill -9 -f intelligent_agent.py
# Then re-run Cell 6
```

### Frontend won't load

```python
# Check logs
!cat /tmp/frontend.log

# Clear and rebuild
%cd /content/reflectly/frontend
!rm -rf node_modules
!npm install
# Then re-run Cell 8
```

### Ollama connection failed

```python
# Check if running
!ps aux | grep ollama

# Restart
!pkill -9 ollama
# Then re-run Cell 4
```

### Port forwarding not working

Just re-run Cell 9 to get fresh URLs.

## 📊 What Gets Installed

### Python Packages
- `flask` - Web framework for backend
- `flask-cors` - CORS support
- `ollama` - LLM integration
- `torch` - PyTorch for neural networks
- `torch-geometric` - Graph neural networks
- `numpy`, `scipy`, `pandas` - Data processing

### System Tools
- Ollama - LLM runtime
- Node.js 18.x - JavaScript runtime
- npm packages - React dependencies

### AI Model
- Mistral 7B - Language model (4.1 GB)

## 🎯 Development Workflow

### Making Changes

1. Edit code in the repository
2. Commit and push to `colab-integration` branch
3. Restart Colab runtime (Runtime → Restart)
4. Run all cells again

### Testing Changes

```python
# After making changes to backend
!pkill -9 -f intelligent_agent.py
# Re-run Cell 6

# After making changes to frontend
%cd /content/reflectly/frontend
!npm start
# Wait for rebuild
```

## 💡 Tips

- **Use GPU**: Not needed for this app, but available via Runtime → Change runtime type
- **Save Outputs**: Download any data before closing Colab
- **Monitor Resources**: Click "RAM" and "Disk" in top-right to check usage
- **Reconnect**: If disconnected, re-run from Cell 4 (Ollama) onwards

## 🚫 What's NOT Included

- ❌ ngrok - Using Colab's native port forwarding instead
- ❌ Docker - Not needed in Colab environment
- ❌ Local setup scripts - All handled in notebook cells

## 📝 Notes

### Differences from Local Setup

| Feature | Local | Colab |
|---------|-------|-------|
| Installation | Manual setup | Automated in notebook |
| Access | localhost only | Public URL via Colab |
| Persistence | Data saved locally | Lost on disconnect |
| Resources | Your machine | Google's servers |
| Cost | Electricity only | Free (with limits) |

### Colab Limitations

- Free tier: 12 hours max runtime
- Idle timeout: ~90 minutes
- GPU access: Limited (but we don't need it)
- Storage: Temporary, cleared on disconnect

### When to Use Colab vs Local

**Use Colab when:**
- Testing the app quickly
- No local compute power
- Sharing with others temporarily
- Learning/experimenting

**Use Local when:**
- Production deployment
- Long-term data storage
- Continuous availability
- Custom configurations

## 🔗 Related Files

- [Reflectly_Colab.ipynb](./Reflectly_Colab.ipynb) - Ready-to-use notebook
- [COLAB_SETUP.md](./COLAB_SETUP.md) - Detailed setup guide
- [backend/](./backend/) - Flask backend code
- [frontend/](./frontend/) - React frontend code

## 🎉 Success Checklist

After running all cells, you should have:

- ✅ Ollama server running
- ✅ Mistral 7B model loaded
- ✅ Backend API responding on port 5000
- ✅ Frontend UI accessible via Colab URL
- ✅ Emotion analysis working
- ✅ Memory graph functioning

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the error logs (`/tmp/backend.log`, `/tmp/frontend.log`)
3. Open an issue on GitHub with error details

---

**Happy coding! 🚀**
