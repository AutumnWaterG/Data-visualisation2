"""Write all 10 Vega-Lite spec files for the FIT2179 assignment."""
import json
from pathlib import Path

SPECS = Path(r"D:\Data visualisation\Data visualisation2\public\specs")
SPECS.mkdir(exist_ok=True)

GEOJSON_URL = "https://raw.githubusercontent.com/rowanhogan/australian-states/master/states.min.geojson"

# Consistent technology color scale (domain + range)
TECH_DOMAIN = [
    "Fibre to the Premises",
    "Hybrid Fibre Coaxial",
    "Fibre to the Curb",
    "Fibre to the Node",
    "Fixed Wireless",
    "Satellite"
]
TECH_RANGE = ["#1565c0", "#1976d2", "#42a5f5", "#78909c", "#f57c00", "#bf360c"]

GEO_DOMAIN = ["Urban", "Minor Rural", "Rural"]
GEO_RANGE  = ["#1565c0", "#43a047", "#f57c00"]

YEAR_DOMAIN = ["2021 (Ookla)", "2025 (ACCC MBA)"]
YEAR_RANGE  = ["#f57c00", "#1565c0"]

# ?? Spec 1: Choropleth map ? Ookla 2021 avg speed by state ???????????????????
s1 = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Average fixed broadband download speed by Australian state, Ookla 2021 Q3.",
    "width": "container",
    "height": 380,
    "projection": {"type": "mercator"},
    "layer": [
        {
            "data": {
                "url": GEOJSON_URL,
                "format": {"type": "json", "property": "features"}
            },
            "transform": [
                {
                    "lookup": "properties.STATE_NAME",
                    "from": {
                        "data": {"url": "/data/ookla-state.json"},
                        "key": "state_name",
                        "fields": ["avg_d_mbps", "state"]
                    },
                    "default": None
                }
            ],
            "mark": {"type": "geoshape", "stroke": "white", "strokeWidth": 1.2},
            "encoding": {
                "color": {
                    "field": "avg_d_mbps",
                    "type": "quantitative",
                    "scale": {
                        "scheme": "blues",
                        "domain": [45, 65],
                        "nice": True
                    },
                    "legend": {
                        "title": "Avg Speed (Mbps)",
                        "orient": "bottom-right",
                        "gradientLength": 100
                    }
                },
                "tooltip": [
                    {"field": "properties.STATE_NAME", "type": "nominal", "title": "State"},
                    {"field": "avg_d_mbps", "type": "quantitative", "title": "Avg Download (Mbps)", "format": ".1f"},
                    {"field": "state", "type": "nominal", "title": "Abbrev."}
                ]
            }
        }
    ],
    "config": {"background": "transparent"}
}
json.dump(s1, open(SPECS / "choropleth-ookla.json", "w"), indent=2)
print("done")

# ?? Spec 2: Grid heatmap ? Ookla speed tiles over Australia ??????????????????
s2 = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Ookla 2021 Q3 fixed broadband speeds binned to 0.5? grid tiles.",
    "width": "container",
    "height": 380,
    "projection": {"type": "mercator"},
    "layer": [
        {
            "data": {
                "url": GEOJSON_URL,
                "format": {"type": "json", "property": "features"}
            },
            "mark": {
                "type": "geoshape",
                "fill": "#e9ecef",
                "stroke": "#adb5bd",
                "strokeWidth": 0.8
            }
        },
        {
            "data": {"url": "/data/ookla-grid.json"},
            "mark": {
                "type": "square",
                "size": 60,
                "opacity": 0.85
            },
            "encoding": {
                "longitude": {"field": "lon", "type": "quantitative"},
                "latitude":  {"field": "lat", "type": "quantitative"},
                "color": {
                    "field": "avg_d_mbps",
                    "type": "quantitative",
                    "scale": {
                        "type": "linear",
                        "domain": [0, 50, 150, 400],
                        "range": ["#bf360c", "#f57c00", "#1976d2", "#1565c0"]
                    },
                    "legend": {
                        "title": "Avg Speed (Mbps)",
                        "orient": "bottom-right",
                        "gradientLength": 110
                    }
                },
                "tooltip": [
                    {"field": "lat", "type": "quantitative", "title": "Latitude", "format": ".2f"},
                    {"field": "lon", "type": "quantitative", "title": "Longitude", "format": ".2f"},
                    {"field": "avg_d_mbps", "type": "quantitative", "title": "Avg Download (Mbps)", "format": ".1f"},
                    {"field": "n", "type": "quantitative", "title": "Tiles in cell"}
                ]
            }
        }
    ],
    "config": {"background": "transparent"}
}
json.dump(s2, open(SPECS / "grid-heatmap.json", "w"), indent=2)
print("done")

