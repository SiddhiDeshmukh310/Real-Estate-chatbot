import React from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from "recharts";

const COLORS = ["#38bdf8", "#818cf8", "#f43f5e", "#10b981"];

export default function ChartSection({ chartData, areas }) {
  if (!chartData || chartData.length === 0 || !areas || areas.length === 0) {
    return null;
  }

  return (
    <div className="chart-container">
      <h4 style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "12px" }}>
        Annual Price Trend (₹/sqft)
      </h4>
      <div style={{ width: "100%", height: 260 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="year" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#fff" }}
            />
            <Legend />
            {areas.map((area, idx) => (
              <Bar
                key={area}
                dataKey={`${area} Price`}
                fill={COLORS[idx % COLORS.length]}
                name={`${area} Price (₹)`}
                radius={[4, 4, 0, 0]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

