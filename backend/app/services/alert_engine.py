"""
Alert Evaluation Engine — background task that checks alert rules every 60s.

Reads the latest sensor readings from Redis, evaluates each enabled rule,
and creates Alert records + Notifications when a threshold is breached.
Respects per-user notification preferences (channels, severity filter,
quiet hours) and sends email via SendGrid when enabled.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone

from app.db.engine import AsyncSessionLocal
from app.db.redis import redis_client
from app.models.alert_rule import AlertRule
from app.models.alert import Alert
from app.models.notification import Notification
from app.models.user import User, UserRole
from app.services.alert_rule_service import AlertRuleService
from app.services.notification_preference_service import NotificationPreferenceService
from app.services.email_service import send_alert_email

from sqlalchemy import select

logger = logging.getLogger("energy_platform")

EVAL_INTERVAL_SECONDS = 60

CONDITION_OPS = {
    "gt":  lambda v, t: v > t,
    "lt":  lambda v, t: v < t,
    "eq":  lambda v, t: abs(v - t) < 1e-9,
    "gte": lambda v, t: v >= t,
    "lte": lambda v, t: v <= t,
}


async def _evaluate_once() -> int:
    """Single evaluation pass. Returns number of alerts created."""
    alerts_created = 0

    keys = []
    async for key in redis_client.scan_iter("device:latest:*"):
        keys.append(key)

    if not keys:
        return 0

    values = await redis_client.mget(keys)
    cached_readings: list[dict] = []
    for val in values:
        if val:
            cached_readings.append(json.loads(val))

    if not cached_readings:
        return 0

    now_utc = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as session:
        rules = await AlertRuleService.get_enabled_rules(session)

        for rule in rules:
            op = CONDITION_OPS.get(rule.condition)
            if not op:
                continue

            matching = [
                r for r in cached_readings
                if r.get("building_id") == str(rule.building_id)
                and r.get("sensor_type") == rule.sensor_type
                and (rule.zone_id is None or r.get("zone_id") == str(rule.zone_id))
            ]

            for reading in matching:
                if op(reading["value"], rule.threshold):
                    alert = Alert(
                        rule_id=rule.id,
                        sensor_id=reading["sensor_id"],
                        value=reading["value"],
                    )
                    session.add(alert)
                    await session.flush()

                    title = f"Alert: {rule.name or rule.sensor_type} {rule.condition} {rule.threshold}"
                    body = f"Sensor {reading['sensor_id']} value={reading['value']} breached rule threshold."
                    severity = rule.severity or "medium"

                    # Notify all admin users, respecting their preferences
                    admin_result = await session.execute(
                        select(User).where(User.role == UserRole.ADMIN).limit(20)
                    )
                    admins = list(admin_result.scalars().all())

                    for admin in admins:
                        pref = await NotificationPreferenceService.get_or_create(session, admin.id)

                        # Check severity filter
                        if not NotificationPreferenceService.passes_severity_filter(severity, pref.min_severity):
                            continue

                        # Check quiet hours (suppress non-critical during quiet hours)
                        if severity != "critical" and NotificationPreferenceService.is_quiet_hours(
                            now_utc.hour, pref.quiet_start_hour, pref.quiet_end_hour
                        ):
                            continue

                        # In-app notification
                        if pref.in_app_enabled:
                            notif = Notification(
                                user_id=admin.id,
                                alert_id=alert.id,
                                channel="in_app",
                                title=title,
                                body=body,
                            )
                            session.add(notif)

                        # Email notification
                        if pref.email_enabled:
                            email_addr = pref.email_address or admin.email
                            notif_email = Notification(
                                user_id=admin.id,
                                alert_id=alert.id,
                                channel="email",
                                title=title,
                                body=body,
                            )
                            session.add(notif_email)
                            # Fire-and-forget email (don't block the loop)
                            asyncio.create_task(
                                send_alert_email(email_addr, title, body, severity)
                            )

                    alerts_created += 1

        await session.commit()

    return alerts_created


async def run_alert_engine() -> None:
    """Long-running task: evaluate alert rules every EVAL_INTERVAL_SECONDS."""
    logger.info("Alert evaluation engine started (interval=%ds)", EVAL_INTERVAL_SECONDS)
    while True:
        try:
            count = await _evaluate_once()
            if count:
                logger.info("Alert engine: created %d alert(s)", count)
        except Exception:
            logger.exception("Alert engine evaluation failed")
        await asyncio.sleep(EVAL_INTERVAL_SECONDS)
