import sqlite3
import glob
import os
import sys
import gc
import csv
from pathlib import Path
from datetime import datetime

CHUNK_SIZE = 5000
DB_PATH = "cyclistic.db"
TABLE_NAME = "trips"

def clean_duration(duration_str):
    if not duration_str:
        return None
    try:
        return float(duration_str.replace(',', ''))
    except:
        return None

def parse_datetime_legacy(dt_str):
    if not dt_str:
        return None
    try:
        dt_str = dt_str.strip('"')
        
        if '-' in dt_str:
            if '.' in dt_str:
                dt_str = dt_str.split('.')[0]
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        else:
            try:
                return datetime.strptime(dt_str, '%m/%d/%Y %H:%M:%S')
            except:
                # Try without seconds
                return datetime.strptime(dt_str, '%m/%d/%Y %H:%M')
    except:
        try:
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None

def parse_datetime(dt_str):
    if not dt_str:
        return None
    if '.' in dt_str:
        dt_str = dt_str.split('.')[0]
    try:
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    except:
        return parse_datetime_legacy(dt_str)

def normalise_usertype(user_type):
    if not user_type:
        return None
    user_type = user_type.lower().strip()
    if user_type in ['subscriber', 'member']:
        return 'member'
    elif user_type in ['customer', 'casual']:
        return 'casual'
    return None

def get_field(row, idx, default=''):
    return row[idx].strip() if idx < len(row) else default

