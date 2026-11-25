# Decision log

The main technical choices in this project: what I chose, what else I considered, and why.
Format per entry: Context → Decision → Alternatives → Consequences.

---

## D1 – Messaging protocol: MQTT
Date: 2026-11-22 · Part: P1

**Context:** Simulated machines produce a sensor reading every second. More than one program
needs this data: `subscriber.py` stores it in SQLite (P1), and `scorer.py` will use it for
failure prediction (P2). Adding a new consumer should not require changing the machines.

**Decision:** Machines publish JSON messages over MQTT to topics `factory/line1/<machine>`.
Consumers subscribe to the topics they need.

**Alternatives considered:**
- **OPC UA** – the industrial standard at machine/PLC level, but client/server, more complex,
  and mainly used to read real PLCs, which this project does not have.
- **REST (machines POST to an API)** – every machine must know the receiver's address;
  no built-in way to deliver one message to several consumers.
- **Kafka** – built for very high throughput and message replay; needs far more
  infrastructure than 4 machines at 1 message per second.
- **Writing directly to SQLite** – simplest, but ties the machines to the database;
  adding the P2 scorer would mean changing machine code.

**Consequences:**
- ➕ Publishers and subscribers are decoupled: the P2 scorer can subscribe without changing the simulator.
- ➕ Lightweight, and the common choice for IIoT telemetry.
- ➖ The broker is an extra component. If it is down, messages are lost (QoS 0, no buffering).
- Note: in a real plant, machine data is usually read via OPC UA and often forwarded to IT
  systems over MQTT. This project simulates the machines and starts at the MQTT layer.

---

## D2 – Machine data for P1: AI4I 2020
Date: 2026-11-22 · Part: P1

**Context:** P1 needs realistic sensor values and failures with known causes for 3 machines,
to feed the OEE calculation and a downtime Pareto chart by cause.

**Decision:** Use the AI4I 2020 Predictive Maintenance dataset (UCI, 10,000 rows) as the
data source for machines M1–M3.

**Alternatives considered:**
- **Microsoft Azure Predictive Maintenance dataset** – hourly time series for 100 machines
  with errors, maintenance and failures. Better as a time series, but larger, has no simple
  per-row failure causes, and switching after the EDA would cost time.
- **NASA C-MAPSS** – turbofan run-to-failure data; suited to remaining-useful-life
  prediction, not a factory line.
- **MetroPT-3** – real compressor data; used in P2 instead, where real time-ordered data matters more.
- **Real lab machine data** – the best option, but not available at the time of this decision.

**Consequences:**
- ➕ Labelled failure causes (TWF, HDF, PWF, OSF, RNF) map directly to downtime causes in the Pareto chart.
- ➕ Small, clean and well known; EDA already done.
- ➖ Synthetic: generated to imitate a milling machine, not recorded from one.
- ➖ Rows are independent samples, not a time series. Replayed one per second, values jump unrealistically.
- ➖ No timestamps, downtime durations, part counts or scrap. Downtime, cycle time and scrap
  rate are simulation rules in `simulator.py`, so the OEE values reflect those rules,
  not real factory performance. This is stated in the README.

---

## D3 – Broker and client library: Mosquitto + paho-mqtt
Date: 2026-11-23 · Part: P1

**Context:** MQTT (D1) needs a broker to route messages and a Python client library.

**Decision:** Mosquitto (official eclipse-mosquitto image, pinned to 2.0.23) running in Docker via docker compose, and paho-mqtt 2.x as the Python client.

**Alternatives considered:**
- **Mosquitto Windows installer** - works, but would have to be redone in Docker for P2 and is not reproducible for others.
- **EMQX / HiveMQ** – built for large-scale or commercial use (clustering, dashboards);
  far more than 4 machines need.
- **Cloud brokers (AWS IoT Core, Azure IoT Hub)** – need accounts, certificates and possibly
  costs, and tie the project to one cloud.
- **Public test broker (test.mosquitto.org)** – no install, but public, sometimes down,
  and not a real setup.
- **aiomqtt / gmqtt** – async (asyncio) clients; adds a concept this project does not need yet.

**Consequences:**
- ➕ Small, free and widely used; runs in Docker from P1, and the same service is reused in P2's full docker compose setup.
- ➕ paho-mqtt is the standard Python MQTT client with many examples.
- ➖ Mosquitto 2.x needs an explicit listener and allow_anonymous in the config, otherwise connections from outside the container are refused. Anonymous access is acceptable only because the port is bound to localhost.
- ➖ Image pinned to an exact version (2.0.23) for reproducibility; updates and security fixes must be applied manually by changing the tag.
- ➖ Single broker, no clustering: a single point of failure (acceptable for a demo).
- ➖ paho-mqtt 2.x changed its API from 1.x (e.g. `CallbackAPIVersion.VERSION2` is required),
  so many online tutorials are outdated.
