# Australia's Broadband Divide — FIT2179 Data Visualisation 2

**Live page:** https://autumnwaterg.github.io/Data-visualisation2/

A data-storytelling page exploring how NBN broadband speed and technology differ across Australian communities, built for the FIT2179 Data Visualisation 2 assignment at Monash University.

## Topic

The Australian National Broadband Network (NBN) promised universal fast internet, but real-world speeds vary dramatically by state, geography, and connection technology. This project visualises those divides using two complementary datasets — a 2021 geographic baseline and a 2025 monitored-panel report — to show where speeds are fast, where they fall short, and which technologies are responsible.

## Data Sources

| Dataset | Description |
|---|---|
| [Ookla Speedtest Open Data](https://registry.opendata.aws/speedtest-global-performance/) | Fixed broadband, Australia, Q3 2021 — 82,000+ crowd-sourced measurements. Used as a **historical geographic baseline**. Licensed CC BY 4.0. |
| [ACCC Measuring Broadband Australia Report 28](https://www.accc.gov.au/consumers/internet-and-phone/broadband-performance-program) | March 2025 — 1,787 monitored NBN household services. **Primary source** for technology, plan-tier, and RSP analysis. Licensed CC BY 2.5 AU. |

## Tools

- [Vega-Lite v5](https://vega.github.io/vega-lite/) — all chart specifications
- [vega-embed v6](https://vega.github.io/vega-embed/) — chart rendering
- [React 19](https://react.dev/) + [Vite 8](https://vitejs.dev/) — build tooling
- [Pure.css](https://purecss.io/) — responsive grid layout
- Python (pandas) — data aggregation scripts

## Project Structure

```
index.html          # Full page: layout, narrative text, CSS, vegaEmbed calls
public/
  specs/            # Vega-Lite JSON specs (one file per chart)
  data/             # Pre-aggregated JSON data files
Dataset/            # Raw CSV files (not committed — too large)
src/                # React entry point (App.jsx renders null; page is static HTML)
process_data.py     # Regenerates public/data/*.json from raw CSVs
write_specs.py      # Regenerates specs for charts 1–10
write_specs2.py     # Regenerates specs for charts 11–17
```

## Development

```bash
npm install
npm run dev       # dev server at http://localhost:5173/Data-visualisation2/
npm run build     # production build → dist/
npm run preview   # preview dist/ locally
npm run lint      # ESLint
```

Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds and deploys `dist/` to GitHub Pages automatically.

## Author

**Zhongfan Dong** — FIT2179 Data Visualisation 2, Monash University, May 2026
