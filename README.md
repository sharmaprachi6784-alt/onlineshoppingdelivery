# Project 23: Online Shopping Delivery & Logistics Analysis

## Overview
This project analyzes e-commerce delivery and logistics performance using `23_delivery_performance.csv`. It evaluates transit times, shipping tier effectiveness, delivery partner rankings, delay classifications, statistical outliers (IQR), and monthly trends to provide actionable logistics recommendations.

## Folder Structure
```text
Project23_Delivery_Logistics_Analysis/
├── outputs/
│   ├── cleaned_delivery_data.csv
│   ├── delivery_duration_summary.csv
│   ├── delivery_partner_ranking.csv
│   ├── highly_delayed_shipments.csv
│   ├── monthly_delivery_trends.csv
│   ├── shipping_method_comparison.csv
│   └── top_10_delayed_shipments.csv
├── visualizations/
│   ├── 01_delivery_duration_distribution.png
│   ├── 02_shipping_method_comparison.png
│   ├── 03_delivery_partner_ranking.png
│   ├── 04_monthly_delivery_trends.png
│   └── 05_delay_and_status_breakdown.png
├── 23_delivery_performance.csv
├── ANALYSIS_REPORT.md
├── project23_analysis.py
├── README.md
├── requirements.txt
└── SRS_Project23.docx
```

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the analysis pipeline:
   ```bash
   python project23_analysis.py
   ```
3. Review generated summary tables in `outputs/` and charts in `visualizations/`.
