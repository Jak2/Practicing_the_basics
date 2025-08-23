# Key Questions to Clarify Requirements

1. Data Sources & Formats  
   - Which sensor or booking systems will feed the real-time status? (e.g. IoT occupancy sensors, calendar API)  
   - In what format and via which protocol will they send data? (REST API, MQTT, WebSocket, Azure Event Hub, etc.)  
   - What authentication or security measures (OAuth, API keys, certificates) are required?

2. Booth Identification & Location  
   - How are booths uniquely identified? (IDs, names, floor/zone information)  
   - Will we need a mapping of booth IDs to physical locations or room names?

3. Update Frequency & Latency  
   - How often must “Occupied/Vacant” status update on the dashboard? (every second, every minute)  
   - What is the acceptable data latency threshold?

4. Historical Data & Retention  
   - Will you provide historical usage logs, or must we store streaming data from scratch?  
   - How long should we retain historical data for trend analysis? (30 days, 90 days, one year)

5. User Roles & Access  
   - Who will use the dashboard, and what permissions are required? (facility managers, executives)  
   - Will different roles see different metrics or drill-downs?

6. Alerts & Notifications  
   - Which events should trigger alerts? (e.g. booth idle > 10 minutes, CO₂ > threshold)  
   - Preferred notification channels: email, SMS, Teams/Slack integration?

7. Performance & Scalability  
   - How many booths and concurrent users must the solution support?  
   - Are there peak-load considerations (end of meeting days, midday spikes)?

8. Integration & Deployment  
   - Is there an existing BI environment (Power BI Service, Tableau Server, Grafana)?  
   - Any corporate policies on cloud vs. on-premises hosting, data residency, or vendor lock-in?

***

# Connecting Real-Time Data to Power BI

1. **Streaming Dataset (Push/Pull API)**  
   - Create a Power BI streaming dataset (via Power BI Service) with fields: BoothID, Timestamp, Status, etc.  
   - Send JSON-formatted POST requests to the Power BI REST API endpoint whenever status changes.  
   - Build a dashboard tile “Custom streaming data” to visualize live status and metrics.

2. **Azure Stream Analytics → Power BI**  
   - Ingest sensor messages into Azure Event Hubs or IoT Hub.  
   - Use an Azure Stream Analytics job to process/transform and output streams directly to Power BI.

3. **DirectQuery on Azure SQL or time-series DB**  
   - Stream data into Azure SQL Database or Azure Data Explorer (Kusto).  
   - Use Power BI DirectQuery mode for near-real-time dashboards with minimal latency.

***

# Alternative Dashboard Solutions

- **Grafana** with Prometheus or InfluxDB  
  -  Native support for time-series data, low latency, IoT integrations (MQTT).  
  -  Flexible alerting and annotation on time-series charts.  

- **Tableau** with Web Data Connector or TabPy  
  -  Web Data Connector for push updates or Python scripts for streaming simulation.  

- **Custom Web App** using React + D3/Chart.js  
  -  Full control over UI/UX, real-time WebSocket feeds, advanced interactivity.

***

# Key Metrics & KPIs

1. **Real-Time Status**  
   - Current occupancy (Occupied vs. Vacant per booth)  

2. **Utilization Metrics**  
   - Utilization Rate (%) = (Total Occupied Time ÷ Available Time) × 100  
   - Average Session Duration (minutes)  
   - Turnaround Time between meetings  

3. **Occupancy Patterns**  
   - Peak Utilization Hours / Days  
   - Idle Time Distribution  

4. **Service Performance**  
   - Number of Unfilled Bookings  
   - Average Wait Time for Occupied State  

5. **Environmental Metrics** (if sensors provided)  
   - Average Room Temperature, Humidity, CO₂, Noise Level  
   - Count of Threshold Breaches (alerts triggered)

***

# Dummy Data Sample

Use this sample to demonstrate a live-updating dashboard in Power BI.  

| BoothID | Timestamp           | Status   | SessionDurationMin | Temperature°C | CO₂ ppm |
|---------|---------------------|----------|--------------------|---------------|---------|
| B001    | 2025-08-24 09:00:00 | Occupied | N/A                | 22.5          | 600     |
| B002    | 2025-08-24 09:00:00 | Vacant   | N/A                | 21.8          | 550     |
| B001    | 2025-08-24 09:30:00 | Vacant   | 30                 | 22.7          | 620     |
| B003    | 2025-08-24 10:15:00 | Occupied | N/A                | 23.1          | 700     |
| B002    | 2025-08-24 10:45:00 | Occupied | N/A                | 21.9          | 560     |
| B002    | 2025-08-24 11:30:00 | Vacant   | 45                 | 22.2          | 580     |

