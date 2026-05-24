# Cyclistic Bike-Share Analysis

### How do annual members and casual riders use Cyclistic bikes differently?

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![SQLite](https://img.shields.io/badge/SQLite-3-green)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Data](https://img.shields.io/badge/Data-2013--2020-lightgrey)

---

## Overview

This project is a portfolio case study.  
I analysed the full Divvy bike-share trip dataset (2013–2020, 30M+ rows across multiple schema versions) to identify behavioural differences between casual riders and annual members.

Due to the dataset size, the pipeline uses chunked CSV ingestion into a local SQLite database, with aggregation queries producing summary statistics that power all visualisations. This approach keeps peak RAM usage under 500 MB.

---

## Business Task

| | |
|---|---|
| **Stakeholder** | Lily Moreno, Director of Marketing, Cyclistic |
| **Goal** | Identify how casual riders and annual members use Cyclistic bikes differently, in order to design a data-driven marketing strategy that converts casual riders into annual members. |

---

## Key Findings

| Finding | Members | Casual Riders |
|:--------|--------:|--------------:|
| **Peak days** | Monday – Friday | Saturday – Sunday |
| **Avg ride duration** | ~12 minutes | ~24 minutes |
| **Peak hours** | 8 am and 5 pm | 12 pm – 4 pm |
| **Top start stations** | Near transit hubs | Lakefront & parks |
| **Seasonal pattern** | Consistent | Strongly seasonal |

---

## Recommendations

1. **Weekend trial campaign (Apr–Jun)**  
   Target casual riders after their second weekend ride with a trial membership offer emphasising unlimited ride duration.

2. **Station-based conversion**  
   Place QR code signage at the top 10 casual start stations, concentrated at Millennium Park and the lakefront.

3. **Digital retargeting (Sat–Sun, 11am–3pm)**  
   Geo-targeted social ads in Chicago lakefront zip codes during the peak casual window.

---

## Project Structure
cyclistic-bike-share/
├── raw_data/ # NOT committed — download from divvy-tripdata.com
├── outputs/
│ ├── charts/ # PNG chart exports (committed)
│ └── summary_stats/ # Small aggregate CSVs (committed)
├── 00_setup.py # Environment and folder check
├── 01_ingest.py # Schema unification + SQLite ingestion
├── 02_aggregate.py # SQL aggregation queries
├── 03_visualize.py # Chart generation
├── README.md
└── requirements.txt


---

## Data Source and Schema Notes

| | |
|---|---|
| **Provider** | Motivate International Inc. / Lyft Bikes and Scooters LLC |
| **Source** | https://divvy-tripdata.com |
| **Period** | 2013 – 2020 Q1 (multiple schema versions) |
| **Privacy** | No PII. Rides cannot be linked to individual users. |

This dataset spans four distinct schemas across years:

| Schema | Years | Column Format |
|:------:|:-----:|:--------------|
| **A** | 2013–2017 | `trip_id`, `starttime`/`stoptime`, `usertype` (Customer/Subscriber) |
| **B** | 2018 Q1 | Verbose column names with "Rental Details" prefixes |
| **C** | 2018 Q2–2019 | `trip_id`, `start_time`/`end_time`, `usertype` |
| **D** | 2020+ | `ride_id`, `started_at`/`ended_at`, `member_casual`, `rideable_type` |

The ingest script normalises all four schemas into Schema D before analysis.

---

## How to Run

```bash
# 1. Clone the repository
git clone https://github.com/YOUR-USERNAME/cyclistic-bike-share.git
cd cyclistic-bike-share

# 2. Set up Python environment (Ubuntu / WSL)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Download raw data
# Get all Divvy trip CSVs from https://divvy-tripdata.com
# Place them in raw_data/ preserving folder structure

# 4. Run in order
python 00_setup.py       # check environment
python 01_ingest.py      # ~5–20 min, creates cyclistic.db
python 02_aggregate.py   # ~1–5 min, creates summary CSVs
python 03_visualize.py   # <1 min, creates chart PNGs
```

## 🛠️ Tools Used

| Tool | Purpose |
|:-----|:--------|
| 🐍 **Python 3.10** | Core language for data processing |
| 📊 **Pandas** | Data transformation and aggregation |
| 🗄️ **SQLite3** (built-in) | Memory-safe storage of 30M+ row dataset |
| 📈 **Matplotlib / Seaborn** | Visualisations |
| 🔧 **Git / GitHub** | Version control and portfolio hosting |
| 🐧 **Ubuntu on WSL** | Development environment |

---

## 👤 Author

**Dollars Ita** • [LinkedIn](https://linkedin.com/in/dollars-ita)