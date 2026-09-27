---
title: Pipelines and cables
slug: groundhog/guides/topics/pipelinescables
section: Groundhog Guides
description: Overview of groundhog's pipelines and cables functionality with links to the API reference.
origin: groundhog
source_url: https://github.com/snakesonabrain/groundhog/blob/v0.15.0/docs/pipelinescables/pipelinescables_toplevel.rst
license: GPL-3.0-or-later
author: Bruno Stuyts
attribution: Adapted from the groundhog documentation by Bruno Stuyts (https://github.com/snakesonabrain/groundhog), licensed under the GNU GPL v3 or later.
groundhog_version: 0.15.0
edited_by_geocore: true
geocore_edit_note: Upstream toctree/autodoc structure restructured into a single topic page that links to the API reference instead of duplicating it.
upstream_docs_url: https://groundhog.readthedocs.io/en/main/pipelinescables/pipelinescables_toplevel.html
---

This page follows the structure of the upstream groundhog documentation for *Pipelines and cables*. For each function it gives the method summary and key formulas from the groundhog docstrings, with a link to the full API reference.

## Pipeline and cable stability

Upstream page: [Pipeline and cable stability](https://groundhog.readthedocs.io/en/main/pipelinescables/stability_toplevel.html)

### Pipeline and cable penetration

Upstream page: [Pipeline and cable penetration](https://groundhog.readthedocs.io/en/main/pipelinescables/penetration.html)

Module [`groundhog.pipelinescables.stability.penetration`](/docs/groundhog/api/pipelinescables/stability/penetration). Summaries and formulas below are taken from the docstrings; the API reference has parameters, units and outputs.

#### contactwidth

Function [`contactwidth`](/docs/groundhog/api/pipelinescables/stability/penetration#contactwidth).

Calculates the contact width depending on the pipeline penetration.

$$
B = 2 \cdot \sqrt{D \cdot z - z^2} \quad \text{for } z < D/2
$$

$$
B=D \quad \text{for } z \geq D/2
$$

*Reference:* DNV-RP-F114

#### penetratedarea

Function [`penetratedarea`](/docs/groundhog/api/pipelinescables/stability/penetration#penetratedarea).

Calculates the penetrated area of the pipeline below the seabed.

$$
A_{bm} = \arcsin \left( \frac{B}{D} \right) \cdot \frac{D^2}{4} - B \cdot \frac{D}{4} \cdot \cos \left( \arcsin(B/D) \right) \quad \text{for } z<D/2
$$

$$
A_{bm} = \frac{\pi \cdot D^2}{8} + D \cdot \left( z - D/2 \right) \quad \text{for } z \geq D/2
$$

*Reference:* DNV-RP-F114

#### embedment_undrained_method1

Function [`embedment_undrained_method1`](/docs/groundhog/api/pipelinescables/stability/penetration#embedment_undrained_method1).

Calculates pipeline embedment in soil which behaves in an undrained manner.

$$
Q_v = Q_{v0} \cdot \left( 1 + d_{ca} \right) + \gamma^{\prime} \cdot A_{bm}
$$

$$
Q_{v0} = F \cdot \left( N_c \cdot s_{u,0} + \rho \cdot B/4 \right) \cdot B
$$

*6 more formulas in the full reference.*

*Reference:* DNV-RP-F114

#### embedment_undrained_method2

Function [`embedment_undrained_method2`](/docs/groundhog/api/pipelinescables/stability/penetration#embedment_undrained_method2).

Calculates the pipeline penetration for deepwater soft clay.

$$
Q_v = \left[ \min \left( 6 \cdot \left( \frac{z}{D} \right)^{0.25}; 3.4 \cdot \left( \frac{10 \cdot z}{D} \right)^{0.5} \right) + 1.5 \cdot \frac{\gamma^{\prime} \cdot A_{bm}}{D \cdot s_u} \right] \cdot D \cdot s_u
$$

*Reference:* DNV-RP-F114

#### embedment_drained

Function [`embedment_drained`](/docs/groundhog/api/pipelinescables/stability/penetration#embedment_drained).

Calculates pipeline embedment in drained conditions using bearing capacity theory.

$$
Q_v = 0.5 \cdot \gamma^{\prime} \cdot N_{\gamma} \cdot B^2 + z_0 \cdot \gamma^{\prime} \cdot N_q \cdot d_q \cdot B
$$

$$
z_0 = 0 \quad \text{for } z < \frac{D}{2} \cdot \left[ 1 - \cos \left( \frac{\pi}{4} + \frac{\varphi^{\prime}}{2} \right) \right]
$$

*2 more formulas in the full reference.*

*Reference:* DNV-RP-F114

#### lay_touchdown_factor

Function [`lay_touchdown_factor`](/docs/groundhog/api/pipelinescables/stability/penetration#lay_touchdown_factor).

Calculates the load concentration factor at the touchdown point.

$$
k_{lay} = 0.6 + 0.4 \cdot \left( \frac{EI \cdot k \cdot W_i}{z_{ini} \cdot T_0^2} \right)^{0.25} \geq 1 \quad \text{for } T_0 > \left[ 3 \cdot \sqrt{EI} \cdot W_i \right]^{2/3}
$$

$$
k = Q_v \ W_i
$$

*Reference:* DNV-RP-F114
