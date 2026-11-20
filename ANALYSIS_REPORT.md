# Online Shopping Delivery & Logistics Analysis Report (Project 23)

## 1. Executive Summary
An end-to-end logistics audit was conducted on `23_delivery_performance.csv` (913 raw shipment records across 9 fields). After deduplicating 13 repeated `Shipment_ID` rows, **900 unique shipments** were analyzed. Overall delivery success stands at **81.89%** (**737 Delivered**), while average delivery duration across valid records is **8.07 days** (median **8.00 days**, standard deviation **4.26 days**).

---

## 2. Data Cleaning & Preparation Methodology
- **Duplicate Removal:** Identified and removed **13 exact duplicate `Shipment_ID` records** (rows `900`–`912`), reducing the dataset from 913 to **900 unique shipments**.
- **Missing `Shipping_Cost` Handling (22 rows):** Imputed missing costs using the **median `Shipping_Cost` grouped by `Shipping_Method`** to preserve service-tier pricing structure without distortion from extreme values.
- **Missing `Delivery_Date` Handling (22 rows in clean set):**
  - **20 `Delivered` records** missing a `Delivery_Date` were imputed using `Order_Date + rounded median Delivery_Days for that Shipping_Method` so completed deliveries remain represented in duration metrics.
  - **2 `In Transit` records** missing a `Delivery_Date` were left as `NaT` because delivery had not yet occurred.

---

## 3. Core Logistics Performance Metrics

### 3.1 Overall Delivery Summary
| Metric | Value |
| :--- | :---: |
| Raw Dataset Records | 913 |
| Duplicate `Shipment_ID` Records Removed | 13 |
| Unique Clean Shipments | 900 |
| Delivered Shipments | 737 |
| In Transit Shipments | 71 |
| Returned Shipments | 55 |
| Failed Shipments | 37 |
| **Overall Delivery Success Rate** | **81.89%** |
| Mean Delivery Duration (NumPy) | 8.07 days |
| Median Delivery Duration (NumPy) | 8.00 days |
| Standard Deviation (NumPy, ddof=1) | 4.26 days |

### 3.2 Shipping Method Comparison
| Shipping Method | Total Shipments | Delivered | Failed | Returned | In Transit | Success Rate (%) | Avg Delivery Days | Avg Cost |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Express** | 238 | 202 | 9 | 13 | 14 | **84.87%** | 8.06 | 341.15 |
| **Same Day** | 225 | 186 | 7 | 14 | 18 | **82.67%** | 8.02 | 314.83 |
| **Economy** | 211 | 171 | 11 | 14 | 15 | **81.04%** | 8.04 | 309.71 |
| **Standard** | 226 | 178 | 10 | 14 | 24 | **78.76%** | 8.14 | 333.47 |

### 3.3 Delivery Partner Ranking
| Delivery Partner | Total Shipments | Volume Rank | Delivered | Success Rate (%) | Avg Delivery Days | Speed Rank (1 = Fastest) | Avg Cost |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Partner D** | 196 | 1 | 168 | **85.71%** | 7.87 | 2 | 332.59 |
| **Partner B** | 184 | 2 | 148 | 80.43% | 8.18 | 4 | 323.10 |
| **Partner E** | 181 | 3 | 149 | 82.32% | **7.78** | 1 | 331.15 |
| **Partner A** | 175 | 4 | 142 | 81.14% | 8.16 | 3 | 324.46 |
| **Partner C** | 164 | 5 | 130 | 79.27% | 8.37 | 5 | 313.68 |

---

## 4. Delay Classification, IQR Outliers & Monthly Trends
- **Delay Classification Rules:**
  - **On-Time (`<= 5 days`):** 282 shipments (31.33%)
  - **Slightly Delayed (`6–10 days`):** 325 shipments (36.11%)
  - **Highly Delayed (`> 10 days`):** 291 shipments (32.33%)
  - **Pending / Unknown (`NaN`):** 2 shipments (0.22%)
- **IQR Outlier Detection:**
  - $Q_1 = 5.0$ days, $Q_3 = 12.0$ days, $	ext{IQR} = 7.0$ days.
  - Upper Fence $= Q_3 + 1.5 	imes 	ext{IQR} = 22.5$ days.
  - Because the dataset's delivery durations are bounded between **1 and 15 days**, **0 shipments** exceed the statistical upper fence of `22.5` days, though **54 shipments** hit the 15-day ceiling.
- **Monthly Trend Highlights:**
  - Order volume spans **January 2025 to October 2026** (22 months).
  - Peak volume months were **July 2026** (51 orders), **April 2025** (49 orders), and **March 2026** (49 orders).
  - Slowest average transit occurred in **May 2025** (9.35 days), while fastest occurred in **February 2025** (6.96 days).

---

## 5. Five Actionable Logistics Recommendations
1. **Reallocate Volume Toward Top-Performing Carriers:** Shift shipments away from **Partner C** (79.27% success rate, 8.37 avg days) toward **Partner D** (85.71% success rate) and **Partner E** (7.78 avg days), especially on Standard-tier routes where completion rates lag at **78.76%**.
2. **Audit SLA Breaches on Premium & Intra-City Lanes:** Several **Same Day** and **Express** intra-city shipments (`SH000448` Delhi–Delhi, `SH000670` Mumbai–Mumbai, `SH000356` Chennai–Chennai) took **15 days** at premium shipping fees (`>540`). Implement automated 48-hour escalation triggers for intra-city and Express orders.
3. **Enforce Data Ingestion Validation & Mandatory Scan Events:** Eliminate the **13 duplicate `Shipment_ID` records** and **22 missing `Delivery_Date` fields** by adding primary-key constraints in the order management database and requiring carrier barcode scans at final delivery.
4. **Reduce Failed & Returned Orders (`92` Combined / `10.22%`):** With `55` Returned and `37` Failed shipments, introduce automated address verification at checkout and SMS/OTP delivery-slot confirmation prior to final-mile dispatch.
5. **Align Customer ETAs & Capacity with Monthly Peaks:** Recalibrate promised delivery windows for **Standard** and **Economy** tiers (currently averaging ~8.0–8.1 days) and pre-allocate carrier capacity ahead of high-volume months (March–July).
