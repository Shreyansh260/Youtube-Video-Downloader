import streamlit as st
import yt_dlp
import os
import tempfile
from pathlib import Path
import time
import random
import re

# Page configuration
st.set_page_config(
    page_title="Universal Media Downloader",
    page_icon="table-lamp.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI (copied from youtube.py)
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
 .youtube-detected {
    background: #0d1b2a;           /* deep navy blue */
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #2196f3; /* soft blue accent */
    margin: 1rem 0;
    color: #e0f7ff;                /* light icy-blue text */
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
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]
        
    def is_youtube_url(self, url):
        """Check if URL is from YouTube"""
        youtube_patterns = [
            r'youtube\.com/watch',
            r'youtu\.be/',
            r'youtube\.com/shorts'
        ]
        return any(re.search(pattern, url) for pattern in youtube_patterns)
    
    def get_youtube_opts(self, method="web"):
        """Get YouTube-specific options"""
        base_opts = {
            'quiet': True,
            'no_warnings': True,
            'extractflat': False,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'ignoreerrors': False,
            'socket_timeout': 30,
        }
        
        if method == "mobile":
            base_opts['http_headers'] = {
                'User-Agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip',
                'X-YouTube-Client-Name': '3',
                'X-YouTube-Client-Version': '19.09.37',
            }
            base_opts['extractor_args'] = {
                'youtube': {
                    'player_client': ['android'],
                    'player_skip': ['webpage'],
                }
            }
        else:  # web method
            base_opts['http_headers'] = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            base_opts['extractor_args'] = {
                'youtube': {
                    'player_client': ['web', 'android'],
                    'player_skip': ['configs'],
                }
            }
        
        return base_opts
    
    def get_standard_opts(self):
        """Get options for non-YouTube platforms"""
        return {
            'quiet': True,
            'no_warnings': True,
            'extractflat': False,
            'http_headers': {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            },
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'ignoreerrors': False,
        }
    
    def get_video_info(self, url):
        """Extract video information"""
        try:
            if self.is_youtube_url(url):
                # Try multiple methods for YouTube
                methods = [("web", self.get_youtube_opts("web")), 
                          ("mobile", self.get_youtube_opts("mobile"))]
                
                for method_name, opts in methods:
                    try:
                        with yt_dlp.YoutubeDL(opts) as ydl:
                            info = ydl.extract_info(url, download=False)
                            if info:
                                st.session_state.working_opts = opts
                                return self.format_video_info(info, url)
                    except Exception as e:
                        if "Sign in to confirm" in str(e):
                            continue
                        else:
                            st.warning(f"Method {method_name} failed: {str(e)[:100]}...")
                            continue
                
                st.error("YouTube access blocked by bot detection")
                return None
            else:
                # Non-YouTube platforms
                opts = self.get_standard_opts()
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        st.session_state.working_opts = opts
                        return self.format_video_info(info, url)
                
        except Exception as e:
            st.error(f"Error analyzing video: {str(e)}")
            return None
    
    def format_video_info(self, info, url):
        """Format video information for display"""
        # Get thumbnail
        thumbnail = info.get('thumbnail', '')
        if not thumbnail and info.get('thumbnails'):
            thumbnails = info.get('thumbnails', [])
            if thumbnails:
                thumbnail = thumbnails[-1].get('url', '')
        
        # Handle view count for different platforms
        view_count = info.get('view_count') or info.get('like_count') or info.get('repost_count') or 0
        
        return {
            'title': info.get('title', 'Unknown Title'),
            'duration': info.get('duration', 0),
            'uploader': info.get('uploader', 'Unknown'),
            'view_count': view_count,
            'upload_date': info.get('upload_date', ''),
            'thumbnail': thumbnail,
            'formats': info.get('formats', []),
            'platform': 'YouTube' if self.is_youtube_url(url) else info.get('extractor_key', 'Unknown')
        }
    
    def download_media(self, url, format_type, quality, output_format):
        """Download media with specified parameters"""
        try:
            if 'working_opts' not in st.session_state:
                st.error("Please analyze the video first")
                return None
                
            opts = st.session_state.working_opts.copy()
            opts['outtmpl'] = f"{self.download_dir}/%(title)s.%(ext)s"
            
            if format_type == "Audio":
                opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': output_format.lower(),
                        'preferredquality': quality,
                    }],
                })
            else:  # Video
                if quality == "Best":
                    opts['format'] = 'best'
                elif quality == "Worst":
                    opts['format'] = 'worst'
                else:
                    opts['format'] = f'best[height<={quality[:-1]}]'
                
                if output_format.lower() != 'original':
                    opts['postprocessors'] = [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': output_format.lower(),
                    }]
            
            # Add delay for YouTube
            if self.is_youtube_url(url):
                time.sleep(1)
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            
            # Find downloaded file
            files = list(Path(self.download_dir).glob('*'))
            return str(files[0]) if files else None
            
        except Exception as e:
            st.error(f"Download failed: {str(e)}")
            return None
    
    def format_duration(self, seconds):
        """Format duration in readable format"""
        if not seconds:
            return "Unknown"
        
        try:
            seconds = int(seconds)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes:02d}:{secs:02d}"
        except:
            return "Unknown"
    
    def format_filesize(self, size):
        """Format file size in readable format"""
        if not size:
            return "Unknown"
        
        try:
            size = float(size)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown"

