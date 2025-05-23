import streamlit as st
import os
import subprocess
import whisper
import tempfile
import yt_dlp

import sys

try:
    import numpy
    print("✅ Numpy is available. Version:", numpy.__version__)
except ImportError as e:
    print("🚫 Numpy import failed:", e)

print("Python executable:", sys.executable)


# Streamlit UI
st.title("English Accent Detector")
video_url = st.text_input("Enter a public MP4 or YouTube video URL:")

if st.button("Analyze"):
    if not video_url:
        st.error("Please enter a valid video URL.")
    else:
        try:
            with st.spinner("Downloading and processing video..."):
                # Clean URL
                clean_url = video_url.strip().split('&')[0]

                # Create temp paths
                temp_dir = tempfile.TemporaryDirectory()
                temp_audio = os.path.join(temp_dir.name, "audio.wav")

                # Download audio with yt_dlp
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(temp_dir.name, 'download.%(ext)s'),
                    'quiet': True,
                    'noplaylist': True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav',
                        'preferredquality': '192',
                    }],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([clean_url])

                # Find downloaded .wav file
                downloaded_files = os.listdir(temp_dir.name)
                wav_files = [f for f in downloaded_files if f.endswith(".wav")]
                if not wav_files:
                    raise RuntimeError("Failed to extract audio.")
                audio_path = os.path.join(temp_dir.name, wav_files[0])

                # Transcribe with Whisper
                st.info("Transcribing and analyzing...")
                model = whisper.load_model("base")
                result = model.transcribe(audio_path, language="en")

                transcript = result['text']
                lang = result.get('language', 'unknown')

                # Accent detection (simple logic)
                if "color" in transcript or "apartment" in transcript:
                    accent = "American"
                    confidence = 90
                elif "flat" in transcript or "colour" in transcript:
                    accent = "British"
                    confidence = 90
                else:
                    accent = "Uncertain"
                    confidence = 50

                # Output
                st.success("Analysis Complete ✅")
                st.write(f"**Detected Accent:** {accent}")
                st.write(f"**Confidence Score:** {confidence}%")
                st.write(f"**Transcript:** {transcript[:300]}...")

        except Exception as e:
            st.error(f"🚫 Failed to process video: {str(e)}")
