import React, { useState } from "react";

export default function DataTable({ tables }) {
  if (!tables || Object.keys(tables).length === 0) {
    return null;
  }

  const areas = Object.keys(tables);
  const [selectedArea, setSelectedArea] = useState(areas[0]);
  const rows = tables[selectedArea] || [];

  if (rows.length === 0) return null;

  const displayCols = ["year", "total sold - igr", "flat - weighted average rate", "total units"];

  return (
    <div style={{ marginTop: "16px" }}>
      <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
        {areas.map((area) => (
          <button
            key={area}
            onClick={() => setSelectedArea(area)}
            className="chip-btn"
            style={{
              background: selectedArea === area ? "var(--user-bubble)" : "var(--bg-card-hover)",
              color: "#fff",
            }}
          >
            {area} Data
          </button>
        ))}
      </div>
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Year</th>
              <th>Units Sold (IGR)</th>
              <th>Weighted Rate (₹/sqft)</th>
              <th>Total Units</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i}>
                <td>{r.year}</td>
                <td>{r["total sold - igr"] ? Number(r["total sold - igr"]).toLocaleString() : 0}</td>
                <td>₹{r["flat - weighted average rate"] ? Number(r["flat - weighted average rate"]).toLocaleString() : 0}</td>
                <td>{r["total units"] ? Number(r["total units"]).toLocaleString() : 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

