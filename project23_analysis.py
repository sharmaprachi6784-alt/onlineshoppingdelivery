import os 
import numpy as np
import pandas as pd

# 1. Load the delivery dataset and inspect its shape, columns, and data types
df = pd.read_csv("23_delivery_performance.csv")
print("Dataset Shape:", df.shape)
print("\nColumns and Data Types:\n", df.dtypes)

# 2. Identify missing values and duplicate Shipment_ID records
print("\nMissing Values:\n", df.isna().sum())
dup_count = int(df["Shipment_ID"].duplicated().sum())
print(f"\nDuplicate Shipment_ID records: {dup_count}")

# Remove duplicate Shipment_ID rows (keep first occurrence)
df_clean = df.drop_duplicates(subset=["Shipment_ID"], keep="first").copy()

# 3. Handle missing Delivery_Date or Shipping_Cost values using median imputation
method_cost_med = df_clean.groupby("Shipping_Method")["Shipping_Cost"].transform("median")
df_clean["Shipping_Cost"] = (
    df_clean["Shipping_Cost"]
    .fillna(method_cost_med)
    .fillna(df_clean["Shipping_Cost"].median())
)

# 4. Convert Order_Date and Delivery_Date to datetime
df_clean["Order_Date"] = pd.to_datetime(df_clean["Order_Date"])
df_clean["Delivery_Date"] = pd.to_datetime(df_clean["Delivery_Date"])

# Impute missing Delivery_Date only for 'Delivered' orders using median Delivery_Days per Shipping_Method
raw_days = (df_clean["Delivery_Date"] - df_clean["Order_Date"]).dt.days
method_days_med = raw_days.groupby(df_clean["Shipping_Method"]).transform("median").round()
mask_deliv_na = (df_clean["Delivery_Status"] == "Delivered") & (df_clean["Delivery_Date"].isna())
df_clean.loc[mask_deliv_na, "Delivery_Date"] = (
    df_clean.loc[mask_deliv_na, "Order_Date"]
    + pd.to_timedelta(method_days_med[mask_deliv_na], unit="D")
)

# 5. Calculate Delivery_Days by subtracting Order_Date from Delivery_Date
df_clean["Delivery_Days"] = (df_clean["Delivery_Date"] - df_clean["Order_Date"]).dt.days

# 6. Calculate total shipments, delivered shipments, and overall delivery success percentage
total_shipments = len(df_clean)
delivered_shipments = int((df_clean["Delivery_Status"] == "Delivered").sum())
success_rate = (delivered_shipments / total_shipments) * 100 if total_shipments > 0 else 0.0

print(f"\nTotal Shipments: {total_shipments}")
print(f"Delivered Shipments: {delivered_shipments}")
print(f"Overall Delivery Success Rate: {success_rate:.2f}%")

# 7. Find delivery duration statistics for each shipping method
method_duration = (
    df_clean.groupby("Shipping_Method")["Delivery_Days"]
    .agg(
        Count="count",
        Mean_Days="mean",
        Median_Days="median",
        Std_Days="std",
        Min_Days="min",
        Max_Days="max",
    )
    .round(2)
    .reset_index()
)
print("\nDelivery Duration by Shipping Method:\n", method_duration.to_string(index=False))

# 8. Rank delivery partners by number of shipments and average delivery duration
partner_ranking = (
    df_clean.groupby("Delivery_Partner")
    .agg(
        Total_Shipments=("Shipment_ID", "count"),
        Delivered_Shipments=("Delivery_Status", lambda s: (s == "Delivered").sum()),
        Avg_Delivery_Days=("Delivery_Days", "mean"),
        Median_Delivery_Days=("Delivery_Days", "median"),
        Avg_Shipping_Cost=("Shipping_Cost", "mean"),
    )
    .reset_index()
)

