# Contributing

## Development setup

Requires [uv](https://github.com/astral-sh/uv).

```bash
uv sync
```

## Code style

This project uses [ruff](https://github.com/astral-sh/ruff) for linting and formatting.

```bash
uv run ruff check python/
uv run ruff format python/
```

All checks must pass before submitting a pull request.

## Adding a new source dataset

1. Add an entry to `DATASET_METADATA` in [python/merge.py](python/merge.py):

```python
"owner/dataset-slug": {
    "local_path": Path("temp/kaggle/datasets/owner/dataset-slug/versions/1/path-to-species-folders"),
    "url": "https://www.kaggle.com/datasets/owner/dataset-slug",
    "description": "Short description.",
    "license": "License name",
    "license_url": "https://link-to-license",
},
```

2. Add the dataset handle to the `datasets` list in [python/download.py](python/download.py).

3. Run the pipeline locally to verify it works (requires Kaggle credentials — see below).

The `local_path` must point to the folder that directly contains the species subdirectories. Check the downloaded structure under `temp/kaggle/datasets/` to find the right path.

## Running the pipeline

> **Note:** This section is only needed if you want to run or test the full pipeline locally. It is not required for contributing via pull request.

Running the pipeline requires a Kaggle account and API token. Get yours at [kaggle.com/settings](https://www.kaggle.com/settings) under **API → Create New Token**, then create a `.env` file:

```
KAGGLE_USERNAME=your-username
KAGGLE_API_TOKEN=your-api-token
```

```bash
# Download source datasets
uv run python -m python.download

# Merge and deduplicate into data/combined-kaggle-mushrooms-dataset
uv run python -m python.merge

# Publish to Kaggle
uv run python -m python.publish "optional version notes"
```

## GitHub Actions

Two workflows are included:

- **Lint** — runs `ruff` on every push to any branch
- **Publish** — runs lint then builds and publishes the dataset; triggered manually via `workflow_dispatch`

Add `KAGGLE_USERNAME` and `KAGGLE_API_TOKEN` as repository secrets under **Settings → Secrets and variables → Actions**.
