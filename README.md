# Sports Performance Analytics — Exploratory Data Analysis

> **EDA on sports performance data to uncover patterns in player and team metrics.**  
> Feature engineering, correlation analysis, and multi-layered visualisations.

![Python](https://img.shields.io/badge/Python-3.10%2B-3b82f6?style=flat-square&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-f59e0b?style=flat-square&logo=jupyter&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.0%2B-06b6d4?style=flat-square&logo=pandas&logoColor=white)
![seaborn](https://img.shields.io/badge/seaborn-0.12%2B-22c55e?style=flat-square)

---

## Objective

Analyse multi-season sports performance data to answer:
1. Which player metrics are the strongest predictors of team success?
2. How do seasonal trends affect individual and team performance?
3. What are the key statistical differences between high- and low-performing teams?

---

## Key Analysis

### 1. Data Profiling
- Missing value audit and imputation strategy
- Distribution analysis for all numeric features
- Outlier identification (IQR method)

### 2. Feature Engineering
- Per-90-minutes normalisation for fair player comparison
- Rolling averages to capture form trends
- Composite performance indices

### 3. Correlation Analysis
- Heatmap of inter-metric correlations
- Top features correlated with win rate
- Multicollinearity check before modelling

### 4. Visualisations
- Player performance scatter plots (e.g., Goals vs xG)
- Team ranking evolution over the season
- Positional breakdown of key metrics
- Distribution comparisons (top vs bottom quartile teams)

---

## Tech Stack

| Tool | Purpose |
|---|---|
| `pandas` | Data loading, cleaning, reshaping |
| `numpy` | Numerical computation |
| `matplotlib` | Base plotting |
| `seaborn` | Statistical visualisations |
| `Jupyter Notebook` | Analysis environment |

---

## Structure

```
Exploratory-Data-Analysis-Sports/
├── EDA_Sports.ipynb       # Main analysis notebook
├── data/
│   └── sports_data.csv    # Dataset
├── charts/                # Exported visualisations
└── README.md
```

---

## Key Findings

- **Possession efficiency** (shots per possession, not raw possession %) is the strongest team-level predictor of goal difference.
- **Expected goals (xG) over-performance** regresses to the mean within 8–10 matches — useful for market timing in fantasy sports contexts.
- **Defensive metrics** (pressures per 90, PPDA) show stronger correlation with clean sheets than raw tackle counts.

---

## Quick Start

```bash
git clone https://github.com/picklerick0316/Exploratory-Data-Analysis-Sports
cd Exploratory-Data-Analysis-Sports
pip install pandas numpy matplotlib seaborn jupyter
jupyter notebook EDA_Sports.ipynb
```

---

## Author

**Harshit Kotnala** — Analytics Engineer & Microsoft BI Specialist  
MSc Business Analytics, University College Cork  
[GitHub](https://github.com/picklerick0316) · [Portfolio](https://harshitkotnala.github.io)
