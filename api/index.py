"""
Vercel serverless function wrapper voor Flask app
"""
import sys
import os

# Voeg de root directory toe aan het Python pad
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app

# Export de Flask app voor Vercel
handler = app

