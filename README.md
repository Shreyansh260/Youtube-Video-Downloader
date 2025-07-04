# 📺 Universal Media Downloader

A powerful and user-friendly Streamlit web app that lets you download videos or audio from 1000+ websites including **YouTube**, **Instagram**, **TikTok**, **Facebook**, **Twitter**, and more.

Built using [`yt-dlp`](https://github.com/yt-dlp/yt-dlp), this tool allows users to analyze, preview, and download content in multiple formats and quality levels — all through a sleek UI.

---

## 🚀 Features

- 🔍 **Media Analysis** - Fetch metadata including title, views, duration, and uploader information
- 🎞️ **Video Downloads** - Download videos in your preferred resolution (1080p, 720p, 480p, etc.)
- 🎧 **Audio Extraction** - Extract audio in multiple formats (MP3, AAC, M4A, FLAC, OGG)
- 🌐 **Wide Platform Support** - Works with 1000+ platforms including:
  - YouTube, Instagram, TikTok, Vimeo
  - Facebook, Twitter, Reddit, Dailymotion
  - Twitch, SoundCloud, Bandcamp
  - And many more!
- 📸 **Instagram Support** - Public posts, reels, and IGTV content
- 💻 **Modern UI** - Beautiful and responsive interface with dark-themed layout
- 📦 **One-Click Download** - Instant file download after conversion
- 🧹 **Auto-Cleanup** - Temporary file management and automatic cleanup

---

## 🖥️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) - Interactive web framework
- **Downloader**: [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Universal media downloader
- **Media Processing**: [FFmpeg](https://ffmpeg.org/) - Format conversion and processing
- **Backend**: Python 3.7+ with standard libraries

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.7 or higher
- FFmpeg (for format conversion)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/universal-media-downloader.git
cd universal-media-downloader
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

#### Windows
1. Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract and add to system PATH

#### Linux/Ubuntu
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

### 4. Run the Application
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

---

## 📋 Requirements

Create a `requirements.txt` file with the following dependencies:

```txt
streamlit>=1.25.0
yt-dlp>=2023.7.6
requests>=2.31.0
Pillow>=9.5.0
```

---

## 🎯 Usage

1. **Launch the App** - Run `streamlit run app.py`
2. **Enter URL** - Paste the media URL you want to download
3. **Analyze** - Click "Analyze" to fetch media information
4. **Choose Format** - Select video quality or audio format
5. **Download** - Click download and get your file instantly

### Supported URL Examples
- YouTube: `https://www.youtube.com/watch?v=VIDEO_ID`
- Instagram: `https://www.instagram.com/p/POST_ID/`
- TikTok: `https://www.tiktok.com/@user/video/VIDEO_ID`
- Twitter: `https://twitter.com/user/status/TWEET_ID`

---

## 🔧 Configuration

### Custom yt-dlp Options
You can modify the downloader behavior by editing the yt-dlp options in your code:

```python
ydl_opts = {
    'format': 'best',
    'outtmpl': '%(title)s.%(ext)s',
    'noplaylist': True,
    'extract_flat': False,
}
```

### Instagram-Specific Headers
For Instagram content, special headers are automatically applied:

```python
instagram_headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; Instagram downloader)',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
}
```

---

## 🚨 Important Notes

- ⚠️ **Public Content Only** - This app only supports public media. Private or login-required content will not be accessible
- ❗ **Educational Use** - This tool is for educational and personal use only. Please respect the Terms of Service of the platforms you interact with
- 🔒 **No Authentication** - The app doesn't store or require any login credentials
- 📱 **Mobile Friendly** - Responsive design works on desktop and mobile devices

---

## 🤝 Contributing

We welcome contributions! Please feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ❤️ Acknowledgements

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - The powerful YouTube download engine that makes this possible
- **[Streamlit](https://streamlit.io/)** - For the amazing frontend framework
- **[FFmpeg](https://ffmpeg.org/)** - For media processing capabilities
- **Open Source Community** - For inspiration and continuous improvement

---

## 🙌 Author

**Shriyansh Singh Rathore**

- 📧 Email: shreyanshsinghrathore7@gmail.com
- 🌐 GitHub: [@yourusername](https://github.com/yourusername)
- 💼 LinkedIn: [Your LinkedIn Profile](https://linkedin.com/in/yourprofile)

---

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/universal-media-downloader/issues) page
2. Create a new issue with detailed information
3. Contact the author via email

---

## 🔮 Future Enhancements

- [ ] Batch download functionality
- [ ] Download progress tracking
- [ ] Playlist support
- [ ] Custom output directory selection
- [ ] Download history
- [ ] API integration for developers

---

<div align="center">

<p>⭐ If you found this project helpful, please give it a star!</p>
<p>Made with ❤️ by Shriyansh Singh Rathore</p>

</div>
