---
title: Installing GeoCore
slug: geocore/installation
section: Getting Started
nav_order: 20
description: Download and install GeoCore on Windows or macOS, and how automatic updates work.
sources:
- README.md
- RELEASE_GUIDE.md
- electron-app/package.json
- electron-app/electron/main.cjs
---

## Download

Installers are published on the [GeoCore releases page](https://github.com/utkarsh-1912/geocore/releases/latest).

| Platform | File | Notes |
|---|---|---|
| Windows | `GeoCore-Setup-<version>.exe` | Per-user installer; administrator rights are not required. |
| macOS | `GeoCore-<version>-<arch>.dmg` | Disk image. A `.zip` of the application is also published. |

There is no portable Windows build. It was removed because it unpacked the whole application, including the calculation engine, to a temporary folder on every launch, which made start-up slow.

## Install

- **Windows:** run the setup file and follow the installer. GeoCore is installed for the current user.
- **macOS:** open the disk image and drag GeoCore to Applications.

The installer contains everything needed to run calculations, including the Python calculation engine and groundhog. No separate Python installation is required.

## First start

On start-up the desktop app launches the local calculation engine in the background. The first calculation can take a little longer while the scientific libraries finish loading.

## Updates

Installed builds check GitHub Releases for a newer version about 15 seconds after launch. A newer version is downloaded in the background and installed when you quit GeoCore. The check is skipped when running from source, and any failure (for example, no internet connection) is ignored: GeoCore keeps working offline.

On macOS, automatic updates only work for properly code-signed builds; ad-hoc signed builds do not update themselves.

## GeoAI models

GeoAI language models are **not** included in the installer. They are downloaded separately from inside GeoCore; see [Setting up a GeoAI model](/docs/geoai/model-setup). Without a model, GeoAI falls back to a simple keyword-based mode.
