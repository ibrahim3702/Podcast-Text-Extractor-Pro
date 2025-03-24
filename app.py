import streamlit as st
import os
import tempfile
import yt_dlp as youtube_dl
import whisper
from pydub import AudioSegment
import google.generativeai as genai
from datetime import datetime
from functools import lru_cache

# Set page config
st.set_page_config(
    page_title="Podcast Text Extractor Pro",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Gemini
# FFmpeg configuration
FFMPEG_PATH = "/usr/bin/ffmpeg"  # Standard path in Streamlit Cloud

# Configure pydub to use the correct FFmpeg path
AudioSegment.converter = FFMPEG_PATH
AudioSegment.ffmpeg = FFMPEG_PATH
AudioSegment.ffprobe = f"{FFMPEG_PATH}probe"  # For ffprobe
# Replace your Gemini initialization with this bulletproof version:

# Method 1: Try Streamlit secrets first
GEMINI_API_KEY = None

if 'GOOGLE_API_KEY' in st.secrets:
    GEMINI_API_KEY = st.secrets['GOOGLE_API_KEY']
    st.success("Loaded API key from Streamlit secrets")
else:
    # Method 2: Try environment variables
    import os
    GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')
    if GEMINI_API_KEY:
        st.info("Loaded API key from environment variables")
    else:
        # Method 3: Direct input (for debugging)
        st.warning("API key not found in secrets or environment variables")
        GEMINI_API_KEY = st.text_input("Enter Google API Key (temporary solution):")
        if not GEMINI_API_KEY:
            st.error("API key required - configure secrets or enter manually")
            st.stop()

# Configure Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    st.balloons()  # Visual confirmation of successful load
except Exception as e:
    st.error(f"Gemini configuration failed: {str(e)}")
    st.stop()
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Custom CSS for dark theme
st.markdown("""
<style>
    /* Main background */
    .main {
        background-color: rgb(14, 17, 23);
        color: #ffffff;
    }
    
    /* Text areas */
    .stTextArea textarea, .stTextArea [data-baseweb=base-input] {
        background-color: rgb(14, 17, 23) !important;
        color: #ffffff !important;
        border: 1px solid #444;
    }
    
    /* Text input */
    .stTextInput input {
        background-color: rgb(14, 17, 23) !important;
        color: #ffffff !important;
        border: 1px solid #444;
    }
    
    /* Select boxes */
    .stSelectbox select {
        background-color: rgb(14, 17, 23) !important;
        color: #ffffff !important;
        border: 1px solid #444;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgb(14, 17, 23);
        border-bottom: 1px solid #444;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #ffffff !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
        border: none;
    }
    
    .stButton>button:hover {
        background-color: #45a049;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background-color: rgba(14, 17, 23, 0.7);
        border: 1px solid #444;
        border-radius: 5px;
        padding: 10px;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: rgb(20, 23, 30);
        color: #ffffff;
    }
    
    /* Footer */
    .footer {
        font-size: 0.8rem;
        color: #aaa;
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("🎙️ Podcast Text Extractor Pro")
st.markdown("""
<div style='background-color: rgba(20, 23, 30, 0.7); padding: 15px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #444'>
    Extract and summarize text from podcasts or videos. Supports YouTube and other platforms.
    The audio is transcribed using OpenAI's Whisper model and summarized with Google Gemini.
</div>
""", unsafe_allow_html=True)

# Sidebar for settings (rest of your existing sidebar code remains the same)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2965/2965300.png", width=100)
    st.header("Settings")
    
    model_size = st.selectbox(
        "Whisper Model Size",
        ["tiny", "base", "small", "medium", "large"],
        index=2,
        help="Larger models are more accurate but slower"
    )
    
    summary_length = st.selectbox(
        "Summary Length",
        ["Short (1-2 sentences)", "Medium (paragraph)", "Detailed (multiple paragraphs)"],
        index=1
    )
    
    st.markdown("---")
    st.markdown("""
    **How to use:**
    1. Enter a podcast/video URL
    2. Click 'Extract Text'
    3. View transcript and summary
    4. Download results
    """)
    st.markdown("---")
    st.markdown("""
    **Note:** 
    - First run may take longer to download models
    - Large videos may take time to process
    """)

# Main content area (rest of your existing code remains the same)
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("Enter podcast/video URL:", placeholder="https://youtu.be/...")
with col2:
    st.write("")
    st.write("")
    process_btn = st.button("Extract Text", key="process")

def download_audio(url):
    """Download audio from URL with improved error handling"""
    try:
        # Create temp directory if it doesn't exist
        temp_dir = tempfile.gettempdir()
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_template = os.path.join(temp_dir, f'podcast_{timestamp}.%(ext)s')
        
        # Check FFmpeg exists (fixed indentation)
        if not os.path.exists(FFMPEG_PATH):
            st.error("FFmpeg not found at configured path")
            return None
            
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': FFMPEG_PATH,  # Explicitly set FFmpeg path
            'outtmpl': output_template,  # Use the template we created
            'quiet': True,
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Get the actual downloaded filename
            filename = ydl.prepare_filename(info)
            audio_path = filename.replace('.webm', '.mp3').replace('.m4a', '.mp3')
            
            # Verify file exists before returning
            if os.path.exists(audio_path):
                return audio_path
            else:
                st.error("Downloaded file not found. FFmpeg may have failed to convert.")
                return None
                
    except Exception as e:
        st.error(f"Download failed: {str(e)}")
        return None
# Improved model loading with caching
@st.cache_resource(show_spinner=False)
def get_whisper_model(model_size="base"):
    """Cache the Whisper model to prevent repeated downloads"""
    try:
        # Check if model is already downloaded
        model_path = os.path.join(os.path.expanduser("~"), ".cache", "whisper")
        if not os.path.exists(model_path):
            os.makedirs(model_path)
        
        # This will only download once per model size
        return whisper.load_model(model_size, download_root=model_path)
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        return None
def generate_summary(text, length):
    """Generate summary using Gemini"""
    try:
        with st.spinner("Generating summary..."):
            length_prompt = {
                "Short (1-2 sentences)": "Provide a very concise summary in 1-2 sentences.",
                "Medium (paragraph)": "Provide a summary in one short paragraph.",
                "Detailed (multiple paragraphs)": "Provide a detailed summary in multiple paragraphs."
            }[length]
            
            prompt = f"""
            Please summarize the following podcast transcript clearly and accurately.
            {length_prompt}
            Focus on the key points and main ideas.
            
            Transcript:
            {text}
            """
            
            response = model.generate_content(prompt)
            return response.text
    except Exception as e:
        st.error(f"Summary generation failed: {str(e)}")
        return None
def transcribe_audio(audio_path, model_size="base"):
    """Transcribe audio with proper file handling to avoid access conflicts"""
    try:
        # Verify file exists and is accessible
        if not os.path.exists(audio_path):
            st.error(f"Audio file not found at: {audio_path}")
            return None
        
        # Load model (cached)
        model = get_whisper_model(model_size)
        if model is None:
            return None

        # Create a copy of the file to avoid access conflicts
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_wav:
            temp_wav_path = tmp_wav.name
        
        try:
            # Convert to WAV format if needed
            if not audio_path.lower().endswith('.wav'):
                audio = AudioSegment.from_file(audio_path)
                audio.export(temp_wav_path, format="wav")
                transcription = model.transcribe(temp_wav_path)
            else:
                # If already WAV, just copy to our temp file
                import shutil
                shutil.copy2(audio_path, temp_wav_path)
                transcription = model.transcribe(temp_wav_path)
            
            return transcription["text"]
        finally:
            # Ensure the temp file is deleted even if errors occur
            if os.path.exists(temp_wav_path):
                try:
                    os.unlink(temp_wav_path)
                except PermissionError:
                    # If still locked, schedule for deletion on program exit
                    import atexit
                    def cleanup():
                        if os.path.exists(temp_wav_path):
                            os.unlink(temp_wav_path)
                    atexit.register(cleanup)
                    
    except Exception as e:
        st.error(f"Transcription failed: {str(e)}")
        return None

if process_btn:
    if not url:
        st.warning("Please enter a URL")
    else:
        with st.spinner("Initializing..."):
            # Download audio
            audio_path = download_audio(url)
            
            if audio_path:
                # Transcribe audio
                text = transcribe_audio(audio_path, model_size)
                
                if text:
                    # Clean up
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                    
                    # Display results in tabs with dark theme
                    tab1, tab2, tab3 = st.tabs(["Transcript", "Summary", "Stats"])
                    
                    with tab1:
                        st.subheader("Full Transcript")
                        st.text_area("Transcript", text, height=400, label_visibility="collapsed")
                        
                        # Download buttons
                        st.download_button(
                            label="Download Transcript",
                            data=text,
                            file_name="transcript.txt",
                            mime="text/plain"
                        )
                    
                    # Generate and show summary
                    summary = generate_summary(text, summary_length)
                    
                    with tab2:
                        st.subheader("AI Summary")
                        if summary:
                            st.markdown(f'<div style="background-color: rgb(14, 17, 23); padding: 10px; border-radius: 5px; border: 1px solid #444">{summary}</div>', unsafe_allow_html=True)
                            st.download_button(
                                label="Download Summary",
                                data=summary,
                                file_name="summary.txt",
                                mime="text/plain"
                            )
                        else:
                            st.warning("Summary could not be generated")
                    
                    with tab3:
                        st.subheader("Statistics")
                        word_count = len(text.split())
                        char_count = len(text)
                        duration = len(text.split()) / 130  # Approx words per minute
                        
                        st.metric("Word Count", f"{word_count:,}")
                        st.metric("Character Count", f"{char_count:,}")
                        st.metric("Estimated Duration", f"{duration:.1f} minutes")
                        
                        st.info("Note: Duration estimation assumes 130 words per minute speech rate")

# Footer
st.markdown("""
<div class="footer">
    Podcast Text Extractor Pro | Powered by Whisper and Google Gemini
    <br>
    <small>For educational purposes only</small>
</div>
""", unsafe_allow_html=True)
