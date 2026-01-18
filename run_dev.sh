#!/bin/bash
# Development server script - Python equivalent van "npm run dev"

echo "🚀 Starting Music Analyzer Development Server..."
echo ""

# Check of dependencies geïnstalleerd zijn
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask niet gevonden. Installeer dependencies eerst:"
    echo "   pip3 install -r requirements.txt"
    echo ""
    exit 1
fi

# Start de Flask app
echo "📂 Project directory: $(pwd)"
echo "🌐 Server starten op http://localhost:5001"
echo ""
echo "Druk op Ctrl+C om te stoppen"
echo "=" * 50
echo ""

python3 app.py
