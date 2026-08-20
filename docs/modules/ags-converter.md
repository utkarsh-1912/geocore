# AGS File Converter

GeoCore includes an automated parser for **AGS (Association of Geotechnical and Geoenvironmental Specialists)** data files.

## Supported Formats
- **AGS 3.1**
- **AGS 4.0**

## Extracted Groups

GeoCore extracts standard AGS groups directly into pandas DataFrames:
- `HOLE`: Borehole metadata, locations, coordinates.
- `GEOL`: Geological stratum descriptions, depths, legend codes.
- `SCPT`: Cone Penetration Test sounding data ($z$, $q_c$, $f_s$, $u_2$).
- `ISPT`: Standard Penetration Test field results ($N$-values).
- `SAMP`: Soil sample indices, recovery rates, and quality ratings.

## Python API Usage

```python
from groundhog.general.agsconversion import AGSConverter

# Initialize converter
converter = AGSConverter("borehole_data.ags", encoding="utf8", agsformat="4")

# Extract group as DataFrame
cpt_df = converter.convert_ags_group("SCPT", verbose_keys=True)
```
