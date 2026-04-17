#!/usr/bin/env python3
# =============================================================================
# scripts/seed_demo_data.py — Generate Realistic Demo Data
# =============================================================================
# PURPOSE: Populate the database with 7 days of realistic time-series data
# so the dashboard and analytics endpoints have something to display.
#
# WHAT IT CREATES:
#   - 2 additional buildings with multiple zones each
#   - 7 days of sensor readings (temperature, humidity, CO2, occupancy)
#   - 7 days of HVAC status snapshots
#   - 7 days of energy meter readings
#   - Sample forecasts and recommendations
#
# USAGE:
#   docker compose exec api python /app/scripts/seed_demo_data.py
#
#   Or locally (with venv activated and DB running):
#   cd backend && python -m scripts.seed_demo_data
#
# SAFE TO RE-RUN: Uses ON CONFLICT DO NOTHING for entities with fixed UUIDs.
# Time-series data is deleted and recreated on each run.
# =============================================================================

import asyncio
import random
import math
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# ---------------------------------------------------------------------------
# Configuration — matches the seed migration's fixed UUIDs
# ---------------------------------------------------------------------------
DEMO_BUILDING_ID = UUID("00000000-0000-4000-8000-000000000001")

BUILDINGS = [
    {
        "id": "00000000-0000-4000-8000-000000000010",
        "name": "Grand Plaza Hotel",
        "address": "456 Innovation Ave, Tech City, TC 20002",
        "type": "hotel",
        "timezone": "America/New_York",
    },
    {
        "id": "00000000-0000-4000-8000-000000000020",
        "name": "Skyline Office Tower",
        "address": "789 Business Blvd, Metro City, MC 30003",
        "type": "office",
        "timezone": "America/Chicago",
    },
]

ZONES = [
    # Demo Hotel zones (building already exists from migration 003)
    {"id": "00000000-0000-4000-8000-000000000002", "building_id": str(DEMO_BUILDING_ID), "name": "Lobby", "floor": 1},
    {"id": "00000000-0000-4000-8000-000000000003", "building_id": str(DEMO_BUILDING_ID), "name": "Restaurant", "floor": 1},
    {"id": "00000000-0000-4000-8000-000000000004", "building_id": str(DEMO_BUILDING_ID), "name": "Floor 2 Guest Rooms", "floor": 2},
    {"id": "00000000-0000-4000-8000-000000000005", "building_id": str(DEMO_BUILDING_ID), "name": "Floor 3 Guest Rooms", "floor": 3},
    # Grand Plaza Hotel zones
    {"id": "00000000-0000-4000-8000-000000000011", "building_id": BUILDINGS[0]["id"], "name": "Main Lobby", "floor": 1},
    {"id": "00000000-0000-4000-8000-000000000012", "building_id": BUILDINGS[0]["id"], "name": "Conference Center", "floor": 2},
    {"id": "00000000-0000-4000-8000-000000000013", "building_id": BUILDINGS[0]["id"], "name": "Pool Area", "floor": 1},
    # Skyline Office zones
    {"id": "00000000-0000-4000-8000-000000000021", "building_id": BUILDINGS[1]["id"], "name": "Reception", "floor": 1},
    {"id": "00000000-0000-4000-8000-000000000022", "building_id": BUILDINGS[1]["id"], "name": "Open Office Floor 5", "floor": 5},
    {"id": "00000000-0000-4000-8000-000000000023", "building_id": BUILDINGS[1]["id"], "name": "Server Room", "floor": -1},
]

SENSOR_TYPES = ["temperature", "humidity", "co2", "occupancy"]

DAYS = 7
READINGS_INTERVAL_MINUTES = 15


def generate_sensor_value(sensor_type: str, hour: int, day_offset: int) -> float:
    """Generate a realistic sensor value with daily/hourly patterns."""
    noise = random.gauss(0, 1)

    if sensor_type == "temperature":
        base = 21.5
        daily_swing = 2.0 * math.sin(2 * math.pi * (hour - 6) / 24)
        return round(base + daily_swing + noise * 0.3, 1)

    elif sensor_type == "humidity":
        base = 45.0
        daily_swing = 5.0 * math.sin(2 * math.pi * (hour - 14) / 24)
        return round(max(20, min(80, base + daily_swing + noise * 2)), 1)

    elif sensor_type == "co2":
        base = 450
        if 8 <= hour <= 18:
            occupancy_boost = 200 * math.sin(math.pi * (hour - 8) / 10)
        else:
            occupancy_boost = 0
        return round(max(350, base + occupancy_boost + noise * 20))

    elif sensor_type == "occupancy":
        if 8 <= hour <= 20:
            base = 30 * math.sin(math.pi * (hour - 8) / 12)
        else:
            base = random.randint(0, 3)
        return max(0, round(base + noise * 3))

    return 0.0


