# Nyx — Open Government Data Interpretability Assessment Tool

**Nyx** is a Python-based tool for automatically assessing the **interpretability of open government datasets** (CSV format).
It produces a **quantitative score** and **visual outputs** to evaluate how understandable, consistent, complete, and informative a dataset is.

---

## Motivation

Open government data plays a central role in transparency, accountability, and civic participation. However, many datasets are difficult to interpret due to issues such as missing values, poor structure, redundancy, or inconsistent formatting.

Nyx addresses this problem by providing a **systematic, reproducible, and scalable approach** to evaluate dataset interpretability. It supports:

* Researchers analyzing data quality
* Public institutions improving data publication practices
* Developers working with open data

---

## What Nyx Measures

Nyx evaluates interpretability across multiple dimensions:

| Metric                       | Description                                                                                                  |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Completeness**             | Proportion of non-missing values in the dataset.                                                             |
| **Conciseness**              | Penalizes redundancy such as duplicate rows and constant columns.                                            |
| **Precision**                | Ratio of valid data relative to total data.                                                                  |
| **Consistency**              | Checks for uniform data types within each column.                                                            |
| **Semantic Consistency**     | Detects similar column names and validates expected formats (e.g., CPF, CNPJ, CEP, dates).                   |
| **Informativeness**          | Measures variability in numerical data using entropy.                                                        |
| **Organization / Structure** | Evaluates dataset structure, including keys, null distribution, correlations, and column-to-row proportions. |

---

## Final Score

Nyx computes a **composite interpretability score** ranging from **0 (low interpretability)** to **1 (high interpretability)**, based on a weighted combination of all metrics.

---

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Usage

Run Nyx on a single dataset:

```bash
python nyx_ranking.py --input file.csv --out results
```

---

## Batch Processing

Nyx also supports batch execution over multiple datasets:

```bash
python batch_runner.py
```

By default, the script reads all CSV files from a `datasets/` directory.

---

## Output

For each execution, Nyx generates:

* **scores.csv**: detailed metric scores and final score
* **radar.png**: radar chart representing interpretability dimensions

For batch execution:

* **resultados_consolidados.csv**: results for all datasets
* **medias_gerais.csv**: aggregated metrics (mean values)
* **radar_medio.png**: average interpretability profile
* **radar_<dataset>.png**: individual radar charts per dataset

---

## Project Structure

```
project/
│
├── nyx_ranking.py
├── batch_runner.py
├── datasets/
│   ├── dataset1.csv
│   ├── dataset2.csv
```

---

## Requirements

* Python 3.8+
* pandas
* numpy
* matplotlib
* rapidfuzz

---

## Contributions

Contributions are welcome. Please feel free to open issues or submit pull requests.

---

## License

This project is distributed under the MIT License.