#!/usr/bin/env python3
"""
Dual-AI Detective Game - Main Entry Point

This is the main entry point for the Dual-AI Detective Game backend.
The actual FastAPI server is located in backend/server.py

This file provides a unified entry point for the application.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    # Import and run the FastAPI server
    from backend.server import app
    import uvicorn
    
    print("🕵️ Starting Dual-AI Detective Game Backend...")
    print("🤖 Dual-AI System: OpenAI GPT-4 + Anthropic Claude")
    print("🎨 Visual Generation: FAL.AI")
    print("🌐 Server: FastAPI")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")