# ?? Spec 3: Grouped bar ? busy hour speed by state (MBA 2025) ????????????????
# National avg line annotation
s3 = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Busy hour trimmed mean download speed by state and geography type, MBA Report 28, 2025.",
    "width": "container",
    "height": 320,
    "data": {"url": "/data/mba-state.json"},
    "layer": [
        {
            "mark": {
                "type": "bar",
                "cornerRadiusTopLeft": 3,
                "cornerRadiusTopRight": 3
            },
            "encoding": {
                "x": {
                    "field": "state",
                    "type": "nominal",
                    "title": "State / Territory",
                    "sort": ["-y"],
                    "axis": {"labelAngle": 0}
                },
                "xOffset": {
                    "field": "geography",
                    "type": "nominal",
                    "scale": {"paddingInner": 0.1}
                },
                "y": {
                    "field": "speed",
                    "type": "quantitative",
                    "title": "Busy Hour Download Speed (Mbps)",
                    "scale": {"zero": True}
                },
                "color": {
                    "field": "geography",
                    "type": "nominal",
                    "scale": {"domain": GEO_DOMAIN, "range": GEO_RANGE},
                    "legend": {"title": "Geography", "orient": "top-right"}
                },
                "tooltip": [
                    {"field": "state", "type": "nominal", "title": "State"},
                    {"field": "geography", "type": "nominal", "title": "Geography"},
                    {"field": "speed", "type": "quantitative", "title": "Speed (Mbps)", "format": ".1f"},
                    {"field": "n", "type": "quantitative", "title": "Panel size"}
                ]
            }
        },
        {
            "mark": {
                "type": "rule",
                "color": "#333",
                "strokeDash": [6, 3],
                "strokeWidth": 1.5,
                "opacity": 0.7
            },
            "data": {
                "values": [{"national_avg": 232.0}]
            },
            "encoding": {
                "y": {"field": "national_avg", "type": "quantitative"}
            }
        },
        {
            "mark": {
                "type": "text",
                "align": "left",
                "dx": 4,
                "dy": -6,
                "color": "#333",
                "fontSize": 11,
                "fontStyle": "italic"
            },
            "data": {
                "values": [{"national_avg": 232.0, "label": "National avg ? 232 Mbps"}]
            },
            "encoding": {
                "x": {"value": 0},
                "y": {"field": "national_avg", "type": "quantitative"},
                "text": {"field": "label", "type": "nominal"}
            }
        }
    ],
    "config": {"background": "transparent", "view": {"stroke": "transparent"}}
}
json.dump(s3, open(SPECS / "bar-state-speed.json", "w"), indent=2)
print("done")

