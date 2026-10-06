---
title: Customising calculator forms
slug: geocore/using/parameter-overrides
section: Using GeoCore
description: Development-mode tool for adjusting field labels, descriptions, units and input patterns of calculator forms.
origin: geocore
source_url: https://github.com/utkarsh-1912/geocore/blob/main/website/_content/geocore/parameter-overrides.md
license: GPL-3.0
author: Utkarsh Gupta
attribution: GeoCore documentation by Utkarsh Gupta, licensed under the GNU GPL v3.
groundhog_version: 0.16.0
edited_by_geocore: false
sources:
- electron-app/src/features/calculations/SchemaForm.jsx
- electron-app/src/features/calculations/SchemaEditor.jsx
- python-backend/core/schema_manager.py
- python-backend/core/router.py
---

GeoCore's calculator forms can be adjusted without changing the code. This is a **development-mode** feature: the **Customize Form** button only appears when GeoCore runs from source in development mode, not in installed builds.

## Editing a field

1. Open a calculator.
2. Click **Customize Form** in the form header.
3. Click the edit control on a field. You can change its:
   - display label,
   - description,
   - unit shown next to the field,
   - placeholder text,
   - input pattern (a regular expression; presets include positive number and integer).
4. Save the change, then click **Done Editing**.

The calculator's guide text can be edited the same way, and images can be attached to fields.

## Where overrides are stored

Overrides are sent to the local calculation engine and saved in `schema_overrides.json` next to the engine; uploaded images are saved under `assets/schema_images`. The overrides change how the form is presented. They do not change the groundhog calculation, its default values or its validation ranges.
