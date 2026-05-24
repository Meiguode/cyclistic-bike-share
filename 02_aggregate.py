import pandas as pd
import sqlite3
import os
import gc
import time

DB_PATH = "cyclistic.db"
OUT_DIR = "outputs/summary_stats"
CHUNK_SIZE = 100000

os.makedirs(OUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
print("Connected to database.")

def query_to_csv_chunked(query, output_file, description="Processing"):
    first_chunk = True
    total_rows = 0
    chunk_num = 0
    
    print(f"  {description}...", end=" ", flush=True)
    start_time = time.time()
    
    for chunk in pd.read_sql(query, conn, chunksize=CHUNK_SIZE):
        if len(chunk) == 0:
            continue
        
        mode = 'w' if first_chunk else 'a'
        header = first_chunk
        chunk.to_csv(output_file, mode=mode, header=header, index=False)
        
        total_rows += len(chunk)
        chunk_num += 1
        first_chunk = False
        
        if chunk_num % 10 == 0:
            print(f"\r  {description}: {total_rows:,} rows processed...", end=" ", flush=True)
        
        del chunk
        gc.collect()
    
    elapsed = time.time() - start_time
    print(f"\r  {description}: ✅ {total_rows:,} rows in {elapsed:.1f}s")
    return total_rows

def query_with_progress(query, description):
    print(f"  {description}...", end=" ", flush=True)
    start_time = time.time()
    result = pd.read_sql(query, conn)
    elapsed = time.time() - start_time
    print(f"✅ {len(result):,} rows in {elapsed:.1f}s")
    return result

print("\n" + "="*60)
print("RUNNING AGGREGATIONS")
print("="*60)

q1 = query_with_progress("""
    SELECT
        member_casual,
        day_of_week,
        COUNT(*) as ride_count,
        ROUND(AVG(ride_length_min), 2) as avg_duration_min
    FROM trips
    WHERE member_casual IN ("member","casual")
      AND day_of_week IS NOT NULL
    GROUP BY member_casual, day_of_week
    ORDER BY member_casual, day_of_week
""", "Q1: Rides by day of week")
q1.to_csv(f"{OUT_DIR}/01_rides_by_day.csv", index=False)

q2 = query_with_progress("""
    SELECT
        member_casual,
        ROUND(AVG(ride_length_min), 2) as avg_duration_min,
        ROUND(MAX(ride_length_min), 2) as max_duration_min,
        COUNT(*) as ride_count
    FROM trips
    WHERE member_casual IN ("member","casual")
    GROUP BY member_casual
""", "Q2: Average duration")
q2.to_csv(f"{OUT_DIR}/02_avg_duration.csv", index=False)

q3 = query_with_progress("""
    SELECT
        member_casual,
        year,
        month_num,
        month,
        COUNT(*) as ride_count
    FROM trips
    WHERE member_casual IN ("member","casual")
      AND month IS NOT NULL
    GROUP BY member_casual, year, month_num, month
    ORDER BY year, month_num
""", "Q3: Monthly ride volume")
q3.to_csv(f"{OUT_DIR}/03_monthly_rides.csv", index=False)

q4 = query_with_progress("""
    SELECT
        member_casual,
        hour,
        COUNT(*) as ride_count
    FROM trips
    WHERE member_casual IN ("member","casual")
      AND hour IS NOT NULL
    GROUP BY member_casual, hour
    ORDER BY member_casual, hour
""", "Q4: Peak hour distribution")
q4.to_csv(f"{OUT_DIR}/04_peak_hours.csv", index=False)

print("\n  Q5: Top stations by user type")
temp_file = f"{OUT_DIR}/_temp_stations.csv"
rows = query_to_csv_chunked("""
    SELECT
        member_casual,
        start_station_name
    FROM trips
    WHERE member_casual IN ("member","casual")
      AND start_station_name IS NOT NULL
      AND start_station_name != ""
""", temp_file, "  Q5: Reading station data")

if rows > 0:
    print("  Q5: Aggregating station data...", end=" ", flush=True)
    start_time = time.time()
    df = pd.read_csv(temp_file)
    q5 = df.groupby(['member_casual', 'start_station_name']).size().reset_index(name='ride_count')
    q5 = q5.sort_values(['member_casual', 'ride_count'], ascending=[True, False])
    q5 = q5.groupby('member_casual').head(15).reset_index(drop=True)
    q5.to_csv(f"{OUT_DIR}/05_top_stations.csv", index=False)
    os.remove(temp_file)
    elapsed = time.time() - start_time
    print(f"✅ {len(q5)} rows in {elapsed:.1f}s")
else:
    print("  Q5: NO DATA")

q6 = query_with_progress("""
    SELECT
        member_casual,
        rideable_type,
        COUNT(*) as ride_count
    FROM trips
    WHERE member_casual IN ("member","casual")
      AND rideable_type IS NOT NULL
      AND rideable_type != ""
    GROUP BY member_casual, rideable_type
    ORDER BY member_casual, ride_count DESC
""", "Q6: Bike type preference")
q6.to_csv(f"{OUT_DIR}/06_bike_type.csv", index=False)

q7 = query_with_progress("""
    SELECT
        member_casual,
        COUNT(*) as total_rides,
        ROUND(AVG(ride_length_min), 2) as avg_min,
        ROUND(SUM(ride_length_min), 0) as total_min
    FROM trips
    WHERE member_casual IN ("member","casual")
    GROUP BY member_casual
""", "Q7: Revenue proxy")

AVG_CASUAL_SPEND = 3.50
q7["est_revenue_proxy"] = q7.apply(
    lambda r: r["total_rides"] * AVG_CASUAL_SPEND if r["member_casual"] == "casual" else "see note",
    axis=1
)
q7.to_csv(f"{OUT_DIR}/07_revenue_proxy.csv", index=False)

q8 = query_with_progress("""
    SELECT
        member_casual,
        year,
        COUNT(*) as ride_count,
        ROUND(AVG(ride_length_min), 2) as avg_duration_min
    FROM trips
    WHERE member_casual IN ("member","casual")
      AND year IS NOT NULL
    GROUP BY member_casual, year
    ORDER BY year
""", "Q8: Yearly trend")
q8.to_csv(f"{OUT_DIR}/08_yearly_trend.csv", index=False)

conn.close()

print("\n" + "="*60)
print("✅ ALL AGGREGATIONS COMPLETE")
print("="*60)
print(f"📁 Files saved to: {OUT_DIR}/")
print("\nOutput files:")
for f in sorted(os.listdir(OUT_DIR)):
    if f.endswith('.csv') and not f.startswith('_temp'):
        size = os.path.getsize(os.path.join(OUT_DIR, f)) / 1024
        print(f"  📄 {f} ({size:.1f} KB)")
print("="*60)