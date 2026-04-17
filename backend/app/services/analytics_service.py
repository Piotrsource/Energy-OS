# =============================================================================
# services/analytics_service.py — Analytics & Dashboard Business Logic
# =============================================================================
# PURPOSE: Aggregate time-series data for the dashboard endpoints:
#   - Energy summary:    Total/avg/peak kWh over time buckets
#   - Carbon emissions:  Estimated CO2 from energy consumption
#   - Anomalies:         Detect unusual sensor readings
#
# TIMESCALEDB FEATURES USED:
#   - time_bucket(): Groups time-series data into fixed intervals (e.g., 1 hour)
#     for efficient aggregation. Much faster than date_trunc() on large datasets.
#   - Chunk exclusion: Automatically skips irrelevant time partitions.
#
# CARBON CALCULATION:
#   CO2 (kg) = kWh × emission_factor
#   Default emission factor: 0.4 kg CO2/kWh (approximate US grid average)
#   This should be configurable per building/region in a future iteration.
# =============================================================================

from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


# Default CO2 emission factor: 0.4 kg CO2 per kWh (approximate US grid average)
# In production, this would be configurable per building or region.
DEFAULT_EMISSION_FACTOR = 0.4


class AnalyticsService:
    """Static methods for dashboard analytics and reporting."""

    @staticmethod
    async def get_energy_summary(
        db: AsyncSession,
        building_id: UUID,
        start: datetime,
        end: datetime,
    ) -> dict:
        """
        Aggregate energy consumption for a building over a time range.

        Uses TimescaleDB's time_bucket() to group readings into hourly buckets.
        Returns total, average, and peak kWh for each hour, plus a grand total.

        Args:
            building_id: The building to analyze.
            start: Start of the time range (inclusive).
            end: End of the time range (inclusive).

        Returns:
            Dict with building_id, start, end, buckets (list), and total_kwh.
        """
        query = text("""
            SELECT
                time_bucket('1 hour', time) AS bucket,
                SUM(kwh) AS total_kwh,
                AVG(kwh) AS avg_kwh,
                MAX(kwh) AS peak_kwh
            FROM energy_meter
            WHERE building_id = :building_id
              AND time >= :start
              AND time <= :end
            GROUP BY bucket
            ORDER BY bucket
        """)

        result = await db.execute(query, {
            "building_id": str(building_id),
            "start": start,
            "end": end,
        })
        rows = result.mappings().all()

        # Calculate grand total across all buckets
        total_kwh = sum(row["total_kwh"] for row in rows) if rows else 0.0

        return {
            "building_id": str(building_id),
            "start": start,
            "end": end,
            "buckets": [
                {
                    "bucket": row["bucket"],
                    "total_kwh": round(row["total_kwh"], 4),
                    "avg_kwh": round(row["avg_kwh"], 4),
                    "peak_kwh": round(row["peak_kwh"], 4),
                }
                for row in rows
            ],
            "total_kwh": round(total_kwh, 4),
        }

    @staticmethod
    async def get_carbon_emissions(
        db: AsyncSession,
        building_id: UUID,
        start: datetime,
        end: datetime,
        emission_factor: float = DEFAULT_EMISSION_FACTOR,
    ) -> dict:
        """
        Estimate CO2 emissions from energy consumption.

        Converts kWh to kg CO2 using the emission factor.
        Groups by hourly buckets for trend visualization.

        Args:
            building_id: The building to analyze.
            start: Start of the time range.
            end: End of the time range.
            emission_factor: kg CO2 per kWh (default: 0.4).

        Returns:
            Dict with building_id, emission_factor, buckets, and total_carbon_kg.
        """
        query = text("""
            SELECT
                time_bucket('1 hour', time) AS bucket,
                SUM(kwh) AS total_kwh
            FROM energy_meter
            WHERE building_id = :building_id
              AND time >= :start
              AND time <= :end
            GROUP BY bucket
            ORDER BY bucket
        """)

        result = await db.execute(query, {
            "building_id": str(building_id),
            "start": start,
            "end": end,
        })
        rows = result.mappings().all()

        total_carbon = 0.0
        buckets = []
        for row in rows:
            carbon_kg = row["total_kwh"] * emission_factor
            total_carbon += carbon_kg
            buckets.append({
                "bucket": row["bucket"],
                "total_kwh": round(row["total_kwh"], 4),
                "carbon_kg": round(carbon_kg, 4),
            })

        return {
            "building_id": str(building_id),
            "start": start,
            "end": end,
            "emission_factor_kg_per_kwh": emission_factor,
            "buckets": buckets,
            "total_carbon_kg": round(total_carbon, 4),
        }

    @staticmethod
    async def get_anomalies(
        db: AsyncSession,
        building_id: UUID,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[dict]:
        """
        Detect anomalies in sensor readings using a simple statistical method.

        APPROACH: For each sensor type in the building, readings that deviate
        more than 3 standard deviations from the mean are flagged as anomalies.
        This is a basic z-score method — the AI/ML engine will provide more
        sophisticated anomaly detection in production.

        Args:
            building_id: The building to check.
            start: Optional start of time range.
            end: Optional end of time range.

        Returns:
            List of anomaly dicts with timestamp, sensor info, and severity.
        """
        # Build the WHERE clause dynamically based on provided filters
        where_clauses = ["building_id = :building_id"]
        params: dict = {"building_id": str(building_id)}

        if start:
            where_clauses.append("time >= :start")
            params["start"] = start
        if end:
            where_clauses.append("time <= :end")
            params["end"] = end

        where_sql = " AND ".join(where_clauses)

        # Step 1: Calculate mean and stddev per sensor type for the building
        # Step 2: Find readings that deviate more than 3 standard deviations
        query = text(f"""
            WITH stats AS (
                SELECT
                    sensor_type,
                    AVG(value) AS mean_val,
                    STDDEV(value) AS stddev_val
                FROM sensor_readings
                WHERE {where_sql}
                GROUP BY sensor_type
                HAVING STDDEV(value) > 0
            )
            SELECT
                sr.time AS timestamp,
                sr.building_id,
                sr.zone_id,
                sr.sensor_type,
                sr.sensor_id,
                sr.value AS actual_value,
                s.mean_val AS expected_value,
                ABS(sr.value - s.mean_val) / s.stddev_val AS z_score
            FROM sensor_readings sr
            JOIN stats s ON sr.sensor_type = s.sensor_type
            WHERE sr.building_id = :building_id
              AND ABS(sr.value - s.mean_val) / s.stddev_val > 3
            ORDER BY sr.time DESC
            LIMIT 100
        """)

        result = await db.execute(query, params)
        rows = result.mappings().all()

        anomalies = []
        for row in rows:
            z = float(row["z_score"])
            # Classify severity based on z-score magnitude
            if z > 5:
                severity = "critical"
            elif z > 4:
                severity = "high"
            elif z > 3.5:
                severity = "medium"
            else:
                severity = "low"

            anomalies.append({
                "id": f"{row['sensor_id']}_{row['timestamp'].isoformat()}",
                "building_id": str(row["building_id"]),
                "zone_id": str(row["zone_id"]),
                "timestamp": row["timestamp"],
                "sensor_type": row["sensor_type"],
                "expected_value": round(float(row["expected_value"]), 2),
                "actual_value": round(float(row["actual_value"]), 2),
                "severity": severity,
                "description": (
                    f"{row['sensor_type']} sensor '{row['sensor_id']}' reported "
                    f"{row['actual_value']:.1f} (expected ~{float(row['expected_value']):.1f}, "
                    f"z-score: {z:.1f})"
                ),
            })

        return anomalies
