import streamlit as st
import yt_dlp
import os
import tempfile
import shutil
from pathlib import Path
import threading
import time
import json
import re
from datetime import datetime
import zipfile
import io

# Page configuration
st.set_page_config(
    page_title="Universal Media Downloader",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .download-card {
        background: #4b0082;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .instagram-card {
        background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .info-box {
        background: #e2e3e5;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #5a67d8 0%, #6b46c1 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

class MediaDownloader:
    def __init__(self):
        self.download_dir = tempfile.mkdtemp()
        self.supported_sites = [
            'YouTube', 'Vimeo', 'Facebook', 'Instagram', 'Twitter', 'TikTok',
            'Dailymotion', 'Twitch', 'Reddit', 'SoundCloud', 'Bandcamp'
        ]
        
    def is_instagram_url(self, url):
        """Check if URL is from Instagram"""
        instagram_patterns = [
            r'instagram\.com/p/',
            r'instagram\.com/reel/',
            r'instagram\.com/tv/',
            r'instagram\.com/stories/',
            r'instagr\.am/p/'
        ]
        return any(re.search(pattern, url) for pattern in instagram_patterns)
    
    def get_instagram_opts(self):
        """Get Instagram-specific yt-dlp options for public content"""
        return {
            'quiet': True,
            'no_warnings': True,
            'extractflat': False,
            # Enhanced Instagram support
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
        }
        
    def get_video_info(self, url):
        """Extract video information without downloading"""
        try:
            ydl_opts = self.get_instagram_opts() if self.is_instagram_url(url) else {
                'quiet': True,
                'no_warnings': True,
                'extractflat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Get the best thumbnail
                thumbnail = info.get('thumbnail', '')
                if not thumbnail and info.get('thumbnails'):
                    # Try to get the highest quality thumbnail
                    thumbnails = info.get('thumbnails', [])
                    if thumbnails:
                        thumbnail = thumbnails[-1].get('url', '')
                
                # Handle view count for different platforms
                view_count = info.get('view_count') or info.get('like_count') or info.get('repost_count') or 0
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', info.get('uploader_id', 'Unknown')),
                    'view_count': view_count,
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'thumbnail': thumbnail,
                    'formats': info.get('formats', []),
                    'webpage_url': info.get('webpage_url', url),
                    'platform': 'Instagram' if self.is_instagram_url(url) else info.get('extractor_key', 'Unknown')
                }
        except Exception as e:
            return None
    
    def get_available_formats(self, url):
        """Get available formats for the video"""
        try:
            ydl_opts = self.get_instagram_opts() if self.is_instagram_url(url) else {
                'quiet': True,
                'no_warnings': True,
                'listformats': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                video_formats = []
                audio_formats = []
                
                for fmt in formats:
                    if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                        # Video + Audio
                        video_formats.append({
                            'format_id': fmt['format_id'],
                            'ext': fmt['ext'],
                            'resolution': fmt.get('resolution', fmt.get('height', 'Unknown')),
                            'fps': fmt.get('fps', ''),
                            'vcodec': fmt.get('vcodec', ''),
                            'acodec': fmt.get('acodec', ''),
                            'filesize': fmt.get('filesize', 0),
                            'quality': fmt.get('quality', 0)
                        })
                    elif fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                        # Audio only
                        audio_formats.append({
                            'format_id': fmt['format_id'],
                            'ext': fmt['ext'],
                            'acodec': fmt.get('acodec', ''),
                            'abr': fmt.get('abr', 0),
                            'filesize': fmt.get('filesize', 0),
                            'quality': fmt.get('quality', 0)
                        })
                
                return video_formats, audio_formats
                
        except Exception as e:
            return [], []
    
    def download_media(self, url, format_type, quality, output_format):
        """Download media with specified parameters"""
        try:
            filename_template = f"{self.download_dir}/%(title)s.%(ext)s"
            
            # Base options
            base_opts = self.get_instagram_opts() if self.is_instagram_url(url) else {
                'quiet': True,
                'no_warnings': True,
            }
            
            if format_type == "Audio":
                ydl_opts = {
                    **base_opts,
                    'format': 'bestaudio/best',
                    'outtmpl': filename_template,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': output_format.lower(),
                        'preferredquality': quality,
                    }],
                }
            else:  # Video
                if quality == "Best":
                    format_selector = 'best'
                elif quality == "Worst":
                    format_selector = 'worst'
                else:
                    format_selector = f'best[height<={quality[:-1]}]'
                
                ydl_opts = {
                    **base_opts,
                    'format': format_selector,
                    'outtmpl': filename_template,
                }
                
                if output_format.lower() != 'original':
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': output_format.lower(),
                    }]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            # Find the downloaded file
            files = list(Path(self.download_dir).glob('*'))
            if files:
                return str(files[0])
            return None
            
        except Exception as e:
            st.error(f"Download failed: {str(e)}")
            return None
    
    def format_filesize(self, size):
        """Format file size in human readable format"""
        if not size or size == 0:
            return "Unknown"
        
        try:
            size = float(size)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except (ValueError, TypeError):
            return "Unknown"
    
    def format_duration(self, seconds):
        """Format duration in human readable format"""
        if not seconds or seconds == 0:
            return "Unknown"
        
        try:
            seconds = int(float(seconds))
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes:02d}:{seconds:02d}"
        except (ValueError, TypeError):
            return "Unknown"

