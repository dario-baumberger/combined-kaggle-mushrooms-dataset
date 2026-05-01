import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import kagglehub

logger = logging.getLogger(__name__)


def download_dataset(handle):
    """Worker function to download a single dataset."""
    try:
        logger.info(f"Starting download for: {handle}")
        path = kagglehub.dataset_download(handle)
        logger.info(f"Finished {handle}. Path: {path}")
        return path
    except Exception as e:
        logger.error(f"Failed to download {handle}: {e}")


def main():
    logging.basicConfig(filename=f"{__name__}.log", level=logging.INFO)
    logger.info("Starting kaggle dataset downloads...")

    # Setup Paths
    repo_root = Path(__file__).resolve().parents[1]
    default_cache = repo_root / "temp" / "kaggle"
    cache_path = Path(os.environ.get("KAGGLEHUB_CACHE", default_cache))
    cache_path.mkdir(parents=True, exist_ok=True)
    os.environ["KAGGLEHUB_CACHE"] = str(cache_path)

    datasets = ["thehir0/mushroom-species", "zlatan599/mushroom1"]

    with ThreadPoolExecutor(max_workers=len(datasets)) as executor:
        executor.map(download_dataset, datasets)


if __name__ == "__main__":
    main()