# ?? Spec 4: Grouped bar ? Urban vs Minor Rural vs Rural by technology ?????????
s4 = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Average busy hour download speed by geography and technology, MBA 2025.",
    "width": "container",
    "height": 320,
    "data": {"url": "/data/mba-geography.json"},
    "mark": {
        "type": "bar",
        "cornerRadiusTopLeft": 3,
        "cornerRadiusTopRight": 3
    },
    "encoding": {
        "x": {
            "field": "geography",
            "type": "nominal",
            "title": "Geography",
            "sort": ["Urban", "Minor Rural", "Rural"],
            "axis": {"labelAngle": 0}
        },
        "xOffset": {
            "field": "technology",
            "type": "nominal"
        },
        "y": {
            "field": "speed",
            "type": "quantitative",
            "title": "Avg Download Speed (Mbps)",
            "scale": {"zero": True}
        },
        "color": {
            "field": "technology",
            "type": "nominal",
            "scale": {"domain": TECH_DOMAIN, "range": TECH_RANGE},
            "legend": {"title": "Technology", "orient": "top-right"}
        },
        "tooltip": [
            {"field": "geography", "type": "nominal", "title": "Geography"},
            {"field": "technology", "type": "nominal", "title": "Technology"},
            {"field": "speed", "type": "quantitative", "title": "Speed (Mbps)", "format": ".1f"},
            {"field": "n", "type": "quantitative", "title": "Panel size"}
        ]
    },
    "config": {"background": "transparent", "view": {"stroke": "transparent"}}
}
json.dump(s4, open(SPECS / "bar-geography-speed.json", "w"), indent=2)
print("done")

# ?? Spec 5: Donut chart ? technology type distribution ????????????????????????
s5 = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Distribution of NBN technology types in the ACCC MBA panel, 2025.",
    "width": 340,
    "height": 280,
    "data": {"url": "/data/mba-tech.json"},
    "mark": {
        "type": "arc",
        "innerRadius": 70,
        "outerRadius": 120,
        "stroke": "white",
        "strokeWidth": 2
    },
    "encoding": {
        "theta": {
            "field": "count",
            "type": "quantitative",
            "stack": True
        },
        "color": {
            "field": "technology",
            "type": "nominal",
            "scale": {"domain": TECH_DOMAIN, "range": TECH_RANGE},
            "legend": {
                "title": "Technology",
                "orient": "right",
                "labelFontSize": 11
            }
        },
        "order": {"field": "count", "type": "quantitative", "sort": "descending"},
        "tooltip": [
            {"field": "technology", "type": "nominal", "title": "Technology"},
            {"field": "count", "type": "quantitative", "title": "Panel count"},
            {
                "field": "count",
                "type": "quantitative",
                "title": "Share",
                "format": ".0f"
            }
        ]
    },
    "config": {"background": "transparent", "view": {"stroke": "transparent"}}
}
json.dump(s5, open(SPECS / "donut-tech.json", "w"), indent=2)
print("done")

# ?? Spec 6: Box plot ? speed by technology ????????????????????????????????????
s6 = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Distribution of busy hour download speeds by technology, MBA Report 28.",
    "width": "container",
    "height": 320,
    "data": {"url": "/data/mba-boxplot.json"},
    "mark": {
        "type": "boxplot",
        "extent": 1.5,
        "outliers": {"size": 20, "opacity": 0.3},
        "median": {"color": "white", "strokeWidth": 2},
        "box": {"size": 40}
    },
    "encoding": {
        "x": {
            "field": "technology",
            "type": "nominal",
            "title": "Technology",
            "sort": {"field": "speed", "op": "median", "order": "descending"},
            "axis": {"labelAngle": -20, "labelLimit": 140}
        },
        "y": {
            "field": "speed",
            "type": "quantitative",
            "title": "Busy Hour Download Speed (Mbps)",
            "scale": {"zero": True}
        },
        "color": {
            "field": "technology",
            "type": "nominal",
            "scale": {"domain": TECH_DOMAIN, "range": TECH_RANGE},
            "legend": None
        },
        "tooltip": [
            {"field": "technology", "type": "nominal", "title": "Technology"},
            {"field": "speed", "type": "quantitative", "title": "Speed (Mbps)", "format": ".1f"}
        ]
    },
    "config": {"background": "transparent", "view": {"stroke": "transparent"}}
}
json.dump(s6, open(SPECS / "boxplot-tech.json", "w"), indent=2)
print("done")

