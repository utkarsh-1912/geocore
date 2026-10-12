---
title: Indian Standard (BIS) calculations
slug: geocore/using/indian-standards
section: Using GeoCore
nav_order: 35
description: Theory, equations, clause references and inputs for GeoCore's IS 6403, IS 1498, IS 2131, IS 1892, IS 1904, IS 2950 and IS 2720 calculators.
sources:
- python-backend/core/standards/bis/README.md
- website/_build/bis_docs.py
---

GeoCore implements a set of Indian Standard (Bureau of Indian Standards) calculations that groundhog does not
cover. They are in the app under **Indian Standards (BIS)** in the *Library* view (and under their engineering task
in the *By task* view), and GeoAI can call them as validated tools.

Each calculation takes SI inputs and cites the clause it applies. Inputs outside the scope of a clause are reported
as errors, never adjusted. Clause notes come back as warnings with the result.

The sections below are generated from the same source as the app's Guide & Theory pages
(`website/_build/bis_docs.py`). Parameter descriptions and units are read from the implementation, so they match
the calculator.

> **Editions implemented.**
> - IS 6403:1981 (Reaffirmed) with Amendment 1. Under revision by BIS.
> - IS 1904:2021.
> - IS 1892:2021.
> - IS 2131:1981. The 2025 revision is not encoded.
> - IS 1498:1970.
> - IS 2950 (Part 1):1981 with Amendment 1.
> - IS 2720 Parts 3/Sec 1 (1980), 5 (1985) and 17 (1986).
>
> Check results against the current edition of each code. BIS code texts are copyrighted and are not included
> with GeoCore.

<!-- geocore:generated indian-standards -->
