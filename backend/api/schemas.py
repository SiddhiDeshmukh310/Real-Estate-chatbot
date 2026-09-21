"""
Structured Pydantic schemas and Whitelists for Real Estate Insights query engine.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

ALLOWED_LOCALITIES = ["Akurdi", "Ambegaon Budruk", "Aundh", "Wakad"]

ALLOWED_OPERATIONS = [
    "average_price",
    "total_units",
    "growth_rate",
    "compare",
    "top_n",
    "locality_summary",
]

ALLOWED_METRICS = [
    "flat_rate",
    "units_sold",
    "carpet_area",
]

ALLOWED_YEARS = [2020, 2021, 2022, 2023, 2024]


class StructuredQuery(BaseModel):
    operation: str = Field(
        default="locality_summary",
        description="The mathematical or analytical operation to perform."
    )
    metric: str = Field(
        default="flat_rate",
        description="The metric requested (flat_rate, units_sold, carpet_area)."
    )
    localities: List[str] = Field(
        default_factory=list,
        description="List of Pune localities requested from the whitelist."
    )
    start_year: int = Field(default=2020, description="Start year (2020-2024).")
    end_year: int = Field(default=2024, description="End year (2020-2024).")
    group_by: Optional[str] = Field(default="year", description="Grouping dimension (year, location).")
    is_valid: bool = Field(default=True, description="Whether the query passed validation.")
    rejection_reason: Optional[str] = Field(default=None, description="Reason for rejection if invalid.")

    @field_validator("operation")
    @classmethod
    def validate_operation(cls, v: str) -> str:
        if v not in ALLOWED_OPERATIONS:
            raise ValueError(f"Operation \x27{v}\x27 is not in allowed operations whitelist: {ALLOWED_OPERATIONS}")
        return v

    @field_validator("metric")
    @classmethod
    def validate_metric(cls, v: str) -> str:
        if v not in ALLOWED_METRICS:
            raise ValueError(f"Metric \x27{v}\x27 is not in allowed metrics whitelist: {ALLOWED_METRICS}")
        return v

    @field_validator("localities")
    @classmethod
    def validate_localities(cls, v: List[str]) -> List[str]:
        cleaned = []
        for loc in v:
            matched = False
            for allowed in ALLOWED_LOCALITIES:
                if loc.lower().strip() == allowed.lower().strip():
                    cleaned.append(allowed)
                    matched = True
                    break
            if not matched:
                raise ValueError(f"Locality \x27{loc}\x27 is not in allowed Pune localities: {ALLOWED_LOCALITIES}")
        return cleaned

    @field_validator("start_year", "end_year")
    @classmethod
    def validate_years(cls, v: int) -> int:
        if v not in ALLOWED_YEARS:
            raise ValueError(f"Year {v} is outside allowed dataset year range 2020-2024.")
        return v

