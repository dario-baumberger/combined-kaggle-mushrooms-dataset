import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

import kagglehub  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATASET_DIR = Path("data/combined-kaggle-mushrooms-dataset")
DATASET_SLUG = "combined-kaggle-mushrooms-dataset"


def get_kaggle_username() -> str:
    for var in ("KAGGLE_USERNAME", "KAGGLE_API_TOKEN"):
        if not os.environ.get(var):
            raise RuntimeError(f"{var} environment variable not set.")
    return os.environ["KAGGLE_USERNAME"]


def main() -> None:
    if not DATASET_DIR.exists():
        logger.error(f"Dataset not found at {DATASET_DIR}. Run merge first.")
        sys.exit(1)

    notebook_src = Path("notebook.ipynb")
    if notebook_src.exists():
        import shutil
        shutil.copy(notebook_src, DATASET_DIR / notebook_src.name)
        logger.info(f"Copied {notebook_src} to {DATASET_DIR}")

    version_notes = sys.argv[1] if len(sys.argv) > 1 else ""
    username = get_kaggle_username()
    handle = f"{username}/{DATASET_SLUG}"

    logger.info(f"Uploading to {handle}...")
    kagglehub.dataset_upload(handle, str(DATASET_DIR), version_notes=version_notes)
    logger.info(f"Done. https://www.kaggle.com/datasets/{handle}")


if __name__ == "__main__":
    main()
