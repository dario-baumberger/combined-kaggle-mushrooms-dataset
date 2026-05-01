# Combined Kaggle Mushrooms Dataset

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Kaggle](https://img.shields.io/badge/Kaggle-Dataset-20BEFF?logo=kaggle)](https://www.kaggle.com/datasets/dariobaumberger/combined-kaggle-mushrooms-dataset)

A pipeline that downloads, merges, deduplicates, and publishes mushroom image datasets from Kaggle into a single unified dataset. All images are normalized to WebP format at max 500px on the longest side and named consistently by species.

The combined dataset is published at [kaggle.com/datasets/dariobaumberger/combined-kaggle-mushrooms-dataset](https://www.kaggle.com/datasets/dariobaumberger/combined-kaggle-mushrooms-dataset).

## What it does

1. **Download** — fetches source datasets from Kaggle via `kagglehub`
2. **Merge** — walks species folders across all sources, converts images to WebP, and removes duplicates via MD5 hashing
3. **Publish** — uploads the combined dataset back to Kaggle

## Source Datasets

| Dataset | Description | License |
|---|---|---|
| [thehir0/mushroom-species](https://www.kaggle.com/datasets/thehir0/mushroom-species) | 100k+ photos of 100+ mushroom species taken in Russia | [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) |
| [zlatan599/mushroom1](https://www.kaggle.com/datasets/zlatan599/mushroom1) | Images of 100+ mushroom species | [MIT](https://opensource.org/licenses/MIT) |

## License

[CC BY-NC 4.0](LICENSE) — free to use and adapt with attribution, not for commercial purposes.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
