---
title: Introduction to groundhog
slug: groundhog/guides/introduction
section: Groundhog Guides
description: Introduction to groundhog, the geotechnical Python library behind GeoCore's calculations.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/docs/index.rst
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Converted from reStructuredText. Sphinx-only 'Indices and tables' section removed; 'Installation requirements' and 'Support groundhog' (pip install steps and a donation/consultancy pitch) removed as not applicable to GeoCore, which already bundles groundhog.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, these functions run through the [calculation catalogue](/docs/geocore/using/modules) or through **GeoAI**, which selects and calls them through its validated Tool Registry — you never need to install Python or groundhog yourself.

[![](https://badge.fury.io/py/groundhog.svg)](https://badge.fury.io/py/groundhog)

![](/docs/assets/groundhog/docs/tutorials/images/groundhog_banner_wide.png)

This Python package contains useful functionality for supporting automated geotechnical calculations.

`groundhog` is first and foremost aimed at education on geotechnical engineering automation with Python. It aims to support students and educators with well-developed examples of geotechnical analysis in Python.

Functionality for onshore and offshore geotechnical problems is included. This package is under constant development so any request for additional functionality can always be submitted to the package author.

The package is developed around four pilars:

- Flexible input parameter validation: Predefined parameter ranges are defined for most functions, based on the range of soil parameters for which the function was originally developed. This validation can be overridden by the user but requires explicit definition of the modified parameter ranges;
- Multiple outputs: Groundhog functions return a Python dictionary including intermediate results or derived quantities;
- Data standardisation: Possibility to read multiple input file formats (e.g. CPT data);
- Soil profiles: Easy encoding and manipulation of soil profiles.

The package was named after the [groundhog](https://en.wikipedia.org/wiki/Groundhog/), an animal that lives in underground burrows. Moreover, the movie [Groundhog Day](https://en.wikipedia.org/wiki/Groundhog_Day_(film)/) where a reporter relives the same day again and again. The groundhog package aims to remove this repetitiveness from your day-to-day geotechnical engineering work.

## Tutorials

[![](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/snakesonabrain/groundhog/main)

Tutorials are provided in the notebooks folder of the project. Jupyter notebooks are provided for the following examples:

- Basic use of groundhog functions
- Soil profile definition, manipulation and plotting
- PCPT data loading
- PCPT data processing
- Loading AGS data
- Axial pile capacity calculation according to Belgian practice
- ...

## Function documentation

Detailed documentation is available on the functions and classes of the package. This documentation is essential for using the functions in `groundhog` correctly as the documentation specifies the physical meaning and the units of input and output variables.

- [General and utility functions](/docs/groundhog/guides/topics/general)
- [Site investigation](/docs/groundhog/guides/topics/site-investigation)
- [Pile calculations](/docs/groundhog/guides/topics/piles)
- [Shallow foundations](/docs/groundhog/guides/topics/shallowfoundations)
- [Consolidation functions](/docs/groundhog/guides/topics/consolidation)
- [Excavations](/docs/groundhog/guides/topics/excavations)
- [Soil dynamics](/docs/groundhog/guides/topics/soildynamics)
- [Standards](/docs/groundhog/guides/topics/standards)
- [Constitutive models](/docs/groundhog/guides/topics/constitutivemodels)
- [Pipelines and cables](/docs/groundhog/guides/topics/pipelinescables)

## Acknowledgements

The code for the validation of function input has been adopted from the python-engineering library and was integrated in the package to reduce the amount of dependencies.

## License and usage restrictions

groundhog. A general-purpose Python library for geotechnical engineering.

> Copyright (C) 2020  Bruno Stuyts
>
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> (at your option) any later version.
>
> This program is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
> GNU General Public License for more details.
>
> You should have received a copy of the GNU General Public License
> along with this program.  If not, see <https://www.gnu.org/licenses/>.
