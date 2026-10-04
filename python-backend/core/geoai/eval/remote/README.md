# GeoAI benchmarks on a rented GPU (AWS or Colab)

The reference laptop (i5-1235U, no GPU) needs about 40 min per model for 40 examples, so benchmarks
run elsewhere. Two ways to do that:

* **AWS**: `run_remote_benchmark.sh` on an EC2 GPU instance.
* **Colab** (free T4): `GeoAI_benchmark_colab.ipynb`, which calls the same script.

Both use the existing harness (`python -m core.geoai.eval.benchmark`) with the cpu-test40 settings:
`eval_test`, stratified 40 examples, decision mode, `n_ctx` 4096, 5 tools, native chat format. They also
set `--n-gpu-layers -1` and run each model or config in its own process.

Results come back as one archive. Unpack it in `python-backend/` and the run folders land in
`core/geoai/eval/results/benchmark/`.

| job | what | run id |
|---|---|---|
| `compact-ab` | qwen3-1.7b, `GEOAI_COMPACT_SCHEMAS=0` vs `1`, same 40 examples | `<prefix>-compact-ab-test40` |
| `models` | heuristic plus every candidate (`MODELS=a,b` to narrow), same 40 examples | `<prefix>-models-test40` |
| `lora` | `--lora PATH` adapter vs its base (qwen3-1.7b), full `eval_test`, go/no-go | `<prefix>-lora-<file>-testfull` |
| `full-test` | qwen3-1.7b plus heuristic on the whole `eval_test` split (325 examples) | `<prefix>-full-test` |

The prefix is `remote-gpu` or `remote-cpu`; Colab uses `colab-t4`.

Every run folder gets these files:

* `leaderboard.json`
* `desktop_latency_estimate.json`: the desktop latency is **estimated**, see below.
* `remote/run_metadata.json`: instance type, GPU, driver, CUDA, llama-cpp-python version, git commit and
  dirty flag, sha256 of `eval_test`, and the settings.
* `remote/logs/`
* `remote/comparisons/`, for `compact-ab` and `lora`. For `lora` this includes `go_no_go.json`.

Re-running a job skips any result file that already exists, so an interrupted run resumes where it stopped.

## Get the code to the box

The box needs the **current** code. The benchmark changes are `--label-suffix`, token counts and
`estimate_desktop_latency`. Do one of these:

* Commit and push, then let the script clone. Pass `--repo URL` and, optionally, `--ref BRANCH`.
* Upload a tarball of the working copy. It includes uncommitted changes and leaves out the venv and
  ignored files. From Git Bash in the repo root:

  ```bash
  git ls-files -co --exclude-standard python-backend | tar -czf geocore-backend.tar.gz -T -
  ```

The git-ignored eval data is regenerated on the box from the same seed. `run_metadata.json` records
its sha256, so you can check that it matches the desktop copy (`core/geoai/training/data/eval_test.jsonl`).

## AWS

### Instance

* **Recommended: `g4dn.xlarge`**. 1x NVIDIA T4 (16 GB), 4 vCPU, 16 GiB RAM. This is the cheapest GPU
  instance, and 16 GB is enough for every candidate, including qwen3-8b Q4_K_M at about 4.8 GB.
  `g4dn.2xlarge` only adds CPU and RAM, which this workload does not need.
* **AMI**: *AWS Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 24.04)*, user `ubuntu`. It comes
  with the NVIDIA driver and CUDA 12.x/13.x, Python 3.12 and git. Find the current AMI id for your region
  in the EC2 console (search "Deep Learning Base OSS Nvidia Driver GPU AMI Ubuntu 24.04"), or from the
  public SSM parameter `/aws/service/deeplearning/ami/x86_64/base-oss-nvidia-driver-gpu-ubuntu-24.04/latest/ami-id`.
* **Storage**: a 100 GB gp3 root volume. You need about 3.5 GB for the CUDA wheel and its install,
  about 29 GB for all twelve candidate GGUFs (`python -m core.geoai.eval.benchmark list`, or sum
  `size_mb` in `CANDIDATES`), about 3 GB for the venv, and room for the AMI itself.
  `compact-ab`/`lora`/`full-test` alone fit easily, and so does `models`.
