"""
LLM API Script

This script configures and initializes a generative AI model using the Google Generative AI library.
"""

import os
import google.generativeai as genai

api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
