import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import os

# === CONFIGURATION ===
input_csv = "Location_Date.csv"  # Input CSV file containing latitude, longitude, end_date, and taxa_name
output_file = "precipitation_data.csv"  # Output CSV file

# === SETUP LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("Open_Meteo_Query.log"),
        logging.StreamHandler()
    ]
)

logging.info("Starting Open Meteo Query script")

# === LOAD INPUT DATA ===
try:
    locations = pd.read_csv(input_csv)
    logging.info(f"Loaded input CSV file: {input_csv}")
except Exception as e:
    logging.error(f"Failed to load input CSV file: {e}")
    raise

# === CREATE OUTPUT FILE IF NOT EXISTS ===
if not os.path.exists(output_file):
    pd.DataFrame(columns=["taxa_name", "latitude", "longitude", "year", "date", "precip_mm"]).to_csv(output_file, index=False)
    logging.info(f"Created new output file: {output_file}")

# === DATA COLLECTION ===
for index, row in locations.iterrows():
    try:
        latitude = row['Lat_machine_readable']
        longitude = row['Long_machine_readable']
        end_date_raw = row['Date_collected_cleaned_machine_readable']  # Example: "1/15/1805"
        taxa_name = row['species']
        start_year = 2000
        end_year = 2024

        # Parse the end_date and extract month and day
        end_date_parsed = datetime.strptime(end_date_raw, "%m/%d/%Y")
        end_day = end_date_parsed.strftime("%m-%d")  # Format as MM-DD

        # Calculate the start_date as 30 days prior to the end_date
        start_date_parsed = end_date_parsed - timedelta(days=30)
        start_day = start_date_parsed.strftime("%m-%d")  # Format as MM-DD

        # Adjust the year for the start_date if it crosses into the previous year
        if start_date_parsed.year < end_date_parsed.year:
            start_year_adjusted = start_year - 1
        else:
            start_year_adjusted = start_year

        logging.info(f"Processing {taxa_name} ({latitude}, {longitude}) with end_date {end_date_raw}")

        for year in range(start_year_adjusted, end_year + 1):
            start_date = f"{year}-{start_day}"
            end_date = f"{year}-{end_day}"

            url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date,
                "end_date": end_date,
                "daily": "precipitation_sum",
                "timezone": "auto"
            }

            logging.info(f"Querying data for year {year}: {start_date} to {end_date}")
            response = requests.get(url, params=params)

            if response.status_code != 200:
                logging.warning(f"Failed for {taxa_name} ({latitude}, {longitude}) in year {year}: {response.status_code}")
                continue

            json_data = response.json()
            dates = json_data.get("daily", {}).get("time", [])
            precipitation = json_data.get("daily", {}).get("precipitation_sum", [])

            for date, prcp in zip(dates, precipitation):
                record = {
                    "taxa_name": taxa_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "year": year,
                    "date": date,
                    "precip_mm": prcp
                }

                # Append the record to the CSV file
                pd.DataFrame([record]).to_csv(output_file, mode='a', header=False, index=False)
                logging.info(f"Appended record to CSV: {record}")

        logging.info(f"Finished processing {taxa_name} ({latitude}, {longitude})")

    except Exception as e:
        logging.error(f"Error processing row {index}: {e}")
        continue