* **Security group**: inbound **SSH (22) from My IP only**, with nothing else open. Use an EC2 key
  pair (`.pem`). No AWS credentials go on the box; the script never calls AWS. It only reads the
  instance type from the instance metadata service, with IMDSv2.
* **Quota**: new accounts often have a vCPU limit of 0 for *Running On-Demand G and VT instances*.
  Request at least 4 in Service Quotas before launching, which can take hours. If you get no GPU quota,
  use the CPU option below.
* **CPU-only option**: `c7i.2xlarge` (8 vCPU, $0.357/h) or `c7i.4xlarge` (16 vCPU, $0.714/h) with
  plain Ubuntu 24.04. The script detects that there is no GPU and installs the CPU wheel. This is less
  useful because it is several times slower than a T4 (`models` would take many hours) and its latency
  is still not the laptop's. The token-based desktop estimate works the same on any hardware, so there
  is little reason to pay for CPU time.

### Run

```bash
# from the desktop (Git Bash); KEY = your key pair file, IP = the instance's public IP
scp -i KEY.pem geocore-backend.tar.gz python-backend/core/geoai/eval/remote/run_remote_benchmark.sh ubuntu@IP:~
ssh -i KEY.pem ubuntu@IP

# on the instance: run inside tmux so a dropped SSH connection does not stop the run
tmux new -s geoai
bash run_remote_benchmark.sh --tarball ~/geocore-backend.tar.gz compact-ab
bash run_remote_benchmark.sh --tarball ~/geocore-backend.tar.gz models full-test
bash run_remote_benchmark.sh --tarball ~/geocore-backend.tar.gz --lora ~/geoai-lora.gguf lora   # copy the .gguf and .gguf.json up first
# or, from a pushed repo:
bash run_remote_benchmark.sh --repo https://github.com/utkarsh-1912/geocore.git compact-ab
```

Detach from tmux with `Ctrl-b d` and reattach with `tmux attach -t geoai`. The first job runs `setup`.
`setup` creates a venv in `~/geoai-bench/venv` and installs llama-cpp-python 0.3.35 from the prebuilt
CUDA wheel index (cu124, or older if the driver needs it). It then checks that GPU offload works,
installs the requirements and regenerates the eval data. Later invocations skip `setup`.

If bash reports `$'\r': command not found`, the script picked up Windows line endings. Fix it with
`sed -i 's/\r$//' run_remote_benchmark.sh`.

### Copy results back, then stop paying

```bash
# on the desktop, in python-backend/
scp -i KEY.pem ubuntu@IP:~/geoai-bench/geoai-benchmark-results-remote-gpu.tar.gz .
tar -xzf geoai-benchmark-results-remote-gpu.tar.gz
python -m core.geoai.eval.benchmark leaderboard --run-id remote-gpu-compact-ab-test40
python -m core.geoai.eval.estimate_desktop_latency --run-id remote-gpu-compact-ab-test40
# sanity check: the GPU full-schema arm vs the laptop's cpu-test40 run (same examples, so the scores should be close)
python -m core.geoai.eval.runner --compare core/geoai/eval/results/benchmark/cpu-test40/qwen3-1.7b.json core/geoai/eval/results/benchmark/remote-gpu-compact-ab-test40/qwen3-1.7b.json
```

* **Stop** the instance in the EC2 console (Instance state -> Stop) when you are between jobs. A
  stopped instance costs nothing for compute, but the 100 GB volume still costs about $8/month.
* **Terminate** it when you are done (Instance state -> Terminate). Terminating deletes the root
  volume, unless you changed "delete on termination".
* Check *EC2 -> Volumes* for leftover volumes.
* Optional: set an AWS Budgets alert, for example at $20.

The website's "Model benchmarks" page uses the most recently written `leaderboard.json`. An unpacked
remote run becomes that page unless you rebuild the run you want afterwards.

### Cost against the $125 credit

On-demand Linux prices from the AWS pricing data behind <https://aws.amazon.com/ec2/pricing/on-demand/>
(feed published 2026-09-25, read 2026-10-04). Prices vary by region and change over time, so check the
page for your region before launching.