async def seed(db_url: str) -> None:
    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        print("Seeding additional buildings...")
        for b in BUILDINGS:
            await db.execute(
                text(
                    "INSERT INTO buildings (id, name, address, type, timezone) "
                    "VALUES (:id, :name, :address, :type, :timezone) "
                    "ON CONFLICT DO NOTHING"
                ),
                b,
            )

        print("Seeding zones...")
        for z in ZONES:
            await db.execute(
                text(
                    "INSERT INTO zones (id, building_id, name, floor) "
                    "VALUES (:id, :building_id, :name, :floor) "
                    "ON CONFLICT DO NOTHING"
                ),
                z,
            )

        await db.commit()

        # Clean old demo time-series data before regenerating
        print("Clearing old demo time-series data...")
        await db.execute(text("DELETE FROM sensor_readings WHERE sensor_id LIKE 'demo-%'"))
        await db.execute(text("DELETE FROM hvac_status WHERE device_id LIKE 'demo-%'"))
        await db.execute(text("DELETE FROM energy_meter WHERE meter_id LIKE 'demo-%'"))
        await db.commit()

        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        start = now - timedelta(days=DAYS)

        # ---------------------------------------------------------------------------
        # SENSOR READINGS
        # ---------------------------------------------------------------------------
        print(f"Generating {DAYS} days of sensor readings...")
        sensor_rows = []
        for zone in ZONES:
            for sensor_type in SENSOR_TYPES:
                sensor_id = f"demo-{sensor_type}-{zone['id'][-4:]}"
                t = start
                while t < now:
                    sensor_rows.append({
                        "time": t.isoformat(),
                        "sensor_id": sensor_id,
                        "building_id": zone["building_id"],
                        "zone_id": zone["id"],
                        "sensor_type": sensor_type,
                        "value": generate_sensor_value(sensor_type, t.hour, (t - start).days),
                    })
                    t += timedelta(minutes=READINGS_INTERVAL_MINUTES)

        # Batch insert in chunks of 2000
        for i in range(0, len(sensor_rows), 2000):
            batch = sensor_rows[i:i + 2000]
            values_clause = ", ".join(
                f"('{r['time']}', '{r['sensor_id']}', '{r['building_id']}', "
                f"'{r['zone_id']}', '{r['sensor_type']}', {r['value']})"
                for r in batch
            )
            await db.execute(text(
                f"INSERT INTO sensor_readings (time, sensor_id, building_id, zone_id, sensor_type, value) "
                f"VALUES {values_clause} ON CONFLICT DO NOTHING"
            ))
        await db.commit()
        print(f"  Inserted {len(sensor_rows)} sensor readings")

        # ---------------------------------------------------------------------------
        # HVAC STATUS
        # ---------------------------------------------------------------------------
        print(f"Generating {DAYS} days of HVAC status data...")
        hvac_rows = []
        hvac_devices = [
            ("ahu", "demo-ahu-{zone_suffix}"),
            ("fcu", "demo-fcu-{zone_suffix}"),
        ]
        for zone in ZONES:
            zone_suffix = zone["id"][-4:]
            for device_type, device_template in hvac_devices:
                device_id = device_template.format(zone_suffix=zone_suffix)
                t = start
                while t < now:
                    if 6 <= t.hour <= 22:
                        status_val = random.choices(
                            ["running", "idle", "running", "running"],
                            weights=[60, 20, 15, 5],
                        )[0]
                        setpoint = round(random.uniform(20.0, 24.0), 1)
                    else:
                        status_val = random.choices(
                            ["idle", "off", "running"],
                            weights=[50, 40, 10],
                        )[0]
                        setpoint = round(random.uniform(18.0, 20.0), 1) if status_val == "running" else None

                    # Occasional fault
                    if random.random() < 0.005:
                        status_val = "fault"
                        setpoint = None

                    hvac_rows.append({
                        "time": t.isoformat(),
                        "device_id": device_id,
                        "building_id": zone["building_id"],
                        "zone_id": zone["id"],
                        "device_type": device_type,
                        "status": status_val,
                        "setpoint": setpoint,
                    })
                    t += timedelta(minutes=30)

        for i in range(0, len(hvac_rows), 2000):
            batch = hvac_rows[i:i + 2000]
            values_clause = ", ".join(
                f"('{r['time']}', '{r['device_id']}', '{r['building_id']}', "
                f"'{r['zone_id']}', '{r['device_type']}', '{r['status']}', "
                f"{'NULL' if r['setpoint'] is None else r['setpoint']})"
                for r in batch
            )
            await db.execute(text(
                f"INSERT INTO hvac_status (time, device_id, building_id, zone_id, device_type, status, setpoint) "
                f"VALUES {values_clause} ON CONFLICT DO NOTHING"
            ))
        await db.commit()
        print(f"  Inserted {len(hvac_rows)} HVAC status entries")

        # ---------------------------------------------------------------------------
        # ENERGY METER READINGS
        # ---------------------------------------------------------------------------
        print(f"Generating {DAYS} days of energy meter data...")
        meter_rows = []
        all_building_ids = [str(DEMO_BUILDING_ID)] + [b["id"] for b in BUILDINGS]
        for building_id in all_building_ids:
            suffix = building_id[-4:]
            meters = [f"demo-main-{suffix}", f"demo-hvac-{suffix}", f"demo-light-{suffix}"]
            for meter_id in meters:
                t = start
                while t < now:
                    if "main" in meter_id:
                        base_kwh = 50.0
                    elif "hvac" in meter_id:
                        base_kwh = 30.0
                    else:
                        base_kwh = 10.0

                    if 8 <= t.hour <= 20:
                        load_factor = 1.0 + 0.5 * math.sin(math.pi * (t.hour - 8) / 12)
                    else:
                        load_factor = 0.3

                    kwh = round(base_kwh * load_factor + random.gauss(0, 2), 2)
                    voltage = round(random.gauss(230, 2), 1)
                    current_val = round(kwh / voltage * 1000, 2) if voltage > 0 else 0

                    meter_rows.append({
                        "time": t.isoformat(),
                        "meter_id": meter_id,
                        "building_id": building_id,
                        "kwh": max(0, kwh),
                        "voltage": voltage,
                        "current": current_val,
                    })
                    t += timedelta(minutes=15)

        for i in range(0, len(meter_rows), 2000):
            batch = meter_rows[i:i + 2000]
            values_clause = ", ".join(
                f"('{r['time']}', '{r['meter_id']}', '{r['building_id']}', "
                f"{r['kwh']}, {r['voltage']}, {r['current']})"
                for r in batch
            )
            await db.execute(text(
                f"INSERT INTO energy_meter (time, meter_id, building_id, kwh, voltage, current) "
                f"VALUES {values_clause} ON CONFLICT DO NOTHING"
            ))
        await db.commit()
        print(f"  Inserted {len(meter_rows)} energy meter readings")

        # ---------------------------------------------------------------------------
        # FORECASTS
        # ---------------------------------------------------------------------------
        print("Generating sample forecasts...")
        forecast_count = 0
        for zone in ZONES[:5]:
            for hour_offset in range(0, 48):
                forecast_time = now + timedelta(hours=hour_offset)
                predicted = generate_sensor_value("temperature", forecast_time.hour, 0)
                await db.execute(
                    text(
                        "INSERT INTO forecasts (id, zone_id, forecast_type, predicted_value, forecast_time) "
                        "VALUES (gen_random_uuid(), :zone_id, :forecast_type, :predicted_value, :forecast_time)"
                    ),
                    {
                        "zone_id": zone["id"],
                        "forecast_type": "energy_consumption",
                        "predicted_value": round(abs(predicted * 5 + random.gauss(0, 3)), 2),
                        "forecast_time": forecast_time.isoformat(),
                    },
                )
                forecast_count += 1
        await db.commit()
        print(f"  Inserted {forecast_count} forecasts")

        # ---------------------------------------------------------------------------
        # RECOMMENDATIONS
        # ---------------------------------------------------------------------------
        print("Generating sample recommendations...")
        rec_types = [
            ("hvac_setpoint", 22.0, 1.5),
            ("lighting_level", 70.0, 15.0),
            ("ventilation_rate", 50.0, 10.0),
        ]
        rec_count = 0
        statuses = ["pending", "pending", "pending", "approved", "applied", "rejected"]
        for zone in ZONES[:5]:
            for rec_type, base_val, spread in rec_types:
                val = round(base_val + random.gauss(0, spread / 2), 1)
                chosen_status = random.choice(statuses)
                applied_at = (
                    f"'{(now - timedelta(hours=random.randint(1, 48))).isoformat()}'"
                    if chosen_status == "applied"
                    else "NULL"
                )
                await db.execute(
                    text(
                        "INSERT INTO recommendations "
                        "(id, zone_id, recommendation_type, value, status, applied_at) "
                        "VALUES (gen_random_uuid(), :zone_id, :rec_type, :value, :status, "
                        f"{applied_at})"
                    ),
                    {
                        "zone_id": zone["id"],
                        "rec_type": rec_type,
                        "value": val,
                        "status": chosen_status,
                    },
                )
                rec_count += 1
        await db.commit()
        print(f"  Inserted {rec_count} recommendations")

    await engine.dispose()
    print("\nDemo data seeding complete!")


if __name__ == "__main__":
    import sys
    import os

    # Try to load DATABASE_URL from environment or .env file
    db_url = os.environ.get("DATABASE_URL")

    if not db_url:
        try:
            from dotenv import load_dotenv
            load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
            db_url = os.environ.get("DATABASE_URL")
        except ImportError:
            pass

    if not db_url:
        db_url = "postgresql+asyncpg://energy_user:energy_pass_dev@localhost:5433/energy_platform"
        print(f"No DATABASE_URL found, using default: {db_url}")

    asyncio.run(seed(db_url))
