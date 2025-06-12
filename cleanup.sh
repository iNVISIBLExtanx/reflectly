#!/bin/bash

echo "🧹 Cleaning up unnecessary files from intelligent-agent-memory branch"
echo "===================================================================="

# Confirm before deletion
read -p "⚠️  This will delete all unnecessary files. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled"
    exit 1
fi

echo "🗑️  Removing unnecessary files..."

# Remove old startup scripts
echo "Removing old startup scripts..."
rm -f start-simple.sh
rm -f start-backend.sh
rm -f start-frontend.sh
rm -f start-agent.sh
rm -f start-intelligent-agent.sh

# Remove test scripts
echo "Removing test scripts..."
rm -f test-backend.sh

# Remove old documentation
echo "Removing old documentation..."
rm -f TROUBLESHOOTING.md

# Remove old backend files (keep only intelligent_agent.py)
echo "Cleaning backend directory..."
rm -f backend/simple_app.py
rm -f backend/simple_requirements.txt
rm -f backend/app.py
rm -f backend/requirements.txt

# Remove old frontend files (keep only the intelligent agent files)
echo "Cleaning frontend directory..."
rm -f frontend/src/SimpleAIDemo.js

# Remove Docker files
echo "Removing Docker files..."
rm -f docker-compose.yml
rm -f backend/Dockerfile
rm -f frontend/Dockerfile

# Remove cleanup scripts
echo "Removing cleanup scripts..."
rm -f cleanup-all.sh
rm -f cleanup-for-ai.sh

# Remove repomix files
echo "Removing repomix files..."
rm -f repomix-output.md
rm -f .repomixignore
rm -f repomix.config.json

# Remove documentation that's not needed
echo "Removing old documentation..."
rm -f README_BIGDATA.md
rm -rf docs/

# Remove big data components
echo "Removing big data components..."
rm -rf spark/
rm -f run_spark_jobs.sh
rm -f copy_spark_jobs.sh

# Remove complex backend components
echo "Removing complex backend components..."
rm -rf backend/models/
rm -rf backend/services/
rm -f backend/user_management.py
rm -f backend/admin_viewer.py

# Remove complex frontend components
echo "Removing complex frontend components..."
rm -rf frontend/src/pages/
rm -rf frontend/src/components/
rm -rf frontend/src/context/
rm -rf frontend/src/utils/

# Clean up any Python cache
echo "Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Clean up node modules (will be reinstalled when needed)
echo "Cleaning node modules..."
rm -rf frontend/node_modules

# Clean up Python virtual environment (will be recreated when needed)
echo "Cleaning Python virtual environment..."
rm -rf backend/venv

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📁 Remaining files:"
echo "├── backend/"
echo "│   └── intelligent_agent.py      # 🤖 Main AI backend"
echo "├── frontend/"
echo "│   ├── src/"
echo "│   │   ├── IntelligentAgentApp.js # 🗺️ Memory map UI"
echo "│   │   ├── App.js                 # ⚛️ React wrapper"
echo "│   │   ├── index.js               # ⚛️ React entry"
echo "│   │   └── index.css              # 🎨 Basic styles"
echo "│   ├── public/index.html          # 📄 HTML template"
echo "│   └── package.json               # 📦 React dependencies"
echo "├── start.sh                       # 🚀 Single startup script"
echo "├── cleanup.sh                     # 🧹 This cleanup script"
echo "└── README.md                      # 📖 Documentation"
echo ""
echo "🎯 Now you have a clean, focused intelligent agent!"
echo "🚀 Run: chmod +x start.sh && ./start.sh"