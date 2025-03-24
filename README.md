# 🎙️ Podcast Text Extractor Pro

![Project Banner](https://thenucleargeeks.com/wp-content/uploads/2024/03/voice_txt.png?w=863&h=0&crop=1)

A powerful Streamlit application that extracts and summarizes text from podcast/video URLs using OpenAI's Whisper for transcription and Google Gemini for AI-powered summarization.

## ✨ Features

- **Audio Extraction**: Download audio from YouTube and other platforms
- **AI Transcription**: Accurate text conversion using Whisper models
- **Smart Summarization**: Gemini-powered summaries in different lengths
- **Dark Mode UI**: Sleek, eye-friendly interface
- **File Export**: Download transcripts and summaries as text files

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FFmpeg installed ([Install Guide](https://ffmpeg.org/download.html))
- Google API key (for Gemini)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/podcast-text-extractor.git

# Navigate to project directory
cd podcast-text-extractor

# Install dependencies
pip install -r requirements.txt
Running Locally
bash
Copy
streamlit run app.py
🔧 Configuration
Set your Google API key:
# In app.py
GEMINI_API_KEY = "your_api_key_here"  # Or set as environment variable
Choose your preferred settings:

Whisper model size (tiny → large)

Summary length (short → detailed)

🖥️ Usage
Enter a podcast/video URL

Click "Extract Text"

View results in three tabs:

Full Transcript

AI Summary

Statistics

Download results as needed

🌐 Deployment
Streamlit Community Cloud
Deploy to Streamlit

Push code to GitHub repository

Create new app in Streamlit Community Cloud

Set environment variables for API keys

Alternative Hosting
Hugging Face Spaces

PythonAnywhere

AWS/GCP/Azure

📂 Project Structure
podcast-text-extractor/
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── README.md              # This file


🤝 Contributing
Contributions welcome! Please follow these steps:

Fork the project

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some amazing feature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

📄 License
Distributed under the MIT License. See LICENSE for more information.

📧 Contact
Your Name - ibrahimfaisal3702@gmail.com
[Project Link: https://podcast-text-extractor.streamlit.app/]

<div align="center"> Made with ❤️ and Python </div> ```
