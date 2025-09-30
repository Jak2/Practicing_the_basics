Here’s a detailed and business-focused list of **metrics** and **data columns** for your dashboard and wireframe, aligning with Bureau Booths’ needs and your mentor’s guidance.

***

## Recommended Metrics & Dashboard Data Columns

### Occupancy & Usage Metrics
- BoothID  
- Booth Name/Location  
- Timestamp  
- Status (Occupied/Vacant)  
- SessionID  
- UserCount (number of people in booth)  
- Session Start Time  
- Session End Time  
- SessionDurationMin  
- WaitTimeAfterVacancyMin  
- BookingSource (calendar, walk-in, app)  
- BookingOrganizerDepartment  
- BookingOrganizerRole (Manager/Staff/etc.)  
- UtilizationRate (%) – per booth, per zone  
- Number of Sessions per Day  
- Peak Usage Hours  
- Average Occupancy per Day/Week

### Environmental & Comfort Metrics
- AverageTemperature°C  
- AverageHumidity%  
- AverageCO₂ppm  
- PeakNoiseLeveldB  
- AverageLightLevelLux  
- Environmental Comfort Score (aggregate/derived metric)

### Alerts & Events
- AlertCount (overall & by type)  
- AlertType (e.g., “CO₂ High”, “Noise High”, “Occupancy Over”)
- AlertTimestamp  
- MaintenanceFlag (Yes/No)  
- CleaningStatus (Pending/Completed)

### Operations & Performance
- BoothZone/Floor  
- EquipmentFaultFlag  
- FaultType  
- FaultResolvedFlag  
- BookingRescheduleCount  
- EnergyConsumptionkWh per session/booth  
- PeakPowerWatts

### Analytical Dimensions
- Department Usage Breakdown  
- Zone/Area Usage Breakdown  
- Time of Day/Week Analysis  
- Historical Usage Trends  
- Environmental Breach Trends  
- Underutilized/Overutilized Booths  
- Suggested Optimization Actions (e.g., reschedule, maintenance, layout change)

***

## Core Metrics for Business Impact

- Real-Time Occupancy Status  
- Booth Utilization Rate  
- Average Session Duration  
- User Footfall per Booth  
- Alert Frequency and Severity  
- Environmental Condition Compliance  
- Department/Zone Allocation and Usage  
- Maintenance & Service Needs  
- Booking Source Effectiveness  
- Trends in Under/Over Utilization

***

## Example Wireframe Elements (for Figma/Airtable/Notion)

- **Dashboard KPI Cards:**  
  Occupied Booths | Avg. Utilization | Avg. Temperature | Alert Count

- **Live Booth Status Grid:**  
  BoothID | Status | UserCount | Temperature | CO₂ | Alert

- **Timeline/Heatmap:**  
  Booth usage by hour/day/week

- **Environmental Charts:**  
  Temperature, CO₂, Noise Level by booth and over time

- **Alerts Table/List:**  
  Booth | Alert Type | Timestamp | Status

- **Department/Zone Breakdown:**  
  Bar/stacked chart of session counts by department/zone

***

This set of columns and metrics will ensure your dashboard and wireframe comprehensively address Bureau Booths’ operational, comfort, and business performance needs. Let me know if you want mock data samples or specific wireframe layouts next!

Absolutely! Here are the formulas for the important metrics, followed by a complete Python code snippet to generate dummy data for your dashboard and wireframe needs:

***

## Key Metrics and Formulas

- **Utilization Rate (%):**  
  $$ \text{Utilization Rate} = \frac{\text{Total Occupied Time}}{\text{Total Available Time}} \times 100 $$
  
- **Session Duration (minutes):**  
  $$ \text{Session Duration} = \text{Session End Time} - \text{Session Start Time} $$
  
- **Average Occupancy (per booth or time period):**  
  $$ \text{Avg Occupancy} = \frac{\text{Sum of UserCounts}}{\text{Number of Sessions}} $$
  
- **Peak Usage Hours:**  
  Most frequent hours in which "Occupied" status is recorded for each booth.
  
- **Wait Time After Vacancy (minutes):**  
  $$ \text{Wait Time} = \text{Next Occupied Session Start} - \text{Previous Session End} $$
  
- **Environmental Comfort Score (example):**  
  $$ \text{Comfort Score} = \frac{\text{Boolean Compliance with Temp/CO₂/Noise targets}}{\text{Number of Metrics}} \times 100 $$
  
