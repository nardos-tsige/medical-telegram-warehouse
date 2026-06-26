# 🏥 Medical Telegram Warehouse

An end-to-end data pipeline for analyzing Ethiopian medical businesses from public Telegram channels.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![dbt](https://img.shields.io/badge/dbt-1.5.0-orange.svg)](https://www.getdbt.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-green.svg)](https://fastapi.tiangolo.com/)
[![Dagster](https://img.shields.io/badge/Dagster-1.4.0-purple.svg)](https://dagster.io/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Business Questions](#business-questions)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Tasks](#tasks)
- [API Endpoints](#api-endpoints)
- [Results](#results)
- [Contributing](#contributing)
- [License](#license)

---

## 📖 Overview

This project builds a robust data platform that generates actionable insights about Ethiopian medical businesses using data scraped from public Telegram channels. The platform implements a modern ELT (Extract, Load, Transform) framework with a layered data architecture.

### Business Need

A well-designed data platform significantly enhances data analysis. This platform answers key business questions such as:

- What are the top 10 most frequently mentioned medical products or drugs across all channels?
- How does the price or availability of a specific product vary across different channels?
- Which channels have the most visual content (e.g., images of pills vs. creams)?
- What are the daily and weekly trends in posting volume for health-related topics?

---

## 🎯 Business Questions

| Question | How It's Answered |
|----------|-------------------|
| Top 10 mentioned products | API: `/api/reports/top-products` |
| Product price/availability across channels | API: `/api/channels/{channel_name}/activity` |
| Channels with most visual content | API: `/api/reports/visual-content` |
| Daily/weekly posting trends | API: `/api/channels/{channel_name}/activity` |

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────────────────────┐

│                        MEDICAL TELEGRAM WAREHOUSE                           │

├─────────────────────────────────────────────────────────────────────────────┤

│                                                                             │

│  📡 Telegram Channels (14)                                                  │

│          ↓                                                                  │

│  🕷️ Scraper (Telethon)                                                      │

│          ↓                                                                  │

│  📂 Data Lake (JSON Files)                                                  │

│          ↓                                                                  │

│  💾 PostgreSQL (raw.telegram_messages)                                      │

│          ↓                                                                  │

│  🔄 dbt Transformations                                                     │

│     ├── staging.stg_telegram_messages (View)                                │

│     ├── marts.dim_channels (8 channels)                                     │

│     ├── marts.dim_dates (31 days)                                           │

│     └── marts.fct_messages (4,849 messages)                                 │

│          ↓                                                                  │

│  🤖 YOLOv8 Enrichment (93 detections)                                       │

│          ↓                                                                  │

│  🚀 FastAPI (5 Endpoints)                                                   │

│          ↓                                                                  │

│  ⏰ Dagster (Daily Orchestration)                                            │

│                                                                             │

└─────────────────────────────────────────────────────────────────────────────┘

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Scraping** | Telethon | Extract data from Telegram channels |
| **Data Lake** | JSON Files | Store raw scraped data |
| **Database** | PostgreSQL 15 | Data warehouse |
| **Transformation** | dbt 1.5.0 | Data modeling and transformation |
| **Object Detection** | YOLOv8 | Image analysis and classification |
| **API** | FastAPI 0.100.0 | REST API for analytics |
| **Orchestration** | Dagster 1.4.0 | Pipeline automation |
| **Containerization** | Docker | Environment consistency |

---

## 📁 Project Structure
medical-telegram-warehouse/

├── .github/

│   └── workflows/

│       └── unittests.yml          # GitHub Actions CI/CD

├── api/

│   ├── init.py

│   ├── main.py                    # FastAPI application

│   ├── database.py                # Database connection

│   └── schemas.py                 # Pydantic models

├── data/

│   ├── raw/

│   │   ├── telegram_messages/     # JSON data lake

│   │   └── images/                # Downloaded images

│   └── processed/                 # YOLO detection results

├── logs/                          # Application logs

├── medical_warehouse/             # dbt project

│   ├── dbt_project.yml

│   ├── profiles.yml

│   ├── models/

│   │   ├── staging/

│   │   │   └── stg_telegram_messages.sql

│   │   └── marts/

│   │       ├── dim_channels.sql

│   │       ├── dim_dates.sql

│   │       ├── fct_messages.sql

│   │       └── schema.yml

│   └── tests/

├── notebooks/                     # Jupyter notebooks

├── scripts/

│   ├── load_raw_data.py           # Load JSON to PostgreSQL

│   └── load_yolo_results.py       # Load YOLO results

├── src/

│   ├── scraper.py                 # Telegram scraper

│   ├── yolo_detect.py             # YOLO object detection

│   └── database.py                # Database utilities

├── tests/                         # Unit tests

├── .env                           # Environment variables (DO NOT COMMIT)

├── .gitignore

├── Dockerfile

├── docker-compose.yml

├── requirements.txt

├── README.md

└── pipeline.py                    # Dagster pipeline

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 15+
- Docker (optional)
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/nardos-tsige/medical-telegram-warehouse.git
cd medical-telegram-warehouse

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# 5. Start PostgreSQL (local or Docker)
docker-compose up -d

# 6. Run the full pipeline
python src/scraper.py
python scripts/load_raw_data.py
cd medical_warehouse
dbt run
dbt test
cd ..
python src/yolo_detect.py
python scripts/load_yolo_results.py
```

---

## 📝 Tasks

### Task 1: Data Scraping and Collection
- Scraped 5,009 messages from 14 channels
- Downloaded 935 images
- Implemented partitioned data lake structure
- Logging system for monitoring

### Task 2: Data Modeling with dbt
- Created star schema with:
  - `dim_channels`: 8 channels
  - `dim_dates`: 31 days
  - `fct_messages`: 4,849 messages
- Implemented data quality tests
- Generated dbt documentation

### Task 3: YOLO Enrichment
- Processed images with YOLOv8
- Classified images into categories:
  - Promotional (24)
  - Lifestyle (26)
  - Product Display (20)
  - Other (23)
- 93 total detections from 50 images

### Task 4: FastAPI Development
- 5 analytical endpoints
- OpenAPI documentation
- Pydantic validation
- Proper error handling

### Task 5: Pipeline Orchestration
- Dagster pipeline with 5 operations
- Daily schedule at 9:00 AM
- Observable and monitorable

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API root |
| GET | `/api/health` | Health check |
| GET | `/api/reports/top-products?limit=10` | Top mentioned products |
| GET | `/api/channels/{channel_name}/activity?days=30` | Channel activity trends |
| GET | `/api/search/messages?query=paracetamol&limit=20` | Search messages |
| GET | `/api/reports/visual-content` | Visual content statistics |

### API Documentation

```bash
# Start the API
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Access Swagger UI
http://localhost:8000/docs

# Access ReDoc
http://localhost:8000/redoc
```

---

## 📊 Results

| Metric | Value |
|--------|-------|
| Total Messages | 5,009 |
| Channels | 14 |
| Images Downloaded | 935 |
| YOLO Detections | 93 |
| dbt Models | 4 (1 staging, 3 marts) |
| API Endpoints | 5 |
| Pipeline Operations | 5 |
| Schedule | Daily at 9:00 AM |

### Channel Distribution

| Channel | Messages | Channel Type |
|---------|----------|--------------|
| ethio_vital_health | 2,691 | Medical |
| PharmacyHubEthiopia | 711 | Pharmaceutical |
| lobelia4cosmetics | 658 | Cosmetics |
| ethiomedicalgroup | 553 | Medical |
| EHPMOFFICIAL | 207 | Medical |
| epn_2025 | 23 | Medical |
| EMA_Ethiopia | 4 | Medical |
| greatethiopharma | 2 | Pharmaceutical |

---

## 🧪 Testing

```bash
# Run dbt tests
cd medical_warehouse
dbt test

# Run Python tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov=api
```

---

## 🐳 Docker Support

```bash
# Build and start containers
docker-compose up -d

# Access services
# FastAPI:    http://localhost:8000
# Dagster:    http://localhost:3000
# PostgreSQL: localhost:5432
```

---

## 📈 Monitoring

### Dagster UI

```bash
dagster dev -f pipeline.py
# Access: http://localhost:3000
```

### Service Status

```bash
# Check API health
curl http://localhost:8000/api/health

# Check PostgreSQL
psql -U medical_user -d medical_warehouse -c "SELECT COUNT(*) FROM marts.fct_messages;"
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code |
| `task-1-data-scraping` | Data scraping implementation |
| `task-2-data-modeling` | dbt modeling |
| `task-3-yolo-enrichment` | YOLO implementation |
| `task-4-api-development` | FastAPI |
| `task-5-pipeline-orchestration` | Dagster |

---

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Telethon](https://github.com/LonamiWebs/Telethon) — Telegram API client
- [dbt](https://www.getdbt.com/) — Data transformation
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) — Object detection
- [FastAPI](https://fastapi.tiangolo.com/) — API framework
- [Dagster](https://dagster.io/) — Pipeline orchestration

---

## 📧 Contact

**Author:** Nardos Tsige  
**GitHub:** [@nardos-tsige](https://github.com/nardos-tsige)  
**Project Link:** [https://github.com/nardos-tsige/medical-telegram-warehouse](https://github.com/nardos-tsige/medical-telegram-warehouse)

---

⭐ **Show Your Support** — If you found this project helpful, please give it a star on GitHub!

---

*Built with ❤️ for Ethiopian medical data analytics*
