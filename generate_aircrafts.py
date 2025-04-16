import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_aircraft_instances(
    work_packages_file: str,
    output_dir: str,
    num_instances: int = 10,
    num_aircrafts: int = 20,
    min_overrun_percentage: float = 0.20,
    min_total_man_hours: float = 201.6,
    max_total_man_hours: float = 259.2,
    max_turnaround_minutes: int = 1680  # 28 hours in minutes
):
    # Load work packages
    work_packages_df = pd.read_csv(work_packages_file)
    work_packages_df["WP number"] = work_packages_df["WP number"].astype(str)
    work_packages_df["Minutes"] = work_packages_df["Minutes"].fillna(0)
    work_packages_df["Man_Hours"] = work_packages_df["Man_Hours"].fillna(0)
    wps = work_packages_df[["WP number", "Minutes", "Man_Hours"]].to_dict("records")
    all_wp_numbers = [wp["WP number"] for wp in wps]

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    def generate_single_instance(instance_id):
        while True:  # Keep generating until all constraints are met
            random_day = datetime.strptime(f"2025-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}", "%Y-%m-%d")
            aircraft_data = []
            used_wps = set()
            total_man_hours = 0.0

            remaining_wps = all_wp_numbers.copy()
            random.shuffle(remaining_wps)

            while len(aircraft_data) < num_aircrafts:
                aircraft_id = 101 + len(aircraft_data)
                landing_hour = random.randint(0, 22)
                landing_minute = random.randint(0, 59)
                landing_time = random_day + timedelta(hours=landing_hour, minutes=landing_minute)

                selected_wps = []
                total_minutes = 0
                total_hours = 0.0

                if remaining_wps:
                    wp_number = remaining_wps.pop()
                    wp_data = next(w for w in wps if w["WP number"] == wp_number)
                    selected_wps.append(wp_number)
                    total_minutes += wp_data["Minutes"]
                    total_hours += wp_data["Man_Hours"]

                while True:
                    wp = random.choice(wps)
                    if wp["WP number"] not in selected_wps:
                        selected_wps.append(wp["WP number"])
                        total_minutes += wp["Minutes"]
                        total_hours += wp["Man_Hours"]
                    estimated_turnaround_minutes = int(total_minutes * (1 + min_overrun_percentage))
                    if total_minutes > 20 and random.random() > 0.5:
                        break

                add_day = random.random() > 0.5
                actual_turnaround_minutes = estimated_turnaround_minutes + (1440 if add_day else 0)

                if actual_turnaround_minutes > max_turnaround_minutes:
                    continue  # skip this aircraft, try again

                departure_time = landing_time + timedelta(minutes=estimated_turnaround_minutes)
                if add_day:
                    departure_time += timedelta(days=1)

                turnaround_str = f"{actual_turnaround_minutes // 60:02d}:{actual_turnaround_minutes % 60:02d}"

                used_wps.update(selected_wps)
                total_man_hours += total_hours

                work_list = ", ".join(str(wp) for wp in selected_wps) if selected_wps else ""
                aircraft_data.append({
                    "Aicraft (A/C) Serial Number": aircraft_id,
                    "A/C Landing Date": landing_time.strftime("%d/%m/%Y"),
                    "A/C Landing Time": landing_time.strftime("%H:%M"),
                    "A/C departure Date": departure_time.strftime("%d/%m/%Y"),
                    "A/C departure Time": departure_time.strftime("%H:%M"),
                    "Turn Around Time": turnaround_str,
                    "Work that needs to be carried out": work_list
                })

            if min_total_man_hours < total_man_hours < max_total_man_hours and set(all_wp_numbers).issubset(used_wps):
                break  # Constraints satisfied

        df = pd.DataFrame(aircraft_data)
        df["Work that needs to be carried out"] = (
            df["Work that needs to be carried out"]
            .fillna("")
            .astype(str)
            .apply(lambda x: x.replace("nan", "").strip(" ,"))
        )
        df.to_csv(f"{output_dir}/aircrafts_instance_{instance_id}.csv", index=False)

    for instance_id in range(1, num_instances + 1):
        generate_single_instance(instance_id)

# Example usage:
# generate_aircraft_instances(
#     work_packages_file="work_packages.csv",
#     output_dir="generated_aircrafts",
#     num_instances=10
# )


if __name__ == "__main__":
    generate_aircraft_instances(
        work_packages_file="work_packages.csv",
        output_dir="generated_aircrafts",
        num_instances=10  # or any number of problem instances you want
    )