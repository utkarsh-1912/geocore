"""
GeoAI fine-tuning (training-side only; AGENTS.md §19, §32).

Runs off-machine on a CUDA GPU (e.g. a free Colab/Kaggle T4) with Unsloth + TRL:

    SFT (LoRA)  ->  GRPO (reward = core.geoai.eval.scoring.reward)  ->  GGUF LoRA export

The desktop app never imports this package's heavy dependencies: torch,
unsloth, trl, peft and datasets are imported lazily inside the functions that
need them, so ``import core.geoai.finetune.*`` works on a CPU-only install and
the ``--dry-run`` paths run locally / in CI.

See README.md in this directory for the workflow and the go/no-go rule.
"""

from core.geoai.finetune.config import FAMILY_PRESETS, FinetuneConfig

__all__ = ["FAMILY_PRESETS", "FinetuneConfig"]