def main():
    # Initialize downloader
    if 'downloader' not in st.session_state:
        st.session_state.downloader = MediaDownloader()
    
    # Header (updated from youtube.py)
    st.markdown("""
    <div class="main-header">
        <h1>📺 Universal Media Downloader</h1>
        <p>Download videos and audio from YouTube, TikTok, Instagram, Vimeo, and 1000+ other platforms</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar (copied from youtube.py)
    with st.sidebar:
        st.header("🎛️ Settings")
        
        # YouTube specific info
        st.subheader("🎯 YouTube Support")
        st.info("✅ Advanced bypass methods")
        st.warning("⚠️ Success rate may vary due to bot protection")
        
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
        st.write("• YouTube: Advanced bypass methods included")
        st.write("• Choose between video or audio download")
        st.write("• Select your preferred quality and format")
        st.write("• Click analyze to preview before downloading")
    
    # Main content (updated layout from youtube.py)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📎 Enter Video URL")
        url = st.text_input(
            "URL",
            placeholder="https://www.youtube.com/watch?v=... or https://www.tiktok.com/@...",
            help="Paste the URL of the video you want to download"
        )
        
        # URL validation
        if url:
            if st.session_state.downloader.is_youtube_url(url):
                st.markdown("""
                <div class="youtube-detected">
                    <strong>🎯 YouTube URL detected</strong><br>
                    Using advanced bypass methods. Success rate may vary due to YouTube's bot protection.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success("✅ URL detected - This platform typically works well")
        
        if url:
            if st.button("🔍 Analyze Video", key="analyze", type="primary"):
                with st.spinner("Analyzing video... Please wait."):
                    video_info = st.session_state.downloader.get_video_info(url)
                    
                    if video_info:
                        st.session_state.video_info = video_info
                        st.success("✅ Video analyzed successfully!")
                        
                        if st.session_state.downloader.is_youtube_url(url):
                            st.balloons()
                    else:
                        st.error("❌ Failed to analyze video")
    
    with col2:
        st.subheader("📊 Quick Stats")
        if 'video_info' in st.session_state:
            info = st.session_state.video_info
            duration = info.get('duration', 0)
            view_count = info.get('view_count', 0)
            uploader = info.get('uploader', 'Unknown')
            platform = info.get('platform', 'Unknown')
            
            st.metric("Duration", st.session_state.downloader.format_duration(duration))
            st.metric("Views", f"{view_count:,}" if view_count and view_count > 0 else "Not available")
            st.metric("Uploader", uploader)
            st.metric("Platform", platform)
        else:
            st.info("Analyze a video to see stats")
    
    # Video information display (updated from youtube.py)
    if 'video_info' in st.session_state:
        st.markdown("---")
        
        info = st.session_state.video_info
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Use download-card styling
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
                
                format_options = ["Original", "MP4", "WEBM"]
                output_format = st.selectbox("Output Format", format_options)
            else:
                quality_options = ["320", "256", "192", "128", "96"]
                quality = st.selectbox("Quality (kbps)", quality_options)
                
                format_options = ["MP3", "AAC", "OGG"]
                output_format = st.selectbox("Output Format", format_options)
        
        with col3:
            st.write("")  # Spacer
            st.write("")  # Spacer
            
            if st.button("🚀 Download", key="download", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("Initializing download...")
                    progress_bar.progress(20)
                    
                    downloaded_file = st.session_state.downloader.download_media(
                        url, format_type, quality, output_format
                    )
                    
                    progress_bar.progress(90)
                    
                    if downloaded_file:
                        progress_bar.progress(100)
                        status_text.text("Download completed!")
                        
                        # Read file for download
                        with open(downloaded_file, 'rb') as f:
                            file_data = f.read()
                            file_name = os.path.basename(downloaded_file)
                            
                            st.download_button(
                                label=f"📥 Download {file_name}",
                                data=file_data,
                                file_name=file_name,
                                mime="application/octet-stream"
                            )
                            
                            # File info
                            file_size = os.path.getsize(downloaded_file)
                            st.info(f"📁 File size: {st.session_state.downloader.format_filesize(file_size)}")
                            
                            # Cleanup
                            try:
                                os.remove(downloaded_file)
                            except:
                                pass
                    else:
                        progress_bar.progress(0)
                        status_text.text("Download failed!")
                        st.error("❌ Download failed")
                        
                except Exception as e:
                    progress_bar.progress(0)
                    status_text.text("")
                    st.error(f"❌ Error: {str(e)}")
    
    # Footer (updated from youtube.py)
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>Universal Media Downloader - Download from 1000+ platforms</p>
        <p>Built with ❤️ using Streamlit and yt-dlp</p>
        <p><small>⚠️ Please respect copyright laws and platform terms of service.</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