def process_row(row, schema):
    result = {}
    
    if schema == "D":
        if len(row) < 13:
            return None
        result['ride_id'] = get_field(row, 0)
        result['rideable_type'] = get_field(row, 1)
        result['started_at'] = parse_datetime(get_field(row, 2))
        result['ended_at'] = parse_datetime(get_field(row, 3))
        result['start_station_name'] = get_field(row, 4)
        result['start_station_id'] = get_field(row, 5)
        result['end_station_name'] = get_field(row, 6)
        result['end_station_id'] = get_field(row, 7)
        result['start_lat'] = float(get_field(row, 8)) if get_field(row, 8) else None
        result['start_lng'] = float(get_field(row, 9)) if get_field(row, 9) else None
        result['end_lat'] = float(get_field(row, 10)) if get_field(row, 10) else None
        result['end_lng'] = float(get_field(row, 11)) if get_field(row, 11) else None
        result['member_casual'] = normalise_usertype(get_field(row, 12))
        result['gender'] = None
        result['birth_year'] = None
        result['duration_sec'] = None
        
    elif schema == "B":
        if len(row) < 12:
            return None
        result['ride_id'] = get_field(row, 0)
        result['rideable_type'] = 'classic_bike'
        result['started_at'] = parse_datetime(get_field(row, 1))
        result['ended_at'] = parse_datetime(get_field(row, 2))
        result['start_station_name'] = get_field(row, 6)
        result['start_station_id'] = get_field(row, 5)
        result['end_station_name'] = get_field(row, 8)
        result['end_station_id'] = get_field(row, 7)
        result['start_lat'] = None
        result['start_lng'] = None
        result['end_lat'] = None
        result['end_lng'] = None
        result['member_casual'] = normalise_usertype(get_field(row, 9))
        result['gender'] = get_field(row, 10) if len(row) > 10 else None
        birth_year = get_field(row, 11) if len(row) > 11 else ''
        result['birth_year'] = int(birth_year) if birth_year and birth_year.isdigit() else None
        dur_str = get_field(row, 4) if len(row) > 4 else ''
        result['duration_sec'] = clean_duration(dur_str)
        
    elif schema == "C":
        if len(row) < 10:
            return None
        result['ride_id'] = get_field(row, 0)
        result['rideable_type'] = 'classic_bike'
        result['started_at'] = parse_datetime(get_field(row, 1))
        result['ended_at'] = parse_datetime(get_field(row, 2))
        result['start_station_name'] = get_field(row, 6) if len(row) > 6 else ''
        result['start_station_id'] = get_field(row, 5) if len(row) > 5 else ''
        result['end_station_name'] = get_field(row, 8) if len(row) > 8 else ''
        result['end_station_id'] = get_field(row, 7) if len(row) > 7 else ''
        result['start_lat'] = None
        result['start_lng'] = None
        result['end_lat'] = None
        result['end_lng'] = None
        result['member_casual'] = normalise_usertype(get_field(row, 9) if len(row) > 9 else '')
        result['gender'] = get_field(row, 10) if len(row) > 10 else None
        result['birth_year'] = int(get_field(row, 11)) if len(row) > 11 and get_field(row, 11) else None
        dur_str = get_field(row, 4) if len(row) > 4 else ''
        result['duration_sec'] = clean_duration(dur_str)
        
    elif schema == "A":
        if len(row) < 10:
            return None
        result['ride_id'] = get_field(row, 0)
        result['rideable_type'] = 'classic_bike'
        result['started_at'] = parse_datetime_legacy(get_field(row, 1))
        result['ended_at'] = parse_datetime_legacy(get_field(row, 2))
        result['start_station_name'] = get_field(row, 6) if len(row) > 6 else ''
        result['start_station_id'] = get_field(row, 5) if len(row) > 5 else ''
        result['end_station_name'] = get_field(row, 8) if len(row) > 8 else ''
        result['end_station_id'] = get_field(row, 7) if len(row) > 7 else ''
        result['start_lat'] = None
        result['start_lng'] = None
        result['end_lat'] = None
        result['end_lng'] = None
        result['member_casual'] = normalise_usertype(get_field(row, 9) if len(row) > 9 else '')
        result['gender'] = get_field(row, 10) if len(row) > 10 else None
        if len(row) > 11:
            birth_val = get_field(row, 11)
            result['birth_year'] = int(birth_val) if birth_val and birth_val.isdigit() else None
        else:
            result['birth_year'] = None
        dur_str = get_field(row, 4) if len(row) > 4 else ''
        result['duration_sec'] = clean_duration(dur_str)
        
    else:
        return None
    
    if result['started_at'] and result['ended_at']:
        delta = result['ended_at'] - result['started_at']
        result['duration_sec'] = delta.total_seconds()
        result['ride_length_min'] = round(delta.total_seconds() / 60, 2)
        result['day_of_week'] = result['started_at'].strftime('%A')
        result['month'] = result['started_at'].strftime('%B')
        result['month_num'] = result['started_at'].month
        result['year'] = result['started_at'].year
        result['hour'] = result['started_at'].hour
    else:
        result['ride_length_min'] = None
        result['day_of_week'] = None
        result['month'] = None
        result['month_num'] = None
        result['year'] = None
        result['hour'] = None
    
    if not result['member_casual']:
        return None
    if not result['started_at']:
        return None
    if result['ride_length_min'] is None or result['ride_length_min'] <= 0:
        return None
    if result['ride_length_min'] < 1 or result['ride_length_min'] > 1440:
        return None
    
    return result

def detect_schema_from_header(header):
    header_str = ' '.join(header).lower()
    
    if 'ride_id' in header_str and 'member_casual' in header_str:
        return "D"
    
    if 'rental details rental id' in header_str:
        return "B"
    
    if 'trip_id' in header_str and 'start_time' in header_str and 'end_time' in header_str:
        return "C"
    
    if 'trip_id' in header_str and 'starttime' in header_str:
        return "A"
    
    return "UNKNOWN"

SKIP_PATTERNS = [
    "divvy_stations", "stations_2013", "stations_2014",
    "stations_2015", "stations_2016", "stations_2017",
    "README", "readme", "Divvy_Stations", "Divvy_Stations_2013",
    "Divvy_Stations_2014", "Divvy_Stations_2015", "Divvy_Stations_2016",
    "Divvy_Stations_2017"
]

