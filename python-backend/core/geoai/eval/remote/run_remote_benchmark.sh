#!/usr/bin/env bash
# Author: Utkarsh Gupta
# License: GPL v3
#
# GeoAI remote benchmark runner (AGENTS.md §21, §31-32).
#
# Runs the GeoAI benchmark harness (python -m core.geoai.eval.benchmark) on a rented Linux box -
# an AWS GPU instance (Deep Learning AMI, NVIDIA driver) or a CPU-only machine - and packs the
# results into one archive to copy back to the desktop. Nothing here creates cloud resources.
#
# Usage:
#   bash run_remote_benchmark.sh [options] JOB [JOB ...]
#
# Jobs (run in the order given; completed result files are skipped, so re-running resumes):
#   setup       venv, requirements, llama-cpp-python (CUDA wheel if nvidia-smi works, else CPU), eval data
#   compact-ab  qwen3-1.7b, GEOAI_COMPACT_SCHEMAS=0 vs 1, the same stratified 40 eval_test examples as cpu-test40
#   models      every candidate in $MODELS (default: all benchmark candidates) + heuristic baseline, same 40 examples
#   lora        $LORA_BASE (default qwen3-1.7b) vs base + adapter --lora PATH, full eval_test, go/no-go
#   full-test   $FULL_MODELS (default qwen3-1.7b) + heuristic on the whole eval_test split
#   pack        tar the results (also done automatically at the end of every invocation)
#   all         compact-ab models full-test (+ lora when --lora is given)
#
# Options (each also settable as the environment variable in brackets):
#   --repo URL       git URL to clone if no checkout exists              [GEOCORE_REPO_URL]
#   --ref REF        branch/tag/commit to clone (default: default branch) [GEOCORE_REF]
#   --tarball FILE   .tar.gz of the repo (or of python-backend/) instead of git [GEOCORE_TARBALL]
#   --work DIR       working directory (default ~/geoai-bench)           [WORK_DIR]
#   --lora PATH      GGUF LoRA adapter for the lora job (sidecar PATH.json next to it) [LORA_PATH]
#   --models LIST    comma-separated candidate keys for the models job   [MODELS]
#   --prefix NAME    run-id prefix (default remote-gpu / remote-cpu)      [RUN_PREFIX]
#   --cpu            force the CPU build even if a GPU is present        [FORCE_CPU=1]
# Other environment knobs: LIMIT (40), N_CTX (4096), MAX_TOOLS (5), N_GPU_LAYERS (-1 GPU / 0 CPU),
#   LLAMA_CPP_VERSION (0.3.35), LLAMA_CUDA_TAG (auto: cu124 or older to fit the driver),
#   LORA_BASE (qwen3-1.7b), LORA_LIMIT (empty = full split), FULL_MODELS (qwen3-1.7b),
#   NO_VENV=1 (install into the current python3 instead of a venv; used by the Colab notebook).
#
# If this script is run from inside a GeoCore checkout (python-backend/core/geoai/eval/remote/), that
# checkout is used and nothing is cloned.
#
# Examples:
#   bash run_remote_benchmark.sh --repo https://github.com/<you>/geocore.git compact-ab
#   bash geocore/python-backend/core/geoai/eval/remote/run_remote_benchmark.sh models full-test
#   bash run_remote_benchmark.sh --lora ~/geoai-lora.gguf lora

set -euo pipefail

# ---------------------------------------------------------------- settings
LLAMA_CPP_VERSION="${LLAMA_CPP_VERSION:-0.3.35}"   # same version as the desktop venv
WHEEL_BASE="https://abetlen.github.io/llama-cpp-python/whl"
WORK_DIR="${WORK_DIR:-$HOME/geoai-bench}"
GEOCORE_REPO_URL="${GEOCORE_REPO_URL:-}"
GEOCORE_REF="${GEOCORE_REF:-}"
GEOCORE_TARBALL="${GEOCORE_TARBALL:-}"
LORA_PATH="${LORA_PATH:-}"
LORA_BASE="${LORA_BASE:-qwen3-1.7b}"
LORA_LIMIT="${LORA_LIMIT:-}"
MODELS="${MODELS:-}"
FULL_MODELS="${FULL_MODELS:-qwen3-1.7b}"
LIMIT="${LIMIT:-40}"
N_CTX="${N_CTX:-4096}"
MAX_TOOLS="${MAX_TOOLS:-5}"
FORCE_CPU="${FORCE_CPU:-0}"
RUN_PREFIX="${RUN_PREFIX:-}"

