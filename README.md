# Cloverkey Gift Shop Revenue Forecast — V2

A Streamlit dashboard for forecasting mature annual gift shop revenue at new hospital locations, using Cloverkey's V2 four-feature regression model.

## Setup

```bash
pip install -r requirements.txt
```

Place the model artifact at:
```
C:\Users\houstonp\Downloads\cloverkey_forecast_v2.joblib
```

Then run:
```bash
streamlit run app.py
```

App opens at `http://localhost:8501`.

## Pages

**Revenue Forecast** — Enter a hospital's average daily census (ADC), gift shop square footage, and payroll deduction availability. Returns:
- Point estimate (most likely mature annual revenue)
- Conservative–optimistic range (P25–P75 from training residuals)
- 3 most similar Cloverkey stores for comparison
- Option to save the forecast

**About This Model** — Training methodology, validation accuracy (MAPE 18.6%), and known limitations.

**Saved Forecasts** — All forecasts saved via the Save Forecast button, displayed in a sortable row layout with timestamp, inputs, and revenue range.

## Model

- 4-feature log-linear regression: ADC, shop size, payroll deduction, ADC×size interaction
- Trained on 35 general acute-care hospitals
- Validated via leave-one-out cross-validation (MAPE 18.6%)

## Known Limitations

| Limitation | Detail |
|---|---|
| Specialty hospitals out of scope | Do not use for Children's or Cancer hospital bids. Use Store 101 (Boston Children's) or Stores 108/122 (Moffitt) as comparables. |
| Top-decile academic medical centers | ADC 700+ hospitals with large shops tend to under-predict by ~15–25%. Flag for manual review. |
| Dual-store hospitals | Divide ADC by the number of planned Cloverkey shops before entering. |
| Year-1 ramp not included | Model predicts mature steady-state revenue. Multiply by ~0.55–0.75 for year-1 projections. |

## Saved Forecasts

Each saved forecast is appended to `prediction_ledger.csv` (excluded from version control) with columns:
`timestamp, hospital_name, adc, size, pd, predicted, low, high, top_comps`
