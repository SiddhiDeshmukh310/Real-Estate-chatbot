# Real Estate Insights - Dataset Documentation

## Dataset Specifications
* **Filename**: `backend/data/realestate.xlsx`
* **File Size**: 14.86 KB (14,860 bytes)
* **Dimensions**: 20 rows, 28 columns
* **Localities Covered (4)**: `Akurdi`, `Ambegaon Budruk`, `Aundh`, `Wakad`
* **Time Horizon**: 5 Years (2020, 2021, 2022, 2023, 2024)
* **Primary Source**: Official Inspector General of Registration (IGR) property registration dataset for Pune.

## Key Data Columns
1. `final location`: Pune locality name.
2. `year`: Registration year (2020–2024).
3. `city`: City name (`Pune`).
4. `total sold - igr`: Total residential/commercial units registered.
5. `flat - weighted average rate`: Weighted average rate in ₹/sqft for flat transactions.
6. `total carpet area supplied (sqft)`: Total carpet area in square feet.

## Provenance Note
This sample dataset contains 20 rows. All supported query types and evaluation benchmark questions are computed directly against these exact columns and years without synthetic data generation.

