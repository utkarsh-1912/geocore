# Installation & System Requirements

GeoCore is distributed as a standalone desktop application for Windows, macOS, and Linux, as well as a developer Python package and Electron workspace.

---

## 💻 System Requirements

| Specification | Minimum | Recommended |
| :--- | :--- | :--- |
| **Operating System** | Windows 10 (64-bit), macOS 11+, Ubuntu 20.04+ | Windows 11 (64-bit), macOS 14+, Ubuntu 22.04+ |
| **Processor** | Dual-core 2.0 GHz Intel / AMD / Apple M1 | Quad-core 3.0+ GHz Intel Core i7 / AMD Ryzen / Apple Silicon |
| **RAM** | 4 GB | 8 GB or higher |
| **Disk Space** | 600 MB free storage | 1.5 GB SSD storage |
| **Display** | 1280 × 800 resolution | 1920 × 1080 Full HD or higher |

---

## 📦 Binary Installation (Pre-built Binaries)

### Windows
1. Download `GeoCore-Setup-1.0.0.exe` from the [GitHub Releases](https://github.com/utkarsh-1912/geocore/releases).
2. Double-click the installer and follow the on-screen prompts.
3. GeoCore installs with bundled Python runtime, FastAPI daemon, and all numerical libraries. No external Python installation is required.

### macOS
1. Download `GeoCore-1.0.0.dmg` for Intel or Apple Silicon.
2. Drag `GeoCore.app` into your `Applications` folder.

### Linux
1. Download `GeoCore-1.0.0.AppImage`.
2. Make it executable:
   ```bash
   chmod +x GeoCore-1.0.0.AppImage
   ./GeoCore-1.0.0.AppImage
   ```

---

## 🛠️ Building from Source

To run or build GeoCore directly from the Git repository:

### 1. Prerequisites
- **Node.js**: v18.0+ or v20.0+ (`npm` or `yarn`)
- **Python**: 3.10, 3.11, or 3.12 (64-bit)
- **Git**

### 2. Clone the Repository
```bash
git clone https://github.com/utkarsh-1912/geocore.git
cd geocore
```

### 3. Setup Python Backend Environment
```bash
cd python-backend
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Setup Electron Frontend
```bash
cd ../electron-app
npm install
```

### 5. Launch Development Server
```bash
# In electron-app directory:
npm run dev
```
