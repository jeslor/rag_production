from pathlib import Path
import torch
from functools import lru_cache

# Absolute project root (config.py lives in /something/.../health_knowledge_engine/)
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data/raw_pdfs"
DB_DIR = BASE_DIR / "vector_storage/chroma_db"

MODEL_NAME = "BAAI/bge-large-en-v1.5"
MODEL_NAME2 = "BAAI/bge-m3"


@lru_cache(maxsize=1)
def get_optimal_chipset() -> str:
    """Determine the optimal compute chipset for local model inference.

    Caches the evaluation result to prevent redundant hardware polling
    across pipeline layers.
    """
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


# Default Hyperparameters
DEFAULT_CHUNK_SIZE = 750
DEFAULT_CHUNK_OVERLAP = 150
