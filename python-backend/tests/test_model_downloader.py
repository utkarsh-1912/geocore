# Author: Utkarsh Gupta
# License: GPL v3
"""Tests for the resumable, checksum-verified GGUF downloader (network mocked)."""

import hashlib
import re

import pytest
import requests

from core.geoai import model_downloader as md

PAYLOAD = bytes(range(256)) * 40  # 10 240 bytes
PAYLOAD_SHA = hashlib.sha256(PAYLOAD).hexdigest()


class FakeResponse:
    def __init__(self, status_code, body=b"", fail_after=None):
        self.status_code = status_code
        self._body = body
        self._fail_after = fail_after

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}", response=self)

    def iter_content(self, chunk_size=1):
        sent = 0
        for i in range(0, len(self._body), 1000):
            if self._fail_after is not None and sent >= self._fail_after:
                raise requests.ConnectionError("connection reset")
            chunk = self._body[i:i + 1000]
            sent += len(chunk)
            yield chunk


class FakeSession:
    """Serves PAYLOAD honouring Range unless ``ignore_range``; scripted per-call overrides."""

    def __init__(self, payload=PAYLOAD, ignore_range=False, script=None):
        self.payload = payload
        self.ignore_range = ignore_range
        self.script = list(script or [])
        self.calls = []

    def get(self, url, headers=None, **kwargs):
        headers = headers or {}
        self.calls.append(headers.get("Range"))
        if self.script:
            action = self.script.pop(0)
            if isinstance(action, FakeResponse):
                return action
            if action == "drop":
                offset = self._offset(headers)
                return FakeResponse(206 if offset else 200, self.payload[offset:], fail_after=3000)
        offset = self._offset(headers)
        if offset and not self.ignore_range:
            if offset >= len(self.payload):
                return FakeResponse(416)
            return FakeResponse(206, self.payload[offset:])
        return FakeResponse(200, self.payload)

    @staticmethod
    def _offset(headers):
        rng = headers.get("Range")
        return int(re.match(r"bytes=(\d+)-", rng).group(1)) if rng else 0


@pytest.fixture(autouse=True)
def _no_backoff(monkeypatch):
    monkeypatch.setattr(md, "_RETRY_BACKOFF_SECONDS", 0.0)


def test_fresh_download_verifies_and_renames(tmp_path):
    dest = tmp_path / "m.gguf"
    session = FakeSession()
    out = md.download_file("u", dest, len(PAYLOAD), PAYLOAD_SHA, session=session)
    assert out == dest and dest.read_bytes() == PAYLOAD
    assert not (tmp_path / "m.gguf.part").exists()
    assert session.calls == [None]


def test_resumes_existing_part_with_range(tmp_path):
    dest = tmp_path / "m.gguf"
    (tmp_path / "m.gguf.part").write_bytes(PAYLOAD[:4000])
    session = FakeSession()
    md.download_file("u", dest, len(PAYLOAD), PAYLOAD_SHA, session=session)
    assert session.calls == ["bytes=4000-"]
    assert dest.read_bytes() == PAYLOAD


def test_server_ignoring_range_restarts_cleanly(tmp_path):
    dest = tmp_path / "m.gguf"
    (tmp_path / "m.gguf.part").write_bytes(b"garbage" * 100)
    md.download_file("u", dest, len(PAYLOAD), PAYLOAD_SHA, session=FakeSession(ignore_range=True))
    assert dest.read_bytes() == PAYLOAD


def test_retries_and_resumes_after_connection_drop(tmp_path):
    dest = tmp_path / "m.gguf"
    session = FakeSession(script=["drop"])
    md.download_file("u", dest, len(PAYLOAD), PAYLOAD_SHA, session=session)
    assert session.calls[0] is None
    assert session.calls[1] == "bytes=3000-"
    assert dest.read_bytes() == PAYLOAD


def test_range_not_satisfiable_means_part_complete(tmp_path):
    dest = tmp_path / "m.gguf"
    (tmp_path / "m.gguf.part").write_bytes(PAYLOAD)
    md.download_file("u", dest, len(PAYLOAD), PAYLOAD_SHA, session=FakeSession())
    assert dest.read_bytes() == PAYLOAD


def test_checksum_mismatch_deletes_part_and_keeps_no_dest(tmp_path):
    dest = tmp_path / "m.gguf"
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        md.download_file("u", dest, len(PAYLOAD), "0" * 64, session=FakeSession())
    assert not dest.exists()
    assert not (tmp_path / "m.gguf.part").exists()


def test_size_mismatch_rejected(tmp_path):
    dest = tmp_path / "m.gguf"
    with pytest.raises(ValueError, match="Size mismatch"):
        md.download_file("u", dest, len(PAYLOAD) + 1, None, session=FakeSession())
    assert not dest.exists()


def test_client_error_is_not_retried(tmp_path):
    session = FakeSession(script=[FakeResponse(404)])
    with pytest.raises(requests.HTTPError):
        md.download_file("u", tmp_path / "m.gguf", session=session)
    assert len(session.calls) == 1


def test_gives_up_after_max_attempts(tmp_path):
    session = FakeSession(script=["drop"] * 3)
    with pytest.raises(RuntimeError, match="after 3 attempts"):
        md.download_file("u", tmp_path / "m.gguf", session=session, max_attempts=3)


def test_resolve_url():
    assert md.hf_resolve_url("unsloth/Qwen3-1.7B-GGUF", "Qwen3-1.7B-Q4_K_M.gguf") == (
        "https://huggingface.co/unsloth/Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q4_K_M.gguf"
    )


@pytest.mark.parametrize("model_id", ["qwen3.5-2b", "qwen3-1.7b", "qwen2.5-1.5b-instruct"])
def test_benchmark_candidates_are_pinned(model_id):
    info = md.RECOMMENDED_MODELS[model_id]
    for key in ("family", "display_name", "repo_id", "filename", "size_mb", "description", "recommended_for"):
        assert info[key]
    assert info["filename"].endswith(".gguf")
    assert re.fullmatch(r"[0-9a-f]{64}", info["sha256"])
    assert abs(info["size_bytes"] / 2**20 - info["size_mb"]) < 1


def test_download_model_uses_verified_downloader(tmp_path, monkeypatch):
    captured = {}

    def fake_download_file(url, dest, expected_size=None, expected_sha256=None, **kw):
        captured.update(url=url, dest=dest, size=expected_size, sha=expected_sha256)
        dest.write_bytes(b"gguf")
        return dest

    monkeypatch.setattr(md, "get_default_model_dir", lambda: tmp_path)
    monkeypatch.setattr(md, "download_file", fake_download_file)
    path = md.download_model("qwen3-1.7b", set_as_active=False)
    info = md.RECOMMENDED_MODELS["qwen3-1.7b"]
    assert path == tmp_path / info["filename"]
    assert captured["url"].endswith(f"/{info['repo_id']}/resolve/main/{info['filename']}")
    assert captured["sha"] == info["sha256"] and captured["size"] == info["size_bytes"]
    assert md.get_download_status()["status"] == "completed"


def test_download_model_skips_already_installed(tmp_path, monkeypatch):
    info = md.RECOMMENDED_MODELS["qwen3-1.7b"]
    monkeypatch.setitem(info, "size_bytes", 4)
    (tmp_path / info["filename"]).write_bytes(b"gguf")
    monkeypatch.setattr(md, "get_default_model_dir", lambda: tmp_path)
    monkeypatch.setattr(md, "download_file", lambda *a, **k: pytest.fail("network used"))
    assert md.download_model("qwen3-1.7b", set_as_active=False) == tmp_path / info["filename"]
