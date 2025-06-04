# 📈 Open Meteo Precipitation Analysis

This repository contains Python scripts and notebooks to:

* **Query** historical precipitation data from the [Open-Meteo Archive API](https://open-meteo.com/).
* **Validate** the data using box-and-whisker plots.
* **Visualize** precipitation patterns by 10-day bins within each month using color-coded bar charts.

Target dataset: **Madison, Wisconsin**, from **2000 to 2024**, focusing on daily precipitation in **June**.

---

## 🔍 Background

### What is Open-Meteo?

[Open-Meteo](https://open-meteo.com/) is a free, no-auth weather data API that provides historical, real-time, and forecast data. We use its **Archive API** to obtain daily **precipitation** records for a specific location and time range.

---

## 📁 Project Structure

```
Open_Meteo/
├── Open_Meteo_Query.py           # Script to query precipitation data and save it as a CSV
├── Open_Meteo_Analysis.ipynb     # Jupyter notebook for visualizing and analyzing the data
├── madison_precip_2000_2024.csv  # Output CSV containing the precipitation data
├── precipitation_whisker_plot.png   # Box-and-whisker plot for data validation
└── precipitation_barchart.png       # Final bar chart of 10-day binned precipitation data
```

---

## 🧰 Prerequisites

Install Python libraries:

```bash
pip install pandas matplotlib seaborn requests
```

---

## 🚀 Step-by-Step Guide

### Step 1: Query Precipitation Data

**Script:** `Open_Meteo_Query.py`

This script sends requests to Open-Meteo's Archive API for each year from 2000–2024, retrieving **daily precipitation data** for the month of **June** in **Madison, WI**.

#### How to Run

```bash
python Open_Meteo_Query.py
```

**Output:**
A CSV file `madison_precip_2000_2024.csv` containing:

* `date`
* `precip_mm` (daily total precipitation in millimeters)

---

### Step 2: Visualize the Data

**Notebook:** `Open_Meteo_Analysis.ipynb`

#### 2a. Data Validation — Box-and-Whisker Plot

This plot shows precipitation distributions per year, helping identify:

* Outliers
* Missing or unreasonable values

**Key steps:**

* Load the CSV.
* Convert date column to datetime.
* Group precipitation by year and month.
* Create a boxplot using Seaborn.

**Output:**
`precipitation_whisker_plot.png`

---

#### 2b. Desired Output — 10-Day Binned Bar Chart

We divide each June into 3 bins:

* `1–10`
* `11–20`
* `21–30`

Then, we:

* Sum precipitation within each 10-day period.
* Plot results as a **stacked bar chart**, color-coded by bin.

**Output:**
`precipitation_barchart.png`

---

## 📊 Example Plots

### Box-and-Whisker Plot

Used for **sanity checking** the dataset per year.

### Stacked Bar Chart

Shows **monthly precipitation sums** broken down into 10-day periods per year.

---

## 🧠 Summary

This project helps:

* **Validate** historical precipitation data from Open-Meteo.
* **Visualize** rainfall trends over time and by intramonth patterns.

Useful for:

* Climatological research
* Fungal ecology
* Environmental pattern detection

