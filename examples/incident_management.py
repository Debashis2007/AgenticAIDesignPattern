"""Production incident management system with multi-agent orchestration."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class RawAlert:
    """Raw alert from monitoring system."""

    id: str
    source: str
    severity: str
    message: str
    timestamp: str
    metadata: dict = field(default_factory=dict)


@dataclass
class NormalizedAlert:
    """Normalized alert."""

    id: str
    severity: AlertSeverity
    category: str
    title: str
    description: str
    source: str
    timestamp: str
    component: str


@dataclass
class CorrelatedAlert:
    """Correlated alert group."""

    group_id: str
    alerts: list[NormalizedAlert]
    correlation_score: float
    root_cause: Optional[str] = None


@dataclass
class AnalyzedIncident:
    """Analyzed incident."""

    incident_id: str
    alerts: list[NormalizedAlert]
    severity_score: float
    impact_assessment: str
    affected_services: list[str]
    root_cause_hypothesis: str


@dataclass
class IncidentResponse:
    """Response recommendations."""

    incident_id: str
    immediate_actions: list[str]
    escalation_level: str
    estimated_resolution_time: str
    affected_customers: int


class IncidentAlertAgent:
    """Normalizes raw alerts."""

    name = "IncidentAlertAgent"

    def process(self, raw_alert: RawAlert) -> NormalizedAlert:
        """Normalize raw alert."""
        # Extract severity
        severity_map = {
            "p1": AlertSeverity.CRITICAL,
            "critical": AlertSeverity.CRITICAL,
            "p2": AlertSeverity.HIGH,
            "high": AlertSeverity.HIGH,
            "p3": AlertSeverity.MEDIUM,
            "medium": AlertSeverity.MEDIUM,
            "low": AlertSeverity.LOW,
        }
        severity = severity_map.get(
            raw_alert.severity.lower(), AlertSeverity.MEDIUM
        )

        # Categorize
        message_lower = raw_alert.message.lower()
        if "database" in message_lower or "db" in message_lower:
            category = "database"
            component = "database_service"
        elif "network" in message_lower or "connection" in message_lower:
            category = "network"
            component = "network_infrastructure"
        elif "api" in message_lower or "service" in message_lower:
            category = "api"
            component = "api_service"
        else:
            category = "system"
            component = "system"

        return NormalizedAlert(
            id=raw_alert.id,
            severity=severity,
            category=category,
            title=raw_alert.message[:80],
            description=raw_alert.message,
            source=raw_alert.source,
            timestamp=raw_alert.timestamp,
            component=component,
        )


class IncidentCorrelationAgent:
    """Correlates related alerts."""

    name = "IncidentCorrelationAgent"

    def process(self, alerts: list[NormalizedAlert]) -> list[CorrelatedAlert]:
        """Correlate related alerts."""
        correlated = []

        # Group by component
        by_component = {}
        for alert in alerts:
            if alert.component not in by_component:
                by_component[alert.component] = []
            by_component[alert.component].append(alert)

        # Create correlation groups
        for component, group_alerts in by_component.items():
            correlation_score = min(len(group_alerts) / 5.0, 1.0)  # Normalized score
            root_cause = self._determine_root_cause(group_alerts)

            correlated.append(
                CorrelatedAlert(
                    group_id=f"incident_{component}_{len(correlated)}",
                    alerts=group_alerts,
                    correlation_score=correlation_score,
                    root_cause=root_cause,
                )
            )

        return correlated

    def _determine_root_cause(self, alerts: list[NormalizedAlert]) -> str:
        """Determine likely root cause."""
        if len(alerts) == 1:
            return "Isolated incident"
        elif len(alerts) > 3:
            return f"Multiple failures in {alerts[0].component}"
        else:
            return f"Related issues in {alerts[0].component}"


class IncidentAnalysisAgent:
    """Analyzes incidents."""

    name = "IncidentAnalysisAgent"

    def process(self, correlated: CorrelatedAlert) -> AnalyzedIncident:
        """Analyze incident."""
        # Calculate severity score
        severity_weights = {
            AlertSeverity.CRITICAL: 1.0,
            AlertSeverity.HIGH: 0.7,
            AlertSeverity.MEDIUM: 0.4,
            AlertSeverity.LOW: 0.1,
        }
        severity_score = max(
            [severity_weights[alert.severity] for alert in correlated.alerts]
        )

        # Impact assessment
        if severity_score >= 0.9:
            impact = "CRITICAL: Service completely unavailable"
            affected_services = ["all_services"]
        elif severity_score >= 0.7:
            impact = "HIGH: Service significantly degraded"
            affected_services = [alert.component for alert in correlated.alerts]
        else:
            impact = "MEDIUM: Service partially degraded"
            affected_services = [alert.component for alert in correlated.alerts]

        return AnalyzedIncident(
            incident_id=correlated.group_id,
            alerts=correlated.alerts,
            severity_score=severity_score,
            impact_assessment=impact,
            affected_services=affected_services,
            root_cause_hypothesis=correlated.root_cause or "Unknown",
        )


class IncidentResponseAgent:
    """Generates response recommendations."""

    name = "IncidentResponseAgent"

    def process(self, incident: AnalyzedIncident) -> IncidentResponse:
        """Generate response."""
        # Immediate actions based on severity
        if incident.severity_score >= 0.9:
            immediate_actions = [
                "Page on-call team immediately",
                "Start incident war room",
                "Initiate automatic failover if available",
            ]
            escalation = "Executive"
            eta = "15 minutes"
            affected_customers = 100000
        elif incident.severity_score >= 0.7:
            immediate_actions = [
                "Alert operations team",
                "Start investigation",
                "Prepare communications",
            ]
            escalation = "Management"
            eta = "30 minutes"
            affected_customers = 10000
        else:
            immediate_actions = [
                "Create incident ticket",
                "Notify team lead",
                "Begin monitoring",
            ]
            escalation = "Team Lead"
            eta = "1 hour"
            affected_customers = 1000

        return IncidentResponse(
            incident_id=incident.incident_id,
            immediate_actions=immediate_actions,
            escalation_level=escalation,
            estimated_resolution_time=eta,
            affected_customers=affected_customers,
        )


class IncidentManagementWorkflow:
    """Orchestrates the incident management pipeline."""

    def __init__(self):
        self.alert_agent = IncidentAlertAgent()
        self.correlation_agent = IncidentCorrelationAgent()
        self.analysis_agent = IncidentAnalysisAgent()
        self.response_agent = IncidentResponseAgent()

    def process_alerts(self, raw_alerts: list[RawAlert]) -> dict:
        """Process alerts through the full pipeline."""
        print(f"\n{'=' * 70}")
        print("INCIDENT MANAGEMENT WORKFLOW")
        print(f"{'=' * 70}\n")

        # Stage 1: Normalize
        print("STAGE 1: Normalizing Alerts")
        print("-" * 70)
        normalized_alerts = []
        for raw_alert in raw_alerts:
            normalized = self.alert_agent.process(raw_alert)
            normalized_alerts.append(normalized)
            print(f"  ✓ Normalized: {normalized.id} -> {normalized.category}")

        # Stage 2: Correlate
        print("\nSTAGE 2: Correlating Alerts")
        print("-" * 70)
        correlated_incidents = self.correlation_agent.process(normalized_alerts)
        for incident in correlated_incidents:
            print(
                f"  ✓ Correlated: {incident.group_id} "
                f"({len(incident.alerts)} alerts, score: {incident.correlation_score:.2f})"
            )

        # Stage 3: Analyze
        print("\nSTAGE 3: Analyzing Incidents")
        print("-" * 70)
        analyzed_incidents = []
        for correlated in correlated_incidents:
            analyzed = self.analysis_agent.process(correlated)
            analyzed_incidents.append(analyzed)
            print(
                f"  ✓ Analyzed: {analyzed.incident_id} "
                f"(severity: {analyzed.severity_score:.2f})"
            )
            print(f"    Impact: {analyzed.impact_assessment}")

        # Stage 4: Respond
        print("\nSTAGE 4: Generating Response")
        print("-" * 70)
        responses = []
        for incident in analyzed_incidents:
            response = self.response_agent.process(incident)
            responses.append(response)
            print(f"  ✓ Response: {response.incident_id}")
            print(f"    Escalation: {response.escalation_level}")
            print(f"    Actions: {', '.join(response.immediate_actions[:1])}")
            print(f"    ETA: {response.estimated_resolution_time}")

        print(f"\n{'=' * 70}\n")

        return {
            "normalized_alerts": normalized_alerts,
            "correlated_incidents": correlated_incidents,
            "analyzed_incidents": analyzed_incidents,
            "responses": responses,
        }


def main():
    """Run the incident management example."""

    # Create sample alerts
    raw_alerts = [
        RawAlert(
            id="alert_001",
            source="prometheus",
            severity="critical",
            message="Database connection pool exhausted",
            timestamp=datetime.now().isoformat(),
        ),
        RawAlert(
            id="alert_002",
            source="prometheus",
            severity="high",
            message="High database query latency detected",
            timestamp=datetime.now().isoformat(),
        ),
        RawAlert(
            id="alert_003",
            source="datadog",
            severity="high",
            message="API response time degradation - database service",
            timestamp=datetime.now().isoformat(),
        ),
        RawAlert(
            id="alert_004",
            source="pagerduty",
            severity="medium",
            message="Network packet loss detected",
            timestamp=datetime.now().isoformat(),
        ),
    ]

    # Run workflow
    workflow = IncidentManagementWorkflow()
    result = workflow.process_alerts(raw_alerts)

    # Print summary
    print("SUMMARY")
    print("-" * 70)
    print(f"Total alerts received: {len(raw_alerts)}")
    print(f"Normalized alerts: {len(result['normalized_alerts'])}")
    print(f"Correlated incidents: {len(result['correlated_incidents'])}")
    print(f"Response recommendations: {len(result['responses'])}")
    print()


if __name__ == "__main__":
    main()
