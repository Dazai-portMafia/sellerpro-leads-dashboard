#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# setup.sh — one-time setup for celebro-leads-dashboard
# Run this from: ~/Desktop/celebro-leads-dashboard/
# ──────────────────────────────────────────────────────────────────────────────

set -e

echo "→ Setting up celebro-leads-dashboard..."

# 1. Create the .github/workflows directory and move the workflow file
mkdir -p .github/workflows
mv fetch-data-workflow.yml .github/workflows/fetch-data.yml 2>/dev/null || true

# 2. Create a placeholder data directory
mkdir -p data
touch data/.gitkeep

# 3. Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.DS_Store
EOF

# 4. Initialise git and push to GitHub
git init
git add -A
git commit -m "feat: initial Celebro Pipeline dashboard with GitHub Pages + daily GSheets sync"
git branch -M main
git remote add origin https://github.com/Dazai-portMafia/celebro-leads-dashboard.git
git push -u origin main

echo ""
echo "✅ Done! Now go to GitHub to enable GitHub Pages:"
echo "   https://github.com/Dazai-portMafia/celebro-leads-dashboard/settings/pages"
echo "   → Source: Deploy from branch → Branch: main → / (root) → Save"
echo ""
echo "   Your live URL will be:"
echo "   https://dazai-portmafia.github.io/celebro-leads-dashboard/"
