"""Simple alert classification agent example."""

import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Alert:
    """Alert data structure."""

    id: str
    severity: str  # critical, high, medium, low
    source: str
    message: str
    timestamp: str


@dataclass
class ClassificationResult:
    """Classification result."""

    alert_id: str
    original_severity: str
    classification: str
    action: str
    reasoning: str


def classify_alert(alert: Alert) -> ClassificationResult:
    """Classify an alert based on rules."""

    # Rule-based classification
    if alert.severity in ["critical", "emergency"]:
        classification = "critical_incident"
        action = "escalate_immediately"
        reasoning = "Critical severity triggers immediate escalation"

    elif alert.severity == "high":
        if "database" in alert.message.lower():
            classification = "database_issue"
            action = "notify_dba_team"
            reasoning = "High severity database issue"
        elif "network" in alert.message.lower():
            classification = "network_issue"
            action = "notify_network_team"
            reasoning = "High severity network issue"
        else:
            classification = "high_severity"
            action = "escalate_soon"
            reasoning = "High severity alert requires escalation"

    elif alert.severity == "medium":
        classification = "medium_severity"
        action = "create_ticket"
        reasoning = "Medium severity - create support ticket"

    else:  # low
        classification = "low_severity"
        action = "log_and_monitor"
        reasoning = "Low severity - monitor and log"

    return ClassificationResult(
        alert_id=alert.id,
        original_severity=alert.severity,
        classification=classification,
        action=action,
        reasoning=reasoning,
    )


def main():
    """Run the simple agent example."""

    # Test alerts
    alerts = [
        Alert(
            id="alert_001",
            severity="critical",
            source="monitoring_system",
            message="Database connection pool exhausted",
            timestamp="2024-01-15T10:30:00Z",
        ),
        Alert(
            id="alert_002",
            severity="high",
            source="network_monitor",
            message="High latency detected on network interface",
            timestamp="2024-01-15T10:31:00Z",
        ),
        Alert(
            id="alert_003",
            severity="medium",
            source="application_log",
            message="Error rate exceeding threshold",
            timestamp="2024-01-15T10:32:00Z",
        ),
        Alert(
            id="alert_004",
            severity="low",
            source="system_monitor",
            message="Disk usage at 85%",
            timestamp="2024-01-15T10:33:00Z",
        ),
    ]

    print("=" * 60)
    print("SIMPLE AGENT EXAMPLE: Alert Classification")
    print("=" * 60)
    print()

    # Process each alert
    for alert in alerts:
        result = classify_alert(alert)

        print(f"Alert ID: {result.alert_id}")
        print(f"  Original Severity: {result.original_severity}")
        print(f"  Classification: {result.classification}")
        print(f"  Recommended Action: {result.action}")
        print(f"  Reasoning: {result.reasoning}")
        print()

    print("=" * 60)
    print("Classification complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
