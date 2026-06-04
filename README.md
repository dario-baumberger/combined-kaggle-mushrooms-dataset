# Combined Kaggle Mushrooms Dataset

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![License: ODbL](https://img.shields.io/badge/License-ODbL-brightgreen.svg)](https://opendatacommons.org/licenses/odbl/)
[![Kaggle](https://img.shields.io/badge/Kaggle-Dataset-20BEFF?logo=kaggle)](https://www.kaggle.com/datasets/dariobaumberger/combined-kaggle-mushrooms-dataset)

A pipeline that downloads, merges, deduplicates, and publishes mushroom image datasets from Kaggle into a single unified dataset. All images are normalized to WebP format at max 500px on the longest side and named consistently by species.

The combined dataset is published at [kaggle.com/datasets/dariobaumberger/combined-kaggle-mushrooms-dataset](https://www.kaggle.com/datasets/dariobaumberger/combined-kaggle-mushrooms-dataset).

This project was developed as part of a Data Science Project Module at [HSLU (Hochschule Luzern)](https://www.hslu.ch).

## What it does

1. **Download** — fetches source datasets from Kaggle via `kagglehub`
2. **Merge** — walks species folders across all sources, converts images to WebP, removes duplicates via MD5 hashing, and discards images that appear under more than one species name
3. **Publish** — uploads the combined dataset back to Kaggle

## Source Datasets

| Dataset | Description | License |
|---|---|---|
| [thehir0/mushroom-species](https://www.kaggle.com/datasets/thehir0/mushroom-species) | 100k+ photos of 100+ mushroom species taken in Russia | [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) |
| [zlatan599/mushroom1](https://www.kaggle.com/datasets/zlatan599/mushroom1) | Images of 100+ mushroom species | [MIT](https://opensource.org/licenses/MIT) |
| [iftekhar08/mo-106](https://www.kaggle.com/datasets/iftekhar08/mo-106) | This dataset contains 27,436 images of mushrooms, categorized into 94 species. | [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) |
| [derekkunowilliams/mushrooms](https://www.kaggle.com/datasets/derekkunowilliams/mushrooms) | This dataset contains images of different mushroom species. | [ODbL v1.0](https://opendatacommons.org/licenses/odbl/1-0/) |
| [tinkhoav/mushroom-classification](https://www.kaggle.com/datasets/tinkhoav/mushroom-classification) | 83.7k files, 277 folders | [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) |

### Checked but rejected
| Dataset | Reason |
|---|---|
|[vegameta23/mushrooms-specified](https://www.kaggle.com/datasets/vegameta23/mushrooms-specified)|Unknown licence|
|[anilkrsah/deepmushroom](https://www.kaggle.com/datasets/anilkrsah/deepmushroom)|Only genus name|
|[hakanerdemm/mushroom-classification-dataset](https://www.kaggle.com/datasets/hakanerdemm/mushroom-classification-dataset)|No species|
|[ilyakondrusevich/mushrooms](https://www.kaggle.com/datasets/ilyakondrusevich/mushrooms)|Requires remapping to get full names|
|[zedsden/mushroom-classification-dataset](https://www.kaggle.com/datasets/zedsden/mushroom-classification-dataset)|Contains english names and also genus names|
|[benedictusjason/edible-and-poisonous-mushroom-classification](https://www.kaggle.com/datasets/benedictusjason/edible-and-poisonous-mushroom-classification)|Structured in filenames, not folders|


## License

This dataset combines sources under multiple licenses. See [LICENSE](LICENSE) for full details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
