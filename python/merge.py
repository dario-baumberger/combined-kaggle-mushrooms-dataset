import hashlib
import io
import logging
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import islice
from pathlib import Path
from typing import TypedDict

from PIL import Image
from tqdm import tqdm


class DatasetInfo(TypedDict, total=False):
    local_path: Path
    depth: int  # folder levels to species: 1 = local_path/<species>/, 2 = local_path/<cat>/<species>/
    url: str
    description: str
    license: str
    license_url: str


TARGET_DATASET_DIR: Path = Path("data/combined-kaggle-mushrooms-dataset")
SUPPORTED_IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp"}

DATASET_METADATA: dict[str, DatasetInfo] = {
    "thehir0/mushroom-species": {
        "local_path": Path("temp/kaggle/datasets/thehir0/mushroom-species/versions/1/dataset"),
        "depth": 1,
        "url": "https://www.kaggle.com/datasets/thehir0/mushroom-species",
        "description": "Over 50,000 photos of 100 species of mushrooms taken in Russia.",
        "license": "CC BY-NC 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc/4.0/",
    },
    "zlatan599/mushroom1": {
        "local_path": Path("temp/kaggle/datasets/zlatan599/mushroom1/versions/2/merged_dataset"),
        "depth": 1,
        "url": "https://www.kaggle.com/datasets/zlatan599/mushroom1",
        "description": "This dataset contains images of different mushroom species divided into over 100 classes.",
        "license": "MIT",
        "license_url": "https://opensource.org/licenses/MIT",
    },
    "iftekhar08/mo-106": {
        "local_path": Path("temp/kaggle/datasets/iftekhar08/mo-106/versions/4/MO_94"),
        "depth": 1,
        "url": "https://www.kaggle.com/datasets/iftekhar08/mo-106",
        "description": "This dataset contains 27,436 images of mushrooms, categorized into 94 species.",
        "license": "CC BY-NC 4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc/4.0/",
    },
    "derekkunowilliams/mushrooms": {
        "local_path": Path("temp/kaggle/datasets/derekkunowilliams/mushrooms/versions/1/mushroom_dataset"),
        "depth": 2,
        "url": "https://www.kaggle.com/datasets/derekkunowilliams/mushrooms",
        "description": "This dataset contains images of different mushroom species.",
        "license": "ODbL v1.0",
        "license_url": "https://opendatacommons.org/licenses/odbl/1-0/",
    },
    "tinkhoav/mushroom-classification": {
        "local_path": Path("temp/kaggle/datasets/tinkhoav/mushroom-classification/versions/3/images"),
        "depth": 1,
        "url": "https://www.kaggle.com/datasets/tinkhoav/mushroom-classification",
        "description": "83.7k files, 277 folders",
        "license": "Apache 2.0",
        "license_url": "https://www.apache.org/licenses/LICENSE-2.0",
    },
}

logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)


def iter_species_folders(root: Path, depth: int):
    if depth <= 1:
        yield from root.iterdir()
    else:
        for sub in root.iterdir():
            if sub.is_dir():
                yield from iter_species_folders(sub, depth - 1)


def process_image(source_path: Path, species_name: str) -> tuple[str, str, bytes]:
    """Converts image to WebP in memory, returns (species, md5, bytes)."""
    buf = io.BytesIO()
    with Image.open(source_path) as img:
        img = img.convert("RGB")
        img.thumbnail((500, 500), Image.BICUBIC)
        img.save(buf, "WEBP", quality=85, method=0)
    data = buf.getvalue()
    return species_name, hashlib.md5(data).hexdigest(), data


def snapshot_species_image_counts(dataset_dir: Path) -> dict[str, int]:
    """Returns {species: image_count} for an existing dataset directory, or {} if absent."""
    images_dir = dataset_dir / "images"
    if not images_dir.exists():
        return {}
    return {
        species_dir.name: sum(1 for _ in species_dir.glob("*.webp"))
        for species_dir in images_dir.iterdir()
        if species_dir.is_dir()
    }


