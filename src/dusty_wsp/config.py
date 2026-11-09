"""Pinned model, data, and evaluation constants for the Dusty weight-space study."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PACKAGE_ROOT / "data"
SOURCE_DIR = DATA_DIR / "source"
DEFAULT_SOURCE_CHECKPOINT = SOURCE_DIR / "model.pt"
DEFAULT_TOKENIZER = SOURCE_DIR / "tokenizer.json"
DEFAULT_MILO_FACTORS = PACKAGE_ROOT / "evidence" / "milo" / "edit_factors.json"
DEFAULT_STAIRS_FACTORS = PACKAGE_ROOT / "evidence" / "stairs" / "stairs_factors.json"
DEFAULT_MILO_DATASET = DATA_DIR / "milo" / "heldout.json"
DEFAULT_MILO_DEVELOPMENT = DATA_DIR / "milo" / "development.json"
DEFAULT_NEUTRAL = DATA_DIR / "milo" / "neutral.json"

# Hugging Face source used by every reported run.
SOURCE_REPO = "mkhordoo/dusty-8m-sft"
SOURCE_REVISION = "43d341f16f17cbeefedfe2475582942ab5891ed1"
SOURCE_COMMIT = "7a624c91611daa06580bb9104d52e8013c47c114"
SOURCE_MODEL_SHA256 = "5d7aa63d2db6d51f38e5e9c25a76facd33c0f84477ad940b97bc6ea6a1e661e5"
TOKENIZER_SHA256 = "989d4b2c4f65d408888261f7d412c8f64ea84a28e124b74ab3a8025e5a92dafe"

# Original, unsanitized artifact hashes. The checkpoint files themselves are not redistributed.
MILO_CANDIDATE_FILE_SHA256 = "273229976486d532933ed277ac6f52d4c74093b0da8c434aa4e4ed3801437a82"
MILO_CANDIDATE_STATE_SHA256 = "c509baf92dc837ff212b177c6330bc643679b109798b91af43617b2cebfeb9b5"
MILO_CANDIDATE_CANDIDATE01_STATE_SHA256 = (
    "a46a03037747b4520b7502ad29e173306027e361d990c13e7c700c68f5806267"
)
SOURCE_STATE_SHA256 = "2df33bf54db0783c294c874c64ff38cdf4525314508cd9cbefec3981c0aeed34"
MILO_DATASET_SHA256 = "d79b58abd895459e809b3118a432694cef3d638632c0f8289591dd815ec89a75"
MILO_EDITED_TENSOR = "layers.7.mlp.2.weight"
MILO_EDITED_TENSOR_SHAPE = (256, 1024)
MILO_TOTAL_PARAMETERS = 7_868_672

STAIRS_CANDIDATE_FILE_SHA256 = "78280c715db5d630797f0fe4f3c28aa72ce9c3b68e06a7085d2c48f207c8492d"
STAIRS_CANDIDATE_STATE_SHA256 = "6230f1fa2a89173548f2af493af12c367600070782ec7ce067076768dc210d72"
STAIRS_EDITED_TENSOR = "layers.1.mlp.2.weight"
STAIRS_EDITED_TENSOR_SHAPE = (256, 1024)
STAIRS_FACTORS_SHA256 = "eac9ac2ffa682d7f7d6f0e50734a46e296ecb920cdb6164c91ebef3cad6281ec"
STAIRS_SEED = 20261105


@dataclass(frozen=True)
class ModelSpec:
    """Architecture of the 8.1M-parameter Dusty checkpoint."""

    vocab_size: int = 4096
    embed_dim: int = 256
    num_layers: int = 8
    num_heads: int = 8
    num_heads_kv: int = 4
    mlp_hidden: int = 1024
    max_seq_len: int = 256
    rms_norm_eps: float = 1e-4
    rope_base: int = 10_000


MODEL = ModelSpec()


@dataclass(frozen=True)
class GenerationConfig:
    """Ordinary SFT inference profile used by the frozen evaluation."""

    max_new_tokens: int = 64
    temperature: float = 0.8
    top_k: int = 5
    top_p: float = 0.8
    eos_token_id: int = 2