partner_ranking["Success_Rate_%"] = (
    partner_ranking["Delivered_Shipments"] / partner_ranking["Total_Shipments"] * 100
).round(2)
partner_ranking["Avg_Delivery_Days"] = partner_ranking["Avg_Delivery_Days"].round(2)
partner_ranking["Median_Delivery_Days"] = partner_ranking["Median_Delivery_Days"].round(2)
partner_ranking["Avg_Shipping_Cost"] = partner_ranking["Avg_Shipping_Cost"].round(2)
partner_ranking["Rank_By_Volume"] = (
    partner_ranking["Total_Shipments"].rank(ascending=False, method="min").astype(int)
)
partner_ranking["Rank_By_Speed"] = (
    partner_ranking["Avg_Delivery_Days"].rank(ascending=True, method="min").astype(int)
)

partner_ranking = partner_ranking.sort_values("Rank_By_Volume")
print("\nDelivery Partner Ranking:\n", partner_ranking.to_string(index=False))

# 9. Compare delivery success rates across shipping methods
method_comparison = (
    df_clean.groupby("Shipping_Method")
    .agg(
        Total_Shipments=("Shipment_ID", "count"),
        Delivered=("Delivery_Status", lambda s: (s == "Delivered").sum()),
        Failed=("Delivery_Status", lambda s: (s == "Failed").sum()),
        Returned=("Delivery_Status", lambda s: (s == "Returned").sum()),
        In_Transit=("Delivery_Status", lambda s: (s == "In Transit").sum()),
        Avg_Delivery_Days=("Delivery_Days", "mean"),
        Avg_Shipping_Cost=("Shipping_Cost", "mean"),
    )
    .reset_index()
)

method_comparison["Success_Rate_%"] = (
    method_comparison["Delivered"] / method_comparison["Total_Shipments"] * 100
).round(2)
method_comparison["Avg_Delivery_Days"] = method_comparison["Avg_Delivery_Days"].round(2)
method_comparison["Avg_Shipping_Cost"] = method_comparison["Avg_Shipping_Cost"].round(2)
print("\nShipping Method Comparison:\n", method_comparison.to_string(index=False))

# 10. Identify the 10 shipments with the longest delivery duration
top_10_longest = (
    df_clean.dropna(subset=["Delivery_Days"])
    .sort_values(by=["Delivery_Days", "Shipping_Cost"], ascending=[False, False])
    .head(10)[
        [
            "Shipment_ID", "Order_Date", "Delivery_Date", "Delivery_Days",
            "Shipping_Method", "Delivery_Partner", "Delivery_Status",
            "Origin_City", "Destination_City", "Shipping_Cost",
        ]
    ]
)
print("\nTop 10 Longest Shipments:\n", top_10_longest.to_string(index=False))

# 11. Dictionary for delivery counts by status & set for unique delivery partners
status_counts = {}
for status in df_clean["Delivery_Status"]:
    status_counts[status] = status_counts.get(status, 0) + 1
unique_partners = set(df_clean["Delivery_Partner"])

# 12. Function that labels each shipment as On-Time, Slightly Delayed, or Highly Delayed
def label_delay(days):
    if pd.isna(days):
        return "Pending / Unknown"
    elif days <= 5:
        return "On-Time"
    elif days <= 10:
        return "Slightly Delayed"
    else:
        return "Highly Delayed"

df_clean["Delay_Status"] = df_clean["Delivery_Days"].apply(label_delay)

# 13. Use NumPy to calculate mean, median, and standard deviation of Delivery_Days
days_array = df_clean["Delivery_Days"].dropna().to_numpy()
np_mean = float(np.mean(days_array))
np_median = float(np.median(days_array))
np_std = float(np.std(days_array, ddof=1))

# 14. Identify unusually long delivery durations using IQR & compare performance by month
q1, q3 = np.percentile(days_array, [25, 75])
iqr = float(q3 - q1)
upper_bound = float(q3 + 1.5 * iqr)
iqr_outliers = df_clean[df_clean["Delivery_Days"] > upper_bound]

df_clean["Order_Month"] = df_clean["Order_Date"].dt.to_period("M").astype(str)
monthly_trends = (
    df_clean.groupby("Order_Month")
    .agg(
        Total_Shipments=("Shipment_ID", "count"),
        Delivered=("Delivery_Status", lambda s: (s == "Delivered").sum()),
        Avg_Delivery_Days=("Delivery_Days", "mean"),
        Avg_Shipping_Cost=("Shipping_Cost", "mean"),
    )
    .reset_index()
)

