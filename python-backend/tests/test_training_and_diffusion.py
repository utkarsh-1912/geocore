# Author: Utkarsh Gupta
# License: GPL v3
"""
Automated Test Suite for Geotechnical Dataset Generation, DPO Alignment,
Conditional Diffusion Modeling, and Local Model Management.
"""

import pytest
import numpy as np
from pathlib import Path

from core.geoai.training.dataset_generator import (
    build_core_training_examples,
    export_dataset_jsonl
)
from core.geoai.training.dpo_dataset import (
    build_dpo_preference_dataset,
    export_dpo_jsonl
)
from core.geoai.diffusion.stratigraphy_diffusion import (
    DiffusionSchedule,
    GeotechnicalDiffusionField1D,
    interpolate_cpt_profile_diffusion
)
from core.geoai.model_downloader import (
    list_available_models,
    RECOMMENDED_MODELS
)


# =====================================================================
# 1. SFT Training & Evaluation Dataset Generator Tests
# =====================================================================

def test_training_dataset_generator():
    examples = build_core_training_examples()
    assert len(examples) >= 10

    categories = {ex.category for ex in examples}
    assert "correct_request" in categories
    assert "ambiguous_request" in categories
    assert "missing_data" in categories
    assert "wrong_units" in categories
    assert "conflicting_data" in categories
    assert "research" in categories
    assert "tool_failure" in categories

    # Test ChatML conversion
    ex_tool = next(e for e in examples if e.expected_action == "tool_call")
    chatml = ex_tool.to_chatml()
    assert len(chatml) == 3
    assert chatml[0]["role"] == "system"
    assert chatml[1]["role"] == "user"
    assert chatml[2]["role"] == "assistant"
    assert chatml[2]["tool_calls"] is not None


def test_export_dataset_jsonl(tmp_path):
    jsonl_path = tmp_path / "sft_dataset.jsonl"
    count = export_dataset_jsonl(jsonl_path)
    assert count >= 10
    assert jsonl_path.exists()
    assert jsonl_path.stat().st_size > 0


# =====================================================================
# 2. DPO Preference Dataset Tests
# =====================================================================

def test_dpo_preference_dataset():
    pairs = build_dpo_preference_dataset()
    assert len(pairs) >= 4

    for p in pairs:
        assert len(p.prompt) > 0
        assert len(p.chosen) > 0
        assert len(p.rejected) > 0
        assert len(p.rationale) > 0


def test_export_dpo_jsonl(tmp_path):
    jsonl_path = tmp_path / "dpo_dataset.jsonl"
    count = export_dpo_jsonl(jsonl_path)
    assert count >= 4
    assert jsonl_path.exists()
    assert jsonl_path.stat().st_size > 0


# =====================================================================
# 3. Geotechnical Conditional Diffusion Tests
# =====================================================================

def test_diffusion_schedule():
    sched = DiffusionSchedule(num_timesteps=20)
    assert len(sched.betas) == 20
    assert len(sched.alphas_cumprod) == 20
    assert 0.0 < sched.alphas_cumprod[-1] < 1.0


def test_conditional_diffusion_exact_observation_matching():
    depth_grid = np.linspace(0.0, 10.0, 51)  # 0 to 10m every 0.2m
    field = GeotechnicalDiffusionField1D(depth_grid)

    obs = {2.0: 4.5, 6.0: 18.2, 8.0: 12.0}  # Known measurements
    sampled_profile = field.sample_conditioned(
        observations=obs,
        prior_mean=10.0,
        prior_std=3.0,
        spatial_correlation_length_m=1.5,
        seed=123
    )

    assert len(sampled_profile) == len(depth_grid)
    
    # Assert exact matching at observation depths
    idx_2m = int(np.argmin(np.abs(depth_grid - 2.0)))
    idx_6m = int(np.argmin(np.abs(depth_grid - 6.0)))
    idx_8m = int(np.argmin(np.abs(depth_grid - 8.0)))

    assert sampled_profile[idx_2m] == pytest.approx(4.5, abs=1e-3)
    assert sampled_profile[idx_6m] == pytest.approx(18.2, abs=1e-3)
    assert sampled_profile[idx_8m] == pytest.approx(12.0, abs=1e-3)


def test_interpolate_cpt_profile_diffusion():
    depth_grid = np.linspace(0.0, 5.0, 26)
    obs_z = [1.0, 3.0]
    obs_qc = [5.0, 15.0]

    res = interpolate_cpt_profile_diffusion(depth_grid, obs_z, obs_qc, seed=42)
    assert "qc_profile_mpa" in res
    assert len(res["qc_profile_mpa"]) == 26
    assert res["method"] == "Conditional Geotechnical DDPM Diffusion"


# =====================================================================
# 4. Model Downloader & Registry Tests
# =====================================================================

def test_model_downloader_list():
    models = list_available_models()
    assert len(models) >= 3
    model_ids = [m["id"] for m in models]
    assert "qwen2.5-1.5b-instruct" in model_ids
    assert "qwen2.5-3b-instruct" in model_ids
    assert "gemma-2-2b-it" in model_ids
    families = {m.get("family") for m in models}
    assert "qwen" in families
    assert "gemma" in families