| instance | us-east-1 / us-west-2 | eu-west-1 | eu-central-1 | ap-south-1 |
|---|---|---|---|---|
| g4dn.xlarge (T4) | $0.526/h | $0.587/h | $0.658/h | $0.579/h |
| g4dn.2xlarge | $0.752/h | $0.838/h | $0.940/h | $0.828/h |
| g5.xlarge (A10G, faster, not needed) | $1.006/h | $1.123/h | $1.258/h | $1.208/h |
| c7i.2xlarge (CPU only) | $0.357/h | $0.383/h | $0.407/h | $0.357/h |
| c7i.4xlarge (CPU only) | $0.714/h | $0.766/h | $0.815/h | $0.714/h |

The gp3 volume costs $0.08/GB-month in us-east-1, so 100 GB is about $0.27/day.

Job times on a g4dn.xlarge T4 are **estimates**, not measurements. They assume Qwen3-1.7B Q4_K_M at a
few thousand prompt tok/s and about 100 generated tok/s, which is about 1-5 s per example.

| job | estimated time | cost at $0.526/h |
|---|---|---|
| first `setup` (1.7 GB wheel, requirements, eval-data generation) | 10-20 min | ~$0.10-0.20 |
| `compact-ab` (2 x 40) | 5-10 min | ~$0.05-0.10 |
| `full-test` (325 + heuristic) | 10-20 min | ~$0.10-0.20 |
| `lora` (2 x 325) | 20-40 min | ~$0.20-0.35 |
| `models` (12 models x 40, ~29 GB of downloads; 4B/7B/8B models are slower) | 30-70 min | ~$0.25-0.65 |
| everything, including setup and idle time | ~2-3 h | ~$1-2 |

The credit covers about 230 g4dn.xlarge hours, so the real risk is leaving the instance running: that
costs about $12.60/day. Spot instances are cheaper and the script is resumable, but spot prices and
interruption rates were not checked here.

The CPU option costs about $0.5-1 for `compact-ab` (estimate: about 20-30 min per 40-example arm on
c7i.4xlarge) and several dollars for `models`.

## Colab (free T4)

1. Open `core/geoai/eval/remote/GeoAI_benchmark_colab.ipynb` in Colab.
2. Set Runtime -> Change runtime type -> T4.
3. Run the cells in order: clone, `setup`, `compact-ab` and/or `lora`, leaderboards and estimates, then
   zip and download.
4. Unpack the zip in `python-backend/`. Windows `tar -xf` handles zip files.

The notebook clones from GitHub, so push the code first, or upload a zip of `python-backend/` to
`/content/geocore/python-backend`.

**After fine-tuning:** the fine-tune notebook (`core/geoai/finetune/colab/GeoAI_finetune.ipynb`) has
step *9b*. It runs the same `lora` job on the adapter it just exported (`/content/geoai-ft/export/geoai-lora.gguf`),
in the same runtime, and downloads the results.

Free Colab sessions can disconnect when idle and GPU time is not guaranteed. Re-running a cell resumes,
because finished result files are skipped. The files live on the runtime disk, which is lost when the
runtime is recycled, so download often.

## Desktop latency (estimated, not measured)

GPU latency says nothing about the laptop. Token counts do carry over: the GGUF, template and prompt
are the same, and the harness now records `prompt_tokens`/`completion_tokens` per example in
`per_example_usage`. `python -m core.geoai.eval.estimate_desktop_latency --run-id RUN` computes the
estimate with this formula:

```
est = prompt_tokens / prompt_tok_s + completion_tokens / gen_tok_s      (+ model_load_s for a cold first request)
```

The throughput comes from `core/geoai/eval/data/desktop_calibration.json`. For Qwen3-1.7B Q4_K_M on
the i5-1235U (2026-10-04) it is about 27 prompt tok/s (17-31) and 4-6 generated tok/s.

* Other models are scaled by GGUF size, which is rougher still.
* The script reports p50/p95 at nominal throughput, plus a range for the fastest and slowest calibration rates.
* It does not model prompt-prefix reuse, LoRA overhead on CPU or tool execution time.
* On the laptop's own earlier runs, the measured latency was 0.5-1.7x the estimate per example, with a
  median of about 0.85 (`--validate`).

The go/no-go rule's latency criterion (adapter p50 at most 1.3x base) is evaluated on whatever machine
ran the job. For a GPU run, confirm desktop latency before shipping an adapter.