def generate_changelog(
    before: dict[str, int],
    after: dict[str, int],
    cross_species_duplicates: list[tuple[str, str, str, Path, str, str, Path]],
    out_path: Path,
) -> None:
    before_set = set(before)
    after_set = set(after)
    added = sorted(after_set - before_set)
    removed = sorted(before_set - after_set)
    changed = sorted(s for s in before_set & after_set if before[s] != after[s])
    unchanged = sorted(s for s in before_set & after_set if before[s] == after[s])

    kaggle_username = os.environ.get("KAGGLE_USERNAME", "dariobaumberger")
    kaggle_url = f"https://www.kaggle.com/datasets/{kaggle_username}/{TARGET_DATASET_DIR.name}"
    lines: list[str] = [
        "# Merge Changelog\n",
        f"[View dataset on Kaggle]({kaggle_url})\n",
        "## Summary",
        f"- Species before: {len(before)}",
        f"- Species after:  {len(after)}",
        f"- Added species:          {len(added)}",
        f"- Removed species:        {len(removed)}",
        f"- Changed image count:    {len(changed)}",
        f"- Unchanged species:      {len(unchanged)}",
        f"- Total images before: {sum(before.values())}",
        f"- Total images after:  {sum(after.values())}",
        f"- Cross-species duplicates removed: {len(cross_species_duplicates)}",
    ]

    if added:
        lines.append("\n## Added Species\n| Species | Images |")
        lines.append("|---|---|")
        for s in added:
            lines.append(f"| {s} | {after[s]} |")

    if removed:
        lines.append("\n## Removed Species\n| Species | Images (before) |")
        lines.append("|---|---|")
        for s in removed:
            lines.append(f"| {s} | {before[s]} |")

    if changed:
        lines.append("\n## Changed Image Count\n| Species | Before | After | Delta |")
        lines.append("|---|---|---|---|")
        for s in changed:
            delta = after[s] - before[s]
            sign = "+" if delta > 0 else ""
            lines.append(f"| {s} | {before[s]} | {after[s]} | {sign}{delta} |")

    if unchanged:
        lines.append("\n## Unchanged Species\n| Species | Images |")
        lines.append("|---|---|")
        for s in unchanged:
            lines.append(f"| {s} | {after[s]} |")

    if cross_species_duplicates:
        _kaggle_root = Path("temp/kaggle/datasets")

        def _rel(p: Path) -> Path:
            try:
                return p.relative_to(_kaggle_root)
            except ValueError:
                return p

        # group by hash
        species_by_hash: dict[str, list[str]] = {}
        paths_by_hash: dict[str, list[Path]] = {}
        for dup in sorted(cross_species_duplicates):
            h = dup[0]
            species_by_hash.setdefault(h, [])
            for s in (dup[1], dup[4]):
                if s not in species_by_hash[h]:
                    species_by_hash[h].append(s)
            paths_by_hash.setdefault(h, [])
            for p in (dup[3], dup[6]):
                if p not in paths_by_hash[h]:
                    paths_by_hash[h].append(p)

        lines.append("\n## Removed: Cross-species Duplicates\n| Hash | Mismatch |")
        lines.append("|---|---|")
        for h, species in sorted(species_by_hash.items()):
            lines.append(f"| {h[:12]} | {', '.join(species)} |")

        lines.append("\n### File Paths\n| Hash | File Path |")
        lines.append("|---|---|")
        for h, paths in sorted(paths_by_hash.items()):
            for p in paths:
                lines.append(f"| {h[:12]} | {_rel(p)} |")

    out_path.write_text("\n".join(lines), encoding="utf-8")


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

    species_image_counts = {}
    for species in sorted(species_to_sources_map.keys()):
        species_path: Path = TARGET_DATASET_DIR / "images" / species
        species_image_counts[species] = sum(1 for _ in species_path.glob("*.webp"))

    total_species = len(species_image_counts)
    total_images = sum(species_image_counts.values())

    readme_lines.append(f"\n## Summary\n- **Total species:** {total_species}\n- **Total images:** {total_images}")

    readme_lines.append("\n## Species Mapping\n| Species | Image Count | Original Sources |\n|---|---|---|")

    for species, image_count in species_image_counts.items():
        sources_list: str = ", ".join(sorted(species_to_sources_map[species]))
        readme_lines.append(f"| {species} | {image_count} | {sources_list} |")

    (TARGET_DATASET_DIR / "README.md").write_text("\n".join(readme_lines), encoding="utf-8")


