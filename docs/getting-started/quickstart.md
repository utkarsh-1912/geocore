# Quickstart Guide

This guide walks you through launching GeoCore, creating a soil profile, running your first Cone Penetration Test (CPT) interpretation, and executing a shallow foundation bearing capacity check.

---

## ⏱️ 5-Minute Walkthrough

### Step 1: Launch the Application
Download and start GeoCore on your machine. The app automatically spawns the local Python FastAPI calculation kernel on `127.0.0.1:8000` with zero cloud dependencies.

```bash
# Developer / Source mode:
npm run dev
```

The Electron main window will open with the full sidebar navigation and interactive module explorer.

---

### Step 2: Create a Soil Profile (`SoilProfile`)
A **SoilProfile** represents layered stratigraphy with depth-dependent parameters:

1. Click **Site Investigation &rarr; Soil Profile** in the left sidebar.
2. Either upload a CSV file or paste tabular data with columns:
   - `Depth from [m]`, `Depth to [m]`
   - `Soil type` (e.g. `Sand`, `Clay`, `Silt`)
   - `Total unit weight [kN/m3]`
   - `qc [MPa]`, `fs [kPa]` (for CPT soundings)
3. GeoCore automatically normalizes column names and stores the profile in the active memory session.

---

### Step 3: Run PCPT Interpretation
1. Navigate to **Site Investigation &rarr; PCPT Processing**.
2. Select your Soil Profile from the dropdown.
3. Configure the interpretation parameters:
   - **Water Table Depth ($z_w$)**: `1.5 m`
   - **Cone Factor ($N_{kt}$)**: `14.0`
   - **Classification Method**: `Robertson (2016)`
4. Click **Execute Calculation**.
5. GeoCore computes normalized $Q_{tn}, F_r, I_c$, plots the multi-panel sounding log, and classifies the layers into Robertson Soil Behavior Type (SBT) zones.

---

### Step 4: Calculate Shallow Foundation Capacity
1. Navigate to **Shallow Foundations &rarr; Undrained Bearing Capacity**.
2. Provide foundation geometry:
   - Foundation Shape: `Rectangle`
   - Width $B$: `3.0 m`, Length $L$: `6.0 m`
   - Embedment Depth $D$: `1.5 m`
3. Enter soil strength:
   - Base Undrained Strength $s_u$: `75.0 kPa`
   - Strength gradient $k$: `2.5 kPa/m`
   - Total Unit Weight $\gamma$: `18.5 kN/m³`
4. Click **Calculate Capacity Envelope**.
5. An interactive Plotly $V-H-M$ envelope is generated showing the safe allowable loading domain and factored design limit.

---

### Step 5: Exporting Reports & Visualizations
- Every plot in GeoCore can be saved as high-resolution PNG, SVG, or vector PDF.
- Full calculation results can be exported as structured JSON, CSV, or formatted Excel spreadsheets.
