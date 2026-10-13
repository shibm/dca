"""Pydantic schemas for Pillar 4: Batch Data Automation & Python Script Execution Framework."""

from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class ScriptParameter(BaseModel):
    name: str
    type: Literal["string", "int", "float", "bool", "list"] = "string"
    description: str
    default: Optional[Any] = None
    required: bool = False


class AutomationScriptMetadata(BaseModel):
    script_id: str
    name: str
    category: Literal["PROCUREMENT", "REVENUE_BILLING", "VENDOR_SLA", "ANOMALY_RISK", "DATA_QUALITY", "GENERAL"]
    description: str
    version: str = "1.0.0"
    author: str = "DCA Automation Framework"
    tags: List[str] = Field(default_factory=list)
    required_fields: List[str] = Field(default_factory=list)
    optional_fields: List[str] = Field(default_factory=list)
    parameters: List[ScriptParameter] = Field(default_factory=list)


class BusinessRule(BaseModel):
    rule_id: str
    rule_name: str
    rule_type: Literal["THRESHOLD", "MANDATORY_FIELD", "CROSS_FIELD", "PATTERN_MATCH", "CONDITIONAL"]
    target_field: str
    severity: Literal["INFO", "LOW", "MEDIUM", "WARNING", "HIGH", "CRITICAL"] = "WARNING"
    description: str
    threshold_value: Optional[float] = None
    operator: Optional[Literal["gt", "gte", "lt", "lte", "eq", "neq", "in", "not_in", "contains"]] = None
    mandatory: Optional[bool] = False


class DataAnomaly(BaseModel):
    anomaly_id: str
    record_index: int
    record_id: Optional[str] = None
    field_name: Optional[str] = None
    anomaly_type: Literal[
        "DUPLICATE_RECORD",
        "Z_SCORE_OUTLIER",
        "MISSING_MANDATORY_FIELD",
        "THRESHOLD_VIOLATION",
        "CROSS_FIELD_INCONSISTENCY",
        "INVALID_FORMAT",
        "SUSPICIOUS_PATTERN"
    ]
    severity: Literal["INFO", "LOW", "MEDIUM", "WARNING", "HIGH", "CRITICAL"]
    description: str
    original_value: Optional[Any] = None
    suggested_value: Optional[Any] = None
    z_score: Optional[float] = None
    confidence_score: float = 0.95


class BusinessInsight(BaseModel):
    insight_id: str
    title: str
    category: str
    metric_type: Literal["CURRENCY", "PERCENTAGE", "COUNT", "RATIO", "SCORE"]
    metric_value: float
    formatted_value: str
    narrative: str
    recommendation: str
    trend: Literal["UP", "DOWN", "NEUTRAL", "RISK"] = "NEUTRAL"


class AutomationJobRequest(BaseModel):
    job_id: Optional[str] = None
    script_ids: List[str] = Field(default_factory=lambda: ["procurement_spend_audit", "statistical_anomaly_detector"])
    raw_records: List[Dict[str, Any]]
    custom_rules: Optional[List[BusinessRule]] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ScriptExecutionLog(BaseModel):
    script_id: str
    script_name: str
    execution_time_ms: float
    status: Literal["SUCCESS", "FAILED", "SKIPPED"]
    records_processed: int
    anomalies_flagged: int
    insights_generated: int
    error_message: Optional[str] = None


class AutomationJobResult(BaseModel):
    job_id: str
    status: Literal["PENDING", "RUNNING", "COMPLETED", "FAILED"]
    started_at: str
    completed_at: str
    execution_time_ms: float
    total_records_ingested: int
    cleaned_records_count: int
    duplicates_detected: int
    anomalies_count: int
    critical_anomalies_count: int
    anomalies: List[DataAnomaly] = Field(default_factory=list)
    insights: List[BusinessInsight] = Field(default_factory=list)
    script_logs: List[ScriptExecutionLog] = Field(default_factory=list)
    summary_metrics: Dict[str, Any] = Field(default_factory=dict)
    sample_cleaned_records: List[Dict[str, Any]] = Field(default_factory=list)