# ?? Spec 7: Scatter ? advertised tier vs actual busy hour speed ???????????????
s7 = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Advertised tier speed vs actual busy hour speed, coloured by technology, MBA 2025.",
    "width": "container",
    "height": 380,
    "layer": [
        {
            "data": {
                "values": [
                    {"x": 0, "y": 0},
                    {"x": 1100, "y": 1100}
                ]
            },
            "mark": {
                "type": "line",
                "color": "#999",
                "strokeDash": [6, 4],
                "strokeWidth": 1.5,
                "opacity": 0.7
            },
            "encoding": {
                "x": {"field": "x", "type": "quantitative"},
                "y": {"field": "y", "type": "quantitative"}
            }
        },
        {
            "data": {
                "values": [{"x": 900, "y": 950, "label": "Perfect delivery (y = x)"}]
            },
            "mark": {
                "type": "text",
                "angle": 38,
                "fontSize": 10,
                "color": "#888",
                "fontStyle": "italic"
            },
            "encoding": {
                "x": {"field": "x", "type": "quantitative"},
                "y": {"field": "y", "type": "quantitative"},
                "text": {"field": "label"}
            }
        },
        {
            "data": {"url": "/data/mba-scatter.json"},
            "mark": {
                "type": "point",
                "opacity": 0.35,
                "size": 40,
                "filled": True
            },
            "encoding": {
                "x": {
                    "field": "tier_mbps",
                    "type": "quantitative",
                    "title": "Advertised Tier Speed (Mbps)",
                    "scale": {"type": "log", "base": 10, "nice": True}
                },
                "y": {
                    "field": "actual_mbps",
                    "type": "quantitative",
                    "title": "Actual Busy Hour Speed (Mbps)",
                    "scale": {"type": "log", "base": 10, "nice": True}
                },
                "color": {
                    "field": "technology",
                    "type": "nominal",
                    "scale": {"domain": TECH_DOMAIN, "range": TECH_RANGE},
                    "legend": {"title": "Technology", "orient": "bottom-right"}
                },
                "tooltip": [
                    {"field": "technology", "type": "nominal", "title": "Technology"},
                    {"field": "tier_label", "type": "nominal", "title": "Plan tier"},
                    {"field": "tier_mbps", "type": "quantitative", "title": "Advertised (Mbps)"},
                    {"field": "actual_mbps", "type": "quantitative", "title": "Actual (Mbps)", "format": ".1f"},
                    {"field": "underperforming", "type": "nominal", "title": "Underperforming?"}
                ]
            }
        }
    ],
    "resolve": {"scale": {"x": "shared", "y": "shared"}},
    "config": {"background": "transparent", "view": {"stroke": "transparent"}}
}
json.dump(s7, open(SPECS / "scatter-tier-actual.json", "w"), indent=2)
print("done")

# ?? Spec 8: Stacked bar ? technology mix by RSP ???????????????????????????????
s8 = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Technology type mix per internet service provider, MBA Report 28.",
    "width": "container",
    "height": 320,
    "data": {"url": "/data/mba-rsp-tech.json"},
    "mark": {
        "type": "bar"
    },
    "encoding": {
        "x": {
            "field": "rsp",
            "type": "nominal",
            "title": "Internet Service Provider",
            "sort": {
                "field": "count",
                "op": "sum",
                "order": "descending"
            },
            "axis": {"labelAngle": -30, "labelLimit": 120}
        },
        "y": {
            "field": "count",
            "type": "quantitative",
            "title": "Number of Panel Services",
            "stack": "normalize",
            "axis": {"format": "%", "title": "Share of services (%)"}
        },
        "color": {
            "field": "technology",
            "type": "nominal",
            "scale": {"domain": TECH_DOMAIN, "range": TECH_RANGE},
            "legend": {"title": "Technology", "orient": "top-right"}
        },
        "tooltip": [
            {"field": "rsp", "type": "nominal", "title": "Provider"},
            {"field": "technology", "type": "nominal", "title": "Technology"},
            {"field": "count", "type": "quantitative", "title": "Services"}
        ]
    },
    "config": {"background": "transparent", "view": {"stroke": "transparent"}}
}
json.dump(s8, open(SPECS / "stacked-rsp-tech.json", "w"), indent=2)
print("done")

