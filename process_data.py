"""
Data processing script for FIT2179 Data Visualisation 2 assignment.
Generates small JSON files from the raw CSVs for use in Vega-Lite specs.
"""

import csv
import json
import re
import math
from collections import defaultdict
from pathlib import Path

OUT = Path(r"D:\Data visualisation\Data visualisation2\public\data")
OUT.mkdir(parents=True, exist_ok=True)

MBA_PATH = r"D:\Data visualisation\Data visualisation2\Dataset\mba-report-28-data-release-march-2025.csv"
OOKLA_PATH = r"D:\Data visualisation\Data visualisation2\Dataset\ookla-performance-australia-fixed-2021-q3-na.csv"

# ── helpers ──────────────────────────────────────────────────────────────────

def safe_float(v, default=None):
    try:
        f = float(v)
        return f if math.isfinite(f) else default
    except (TypeError, ValueError):
        return default

def round2(v):
    return round(v, 2) if v is not None else None

def geom_centroid(geom_str):
    nums = re.findall(r"-?\d+\.?\d*", geom_str)
    nums = [float(n) for n in nums]
    lats = nums[0::2]
    lons = nums[1::2]
    return sum(lats) / len(lats), sum(lons) / len(lons)

def assign_state(lat, lon):
    if lat < -39.5:
        return "TAS"
    if lon < 129.0:
        return "WA"
    if -35.95 < lat < -35.05 and 148.75 < lon < 149.45:
        return "ACT"
    if lon < 138.0 and lat > -26.0:
        return "NT"
    if lon < 141.0:
        return "SA"
    if lat > -28.9 and lon >= 138.0:
        return "QLD"
    if lat < -34.1 and lon < 149.6:
        return "VIC"
    if lat < -37.5:
        return "VIC"
    return "NSW"

def tier_mbps(tier_str):
    m = re.match(r"(\d+)", tier_str)
    return int(m.group(1)) if m else None

# ── Read MBA data ─────────────────────────────────────────────────────────────