monthly_trends["Success_Rate_%"] = (
    monthly_trends["Delivered"] / monthly_trends["Total_Shipments"] * 100
).round(2)
monthly_trends["Avg_Delivery_Days"] = monthly_trends["Avg_Delivery_Days"].round(2)
monthly_trends["Avg_Shipping_Cost"] = monthly_trends["Avg_Shipping_Cost"].round(2)

# 15. Simple Shipment class
class Shipment:
    def __init__(self, shipment_id, partner, delivery_days):
        self.shipment_id = shipment_id
        self.partner = partner
        self.delivery_days = delivery_days

    def __repr__(self):
        return f"Shipment(id='{self.shipment_id}', partner='{self.partner}', delivery_days={self.delivery_days})"

sample_objects = [
    Shipment(r.Shipment_ID, r.Delivery_Partner, r.Delivery_Days)
    for r in df_clean.dropna(subset=["Delivery_Days"]).head(5).itertuples()
]

# Tabular summaries (NumPy + pandas only)
hist_counts, bin_edges = np.histogram(days_array, bins=15)
duration_bins_df = pd.DataFrame({
    "Bin_Start_Days": np.round(bin_edges[:-1], 2),
    "Bin_End_Days": np.round(bin_edges[1:], 2),
    "Shipment_Count": hist_counts,
})

delay_breakdown_df = (
    df_clean["Delay_Status"].value_counts(dropna=False)
    .rename_axis("Delay_Status").reset_index(name="Shipment_Count")
)

status_breakdown_df = (
    pd.Series(status_counts, name="Shipment_Count")
    .sort_values(ascending=False).rename_axis("Delivery_Status").reset_index()
)

print("\nDelay Status Breakdown:\n", delay_breakdown_df.to_string(index=False))
print("\nDelivery Status Breakdown:\n", status_breakdown_df.to_string(index=False))
print("\nMonthly Trends:\n", monthly_trends.to_string(index=False))
print("\nSample Shipment Objects:\n", sample_objects)

# Export deliverables to outputs/
import os

os.makedirs("outputs", exist_ok=True)
df_clean.to_csv("outputs/cleaned_delivery_data.csv", index=False)
method_comparison.to_csv("outputs/shipping_method_comparison.csv", index=False)
partner_ranking.to_csv("outputs/delivery_partner_ranking.csv", index=False)
top_10_longest.to_csv("outputs/top_10_delayed_shipments.csv", index=False)
df_clean[df_clean["Delay_Status"] == "Highly Delayed"].to_csv("outputs/highly_delayed_shipments.csv", index=False)
monthly_trends.to_csv("outputs/monthly_delivery_trends.csv", index=False)
duration_bins_df.to_csv("outputs/delivery_duration_histogram.csv", index=False)

summary_metrics = pd.DataFrame({
    "Metric": [
        "Raw Records", "Duplicate Shipment_IDs Removed", "Unique Clean Shipments",
        "Delivered Shipments", "Overall Delivery Success Rate (%)",
        "Mean Delivery Days (NumPy)", "Median Delivery Days (NumPy)",
        "Std Dev Delivery Days (NumPy)", "IQR (Q3 - Q1)", "IQR Upper Fence (Days)",
        "IQR Outlier Shipments Count", "Unique Delivery Partners",
    ],
    "Value": [
        len(df), dup_count, total_shipments, delivered_shipments, round(success_rate, 2),
        round(np_mean, 2), round(np_median, 2), round(np_std, 2), round(iqr, 2),
        round(upper_bound, 2), len(iqr_outliers), len(unique_partners),
    ],
})

os.makedirs("outputs",exist_ok=True)
df_clean.to_csv("outputs/cleaned_data.csv",index=False)
summary_metrics.to_csv("outputs/delivery_duration_summary.csv", index=False)
print("\nAll outputs generated successfully using only NumPy and pandas.")