def main():
    # Initialize downloader
    if 'downloader' not in st.session_state:
        st.session_state.downloader = MediaDownloader()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📺 Universal Media Downloader</h1>
        <p>Download videos and audio from YouTube, Vimeo, Instagram, TikTok, and 1000+ other platforms</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ Settings")
        
        # Instagram specific info
        st.subheader("📸 Instagram Support")
        st.info("✅ Public posts, reels, and IGTV videos")
        st.warning("⚠️ Only public content is supported")
        
        # Supported platforms
        st.subheader("Supported Platforms")
        platforms = st.session_state.downloader.supported_sites
        for i in range(0, len(platforms), 2):
            col1, col2 = st.columns(2)
            with col1:
                if i < len(platforms):
                    st.write(f"• {platforms[i]}")
            with col2:
                if i + 1 < len(platforms):
                    st.write(f"• {platforms[i + 1]}")
        
        st.markdown("---")
        
        # Quick tips
        st.subheader("💡 Quick Tips")
        st.write("• Paste any video URL in the input field")
        st.write("• Instagram: Only public posts work")
        st.write("• Choose between video or audio download")
        st.write("• Select your preferred quality and format")
        st.write("• Click analyze to preview before downloading")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📎 Enter Video URL")
        url = st.text_input(
            "URL",
            placeholder="https://www.instagram.com/p/... or https://www.youtube.com/watch?v=...",
            help="Paste the URL of the public video you want to download"
        )
        
        # URL validation
        if url:
            if st.session_state.downloader.is_instagram_url(url):
                st.info("📸 Instagram URL detected - Only public content can be downloaded")
        
        if url:
            if st.button("🔍 Analyze Video", key="analyze"):
                with st.spinner("Analyzing video..."):
                    video_info = st.session_state.downloader.get_video_info(url)
                    
                    if video_info:
                        st.session_state.video_info = video_info
                        st.session_state.video_formats, st.session_state.audio_formats = st.session_state.downloader.get_available_formats(url)
                        st.success("✅ Video analyzed successfully!")
                    else:
                        st.error("❌ Failed to analyze video. Please check the URL and ensure the content is public.")
    
    with col2:
        st.subheader("📊 Quick Stats")
        if 'video_info' in st.session_state:
            info = st.session_state.video_info
            duration = info.get('duration', 0)
            view_count = info.get('view_count', 0)
            uploader = info.get('uploader', 'Unknown')
            platform = info.get('platform', 'Unknown')
            
            st.metric("Duration", st.session_state.downloader.format_duration(duration))
            
            # Handle views differently for Instagram vs other platforms
            if platform == 'Instagram':
                st.metric("Likes/Views", f"{view_count:,}" if view_count and view_count > 0 else "Not available")
            else:
                st.metric("Views", f"{view_count:,}" if view_count and view_count > 0 else "Not available")
            
            st.metric("Uploader", uploader)
            st.metric("Platform", platform)
        else:
            st.info("Analyze a video to see stats")
    
    # Video information display
    if 'video_info' in st.session_state:
        st.markdown("---")
        
        info = st.session_state.video_info
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Different styling for Instagram
            if info.get('platform') == 'Instagram':
                view_text = "Likes/Views" if info.get('view_count', 0) > 0 else "Engagement"
                view_value = f"{info.get('view_count', 0):,}" if info.get('view_count', 0) > 0 else "Not available"
                
                st.markdown(f"""
                <div class="instagram-card">
                    <h3>📸 {info['title']}</h3>
                    <p><strong>Platform:</strong> Instagram</p>
                    <p><strong>Uploader:</strong> {info['uploader']}</p>
                    <p><strong>Duration:</strong> {st.session_state.downloader.format_duration(info['duration'])}</p>
                    <p><strong>{view_text}:</strong> {view_value}</p>
                    <p><strong>Upload Date:</strong> {info['upload_date']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                view_value = f"{info.get('view_count', 0):,}" if info.get('view_count', 0) > 0 else "Not available"
                st.markdown(f"""
                <div class="download-card">
                    <h3>📹 {info['title']}</h3>
                    <p><strong>Platform:</strong> {info.get('platform', 'Unknown')}</p>
                    <p><strong>Uploader:</strong> {info['uploader']}</p>
                    <p><strong>Duration:</strong> {st.session_state.downloader.format_duration(info['duration'])}</p>
                    <p><strong>Views:</strong> {view_value}</p>
                    <p><strong>Upload Date:</strong> {info['upload_date']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            if info.get('thumbnail'):
                try:
                    st.image(info['thumbnail'], caption="Thumbnail", use_container_width=True)
                except Exception as e:
                    st.warning("⚠️ Thumbnail not available")
            else:
                st.info("📷 No thumbnail available")
        
        # Download options
        st.subheader("⚙️ Download Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            format_type = st.selectbox(
                "Format Type",
                ["Video", "Audio"],
                help="Choose whether to download video or audio only"
            )
        
        with col2:
            if format_type == "Video":
                quality_options = ["Best", "1080p", "720p", "480p", "360p", "Worst"]
                quality = st.selectbox("Quality", quality_options)
                
                format_options = ["Original", "MP4", "AVI", "MKV", "WEBM"]
                output_format = st.selectbox("Output Format", format_options)
            else:
                quality_options = ["320", "256", "192", "128", "64"]
                quality = st.selectbox("Quality (kbps)", quality_options)
                
                format_options = ["MP3", "AAC", "OGG", "M4A", "FLAC"]
                output_format = st.selectbox("Output Format", format_options)
        
        with col3:
            st.write("")  # Spacer
            st.write("")  # Spacer
            
            if st.button("🚀 Download", key="download", type="primary"):
                with st.spinner("Downloading... This may take a few minutes."):
                    downloaded_file = st.session_state.downloader.download_media(
                        url, format_type, quality, output_format
                    )
                    
                    if downloaded_file:
                        st.success("✅ Download completed successfully!")
                        
                        # Read file for download
                        with open(downloaded_file, 'rb') as f:
                            file_data = f.read()
                        
                        # Create download button
                        filename = os.path.basename(downloaded_file)
                        st.download_button(
                            label=f"📥 Download {filename}",
                            data=file_data,
                            file_name=filename,
                            mime="application/octet-stream"
                        )
                        
                        # File info
                        file_size = os.path.getsize(downloaded_file)
                        st.info(f"📁 File size: {st.session_state.downloader.format_filesize(file_size)}")
                        
                        # Clean up
                        os.remove(downloaded_file)
                    else:
                        st.error("❌ Download failed. Please ensure the content is public and try again.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>Universal Media Downloader - Download from 1000+ platforms</p>
        <p>Built with ❤️ using Streamlit and yt-dlp</p>
        <p><small>⚠️ Only public content can be downloaded. Respects platform terms of service.</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()