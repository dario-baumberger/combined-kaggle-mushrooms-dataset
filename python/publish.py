import base64
import json
import logging
import os
import sys
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

import kagglehub  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATASET_DIR = Path("data/combined-kaggle-mushrooms-dataset")
DATASET_SLUG = "combined-kaggle-mushrooms-dataset"


def get_kaggle_credentials() -> tuple[str, str]:
    for var in ("KAGGLE_USERNAME", "KAGGLE_API_TOKEN"):
        if not os.environ.get(var):
            raise RuntimeError(f"{var} environment variable not set.")
    return os.environ["KAGGLE_USERNAME"], os.environ["KAGGLE_API_TOKEN"]


def get_current_kaggle_version(username: str, slug: str, api_token: str) -> int | None:
    url = f"https://www.kaggle.com/api/v1/datasets/{username}/{slug}"
    creds = base64.b64encode(f"{username}:{api_token}".encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {creds}"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())["currentDatasetVersionNumber"]
    except Exception as e:
        logger.warning(f"Could not fetch Kaggle version number: {e}")
        return None


def write_github_output(key: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a") as f:
            f.write(f"{key}={value}\n")


def main() -> None:
    if not DATASET_DIR.exists():
        logger.error(f"Dataset not found at {DATASET_DIR}. Run merge first.")
        sys.exit(1)

    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    version_notes = next((a for a in args if a != "--dry-run"), "")

    username, api_token = get_kaggle_credentials()
    handle = f"{username}/{DATASET_SLUG}"

    if dry_run:
        logger.info(f"[DRY RUN] Would upload to {handle} with notes: {version_notes!r}")
        return

    logger.info(f"Uploading to {handle}...")
    kagglehub.dataset_upload(handle, str(DATASET_DIR), version_notes=version_notes)
    logger.info(f"Done. https://www.kaggle.com/datasets/{handle}")

    version = get_current_kaggle_version(username, DATASET_SLUG, api_token)
    if version:
        logger.info(f"Published as Kaggle version {version}")
        write_github_output("kaggle_version", str(version))


if __name__ == "__main__":
    main()