- **Alert Count:**  
  Number of times environmental metrics or occupancy exceed set thresholds per period.

- **Energy Consumption (kWh):**  
  $$ \text{Energy Consumption (session)} = \frac{\text{Session Duration (hours)} \times \text{Peak Power (Watts)}}{1000} $$

***

## Python Code to Generate Dummy Data

```python
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Generate dummy data for 10 booths and 100 sessions
NUM_BOOTHS = 10
NUM_SESSIONS = 100

booth_ids = [f'B{str(i).zfill(3)}' for i in range(1, NUM_BOOTHS + 1)]
booking_sources = ['Calendar', 'Walk-in', 'App']
departments = ['HR', 'Engineering', 'Marketing', 'Finance', 'Sales']
roles = ['Manager', 'Staff', 'Executive']
cleaning_status = ['Pending', 'Completed']

data = []

start_date = datetime(2025, 9, 1, 8, 0)

for i in range(NUM_SESSIONS):
    booth_id = random.choice(booth_ids)
    date_offset = timedelta(days=random.randint(0, 28), hours=random.randint(0, 10), minutes=random.randint(0, 50))
    session_start = start_date + date_offset
    duration_min = random.randint(15, 120)
    session_end = session_start + timedelta(minutes=duration_min)
    status = 'Occupied'
    user_count = random.randint(1, 6)
    wait_time_min = random.randint(0, 60)
    booking_source = random.choice(booking_sources)
    organizer_dept = random.choice(departments)
    organizer_role = random.choice(roles)
    avg_temp = round(np.random.normal(22, 2), 1)
    avg_humidity = round(np.random.normal(45, 10), 1)
    avg_co2 = int(np.random.normal(600, 150))
    peak_noise = int(np.random.normal(60, 10))
    avg_light = int(np.random.normal(200, 50))
    comfort_score = round(random.uniform(80, 100), 1)
    alert_count = np.random.poisson(0.5)
    maintenance_flag = random.choice([0, 1])
    cleaning_stat = random.choice(cleaning_status)
    booth_zone = random.choice(['North', 'South', 'East', 'West'])
    equipment_fault = random.choice([0, 1])
    fault_type = random.choice(['None', 'Sensor', 'Door', 'Vent'])
    fault_resolved = random.choice([0, 1])
    booking_reschedules = random.randint(0, 3)
    peak_power_watts = random.randint(50, 200)
    session_duration_hr = duration_min/60
    energy_consumption = round(session_duration_hr * peak_power_watts / 1000, 2)

    data.append({
        'BoothID': booth_id,
        'BoothZone': booth_zone,
        'Timestamp': session_start.strftime("%Y-%m-%d %H:%M"),
        'Status': status,
        'SessionID': f'S{str(i).zfill(4)}',
        'UserCount': user_count,
        'SessionStartTime': session_start.strftime("%Y-%m-%d %H:%M"),
        'SessionEndTime': session_end.strftime("%Y-%m-%d %H:%M"),
        'SessionDurationMin': duration_min,
        'WaitTimeAfterVacancyMin': wait_time_min,
        'BookingSource': booking_source,
        'BookingOrganizerDepartment': organizer_dept,
        'BookingOrganizerRole': organizer_role,
        'UtilizationRate': round(random.uniform(20, 95), 1),
        'AvgTemperature°C': avg_temp,
        'AvgHumidity%': avg_humidity,
        'AvgCO₂ppm': avg_co2,
        'PeakNoiseLeveldB': peak_noise,
        'AvgLightLevelLux': avg_light,
        'EnvironmentalComfortScore': comfort_score,
        'AlertCount': alert_count,
        'MaintenanceFlag': maintenance_flag,
        'CleaningStatus': cleaning_stat,
        'EquipmentFaultFlag': equipment_fault,
        'FaultType': fault_type,
        'FaultResolvedFlag': fault_resolved,
        'BookingRescheduleCount': booking_reschedules,
        'EnergyConsumptionkWh': energy_consumption,
        'PeakPowerWatts': peak_power_watts,
    })

df = pd.DataFrame(data)
print(df.head())
```

