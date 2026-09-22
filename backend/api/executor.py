"""
Pandas Executor for Real Estate Insights.
Computes deterministic results, charts, and summary text strictly from Excel data.
"""

from typing import Dict, Any, List
import pandas as pd
from .schemas import StructuredQuery
from .excel_loader import get_area_data


def _clean_numeric(val: Any) -> float:
    if pd.isna(val) or val in ["", "-", None]:
        return 0.0
    try:
        clean_str = str(val).replace(",", "").replace("\u20b9", "").strip()
        return float(clean_str)
    except (ValueError, TypeError):
        return 0.0


def execute_query(query_struct: StructuredQuery) -> Dict[str, Any]:
    if not query_struct.is_valid or not query_struct.localities:
        return {
            "summary": query_struct.rejection_reason or "Invalid query or no Pune locality matched.",
            "chart": [],
            "tables": {},
            "areas": []
        }

    data_dict: Dict[str, pd.DataFrame] = {}
    for area in query_struct.localities:
        df = get_area_data(area)
        if not df.empty:
            data_dict[area] = df

    if not data_dict:
        return {
            "summary": f"No data found for localities: {query_struct.localities}",
            "chart": [],
            "tables": {},
            "areas": []
        }

    areas = list(data_dict.keys())
    chart_data = _build_chart_data(areas, data_dict)
    summary_text = _generate_summary(query_struct, areas, data_dict)

    tables = {}
    for area, df in data_dict.items():
        # Replace NaN with None for JSON compliance
        tables[area] = df.where(pd.notna(df), None).to_dict(orient="records")

    return {
        "summary": summary_text,
        "chart": chart_data,
        "tables": tables,
        "areas": areas
    }


def _generate_summary(query_struct: StructuredQuery, areas: List[str], data_dict: Dict[str, pd.DataFrame]) -> str:
    if query_struct.operation == "top_n" or len(areas) >= 4:
        summary = "### Best Investment Insights (2020\u20132024)\n\n"
        best_area = None
        best_growth = -999.0
        for area in areas:
            df = data_dict[area]
            r2020 = df[df["year"] == 2020]
            r2024 = df[df["year"] == 2024]
            p2020 = _clean_numeric(r2020["flat - weighted average rate"].iloc[0]) if not r2020.empty else 0.0
            p2024 = _clean_numeric(r2024["flat - weighted average rate"].iloc[0]) if not r2024.empty else 0.0
            growth = round(((p2024 - p2020) / p2020) * 100, 1) if p2020 > 0 else 0.0
            units = int(_clean_numeric(df["total sold - igr"].sum()))
            summary += f"* **{area}**: +{growth}% growth (₹{int(p2020):,}/sqft -> ₹{int(p2024):,}/sqft) | {units:,} units sold\n"
            if growth > best_growth:
                best_growth = growth
                best_area = area
        summary += f"\n**Top Performer: {best_area}** (+{best_growth}% price appreciation from 2020 to 2024)."
        return summary

    if query_struct.operation == "compare" or len(areas) >= 2:
        summary = "### Locality Comparison (2020\u20132024)\n\n"
        best_area = None
        best_growth = -999.0
        for area in areas:
            df = data_dict[area]
            r2020 = df[df["year"] == 2020]
            r2024 = df[df["year"] == 2024]
            p2020 = _clean_numeric(r2020["flat - weighted average rate"].iloc[0]) if not r2020.empty else 0.0
            p2024 = _clean_numeric(r2024["flat - weighted average rate"].iloc[0]) if not r2024.empty else 0.0
            growth = round(((p2024 - p2020) / p2020) * 100, 1) if p2020 > 0 else 0.0
            units = int(_clean_numeric(df["total sold - igr"].sum()))
            summary += f"* **{area}**: +{growth}% growth | ₹{int(p2024):,}/sqft in 2024 | {units:,} total units sold\n"
            if growth > best_growth:
                best_growth = growth
                best_area = area
        summary += f"\n**Higher Growth Locality: {best_area}** (+{best_growth}% appreciation)."
        return summary

    # Single Locality Analysis
    area = areas[0]
    df = data_dict[area]
    r2020 = df[df["year"] == 2020]
    r2024 = df[df["year"] == 2024]
    p2020 = _clean_numeric(r2020["flat - weighted average rate"].iloc[0]) if not r2020.empty else 0.0
    p2024 = _clean_numeric(r2024["flat - weighted average rate"].iloc[0]) if not r2024.empty else 0.0
    growth = round(((p2024 - p2020) / p2020) * 100, 1) if p2020 > 0 else 0.0
    units = int(_clean_numeric(df["total sold - igr"].sum()))
    return (
        f"### {area} Overview (2020\u20132024)\n\n"
        f"* **Price Trend**: ₹{int(p2020):,}/sqft in 2020 -> ₹{int(p2024):,}/sqft in 2024 (+{growth}% overall growth)\n"
        f"* **Total Volume**: {units:,} residential units sold between 2020 and 2024\n"
        f"* **Data Source**: Official IGR registration dataset"
    )


def _build_chart_data(areas: List[str], data_dict: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
    chart = []
    for year in [2020, 2021, 2022, 2023, 2024]:
        entry: Dict[str, Any] = {"year": str(year)}
        for area in areas:
            df = data_dict.get(area, pd.DataFrame())
            row = df[df["year"] == year]
            price = int(_clean_numeric(row["flat - weighted average rate"].iloc[0])) if not row.empty else 0
            units = int(_clean_numeric(row["total sold - igr"].iloc[0])) if not row.empty else 0
            entry[f"{area} Price"] = price
            entry[f"{area} Units"] = units
        chart.append(entry)
    return chart