def main(max_workers: int = os.cpu_count(), batch_size: int = 1000) -> None:
    before_snapshot = snapshot_species_image_counts(TARGET_DATASET_DIR)

    if TARGET_DATASET_DIR.exists():
        shutil.rmtree(TARGET_DATASET_DIR)

    processing_tasks: list[tuple[Path, str, str]] = []  # (path, species, source_id)
    species_to_sources_map: dict[str, set[str]] = {}

    for source_id, info in DATASET_METADATA.items():
        data_root_path: Path = info["local_path"]

        if not data_root_path.exists():
            logger.warning(f"Species root {data_root_path} not found. Skipping {source_id}.")
            continue

        for species_folder in iter_species_folders(data_root_path, info.get("depth", 1)):
            try:
                if not species_folder.is_dir():
                    continue
            except OSError:
                continue
            for file_path in species_folder.rglob("*"):
                try:
                    if file_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                        species_name: str = file_path.parent.name.replace("_", " ")
                        processing_tasks.append((file_path, species_name, source_id))
                        species_to_sources_map.setdefault(species_name, set()).add(source_id)
                except OSError:
                    continue

    processing_tasks.sort(key=lambda t: (t[2], t[1], str(t[0])))

    # hash → (species, source_id, src_path, out_path)  — out_path is None if deleted
    unique_hashes: dict[str, tuple[str, str, Path, Path | None]] = {}
    species_counters: dict[str, int] = {}
    cross_species_duplicates: list[tuple[str, str, str, Path, str, str, Path]] = []
    task_iter = iter(processing_tasks)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        with tqdm(total=len(processing_tasks), desc="Processing and Deduplicating") as progress:
            while chunk := list(islice(task_iter, batch_size)):
                futures = {
                    executor.submit(process_image, img_path, species): (img_path, source_id)
                    for img_path, species, source_id in chunk
                }
                for future in as_completed(futures):
                    src_path, source_id = futures[future]
                    try:
                        species_name, content_hash, data = future.result()
                        if content_hash not in unique_hashes:
                            species_dir: Path = TARGET_DATASET_DIR / "images" / species_name
                            species_dir.mkdir(parents=True, exist_ok=True)
                            count = species_counters.get(species_name, 1)
                            species_counters[species_name] = count + 1
                            out_path = species_dir / f"{species_name}_{count}.webp"
                            out_path.write_bytes(data)
                            unique_hashes[content_hash] = (species_name, source_id, src_path, out_path)
                        else:
                            saved_species, saved_source, saved_src, saved_out = unique_hashes[content_hash]
                            if saved_species != species_name:
                                cross_species_duplicates.append(
                                    (
                                        content_hash,
                                        saved_species,
                                        saved_source,
                                        saved_src,
                                        species_name,
                                        source_id,
                                        src_path,
                                    )
                                )
                                if saved_out is not None and saved_out.exists():
                                    saved_out.unlink()
                                    unique_hashes[content_hash] = (saved_species, saved_source, saved_src, None)
                    except Exception as e:
                        logger.error(f"Failed task: {e}")
                    finally:
                        progress.update(1)

    if cross_species_duplicates:
        logger.warning(f"{len(cross_species_duplicates)} cross-species duplicates removed — see CHANGELOG.md")

    generate_dataset_readme(species_to_sources_map)

    after_snapshot = snapshot_species_image_counts(TARGET_DATASET_DIR)
    changelog_path = TARGET_DATASET_DIR / "CHANGELOG.md"
    generate_changelog(before_snapshot, after_snapshot, cross_species_duplicates, changelog_path)
    logger.info(f"Changelog written to {changelog_path}")
    logger.info(f"Complete. Dataset at {TARGET_DATASET_DIR}")


if __name__ == "__main__":
    main()
