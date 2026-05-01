import hashlib
import logging
import sys
from collections import Counter
from pathlib import Path

from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMAGES_DIR = Path("data/combined-kaggle-mushrooms-dataset/images")


def main() -> None:
    if not IMAGES_DIR.exists():
        logger.error(f"Images directory not found at {IMAGES_DIR}. Run merge first.")
        sys.exit(1)

    files = list(IMAGES_DIR.rglob("*.webp"))
    hashes = [hashlib.md5(f.read_bytes()).hexdigest() for f in tqdm(files, desc="Hashing")]
    counts = Counter(hashes)
    dupes = {h: c for h, c in counts.items() if c > 1}

    logger.info(f"Total:      {len(files)}")
    logger.info(f"Unique:     {len(counts)}")
    logger.info(f"Duplicates: {len(dupes)}")

    if dupes:
        logger.error("Duplicate images found. Dataset is not clean.")
        sys.exit(1)

    logger.info("All images are unique.")


if __name__ == "__main__":
    main()