JOBS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) GEOCORE_REPO_URL="$2"; shift 2 ;;
    --ref) GEOCORE_REF="$2"; shift 2 ;;
    --tarball) GEOCORE_TARBALL="$2"; shift 2 ;;
    --work) WORK_DIR="$2"; shift 2 ;;
    --lora) LORA_PATH="$2"; shift 2 ;;
    --models) MODELS="$2"; shift 2 ;;
    --prefix) RUN_PREFIX="$2"; shift 2 ;;
    --cpu) FORCE_CPU=1; shift ;;
    -h|--help) sed -n '2,44p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    setup|compact-ab|models|lora|full-test|pack|all) JOBS+=("$1"); shift ;;
    *) echo "unknown argument: $1 (see --help)" >&2; exit 2 ;;
  esac
done
[[ ${#JOBS[@]} -gt 0 ]] || { echo "no job given (setup|compact-ab|models|lora|full-test|pack|all), see --help" >&2; exit 2; }

log() { printf '\n[%s] %s\n' "$(date -u +%H:%M:%S)" "$*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

mkdir -p "$WORK_DIR"
WORK_DIR="$(cd "$WORK_DIR" && pwd)"
VENV="$WORK_DIR/venv"
PY="$VENV/bin/python"
if [[ "${NO_VENV:-0}" == "1" ]]; then   # Colab: install into the notebook's own Python
  PY="$(command -v python3)"
fi
ENV_FILE="$WORK_DIR/env.sh"          # extra LD_LIBRARY_PATH etc. found during setup
# Models + GeoAI config live here, isolated from any ~/.geocore (defaults = desktop defaults).
export GEOCORE_CONFIG_DIR="$WORK_DIR/geocore-config"
export PIP_DISABLE_PIP_VERSION_CHECK=1
unset GEOAI_THINKING GEOAI_LORA_PATH GEOAI_CHAT_FORMAT GEOAI_COMPACT_SCHEMAS || true

# ---------------------------------------------------------------- hardware
HAS_GPU=0
if [[ "$FORCE_CPU" != "1" ]] && command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi -L >/dev/null 2>&1; then
  HAS_GPU=1
fi
N_GPU_LAYERS="${N_GPU_LAYERS:-$([[ $HAS_GPU == 1 ]] && echo -1 || echo 0)}"
RUN_PREFIX="${RUN_PREFIX:-$([[ $HAS_GPU == 1 ]] && echo remote-gpu || echo remote-cpu)}"

# ---------------------------------------------------------------- code
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
locate_backend() {
  # 1) the checkout this script lives in; 2) $WORK_DIR/geocore (clone or tarball)
  local own; own="$(cd "$SCRIPT_DIR/../../../.." 2>/dev/null && pwd || true)"
  if [[ -n "$own" && -f "$own/core/geoai/eval/benchmark.py" && -f "$own/requirements.txt" ]]; then
    BACKEND="$own"; return
  fi
  local src="$WORK_DIR/geocore"
  if [[ ! -d "$src" ]]; then
    if [[ -n "$GEOCORE_TARBALL" ]]; then
      log "extracting $GEOCORE_TARBALL -> $src"
      mkdir -p "$src.part" && tar -xzf "$GEOCORE_TARBALL" -C "$src.part" && mv "$src.part" "$src"
    elif [[ -n "$GEOCORE_REPO_URL" ]]; then
      log "cloning $GEOCORE_REPO_URL ${GEOCORE_REF:+(ref $GEOCORE_REF)} -> $src"
      command -v git >/dev/null || die "git is required"
      if [[ -n "$GEOCORE_REF" ]]; then
        git clone "$GEOCORE_REPO_URL" "$src.part" && git -C "$src.part" checkout -q "$GEOCORE_REF"
      else
        git clone --depth 1 "$GEOCORE_REPO_URL" "$src.part"
      fi
      mv "$src.part" "$src"
    else
      die "no GeoCore code: run from a checkout, or pass --repo URL or --tarball FILE"
    fi
  fi
  local found
  found="$(find "$src" -maxdepth 6 -path '*/core/geoai/eval/benchmark.py' -print -quit 2>/dev/null || true)"
  [[ -n "$found" ]] || die "no python-backend/core/geoai/eval/benchmark.py under $src"
  BACKEND="$(cd "$(dirname "$found")/../../.." && pwd)"
}
locate_backend
RESULTS="$BACKEND/core/geoai/eval/results/benchmark"
log "backend: $BACKEND  gpu=$HAS_GPU  n_gpu_layers=$N_GPU_LAYERS  prefix=$RUN_PREFIX"

# ---------------------------------------------------------------- setup
cuda_tag() {
  # Prebuilt CUDA wheels: cu121 cu122 cu123 cu124 cu125 (CUDA 12, compute >= 6.0; a T4 is 7.5) and
  # cu130/cu132. Pick cu124 (or older if the driver's CUDA version is lower). Override: LLAMA_CUDA_TAG.
  if [[ -n "${LLAMA_CUDA_TAG:-}" ]]; then echo "$LLAMA_CUDA_TAG"; return; fi
  local v major minor
  v="$(nvidia-smi 2>/dev/null | sed -n 's/.*CUDA Version: *\([0-9][0-9]*\.[0-9][0-9]*\).*/\1/p' | head -1)"
  major="${v%%.*}"; minor="${v#*.}"
  if [[ -z "$v" || "$major" -gt 12 ]] || { [[ "$major" -eq 12 ]] && [[ "$minor" -ge 4 ]]; }; then echo cu124
  elif [[ "$major" -eq 12 && "$minor" -ge 2 ]]; then echo cu122
  elif [[ "$major" -eq 12 ]]; then echo cu121
  else die "driver CUDA version $v < 12.0: no matching prebuilt wheel (set LLAMA_CUDA_TAG or update the driver)"
  fi
}

llama_check() {  # prints "<version> gpu_offload=<bool>", non-zero exit if the import fails
  ( [[ -f "$ENV_FILE" ]] && source "$ENV_FILE"; "$PY" - <<'EOF'
import llama_cpp
print(llama_cpp.__version__, "gpu_offload=%s" % bool(llama_cpp.llama_supports_gpu_offload()))
EOF
  )
}

install_llama() {
  local idx="$1"
  log "installing llama-cpp-python==$LLAMA_CPP_VERSION from $WHEEL_BASE/$idx (prebuilt wheel)"
  # Only the wheel index and wheels only (PyPI has just the sdist, which would silently build a
  # CPU-only library); then llama-cpp-python's small pure-Python dependencies from PyPI.
  "$PY" -m pip install --no-cache-dir --no-deps --only-binary=:all: --index-url "$WHEEL_BASE/$idx" \
      "llama-cpp-python==$LLAMA_CPP_VERSION" || return 1
  "$PY" -m pip install "numpy>=1.20.0" "typing-extensions>=4.5.0" "diskcache>=5.6.1" "jinja2>=2.11.3"
}

fix_cuda_libs() {
  # Import failed (e.g. libcudart.so.12 / libcublas.so.12 not found): try the system CUDA 12 toolkit,
  # then NVIDIA's pip runtime packages. Whatever works is written to env.sh and sourced for every run.
  local d
  for d in /usr/local/cuda-12*/lib64 /usr/local/cuda/lib64; do
    [[ -d "$d" ]] || continue
    echo "export LD_LIBRARY_PATH=\"$d:\${LD_LIBRARY_PATH:-}\"" > "$ENV_FILE"
    llama_check >/dev/null 2>&1 && { log "using CUDA libraries from $d"; return 0; }
  done
  log "installing NVIDIA CUDA 12 runtime wheels"
  "$PY" -m pip install --no-cache-dir nvidia-cuda-runtime-cu12 nvidia-cublas-cu12
  local libs
  libs="$("$PY" -c 'import glob, os, nvidia; print(":".join(sorted({os.path.dirname(p) for b in nvidia.__path__ for p in glob.glob(os.path.join(b, "*", "lib", "*.so*"))})))')"
  echo "export LD_LIBRARY_PATH=\"$libs:\${LD_LIBRARY_PATH:-}\"" > "$ENV_FILE"
  llama_check >/dev/null 2>&1
}

do_setup() {
  local marker="$WORK_DIR/.setup-done"
  local want; want="llama=$LLAMA_CPP_VERSION gpu=$HAS_GPU req=$(sha256sum "$BACKEND/requirements.txt" | cut -c1-16)"
  if [[ -f "$marker" && "$(cat "$marker")" == "$want" && -x "$PY" ]] && llama_check >/dev/null 2>&1; then
    log "setup already done ($want): $(llama_check)"
  else
    command -v python3 >/dev/null || die "python3 is required"
    "$(command -v python3)" -c 'import sys; assert sys.version_info >= (3, 10), sys.version' \
      || die "Python >= 3.10 required"
    if [[ ! -x "$PY" ]]; then
      log "creating venv $VENV"
      if ! python3 -m venv "$VENV"; then
        log "python3-venv missing; installing it (sudo apt-get)"
        sudo apt-get update -y && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv
        python3 -m venv "$VENV"
      fi
    fi
    [[ "${NO_VENV:-0}" == "1" ]] || "$PY" -m pip install -q --upgrade pip wheel
    if [[ $HAS_GPU == 1 ]]; then
      local tag; tag="$(cuda_tag)"
      if ! install_llama "$tag"; then
        log "no prebuilt $tag wheel fits; building from source with CUDA (needs nvcc, ~10-20 min)"
        export PATH="/usr/local/cuda/bin:$PATH"
        CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 "$PY" -m pip install --no-cache-dir \
          "llama-cpp-python==$LLAMA_CPP_VERSION"
      fi
      llama_check >/dev/null 2>&1 || fix_cuda_libs || die "llama_cpp does not import; see the messages above"
      llama_check | grep -q "gpu_offload=True" || die "llama-cpp-python has no GPU offload (CPU build installed?)"
    else
      if ! install_llama cpu; then
        log "no prebuilt CPU wheel fits; building from source (~5-10 min)"
        "$PY" -m pip install --no-cache-dir "llama-cpp-python==$LLAMA_CPP_VERSION"
      fi
    fi
    log "installing GeoCore backend requirements (llama-cpp-python already pinned)"
    grep -viE '^[[:space:]]*llama-cpp-python' "$BACKEND/requirements.txt" > "$WORK_DIR/requirements.nollama.txt"
    "$PY" -m pip install -r "$WORK_DIR/requirements.nollama.txt"
    echo "$want" > "$marker"
    log "llama-cpp-python: $(llama_check)"
  fi
  # Eval data is git-ignored; regenerate it deterministically once (same seed/generator as the desktop).
  if [[ ! -f "$BACKEND/core/geoai/training/data/eval_test.jsonl" ]]; then
    log "generating the GeoAI eval/SFT data (deterministic, a few minutes)"
    (cd "$BACKEND" && "$PY" -m core.geoai.training.scaleup --out core/geoai/training/data >/dev/null)
  fi
}

# ---------------------------------------------------------------- helpers
bench() { ( [[ -f "$ENV_FILE" ]] && source "$ENV_FILE"; cd "$BACKEND" && "$PY" -m core.geoai.eval.benchmark "$@" ); }
pymod() { ( [[ -f "$ENV_FILE" ]] && source "$ENV_FILE"; cd "$BACKEND" && "$PY" -m "$@" ); }

download() {  # download candidate GGUFs (skips files already present)
  local k
  for k in "$@"; do bench download "$k"; done
}

write_meta() {  # $1 = run-id, rest = "key=value" settings
  local run_id="$1"; shift
  local dir="$RESULTS/$run_id/remote"
  mkdir -p "$dir"
  local gpu="" driver="" cuda="" itype=""
  if [[ $HAS_GPU == 1 ]]; then
    gpu="$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1)"
    driver="$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)"
    cuda="$(nvidia-smi | sed -n 's/.*CUDA Version: *\([0-9.]*\).*/\1/p' | head -1)"
  fi
  # EC2 instance type via IMDSv2 (no credentials involved); empty elsewhere.
  local tok
  tok="$(curl -s -m 2 -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' 2>/dev/null || true)"
  [[ -n "$tok" ]] && itype="$(curl -s -m 2 -H "X-aws-ec2-metadata-token: $tok" http://169.254.169.254/latest/meta-data/instance-type 2>/dev/null || true)"
  local commit="" dirty=""
  if git -C "$BACKEND" rev-parse HEAD >/dev/null 2>&1; then
    commit="$(git -C "$BACKEND" rev-parse HEAD)"
    [[ -n "$(git -C "$BACKEND" status --porcelain -- . 2>/dev/null | grep -v 'eval/results/' || true)" ]] && dirty=1
  fi
  ( [[ -f "$ENV_FILE" ]] && source "$ENV_FILE"
    GPU="$gpu" DRIVER="$driver" CUDA="$cuda" ITYPE="$itype" COMMIT="$commit" DIRTY="$dirty" \
    TARBALL="$GEOCORE_TARBALL" BACKEND="$BACKEND" NGL="$N_GPU_LAYERS" \
    "$PY" - "$dir/run_metadata.json" "$run_id" "$@" <<'EOF'
import hashlib, json, os, platform, sys
from datetime import datetime, timezone
out, run_id, settings = sys.argv[1], sys.argv[2], dict(a.split("=", 1) for a in sys.argv[3:])
def sha(p):
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()
    except OSError:
        return None
try:
    import llama_cpp
    llama = {"version": llama_cpp.__version__, "gpu_offload": bool(llama_cpp.llama_supports_gpu_offload())}
except Exception as e:  # recorded, not fatal
    llama = {"error": str(e)}
cpu = ""
try:
    cpu = next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), "")
except OSError:
    pass
meta = {
    "run_id": run_id,
    "written_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "instance_type": os.environ["ITYPE"] or None,
    "gpu": os.environ["GPU"] or None, "nvidia_driver": os.environ["DRIVER"] or None,
    "driver_cuda_version": os.environ["CUDA"] or None, "n_gpu_layers": int(os.environ["NGL"]),
    "cpu": cpu, "cpu_count": os.cpu_count(), "os": platform.platform(), "python": sys.version.split()[0],
    "llama_cpp_python": llama,
    "git_commit": os.environ["COMMIT"] or None, "git_dirty": bool(os.environ["DIRTY"]),
    "code_tarball": os.environ["TARBALL"] or None,
    "eval_test_sha256": sha(os.path.join(os.environ["BACKEND"], "core/geoai/training/data/eval_test.jsonl")),
    "settings": settings,
}
json.dump(meta, open(out, "w"), indent=1)
print("wrote", out)
EOF
  )
}

done_file() { [[ -f "$RESULTS/$1/$2.json" ]]; }   # run-id, label

run_one() {  # run-id label log-name -- benchmark run args...  (one model/config per process)
  local run_id="$1" label="$2"; shift 2
  if done_file "$run_id" "$label"; then log "skip $run_id/$label (done)"; return 0; fi
  mkdir -p "$RESULTS/$run_id/remote/logs"
  log "run $run_id/$label"
  bench run --run-id "$run_id" "$@" 2>&1 | tee "$RESULTS/$run_id/remote/logs/$label.log"
  done_file "$run_id" "$label" || die "$run_id/$label produced no result file (see remote/logs/$label.log)"
}

finish_run() {  # leaderboard + desktop-latency estimate (both rebuilt from the result files)
  local run_id="$1"
  bench leaderboard --run-id "$run_id" | tail -n 20
  pymod core.geoai.eval.estimate_desktop_latency --run-id "$run_id" || log "estimate failed for $run_id (non-fatal)"
}

limit_args() { [[ -n "$1" ]] && echo "--limit $1" || true; }

common_args() {  # mode, n_ctx, tools, GPU layers: identical for every model in a run
  echo "--split test --mode decision --n-ctx $N_CTX --max-tools $MAX_TOOLS --n-gpu-layers $N_GPU_LAYERS"
}

# ---------------------------------------------------------------- jobs
job_compact_ab() {
  local run_id="$RUN_PREFIX-compact-ab-test$LIMIT"
  download qwen3-1.7b
  write_meta "$run_id" job=compact-ab limit="$LIMIT" chat_format=native
  # shellcheck disable=SC2046
  (export GEOAI_COMPACT_SCHEMAS=0
   run_one "$run_id" qwen3-1.7b --models qwen3-1.7b $(common_args) $(limit_args "$LIMIT") --chat-format native)
  # shellcheck disable=SC2046
  (export GEOAI_COMPACT_SCHEMAS=1
   run_one "$run_id" qwen3-1.7b-compact --models qwen3-1.7b --label-suffix=-compact \
     $(common_args) $(limit_args "$LIMIT") --chat-format native)
  finish_run "$run_id"
  mkdir -p "$RESULTS/$run_id/remote/comparisons"
  pymod core.geoai.eval.runner --compare "$RESULTS/$run_id/qwen3-1.7b.json" "$RESULTS/$run_id/qwen3-1.7b-compact.json" \
    --out "$RESULTS/$run_id/remote/comparisons/full_vs_compact.json"
}

model_keys() {  # $MODELS or every candidate
  if [[ -n "$MODELS" ]]; then tr ',' ' ' <<<"$MODELS"; return; fi
  ( cd "$BACKEND" && "$PY" -c 'from core.geoai.eval.benchmark import CANDIDATES; print(" ".join(CANDIDATES))' )
}

chat_format_for() {  # native for template tool-callers (as in cpu-test40); auto for prompted models (Gemma 3)
  ( cd "$BACKEND" && "$PY" -c "from core.geoai.eval.benchmark import CANDIDATES as C; import sys
print('' if C['$1'].tool_format.startswith('prompted') else '--chat-format native')" )
}

job_models() {
  local run_id="$RUN_PREFIX-models-test$LIMIT" k
  local keys; keys="$(model_keys)"
  # shellcheck disable=SC2086
  download $keys
  write_meta "$run_id" job=models limit="$LIMIT" models="$(tr ' ' ',' <<<"$keys")"
  # shellcheck disable=SC2046
  run_one "$run_id" heuristic --models "" --heuristic $(common_args) $(limit_args "$LIMIT")
  for k in $keys; do
    # shellcheck disable=SC2046
    run_one "$run_id" "$k" --models "$k" $(common_args) $(limit_args "$LIMIT") $(chat_format_for "$k")
  done
  finish_run "$run_id"
}

job_lora() {
  [[ -n "$LORA_PATH" ]] || die "lora job needs --lora PATH (GGUF LoRA adapter)"
  [[ -f "$LORA_PATH" ]] || die "adapter not found: $LORA_PATH"
  LORA_PATH="$(cd "$(dirname "$LORA_PATH")" && pwd)/$(basename "$LORA_PATH")"
  [[ -f "$LORA_PATH.json" ]] || log "WARNING: no sidecar $LORA_PATH.json; the provider may refuse the adapter"
  local tag; tag="$(basename "$LORA_PATH" .gguf)"
  local run_id="$RUN_PREFIX-lora-$tag-test${LORA_LIMIT:-full}"
  download "$LORA_BASE"
  write_meta "$run_id" job=lora lora_path="$LORA_PATH" lora_sha256="$(sha256sum "$LORA_PATH" | cut -d' ' -f1)" \
    base="$LORA_BASE" limit="${LORA_LIMIT:-full}" chat_format=native
  # base and adapter in separate processes; same examples, native template, thinking off
  # shellcheck disable=SC2046
  run_one "$run_id" "$LORA_BASE" --models "$LORA_BASE" $(common_args) $(limit_args "$LORA_LIMIT") --chat-format native
  # shellcheck disable=SC2046
  run_one "$run_id" "$LORA_BASE+geoai-lora" --models "$LORA_BASE" --lora "$LORA_BASE=$LORA_PATH" \
    $(common_args) $(limit_args "$LORA_LIMIT") --chat-format native
  finish_run "$run_id"
  mkdir -p "$RESULTS/$run_id/remote/comparisons"
  pymod core.geoai.eval.runner --compare "$RESULTS/$run_id/$LORA_BASE.json" "$RESULTS/$run_id/$LORA_BASE+geoai-lora.json" \
    --out "$RESULTS/$run_id/remote/comparisons/base_vs_lora.json"
  ( cd "$BACKEND" && "$PY" - "$RESULTS/$run_id" "$LORA_BASE" <<'EOF'
import json, sys
from pathlib import Path
from core.geoai.finetune.export import go_no_go
d, key = Path(sys.argv[1]), sys.argv[2]
base = json.loads((d / f"{key}.json").read_text(encoding="utf-8"))
cand = json.loads((d / f"{key}+geoai-lora.json").read_text(encoding="utf-8"))
adapter = (cand["meta"].get("model_info") or {}).get("lora_adapter") or {}
status = adapter.get("status")
decision = go_no_go(base, cand)
decision["adapter_status"] = status
decision["note"] = ("p50 latency criterion was measured on this machine (GPU), not on the desktop; "
                    "see desktop_latency_estimate.json and re-check latency on the desktop before shipping")
(d / "remote" / "comparisons" / "go_no_go.json").write_text(json.dumps(decision, indent=1), encoding="utf-8")
print(json.dumps(decision, indent=1))
if status != "active":
    print(f"WARNING: adapter status is {status!r}, so the '+geoai-lora' run used the base model only.")
EOF
  )
}

job_full_test() {
  local run_id="$RUN_PREFIX-full-test" k
  # shellcheck disable=SC2086
  download $(tr ',' ' ' <<<"$FULL_MODELS")
  write_meta "$run_id" job=full-test models="$FULL_MODELS" chat_format=native
  # shellcheck disable=SC2046
  run_one "$run_id" heuristic --models "" --heuristic $(common_args)
  for k in $(tr ',' ' ' <<<"$FULL_MODELS"); do
    # shellcheck disable=SC2046
    run_one "$run_id" "$k" --models "$k" $(common_args) $(chat_format_for "$k")
  done
  finish_run "$run_id"
}

job_pack() {
  [[ -d "$RESULTS" ]] || { log "nothing to pack yet"; return 0; }
  local runs; runs="$(cd "$RESULTS" && ls -d "$RUN_PREFIX"-* 2>/dev/null || true)"
  [[ -n "$runs" ]] || { log "no $RUN_PREFIX-* runs to pack"; return 0; }
  local archive="$WORK_DIR/geoai-benchmark-results-$RUN_PREFIX.tar.gz"
  # paths relative to python-backend/, so `tar -xzf` there drops them into place
  # shellcheck disable=SC2086
  (cd "$BACKEND" && tar -czf "$archive.part" $(for r in $runs; do echo "core/geoai/eval/results/benchmark/$r"; done))
  mv "$archive.part" "$archive"
  log "results archive: $archive ($(du -h "$archive" | cut -f1))"
  echo "copy it back with:  scp -i KEY.pem ubuntu@<public-ip>:$archive ."
}

# ---------------------------------------------------------------- main
do_setup
for job in "${JOBS[@]}"; do
  case "$job" in
    setup) ;;
    compact-ab) job_compact_ab ;;
    models) job_models ;;
    lora) job_lora ;;
    full-test) job_full_test ;;
    pack) ;;
    all) job_compact_ab; job_models; job_full_test; if [[ -n "$LORA_PATH" ]]; then job_lora; fi ;;
  esac
done
job_pack
log "done"
