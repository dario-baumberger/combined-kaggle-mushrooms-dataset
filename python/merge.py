import hashlib
import io
import logging
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TypedDict

from PIL import Image
from tqdm import tqdm


class DatasetInfo(TypedDict):
    local_path: Path  # The root of the downloaded dataset
    species_root: str  # The relative sub-path to where species folders live
    url: str
    description: str
    license: str
    license_url: str


TARGET_DATASET_DIR: Path = Path("data/combined-kaggle-mushrooms-dataset")
SUPPORTED_IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp"}

DATASET_METADATA: dict[str, DatasetInfo] = {
    "thehir0/mushroom-species": {
        "local_path": Path("temp/kaggle/datasets/thehir0/mushroom-species/versions/1/dataset"),
        "url": "https://www.kaggle.com/datasets/thehir0/mushroom-species",
        "description": "Over 50,000 photos of 100 species of mushrooms taken in Russia.",
        "license": "CC BY-NC 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc/4.0/",
    },
    "zlatan599/mushroom1": {
        "local_path": Path("temp/kaggle/datasets/zlatan599/mushroom1/versions/2/merged_dataset"),
        "url": "https://www.kaggle.com/datasets/zlatan599/mushroom1",
        "description": "This dataset contains images of different mushroom species divided into over 100 classes.",
        "license": "MIT",
        "license_url": "https://opensource.org/licenses/MIT",
    },
}

logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)


def process_image(source_path: Path, species_name: str) -> tuple[str, str, bytes]:
    """Converts image to WebP in memory, returns (species, md5, bytes)."""
    buf = io.BytesIO()
    with Image.open(source_path) as img:
        img = img.convert("RGB")
        img.thumbnail((500, 500), Image.BICUBIC)
        img.save(buf, "WEBP", quality=85, method=0)
    data = buf.getvalue()
    return species_name, hashlib.md5(data).hexdigest(), data


def generate_dataset_readme(species_to_sources_map: dict[str, set[str]]) -> None:
    """Generates a README.md with source metadata and species counts."""
    readme_lines: list[str] = [
        "# Combined Mushroom Dataset\n",
        "## Sources\n| Source | Description | License |\n|---|---|---|",
    ]

    for source_id, metadata in DATASET_METADATA.items():
        source_link: str = f"[{source_id}]({metadata['url']})"
        license_link: str = f"[{metadata['license']}]({metadata['license_url']})"
        readme_lines.append(f"| {source_link} | {metadata['description']} | {license_link} |")

    readme_lines.append("\n## Species Mapping\n| Species | Image Count | Original Sources |\n|---|---|---|")

    for species in sorted(species_to_sources_map.keys()):
        species_path: Path = TARGET_DATASET_DIR / "images" / species
        image_count: int = len(list(species_path.glob("*.webp")))
        sources_list: str = ", ".join(sorted(species_to_sources_map[species]))
        readme_lines.append(f"| {species} | {image_count} | {sources_list} |")

    (TARGET_DATASET_DIR / "README.md").write_text("\n".join(readme_lines), encoding="utf-8")


def main(max_workers: int = 8) -> None:
    if TARGET_DATASET_DIR.exists():
        shutil.rmtree(TARGET_DATASET_DIR)

    processing_tasks: list[tuple[Path, str]] = []
    species_to_sources_map: dict[str, set[str]] = {}

    for source_id, info in DATASET_METADATA.items():
        data_root_path: Path = info["local_path"]

        if not data_root_path.exists():
            logger.warning(f"Species root {data_root_path} not found. Skipping {source_id}.")
            continue

        for species_folder in data_root_path.iterdir():
            try:
                if not species_folder.is_dir():
                    continue
            except OSError:
                continue
            species_name: str = species_folder.name
            for file_path in species_folder.rglob("*"):
                try:
                    if file_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                        processing_tasks.append((file_path, species_name))
                        species_to_sources_map.setdefault(species_name, set()).add(source_id)
                except OSError:
                    continue

    unique_hashes: set[str] = set()
    species_counters: dict[str, int] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_image, img_path, species): None for img_path, species in processing_tasks}

        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing and Deduplicating"):
            try:
                species_name, content_hash, data = future.result()
                if content_hash not in unique_hashes:
                    unique_hashes.add(content_hash)
                    species_dir: Path = TARGET_DATASET_DIR / "images" / species_name
                    species_dir.mkdir(parents=True, exist_ok=True)
                    count = species_counters.get(species_name, 1)
                    species_counters[species_name] = count + 1
                    (species_dir / f"{species_name}_{count}.webp").write_bytes(data)
            except Exception as e:
                logger.error(f"Failed task: {e}")

    generate_dataset_readme(species_to_sources_map)
    logger.info(f"Complete. Dataset at {TARGET_DATASET_DIR}")


if __name__ == "__main__":
    main()