def should_skip(filepath):
    name = Path(filepath).name.lower()
    if 'station' in str(filepath).lower():
        return True
    return any(p.lower() in name for p in SKIP_PATTERNS)

def ingest_all():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())
    
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            ride_id TEXT,
            rideable_type TEXT,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            start_station_name TEXT,
            start_station_id TEXT,
            end_station_name TEXT,
            end_station_id TEXT,
            start_lat REAL,
            start_lng REAL,
            end_lat REAL,
            end_lng REAL,
            member_casual TEXT,
            gender TEXT,
            birth_year INTEGER,
            duration_sec REAL,
            ride_length_min REAL,
            day_of_week TEXT,
            month TEXT,
            month_num INTEGER,
            year INTEGER,
            hour INTEGER
        )
    """)
    conn.commit()
    
    total_rows = 0
    total_skipped = 0
    files = sorted(glob.glob("raw_data/**/*.csv", recursive=True))
    files = [f for f in files if not should_skip(f)]
    print(f"Trip files to process: {len(files)}")
    
    for i, filepath in enumerate(files):
        filename = Path(filepath).name
        folder = Path(filepath).parent.name
        display_name = f"{folder}/{filename}" if folder != "raw_data" else filename
        print(f"  [{i+1}/{len(files)}] {display_name}...", end=" ", flush=True)
        
        file_rows = 0
        file_bad = 0
        batch = []
        
        try:
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)
                schema = detect_schema_from_header(header)
                
                if schema == "UNKNOWN":
                    print(f"SKIPPED (unknown schema)")
                    continue
                
                for row_num, row in enumerate(reader, 2):
                    processed = process_row(row, schema)
                    
                    if processed is None:
                        file_bad += 1
                        continue
                    
                    batch.append((
                        processed.get('ride_id'),
                        processed.get('rideable_type'),
                        processed.get('started_at'),
                        processed.get('ended_at'),
                        processed.get('start_station_name'),
                        processed.get('start_station_id'),
                        processed.get('end_station_name'),
                        processed.get('end_station_id'),
                        processed.get('start_lat'),
                        processed.get('start_lng'),
                        processed.get('end_lat'),
                        processed.get('end_lng'),
                        processed.get('member_casual'),
                        processed.get('gender'),
                        processed.get('birth_year'),
                        processed.get('duration_sec'),
                        processed.get('ride_length_min'),
                        processed.get('day_of_week'),
                        processed.get('month'),
                        processed.get('month_num'),
                        processed.get('year'),
                        processed.get('hour')
                    ))
                    
                    file_rows += 1
                    
                    if len(batch) >= CHUNK_SIZE:
                        cursor.executemany(f"""
                            INSERT INTO {TABLE_NAME} VALUES (
                                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
                            )
                        """, batch)
                        conn.commit()
                        batch = []
                        gc.collect()
                
                if batch:
                    cursor.executemany(f"""
                        INSERT INTO {TABLE_NAME} VALUES (
                            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
                        )
                    """, batch)
                    conn.commit()
                
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            continue
        
        total_rows += file_rows
        total_skipped += file_bad
        print(f"✅ {file_rows:,} rows ({file_bad:,} filtered)")
    
    
    conn.commit()
    conn.close()
    
    print(f"\n" + "="*70)
    print(f"INGEST COMPLETE")
    print(f"="*70)
    print(f"  Total rows written:  {total_rows:,}")
    print(f"  Total rows filtered: {total_skipped:,}")
    
    if os.path.exists(DB_PATH):
        db_size = os.path.getsize(DB_PATH) / (1024**3)
        print(f"  Database size:       {db_size:.2f} GB")
    

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        ans = input(f"  {DB_PATH} already exists. Overwrite? (y/n): ")
        if ans.lower() != "y":
            print("Aborted.")
            sys.exit()
        os.remove(DB_PATH)
        print(f"  Removed existing {DB_PATH}")
    ingest_all()