print("Reading MBA data...")
mba_rows = []
with open(MBA_PATH, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        mba_rows.append(row)

print(f"  {len(mba_rows)} MBA rows")

# ── 1. mba-state.json  — busy hour speed by state × geography ────────────────
# For chart 3: grouped bar — busy hour download speed by state

print("Generating mba-state.json...")

geo_keep = {"Urban", "Minor Rural", "Major Rural", "Rural", "Remote", "Isolated"}
# We'll collapse to 3 categories for cleaner chart
geo_remap = {"Urban": "Urban", "Minor Rural": "Rural", "Major Rural": "Rural",
             "Rural": "Rural", "Remote": "Rural", "Isolated": "Rural"}

state_geo = defaultdict(list)
for row in mba_rows:
    state = row["state_or_territory"].strip()
    geo = row["geography"].strip()
    speed = safe_float(row["Busy hour trimmed mean download speed"])
    if not state or not geo or speed is None or state == "NT + SA":
        continue
    geo2 = geo_remap.get(geo, None)
    if geo2:
        state_geo[(state, geo2)].append(speed)

mba_state = []
for (state, geo), speeds in state_geo.items():
    mba_state.append({
        "state": state,
        "geography": geo,
        "speed": round2(sum(speeds) / len(speeds)),
        "n": len(speeds)
    })

mba_state.sort(key=lambda x: (x["state"], x["geography"]))
with open(OUT / "mba-state.json", "w") as f:
    json.dump(mba_state, f)
print(f"  {len(mba_state)} records")

# ── 2. mba-geography.json  — speed by geography × technology ─────────────────
# For chart 4: grouped bar — Urban vs Minor Rural vs Rural by technology

print("Generating mba-geography.json...")

geo_tech = defaultdict(list)
for row in mba_rows:
    geo = row["geography"].strip()
    tech = row["technology"].strip()
    speed = safe_float(row["Busy hour trimmed mean download speed"])
    if not geo or not tech or speed is None:
        continue
    geo2 = geo_remap.get(geo, None)
    if geo2:
        geo_tech[(geo2, tech)].append(speed)

mba_geo = []
for (geo, tech), speeds in geo_tech.items():
    mba_geo.append({
        "geography": geo,
        "technology": tech,
        "speed": round2(sum(speeds) / len(speeds)),
        "n": len(speeds)
    })

mba_geo.sort(key=lambda x: (x["geography"], x["technology"]))
with open(OUT / "mba-geography.json", "w") as f:
    json.dump(mba_geo, f)
print(f"  {len(mba_geo)} records")

# ── 3. mba-tech.json  — technology type distribution ─────────────────────────
# For chart 5: donut chart

print("Generating mba-tech.json...")

tech_counts = defaultdict(int)
for row in mba_rows:
    tech = row["technology"].strip()
    if tech:
        tech_counts[tech] += 1

mba_tech = [{"technology": k, "count": v} for k, v in sorted(tech_counts.items(), key=lambda x: -x[1])]
with open(OUT / "mba-tech.json", "w") as f:
    json.dump(mba_tech, f)
print(f"  {len(mba_tech)} technology types")

# ── 4. mba-boxplot.json  — speed by technology (individual records) ───────────
# For chart 6: box plot

print("Generating mba-boxplot.json...")

mba_box = []
for row in mba_rows:
    tech = row["technology"].strip()
    speed = safe_float(row["Busy hour trimmed mean download speed"])
    if tech and speed is not None and speed > 0:
        mba_box.append({"technology": tech, "speed": round2(speed)})

with open(OUT / "mba-boxplot.json", "w") as f:
    json.dump(mba_box, f)
print(f"  {len(mba_box)} records")

# ── 5. mba-scatter.json  — tier vs actual speed by technology ─────────────────
# For chart 7: scatter plot

print("Generating mba-scatter.json...")

mba_scatter = []
for row in mba_rows:
    tech = row["technology"].strip()
    tier = row["tier"].strip()
    actual = safe_float(row["Busy hour trimmed mean download speed"])
    t_mbps = tier_mbps(tier) if tier else None
    if tech and t_mbps and actual is not None and actual > 0:
        mba_scatter.append({
            "technology": tech,
            "tier_mbps": t_mbps,
            "actual_mbps": round2(actual),
            "tier_label": tier,
            "underperforming": row["is_this_service_underperforming"].strip()
        })

with open(OUT / "mba-scatter.json", "w") as f:
    json.dump(mba_scatter, f)
print(f"  {len(mba_scatter)} records")

# ── 6. mba-rsp-tech.json  — technology mix by RSP ────────────────────────────
# For chart 8: stacked bar

print("Generating mba-rsp-tech.json...")

rsp_tech = defaultdict(lambda: defaultdict(int))
for row in mba_rows:
    rsp = row["rsp"].strip()
    tech = row["technology"].strip()
    if rsp and tech and rsp != "Other RSPs":
        rsp_tech[rsp][tech] += 1

# Keep RSPs with enough data
rsp_total = {rsp: sum(techs.values()) for rsp, techs in rsp_tech.items()}
top_rsps = sorted(rsp_total, key=lambda x: -rsp_total[x])[:12]

mba_rsp = []
for rsp in top_rsps:
    for tech, count in rsp_tech[rsp].items():
        mba_rsp.append({"rsp": rsp, "technology": tech, "count": count})

with open(OUT / "mba-rsp-tech.json", "w") as f:
    json.dump(mba_rsp, f)
print(f"  {len(mba_rsp)} records ({len(top_rsps)} RSPs)")

# ── 7. mba-underperform.json  — % underperforming by technology ───────────────
# For chart 9: bar chart

print("Generating mba-underperform.json...")

tech_under = defaultdict(lambda: {"total": 0, "under": 0})
for row in mba_rows:
    tech = row["technology"].strip()
    under = row["is_this_service_underperforming"].strip()
    if tech:
        tech_under[tech]["total"] += 1
        if under == "TRUE":
            tech_under[tech]["under"] += 1

mba_under = []
for tech, counts in tech_under.items():
    pct = round2(100.0 * counts["under"] / counts["total"]) if counts["total"] else 0
    mba_under.append({
        "technology": tech,
        "pct_underperforming": pct,
        "total": counts["total"],
        "underperforming": counts["under"]
    })
mba_under.sort(key=lambda x: -x["pct_underperforming"])

with open(OUT / "mba-underperform.json", "w") as f:
    json.dump(mba_under, f)
print(f"  {len(mba_under)} records")

# ── 8. mba-comparison.json  — MBA state averages for comparison chart ──────────
# For chart 10: side-by-side with Ookla

print("Generating MBA state averages for comparison...")

state_speeds_mba = defaultdict(list)
for row in mba_rows:
    state = row["state_or_territory"].strip()
    speed = safe_float(row["Busy hour trimmed mean download speed"])
    if state and speed is not None and state != "NT + SA":
        state_speeds_mba[state].append(speed)

mba_state_avg = {s: round2(sum(v) / len(v)) for s, v in state_speeds_mba.items()}
print(f"  MBA state averages: {mba_state_avg}")

# ── 9. Process Ookla data ─────────────────────────────────────────────────────

print("Reading Ookla data (this may take a moment)...")

ookla_rows = []
with open(OOKLA_PATH, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ookla_rows.append(row)

print(f"  {len(ookla_rows)} Ookla rows")

# Extract centroids and assign states
print("Assigning states to Ookla tiles...")
state_speeds_ookla = defaultdict(list)
grid_cells = defaultdict(list)  # (lat_bin, lon_bin) -> [speeds]

for row in ookla_rows:
    speed_kbps = safe_float(row["avg_d_kbps"])
    if speed_kbps is None or speed_kbps <= 0:
        continue
    geom = row["geom"]
    if not geom:
        continue
    try:
        lat, lon = geom_centroid(geom)
    except Exception:
        continue

    state = assign_state(lat, lon)
    speed_mbps = speed_kbps / 1000.0
    state_speeds_ookla[state].append(speed_mbps)

    # Grid: 0.5° cells
    lat_bin = round(lat * 2) / 2  # nearest 0.5°
    lon_bin = round(lon * 2) / 2
    grid_cells[(lat_bin, lon_bin)].append(speed_mbps)

print(f"  States found: {sorted(state_speeds_ookla.keys())}")
ookla_state_avg = {s: round2(sum(v) / len(v)) for s, v in state_speeds_ookla.items()}
print(f"  Ookla state averages: {ookla_state_avg}")

# ── 10. ookla-state.json ──────────────────────────────────────────────────────

print("Generating ookla-state.json...")

STATE_NAMES = {
    "NSW": "New South Wales", "VIC": "Victoria", "QLD": "Queensland",
    "SA": "South Australia", "WA": "Western Australia", "TAS": "Tasmania",
    "NT": "Northern Territory", "ACT": "Australian Capital Territory"
}

ookla_state = []
for state, avg in ookla_state_avg.items():
    ookla_state.append({
        "state": state,
        "state_name": STATE_NAMES.get(state, state),
        "avg_d_mbps": avg,
        "n": len(state_speeds_ookla[state])
    })
ookla_state.sort(key=lambda x: -x["avg_d_mbps"])

with open(OUT / "ookla-state.json", "w") as f:
    json.dump(ookla_state, f)
print(f"  {len(ookla_state)} states: {[(r['state'], r['avg_d_mbps']) for r in ookla_state]}")

# ── 11. ookla-grid.json ───────────────────────────────────────────────────────

print("Generating ookla-grid.json...")

ookla_grid = []
for (lat_bin, lon_bin), speeds in grid_cells.items():
    ookla_grid.append({
        "lat": lat_bin,
        "lon": lon_bin,
        "avg_d_mbps": round2(sum(speeds) / len(speeds)),
        "n": len(speeds)
    })

# Sort and filter to Australia bounds
ookla_grid = [g for g in ookla_grid if -44 <= g["lat"] <= -10 and 113 <= g["lon"] <= 154]
ookla_grid.sort(key=lambda x: (x["lat"], x["lon"]))

with open(OUT / "ookla-grid.json", "w") as f:
    json.dump(ookla_grid, f)

size_kb = (OUT / "ookla-grid.json").stat().st_size / 1024
print(f"  {len(ookla_grid)} grid cells, {size_kb:.0f} KB")

# ── 12. comparison.json  — 2021 Ookla vs 2025 MBA by state ───────────────────

print("Generating comparison.json...")

all_states = sorted(set(list(ookla_state_avg.keys()) + list(mba_state_avg.keys())))
comparison = []
for state in all_states:
    if state in ookla_state_avg:
        comparison.append({
            "state": state,
            "year": "2021 (Ookla)",
            "speed": ookla_state_avg[state],
            "source": "Ookla Speedtest"
        })
    if state in mba_state_avg:
        comparison.append({
            "state": state,
            "year": "2025 (ACCC MBA)",
            "speed": mba_state_avg[state],
            "source": "ACCC MBA Report 28"
        })

with open(OUT / "comparison.json", "w") as f:
    json.dump(comparison, f)
print(f"  {len(comparison)} records")

# ── Summary ───────────────────────────────────────────────────────────────────

print("\n=== Generated files ===")
for p in sorted(OUT.glob("*.json")):
    print(f"  {p.name}: {p.stat().st_size/1024:.1f} KB")
print("Done!")
