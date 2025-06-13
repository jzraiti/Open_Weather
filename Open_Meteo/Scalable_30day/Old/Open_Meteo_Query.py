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
    handlers=[logging.FileHandler("Open_Meteo_Query.log"), logging.StreamHandler()],
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
    pd.DataFrame(
        columns=["taxa_name", "latitude", "longitude", "year", "date", "precip_mm"]
    ).to_csv(output_file, index=False)
    logging.info(f"Created new output file: {output_file}")

# === DATA COLLECTION ===
for index, row in locations.iterrows():
    try:
        latitude = row["Lat_machine_readable"]
        longitude = row["Long_machine_readable"]
        end_date_raw = row["Date_collected_cleaned_machine_readable"]
        taxa_name = row["species"]
        start_year = 2000
        end_year = 2024

        end_date_parsed = datetime.strptime(end_date_raw, "%m/%d/%Y")
        end_day = end_date_parsed.strftime("%m-%d")
        start_date_parsed = end_date_parsed - timedelta(days=30)
        start_day = start_date_parsed.strftime("%m-%d")

        logging.info(
            f"Processing {taxa_name} ({latitude}, {longitude}) with end_date {end_date_raw}"
        )

        for year in range(start_year, end_year + 1):
            # If the 30-day window crosses into the previous year
            if start_date_parsed.month > end_date_parsed.month or (
                start_date_parsed.month == end_date_parsed.month
                and start_date_parsed.day > end_date_parsed.day
            ):
                # First part: previous year, from start_day to Dec 31
                prev_year = year - 1
                start_date1 = f"{prev_year}-{start_day}"
                end_date1 = f"{prev_year}-12-31"
                # Second part: current year, from Jan 1 to end_day
                start_date2 = f"{year}-01-01"
                end_date2 = f"{year}-{end_day}"

                date_ranges = [
                    (start_date1, end_date1, prev_year),
                    (start_date2, end_date2, year),
                ]
            else:
                # Normal case: all within the same year
                start_date = f"{year}-{start_day}"
                end_date = f"{year}-{end_day}"
                date_ranges = [(start_date, end_date, year)]

            for start_date, end_date, record_year in date_ranges:
                url = "https://archive-api.open-meteo.com/v1/archive"
                params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": start_date,
                    "end_date": end_date,
                    "daily": "precipitation_sum",
                    "timezone": "auto",
                }

                response = None
                retries = 0
                max_retries = 3
                timeout_seconds = 10
                while retries < max_retries:
                    try:
                        logging.info(
                            f"Querying data for year {record_year}: {start_date} to {end_date} (Attempt {retries + 1})"
                        )
                        response = requests.get(
                            url, params=params, timeout=timeout_seconds
                        )
                        if response.status_code == 200:
                            break
                        else:
                            logging.warning(
                                f"Non-200 response for {taxa_name} ({latitude}, {longitude}) in year {record_year}: {response.status_code}"
                            )
                    except requests.exceptions.Timeout:
                        logging.warning(
                            f"Timeout for {taxa_name} ({latitude}, {longitude}) in year {record_year}. Retrying..."
                        )
                    except requests.exceptions.RequestException as e:
                        logging.error(
                            f"Request error for {taxa_name} ({latitude}, {longitude}) in year {record_year}: {e}"
                        )
                    retries += 1

                if (
                    response is None
                    or retries == max_retries
                    or response.status_code != 200
                ):
                    logging.error(
                        f"Failed to retrieve data for {taxa_name} ({latitude}, {longitude}) in year {record_year} after {max_retries} attempts"
                    )
                    continue

                json_data = response.json()
                dates = json_data.get("daily", {}).get("time", [])
                precipitation = json_data.get("daily", {}).get("precipitation_sum", [])

                for date, prcp in zip(dates, precipitation):
                    record = {
                        "taxa_name": taxa_name,
                        "desired_end_date": end_date_raw,
                        "latitude": latitude,
                        "longitude": longitude,
                        "year": record_year,
                        "date": date,
                        "precip_mm": prcp,
                    }

                    pd.DataFrame([record]).to_csv(
                        output_file, mode="a", header=False, index=False
                    )
                    logging.info(f"Appended record to CSV: {record}")

        logging.info(f"Finished processing {taxa_name} ({latitude}, {longitude})")

    except Exception as e:
        logging.error(f"Error processing row {index}: {e}")
        continue
