---
title: General and utility functions
slug: groundhog/guides/topics/general
section: Groundhog Guides
description: Overview of groundhog's general and utility functions functionality with links to the API reference.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/docs/general/general_toplevel.rst
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Upstream toctree/autodoc structure restructured into a single topic page that links to the API reference instead of duplicating it, with a short note on how to run this in GeoCore prepended.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/general/general_toplevel.html
---

> **Adapted from groundhog's own documentation.** Inside GeoCore, these functions run through the [calculation catalogue](/docs/geocore/using/modules) or through **GeoAI**, which selects and calls them through its validated Tool Registry — you never need to install Python or groundhog yourself.

This page follows the structure of the upstream groundhog documentation for *General and utility functions*. For each function it gives the method summary and key formulas from the groundhog docstrings, with a link to the full API reference.

## Soil profiles and gridscd

Upstream page: [Soil profiles and gridscd](https://groundhog.readthedocs.io/en/main/general/soilprofiles.html)

### SoilProfile

Class [`SoilProfile`](/docs/groundhog/api/general/soilprofile#soilprofile).

A SoilProfile object is a Pandas dataframe with specific functionality for geotechnical calculations.

### CalculationGrid

Class [`CalculationGrid`](/docs/groundhog/api/general/soilprofile#calculationgrid).

A CalculationGrid is an object which consist of a dataframe with nodes .nodes and a dataframe with elements .elements.

## Plotting

Upstream page: [Plotting](https://groundhog.readthedocs.io/en/main/general/plotting.html)

Module [`groundhog.general.plotting`](/docs/groundhog/api/general/plotting). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### plot_with_log

Function [`plot_with_log`](/docs/groundhog/api/general/plotting#plot_with_log).

Plots a given number of traces in a plot with a soil mini-log on the left hand side.

### LogPlot

Class [`LogPlot`](/docs/groundhog/api/general/plotting#logplot).

Class for planneled plots with a minilog on the side.

### LogPlotMatplotlib

Class [`LogPlotMatplotlib`](/docs/groundhog/api/general/plotting#logplotmatplotlib).

Class for planneled plots with a minilog on the side, using the Matplotlib plotting backend

### peak_picker

Function [`peak_picker`](/docs/groundhog/api/general/plotting#peak_picker).

Generates an interactive Matplotlib plot which allows you to pick the peak from a graph with e.g.

## Validation

Upstream page: [Validation](https://groundhog.readthedocs.io/en/main/general/validation.html)

Module [`groundhog.general.validation`](/docs/groundhog/api/general/validation). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### validate_float

Function [`validate_float`](/docs/groundhog/api/general/validation#validate_float).

Validates whether a variable can be used as a floating point number and whether it is within specified bounds If a value equals one of the bounds, the validation passes

### validate_integer

Function [`validate_integer`](/docs/groundhog/api/general/validation#validate_integer).

Validates whether a variable can be used as an integer and whether it is within specified bounds If a value equals one of the bounds, the validation passes

### validate_boolean

Function [`validate_boolean`](/docs/groundhog/api/general/validation#validate_boolean).

Validates whether a variable can be used as a boolean

### validate_string

Function [`validate_string`](/docs/groundhog/api/general/validation#validate_string).

Validates whether a variable can be used as a string.

### validate_list

Function [`validate_list`](/docs/groundhog/api/general/validation#validate_list).

Validates whether a list contains numbers.

### map_args

Function [`map_args`](/docs/groundhog/api/general/validation#map_args).

Constructs a data structure with all parameters, their values and the validation parameters which need to be used during validation.

### Validator

Class [`Validator`](/docs/groundhog/api/general/validation#validator).

The Validator has the following features

### check_layer_overlap

Function [`check_layer_overlap`](/docs/groundhog/api/general/validation#check_layer_overlap).

Checks possible overlap on a dataframe

## AGS to Pandas converter reference

Upstream page: [AGS to Pandas converter reference](https://groundhog.readthedocs.io/en/main/general/agsconversion.html)

### AGSConverter

Class [`AGSConverter`](/docs/groundhog/api/general/agsconversion#agsconverter).

## Parameter mapping

Upstream page: [Parameter mapping](https://groundhog.readthedocs.io/en/main/general/parameter_mapping.html)

Module [`groundhog.general.parameter_mapping`](/docs/groundhog/api/general/parameter_mapping). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

### map_depth_properties

Function [`map_depth_properties`](/docs/groundhog/api/general/parameter_mapping#map_depth_properties).

Maps properties defined in a dataframe with layers to a dataframe with nodal depth positions.

### merge_two_dicts

Function [`merge_two_dicts`](/docs/groundhog/api/general/parameter_mapping#merge_two_dicts).

Merges two dictionaries

### reverse_dict

Function [`reverse_dict`](/docs/groundhog/api/general/parameter_mapping#reverse_dict).

Turn dictionary keys into values and values into keys

### latlon_distance

Function [`latlon_distance`](/docs/groundhog/api/general/parameter_mapping#latlon_distance).

Calculates the offset in meters from two pairs of coordinates specified in longitude and latitude (WGS84)

### get_projected_point

Function [`get_projected_point`](/docs/groundhog/api/general/parameter_mapping#get_projected_point).

Finds the coordinates of a point projected onto a line

### offsets

Function [`offsets`](/docs/groundhog/api/general/parameter_mapping#offsets).

Calculates the offset between a point and a line joining a given start- and endpoint.