- **How to use:**  
  -  Push each new row via REST API to a Power BI streaming dataset.  
  -  Create a "Current Status" card visual filtered on the latest Timestamp per BoothID.  
  -  Build line charts for Temperature and CO₂ over time and bar charts for Utilization Rate.

***

With these questions, integration approaches, alternative platforms, metrics, and dummy data, you’ll be ready to engage Bureau Booths, design an effective real-time dashboard, and showcase your analytical value.


# Mock Data Schema for a Robust Dashboard

To create a comprehensive mock dataset (with at least 20 fields) that powerfully demonstrates your analytical and visualization skills, include the following columns:

1. BoothID  
2. Timestamp  
3. Status (“Occupied”/“Vacant”)  
4. SessionID  
5. UserCount  
6. BookingSource (e.g., Calendar, Walk-in, Mobile App)  
7. SessionDurationMin  
8. WaitTimeMin (time between vacancy and next occupancy)  
9. OrganizerDepartment  
10. OrganizerRole (e.g., Manager, Engineer)  
11. AverageTemperature°C  
12. AverageHumidity%  
13. AverageCO₂ppm  
14. PeakNoiseLeveldB  
15. AverageLightLux  
16. MotionEventCount (number of movement triggers)  
17. AlertCount (environmental threshold breaches)  
18. UtilizationRate% (rolling window)  
19. MaintenanceFlag (Yes/No)  
20. CleaningStatus (Pending/Completed)  
21. FloorZone  
22. EquipmentFaultFlag (Yes/No)  
23. EnergyConsumptionkWh  
24. PeakPowerWatts  

***

# Recommended Visualizations

1. **Real-Time Status Grid**  
   -  A tiled matrix showing each BoothID with green/red status indicators and a live timestamp.  
   -  Highlights immediate availability.

2. **Occupancy Heatmap (by Hour & Day)**  
   -  Calendar-style heatmap: booths on rows, hours on columns.  
   -  Visualizes peak usage times and underutilized slots.

3. **Utilization Trend Line**  
   -  Time series of UtilizationRate% across days or weeks.  
   -  Reveals longer-term patterns and seasonality.

4. **Session Duration Distribution**  
   -  Histogram of SessionDurationMin.  
   -  Identifies common meeting lengths and outliers.

5. **Wait Time & Turnaround Box-Plot**  
   -  Box-plot of WaitTimeMin by BoothID or Zone.  
   -  Highlights efficiency in room turnover.

6. **Environmental KPI Cards**  
   -  Four small cards showing current AverageTemperature, CO₂, Humidity, Noise.  
   -  With conditional formatting to flag deviations.

7. **Threshold Alert Bar Chart**  
   -  Bar chart of AlertCount by booth or metric type.  
   -  Prioritizes which booths or sensors need attention.

8. **Booking Source Pie/Donut Chart**  
   -  Proportional distribution of BookingSource.  
   -  Reveals reliance on calendar vs. walk-ins.

9. **Department Usage Stacked Bar**  
   -  Stacked bars of total SessionDurationMin by OrganizerDepartment across booths.  
   -  Shows which teams use spaces most.

10. **Floor-Zone Map Overlay**  
   -  Spatial floor plan background with colored circles proportional to UtilizationRate%.  
   -  Intuitive view of hotspot zones.

11. **Energy Consumption vs. Occupancy Scatter**  
   -  Scatter plot with UserCount on x-axis and EnergyConsumptionkWh on y-axis.  
   -  Correlates usage intensity to energy cost.

12. **Maintenance & Fault Dashboard**  
   -  Dual-axis chart: EquipmentFaultFlag counts (bars) vs. MaintenanceFlag ratio (line).  
   -  Monitors reliability and service needs.

***

By modeling your mock data with these 24 fields and building the above visuals, you will showcase advanced data-engineering, real-time analytics integration, and actionable insight delivery—demonstrating exceptional value to Bureau Booths.