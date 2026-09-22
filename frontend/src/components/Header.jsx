import React from "react";
import { Building2, Sparkles } from "lucide-react";

export default function Header() {
  return (
    <header className="app-header">
      <div className="header-brand">
        <div className="header-icon">
          <Building2 size={24} />
        </div>
        <div>
          <h1 className="header-title">Real Estate Insights</h1>
          <p className="header-subtitle">Pune Locality Price Trends & Investment Analytics</p>
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--accent-primary)", fontSize: "0.85rem", fontWeight: "500" }}>
        <Sparkles size={16} />
        <span>v2.0 Clean Architecture</span>
      </div>
    </header>
  );
}

