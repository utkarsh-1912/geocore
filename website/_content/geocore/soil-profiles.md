---
title: Soil profiles and AGS data
slug: geocore/using/soil-profiles
section: Using GeoCore
nav_order: 20
description: Create groundhog SoilProfile objects from CSV or Excel files, and load AGS files.
sources:
- python-backend/core/registry.py
- python-backend/core/router.py
- python-backend/core/state.py
- electron-app/src/features/calculations/SoilProfileModal.jsx
---

Several calculators (for example settlement calculations, calculation grids and log plots) work on a **soil profile**: a table of layers with a top depth, a bottom depth and layer properties. GeoCore stores soil profiles as groundhog [`SoilProfile`](/docs/groundhog/api/general/soilprofile#soilprofile) objects.

## Creating a soil profile

A soil profile can be created from:

- a **CSV** (`.csv`) or **Excel** (`.xlsx`, `.xls`) file, or
- a table of layers entered in the application.

When the profile is created, GeoCore:

1. Renames the columns you select as the top and bottom depth to `Depth from [m]` and `Depth to [m]`, the names groundhog requires.
2. Converts every column that contains numbers to numeric values.
3. Adds units to column names that lack them, because groundhog expects headers of the form `Name [unit]`. Headers that already contain `[...]` are kept as they are. Otherwise:
   - a trailing suffix after an underscore made only of letters, digits and underscores becomes the unit, so `Undrained shear strength_kPa` becomes `Undrained shear strength [kPa]`;
   - other numeric columns get `[-]`.
4. By default, fills empty numeric cells with `0`. Check your data if some properties are legitimately missing.

Writing units in square brackets yourself is the most reliable option, especially for units such as `kN/m3` that contain a `/`.

### Example CSV

```text
Depth from,Depth to,Soil type,Total unit weight [kN/m3],Undrained shear strength [kPa]
0,2,Sand,19,0
2,8,Clay,17.5,40
8,15,Clay,18,65
```

After import, choose `Depth from` and `Depth to` as the depth columns. groundhog's own requirements for soil profiles are described in the [SoilProfile reference](/docs/groundhog/api/general/soilprofile#soilprofile).

## Saved objects

Soil profiles and other objects you create are listed in the object manager and can be viewed or deleted. They are saved by the calculation engine to a local `saved_objects.json` file and restored the next time GeoCore starts.

## AGS files

The **AGSConverter** calculator loads an AGS file (AGS 4 by default) and lists the groups it contains. **convert_ags_group()** then extracts one group (for example `GEOL` or `SCPT`) as a table. Both run groundhog's [`AGSConverter`](/docs/groundhog/api/general/agsconversion#agsconverter).
