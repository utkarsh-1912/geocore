---
title: Installing GeoCore
slug: geocore/installation
section: Getting Started
description: Download and install GeoCore on Windows, macOS or Linux, where it keeps your data, and how automatic updates work.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/geocore/installation.md
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.16.0
edited_by_geocore: false
sources:
- README.md
- RELEASE_GUIDE.md
- electron-app/package.json
- electron-app/electron/main.cjs
- python-backend/core/paths.py
- python-backend/core/state.py
---

## Download

Installers are published on the [GeoCore releases page](https://github.com/utkarsh-1912/geocore/releases/latest). All builds are 64-bit.

| Platform | File | Notes |
|---|---|---|
| Windows | `GeoCore-Setup-<version>.exe` | Installer for the current user; administrator rights are not required. |
| macOS, Apple Silicon | `GeoCore-<version>-arm64.dmg` | Disk image. `GeoCore-<version>-arm64-mac.zip` contains the same application. |
| macOS, Intel | `GeoCore-<version>.dmg` | Disk image. `GeoCore-<version>-mac.zip` contains the same application. |
| Linux | `GeoCore-<version>.AppImage` | Runs without installation and updates itself. |
| Linux (Debian, Ubuntu) | `geocore_<version>_amd64.deb` | System package. Does not update itself. |

There is no portable Windows build. It was removed because it unpacked the whole application, including the calculation engine, to a temporary folder on every launch, which made start-up slow.

## Install

- **Windows:** run the setup file. The installer lets you choose the installation folder and creates desktop and Start menu shortcuts. GeoCore is installed for the current user.
- **macOS:** open the disk image and drag GeoCore to Applications.
- **Linux, AppImage:** make the file executable (`chmod +x GeoCore-<version>.AppImage`) and run it.
- **Linux, .deb:** install it with `sudo apt install ./geocore_<version>_amd64.deb`.

The installer contains everything needed to run calculations, including the Python calculation engine and groundhog. No separate Python installation is required.

## First start

On start-up the desktop app launches the local calculation engine in the background; the status indicator at the bottom of the sidebar shows when it is ready. The first calculation can take a little longer while the scientific libraries finish loading.

## Where GeoCore keeps your data

Your data is stored per user, outside the installation folder, so it survives updates and reinstalls:

| Item | Windows | macOS / Linux |
|---|---|---|
| Saved soil profiles and CPT tables (`saved_objects.json`) | `%APPDATA%\GeoCore` | `~/.geocore` |
| Project settings, such as the groundwater level used by GeoAI | `%APPDATA%\GeoCore` | `~/.geocore` |
| GeoAI models and settings | `%APPDATA%\GeoCore` | `~/.geocore` |

The calculation history and favourites shown in the app are stored by the desktop app itself.

## Updates

The Windows installer, the macOS app and the Linux AppImage check GitHub Releases for a newer version about 15 seconds after launch. A newer version is downloaded in the background and installed when you quit GeoCore. The check is skipped when running from source, and any failure (for example, no internet connection) is ignored: GeoCore keeps working offline.

- On macOS, automatic updates only work for properly code-signed builds; ad-hoc signed builds do not update themselves.
- The Linux `.deb` package cannot update itself. Install the new `.deb` for each release, or use the AppImage.

## GeoAI models

GeoAI language models are **not** included in the installer. They are downloaded separately from inside GeoCore; see [Setting up a GeoAI model](/docs/geoai/model-setup). Without a model, GeoAI falls back to a simple keyword-based mode.
