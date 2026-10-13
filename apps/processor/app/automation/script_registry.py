"""Pluggable script registry and executor for batch automation."""

from __future__ import annotations
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
from app.schemas.automation import (
    AutomationScriptMetadata,
    BusinessInsight,
    DataAnomaly,
    ScriptExecutionLog,
)

# Import built-in scripts
from app.automation.scripts import (
    procurement_spend_audit,
    revenue_billing_reconciliation,
    vendor_sla_penalty_calculator,
    statistical_anomaly_detector,
)


class ScriptRegistry:
    """Registry managing available automation scripts and their execution."""

    def __init__(self):
        self._scripts: Dict[str, Tuple[AutomationScriptMetadata, Callable]] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(
            procurement_spend_audit.SCRIPT_METADATA,
            procurement_spend_audit.run,
        )
        self.register(
            revenue_billing_reconciliation.SCRIPT_METADATA,
            revenue_billing_reconciliation.run,
        )
        self.register(
            vendor_sla_penalty_calculator.SCRIPT_METADATA,
            vendor_sla_penalty_calculator.run,
        )
        self.register(
            statistical_anomaly_detector.SCRIPT_METADATA,
            statistical_anomaly_detector.run,
        )

    def register(self, metadata: AutomationScriptMetadata, runner_fn: Callable) -> None:
        """Register a new script plugin."""
        self._scripts[metadata.script_id] = (metadata, runner_fn)

    def get_metadata(self, script_id: str) -> Optional[AutomationScriptMetadata]:
        entry = self._scripts.get(script_id)
        return entry[0] if entry else None

    def list_scripts(self) -> List[AutomationScriptMetadata]:
        return [entry[0] for entry in self._scripts.values()]

    def execute_script(
        self, script_id: str, records: List[Dict[str, Any]], parameters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[DataAnomaly], List[BusinessInsight], Dict[str, Any], ScriptExecutionLog]:
        """Execute a single script safely with performance timing."""
        params = parameters or {}
        entry = self._scripts.get(script_id)

        if not entry:
            log = ScriptExecutionLog(
                script_id=script_id,
                script_name="Unknown Script",
                execution_time_ms=0.0,
                status="FAILED",
                records_processed=0,
                anomalies_flagged=0,
                insights_generated=0,
                error_message=f"Script '{script_id}' is not registered.",
            )
            return [], [], {}, log

        metadata, runner_fn = entry
        start_time = time.perf_counter()

        try:
            anomalies, insights, metrics = runner_fn(records, params)
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            log = ScriptExecutionLog(
                script_id=script_id,
                script_name=metadata.name,
                execution_time_ms=duration_ms,
                status="SUCCESS",
                records_processed=len(records),
                anomalies_flagged=len(anomalies),
                insights_generated=len(insights),
                error_message=None,
            )
            return anomalies, insights, metrics, log
        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            log = ScriptExecutionLog(
                script_id=script_id,
                script_name=metadata.name,
                execution_time_ms=duration_ms,
                status="FAILED",
                records_processed=len(records),
                anomalies_flagged=0,
                insights_generated=0,
                error_message=str(e),
            )
            return [], [], {}, log


# Global registry singleton
REGISTRY = ScriptRegistry()