### same code but added feature to export to csv
```python
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Generate dummy data for 10 booths and 100 sessions
NUM_BOOTHS = 10
NUM_SESSIONS = 100

booth_ids = [f'B{str(i).zfill(3)}' for i in range(1, NUM_BOOTHS + 1)]
booking_sources = ['Calendar', 'Walk-in', 'App']
departments = ['HR', 'Engineering', 'Marketing', 'Finance', 'Sales']
roles = ['Manager', 'Staff', 'Executive']
cleaning_status = ['Pending', 'Completed']

data = []

start_date = datetime(2025, 9, 1, 8, 0)

for i in range(NUM_SESSIONS):
    booth_id = random.choice(booth_ids)
    date_offset = timedelta(days=random.randint(0, 28), hours=random.randint(0, 10), minutes=random.randint(0, 50))
    session_start = start_date + date_offset
    duration_min = random.randint(15, 120)
    session_end = session_start + timedelta(minutes=duration_min)
    status = 'Occupied'
    user_count = random.randint(1, 6)
    wait_time_min = random.randint(0, 60)
    booking_source = random.choice(booking_sources)
    organizer_dept = random.choice(departments)
    organizer_role = random.choice(roles)
    avg_temp = round(np.random.normal(22, 2), 1)
    avg_humidity = round(np.random.normal(45, 10), 1)
    avg_co2 = int(np.random.normal(600, 150))
    peak_noise = int(np.random.normal(60, 10))
    avg_light = int(np.random.normal(200, 50))
    comfort_score = round(random.uniform(80, 100), 1)
    alert_count = np.random.poisson(0.5)
    maintenance_flag = random.choice([0, 1])
    cleaning_stat = random.choice(cleaning_status)
    booth_zone = random.choice(['North', 'South', 'East', 'West'])
    equipment_fault = random.choice([0, 1])
    fault_type = random.choice(['None', 'Sensor', 'Door', 'Vent'])
    fault_resolved = random.choice([0, 1])
    booking_reschedules = random.randint(0, 3)
    peak_power_watts = random.randint(50, 200)
    session_duration_hr = duration_min/60
    energy_consumption = round(session_duration_hr * peak_power_watts / 1000, 2)

    data.append({
        'BoothID': booth_id,
        'BoothZone': booth_zone,
        'Timestamp': session_start.strftime("%Y-%m-%d %H:%M"),
        'Status': status,
        'SessionID': f'S{str(i).zfill(4)}',
        'UserCount': user_count,
        'SessionStartTime': session_start.strftime("%Y-%m-%d %H:%M"),
        'SessionEndTime': session_end.strftime("%Y-%m-%d %H:%M"),
        'SessionDurationMin': duration_min,
        'WaitTimeAfterVacancyMin': wait_time_min,
        'BookingSource': booking_source,
        'BookingOrganizerDepartment': organizer_dept,
        'BookingOrganizerRole': organizer_role,
        'UtilizationRate': round(random.uniform(20, 95), 1),
        'AvgTemperature°C': avg_temp,
        'AvgHumidity%': avg_humidity,
        'AvgCO₂ppm': avg_co2,
        'PeakNoiseLeveldB': peak_noise,
        'AvgLightLevelLux': avg_light,
        'EnvironmentalComfortScore': comfort_score,
        'AlertCount': alert_count,
        'MaintenanceFlag': maintenance_flag,
        'CleaningStatus': cleaning_stat,
        'EquipmentFaultFlag': equipment_fault,
        'FaultType': fault_type,
        'FaultResolvedFlag': fault_resolved,
        'BookingRescheduleCount': booking_reschedules,
        'EnergyConsumptionkWh': energy_consumption,
        'PeakPowerWatts': peak_power_watts,
    })

df = pd.DataFrame(data)

# --- NEW CODE SECTION ---

# Define the file name for the CSV output
output_file = 'booth_session_data.csv'

# Save the DataFrame to a CSV file
# index=False prevents pandas from writing the DataFrame index as a column in the CSV
df.to_csv(output_file, index=False)

print(f"Successfully generated and saved data to {output_file}")
print("\nFirst 5 rows of the DataFrame:")
print(df.head())
```

- This code will generate a DataFrame with realistic dummy data covering all key columns above.
- You can export (`df.to_csv('booth_dashboard_dummy_data.csv', index=False)`) and use this data in your dashboard or wireframe.

Let me know if you’d like a sample data file or more advanced simulation details!