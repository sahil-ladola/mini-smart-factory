# P1 · Data pipeline + OEE dashboard

Simulated machines publish sensor readings over MQTT; a subscriber stores them in SQLite;
SQL views compute OEE (Availability × Performance × Quality); Power BI shows OEE, downtime causes and MTBF/MTTR;
Power Automate drafts the end-of-shift report.

**Status:** 🚧 In progress

## Data
- `data/ai4i2020.csv`: AI4I 2020 Predictive Maintenance Dataset (UCI), used as the behaviour of the simulated machines.