# ?? Spec 9: Bar ? % underperforming by technology ????????????????????????????
s9 = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Percentage of services classified as underperforming by technology type, MBA Report 28.",
    "width": "container",
    "height": 300,
    "data": {"url": "/data/mba-underperform.json"},
    "layer": [
        {
            "mark": {
                "type": "bar",
                "cornerRadiusTopLeft": 4,
                "cornerRadiusTopRight": 4
            },
            "encoding": {
                "x": {
                    "field": "technology",
                    "type": "nominal",
                    "title": "Technology",
                    "sort": "-y",
                    "axis": {"labelAngle": -20, "labelLimit": 140}
                },
                "y": {
                    "field": "pct_underperforming",
                    "type": "quantitative",
                    "title": "Underperforming Services (%)",
                    "scale": {"zero": True, "domain": [0, 100]}
                },
                "color": {
                    "field": "pct_underperforming",
                    "type": "quantitative",
                    "scale": {
                        "domain": [0, 20, 50, 100],
                        "range": ["#1565c0", "#f57c00", "#e53935", "#b71c1c"]
                    },
                    "legend": None
                },
                "tooltip": [
                    {"field": "technology", "type": "nominal", "title": "Technology"},
                    {"field": "pct_underperforming", "type": "quantitative", "title": "Underperforming (%)", "format": ".1f"},
                    {"field": "underperforming", "type": "quantitative", "title": "Count"},
                    {"field": "total", "type": "quantitative", "title": "Panel total"}
                ]
            }
        },
        {
            "mark": {
                "type": "text",
                "align": "center",
                "baseline": "bottom",
                "dy": -4,
                "fontSize": 12,
                "fontWeight": "bold"
            },
            "encoding": {
                "x": {
                    "field": "technology",
                    "type": "nominal",
                    "sort": "-y"
                },
                "y": {
                    "field": "pct_underperforming",
                    "type": "quantitative"
                },
                "text": {
                    "field": "pct_underperforming",
                    "type": "quantitative",
                    "format": ".0f"
                },
                "color": {
                    "condition": {
                        "test": "datum.pct_underperforming > 40",
                        "value": "#b71c1c"
                    },
                    "value": "#333"
                }
            }
        }
    ],
    "config": {"background": "transparent", "view": {"stroke": "transparent"}}
}
json.dump(s9, open(SPECS / "bar-underperform.json", "w"), indent=2)
print("done")

# ?? Spec 10: Side-by-side bar ? 2021 Ookla vs 2025 MBA by state ??????????????
s10 = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Average download speed by state: 2021 Ookla vs 2025 ACCC MBA comparison.",
    "width": "container",
    "height": 320,
    "data": {"url": "/data/comparison.json"},
    "layer": [
        {
            "mark": {
                "type": "bar",
                "cornerRadiusTopLeft": 3,
                "cornerRadiusTopRight": 3
            },
            "encoding": {
                "x": {
                    "field": "state",
                    "type": "nominal",
                    "title": "State / Territory",
                    "sort": ["ACT", "NSW", "QLD", "TAS", "VIC", "WA", "NT", "SA"],
                    "axis": {"labelAngle": 0}
                },
                "xOffset": {
                    "field": "year",
                    "type": "nominal",
                    "sort": YEAR_DOMAIN
                },
                "y": {
                    "field": "speed",
                    "type": "quantitative",
                    "title": "Average Download Speed (Mbps)",
                    "scale": {"zero": True}
                },
                "color": {
                    "field": "year",
                    "type": "nominal",
                    "scale": {"domain": YEAR_DOMAIN, "range": YEAR_RANGE},
                    "legend": {"title": "Dataset", "orient": "top-right"}
                },
                "tooltip": [
                    {"field": "state", "type": "nominal", "title": "State"},
                    {"field": "year", "type": "nominal", "title": "Dataset"},
                    {"field": "speed", "type": "quantitative", "title": "Avg Speed (Mbps)", "format": ".1f"},
                    {"field": "source", "type": "nominal", "title": "Source"}
                ]
            }
        }
    ],
    "config": {"background": "transparent", "view": {"stroke": "transparent"}}
}
json.dump(s10, open(SPECS / "comparison-state.json", "w"), indent=2)
print("done")

print("\nAll 10 specs written.")
