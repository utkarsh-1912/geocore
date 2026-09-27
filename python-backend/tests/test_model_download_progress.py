# Author: Utkarsh Gupta
# License: GPL v3
"""Tests for GGUF model download progress reporting (percent / speed / ETA)."""

import pytest

from core.geoai import model_downloader as md


def test_compute_progress_first_sample():
    stats = md.compute_progress(
        downloaded_bytes=50, total_bytes=200, prev_bytes=0, dt_seconds=1.0, prev_speed_bps=None
    )
    assert stats["percent"] == pytest.approx(25.0)
    assert stats["speed_bps"] == pytest.approx(50.0)
    assert stats["eta_seconds"] == pytest.approx(3.0)  # 150 bytes left at 50 B/s


def test_compute_progress_smooths_speed():
    stats = md.compute_progress(
        downloaded_bytes=200, total_bytes=1000, prev_bytes=100, dt_seconds=1.0, prev_speed_bps=200.0
    )
    # 0.3 * 100 + 0.7 * 200
    assert stats["speed_bps"] == pytest.approx(170.0)
    assert stats["eta_seconds"] == pytest.approx(800 / 170.0)


def test_compute_progress_unknown_total():
    stats = md.compute_progress(
        downloaded_bytes=100, total_bytes=None, prev_bytes=0, dt_seconds=1.0, prev_speed_bps=None
    )
    assert stats["percent"] is None
    assert stats["eta_seconds"] is None
    assert stats["speed_bps"] == pytest.approx(100.0)


def test_compute_progress_clamps_percent():
    stats = md.compute_progress(
        downloaded_bytes=1100, total_bytes=1000, prev_bytes=1000, dt_seconds=1.0, prev_speed_bps=None
    )
    assert stats["percent"] == 100.0
    assert stats["eta_seconds"] == 0.0


def test_compute_progress_zero_dt_keeps_previous_speed():
    stats = md.compute_progress(
        downloaded_bytes=500, total_bytes=1000, prev_bytes=500, dt_seconds=0.0, prev_speed_bps=250.0
    )
    assert stats["speed_bps"] == 250.0
    assert stats["eta_seconds"] == pytest.approx(2.0)


def test_partial_download_size_reads_part_file(tmp_path):
    fname = "model-q4_k_m.gguf"
    assert md._partial_download_size(tmp_path, fname) == 0

    (tmp_path / f"{fname}.part").write_bytes(b"x" * 1234)
    (tmp_path / "other.gguf.part").write_bytes(b"x" * 9999)
    assert md._partial_download_size(tmp_path, fname) == 1234


def test_download_status_exposes_progress_fields():
    status = md.get_download_status()
    for key in ("downloaded_bytes", "total_bytes", "percent", "speed_bps", "eta_seconds", "elapsed_seconds"):
        assert key in status
