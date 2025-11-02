# 🚀 SyncD2D - Advanced File Sync Tool

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

**Fast, reliable, and beautiful file synchronization tool with modern UI.**

![SyncD2D Screenshot](https://github.com/user-attachments/assets/cc33d667-61da-4807-8014-dc93576b2f5a)

## ✨ Features

- 🎨 **Beautiful Terminal UI** - Catppuccin, Tokyo Night, Dracula themes
- ⚡ **Lightning Fast** - Parallel file copying with multi-threading
- 🔐 **Secure Sync** - Optional MD5 hash verification
- 🌍 **Multi-language** - Vietnamese & English support
- 💾 **Resume Support** - Continue interrupted syncs
- 🎯 **Smart Comparison** - Analyze differences before syncing
- 🖥️ **Cross-platform** - Windows, macOS, Linux

## 📥 Installation

### Quick Start (No Python Required!)

**Download the latest release for your platform:**

#### Windows
1. Download `SyncD2D-Windows.zip` from [Releases](../../releases)
2. Extract and run `SyncD2D.exe`
3. Done! 🎉

#### macOS
1. Download `SyncD2D-macOS.zip` from [Releases](../../releases)
2. Extract and run `SyncD2D`
3. If blocked by Gatekeeper: Right-click → Open

#### Linux
1. Download `SyncD2D-Linux.zip` from [Releases](../../releases)
2. Extract and make executable: `chmod +x SyncD2D`
3. Run: `./SyncD2D`

### Build from Source
```bash
# Clone the repository
git clone https://github.com/ArkParado/SyncD2D.git
cd SyncD2D

# Install dependencies
pip install -r requirements.txt

# Run directly
python file_sync.py

# Or build executable
python build_app.py
```
### 🎮 Usage

1. **Launch the app**
2. **Select source drive** - Choose where to copy from
3. **Select destination drive** - Choose where to copy to
4. **Choose action:**
   - 🔍 Compare - See differences
   - 👁️ Preview - Dry run (no changes)
   - ⚡ Quick Sync - Fast parallel copy
   - 🔐 Secure Sync - With hash verification

### 🎨 Themes

Choose from 8 beautiful themes:
- Catppuccin (Mocha, Latte, Frappé, Macchiato)
- Tokyo Night
- Dracula
- Nord
- Gruvbox

### 🛠️ Configuration

Settings are saved in `file_sync_config.json`:
- Theme preference
- Language selection

## 📊 Technical Details

- **Language:** Python 3.8+
- **Dependencies:** tqdm, Pillow
- **Threading:** Configurable workers (default: 4)
- **Chunk Size:** 1MB for hash calculations
- **Resume State:** Saved in `sync_state.json`

---

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- [Catppuccin](https://github.com/catppuccin/catppuccin) - Beautiful color schemes
- [tqdm](https://github.com/tqdm/tqdm) - Progress bars
- [PyInstaller](https://www.pyinstaller.org/) - Executable packaging

### 📧 Contact

Tran Phuc Hung - **ArkParado** - [arkparado](https://www.instagram.com/arkparado/)

Project Link: [https://github.com/ArkParado/SyncD2D](https://github.com/ArkParado/SyncD2D)
---

⭐ **Star this repo if you find it useful!**
