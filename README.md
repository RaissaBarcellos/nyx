# Nyx — Open Government Data Interpretability Assessment Tool

**Nyx** is a Python-based tool designed to automatically evaluate the **interpretability** of open government datasets (CSV format).  
It quantifies how **clear, consistent, complete, and informative** a dataset is, producing both a **numerical score** and a **visual radar chart**.

---

## Overview

Nyx aims to support **data transparency and reusability** by helping data publishers and researchers assess whether open data is easy to understand and use.  
It evaluates multiple interpretability dimensions and outputs structured results for analysis and comparison.

---

## ⚙️ What Nyx Measures

| Metric | Description |
|---------|--------------|
| **Completeness** | Measures how much of the dataset is filled (absence of missing values). |
| **Conciseness** | Penalizes redundant data such as duplicate rows or constant columns. |
| **Precision** | Evaluates the ratio of valid data to total data. |
| **Consistency** | Checks for coherent data types within each column. |
| **Semantic Consistency** | Detects semantically similar column names and validates expected formats (e.g., CPF, CNPJ, postal codes). |
| **Informativeness** | Measures variability across numerical columns using entropy. |
| **Organization/Structure** | Evaluates dataset structure — primary keys, null ratios, correlations, and column-to-row proportions. |

---

## Final Score

The **final interpretability score** is a weighted average of all metrics, ranging from **0 (low interpretability)** to **1 (high interpretability)**.

## Configure

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

python nyx-ranking.py --input file.csv --out results

---

## Output Files

After running Nyx, a folder is created with two main outputs:

