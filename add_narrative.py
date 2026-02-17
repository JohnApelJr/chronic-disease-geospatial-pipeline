#!/usr/bin/env python3
"""
Inject narrative markdown cells into analysis.ipynb.
Run from the project root:
    python3 add_narrative.py
"""

import json

NOTEBOOK_PATH = "notebooks/analysis.ipynb"

# Each entry: (insert_before_cell_index, markdown_content)
# Indices refer to the ORIGINAL 0-based code cell positions.
# We insert in reverse order so indices don't shift.

NARRATIVE_CELLS = [
    (0, """# Chronic Disease Disparities & Healthcare Access: A Geospatial Analysis

**Author:** John Apel | M.S. Applied Data Science, Syracuse University

This notebook builds a reproducible ETL pipeline that integrates county-level health data from the **CDC PLACES** program with socioeconomic indicators from the **U.S. Census Bureau** to map the geographic intersection of chronic disease burden, healthcare access, and poverty across nearly 3,000 U.S. counties.

**Research Questions:**
1. Where do chronic disease, lack of healthcare access, and poverty converge geographically?
2. Which health and socioeconomic factors are most strongly correlated at the county level?
3. How do health outcomes in Western North Carolina compare to state and national averages — and how much do they vary within the region?

**Data Sources:**
- CDC PLACES (2024 release) — county-level health estimates from BRFSS
- U.S. Census Bureau American Community Survey (2022, 5-year estimates)
- Census TIGER/Line shapefiles for county boundary geometries"""),

    (1, """---
## Step 1: CDC PLACES Data Ingestion

The CDC's [PLACES](https://www.cdc.gov/places/) program provides model-based estimates for 40 health measures at the county, place, census tract, and ZIP code levels. We'll pull data via the Socrata REST API on `data.cdc.gov`.

We start by fetching three core chronic disease measures: **diabetes prevalence**, **obesity prevalence**, and **coronary heart disease (CHD)** prevalence among adults."""),

    (3, """### Discovering Available Measures

Before filtering, we need to understand the dataset structure — what columns exist, what measures are available, and how records are organized. This discovery step prevents assumptions about field names that could cause errors downstream."""),

    (5, """### Fetching Target Disease Measures

We pull three disease indicators and immediately filter to the **latest year** and **age-adjusted prevalence** estimates. Age-adjusted rates are preferred for geographic comparisons because they remove the confounding effect of different age distributions across counties — a county with an older population would otherwise appear to have higher disease rates even if the underlying risk is the same."""),

    (7, """### Cleaning and Standardization

This step converts raw API responses into an analysis-ready format: renaming columns for clarity, casting data types, constructing 5-digit FIPS county codes (the standard geographic identifier used across federal datasets), and dropping records with missing values. We also capture confidence intervals for potential use in downstream analysis."""),

    (8, """### Pivoting to Wide Format

We reshape from long format (one row per county per measure) to wide format (one row per county, one column per measure). This structure is essential for correlation analysis and for merging with other data sources. The pivot also serves as a validation step — if we get roughly 3,000 rows, we know we have one record per county as expected."""),

    (9, """### Validation

Before moving on, we verify the data makes sense: checking distributions, confirming value ranges are plausible (diabetes prevalence should be roughly 5-25%, not 50-90%), and looking at which counties rank highest. This quick sanity check catches data quality issues early."""),

    (11, """### Scatter Plot: Obesity vs. Diabetes

This initial visualization serves two purposes: it validates that the data shows expected epidemiological relationships (obesity and diabetes should be positively correlated), and it provides a baseline understanding of the strength of that relationship before we introduce additional variables."""),

    (12, """---
## Step 2: Healthcare Access & Socioeconomic Data

Disease prevalence alone doesn't tell the full story. To understand *why* some counties have higher chronic disease rates, we need to layer in data on healthcare access and economic conditions.

### Part A: Additional PLACES Health Measures

We return to the same CDC PLACES API to pull four additional measures that capture healthcare access and health behaviors:
- **ACCESS2** — % adults 18-64 without health insurance
- **LPA** — % adults with no leisure-time physical activity
- **CHECKUP** — % adults with a routine checkup in the past year
- **MHLTH** — % adults reporting poor mental health ≥14 days"""),

    (15, """### Part B: Census Bureau Socioeconomic Data

The U.S. Census Bureau's American Community Survey (ACS) provides socioeconomic indicators at the county level. We query the Census REST API for **median household income** and **poverty rate** — two measures widely used in health equity research as proxies for economic well-being.

The Census API is publicly accessible without authentication for basic queries, and returns data keyed by state + county FIPS codes, which we'll combine into 5-digit FIPS codes to match our CDC data."""),

    (17, """### Merging All Data Sources

This is the core integration step. We join CDC health data with Census socioeconomic data on 5-digit FIPS county codes using a left join — keeping all counties from our health dataset and attaching economic indicators where available. After this merge, each row represents one county with up to 9 measures spanning health outcomes, healthcare access, and economic status."""),

    (19, """### Correlation Analysis

With all variables in one dataset, we can now examine how health outcomes, healthcare access, and socioeconomic status relate to each other at the county level. The correlation matrix reveals which factors move together — and which relationships are strongest.

Key things to look for:
- Which health measure correlates most strongly with diabetes?
- Does poverty correlate more strongly with disease than lack of insurance?
- Are there any surprising weak correlations?"""),

    (21, """---
## Step 3: Geospatial Analysis & Mapping

Numbers in a table tell part of the story. Maps tell the rest — they reveal geographic clustering, regional patterns, and spatial relationships that aren't visible in summary statistics. 

We load county boundary shapefiles from the Census Bureau's TIGER/Line program and merge our health + socioeconomic data to create map-ready GeoDataFrames."""),

    (23, """### Choropleth Maps: Disease Prevalence

These maps visualize county-level prevalence using quantile classification (6 classes), which ensures each color bin contains roughly the same number of counties. This approach highlights relative differences across the full distribution rather than being skewed by outliers."""),

    (26, """### Triple Burden Analysis

This is the central analytical contribution of the project. We identify counties that rank in the **top quartile (75th percentile) nationally** on three dimensions simultaneously:

1. **High diabetes prevalence** — disease burden
2. **High uninsured rate** — healthcare access barrier
3. **High poverty rate** — economic vulnerability

Counties meeting all three criteria represent places where health need is greatest and capacity to address it is most constrained. These are the communities where targeted public health investment could have the highest impact."""),

    (28, """### Interactive Map

Static maps are useful for presentations and reports, but interactive maps allow stakeholders to explore the data themselves. This Folium map renders all ~3,000 counties as a choropleth with hover tooltips showing every measure for each county.

The resulting HTML file can be shared as a standalone webpage — no server required."""),

    (30, """---
## Step 4: Western North Carolina — Regional Deep Dive

National-level analysis identifies broad patterns, but public health decisions are made at the regional and local level. This section zooms into **Western North Carolina (WNC)** — 18 counties in the Appalachian mountain region — to examine how health outcomes and socioeconomic conditions vary within a single region.

WNC presents an interesting case study: it includes Asheville (Buncombe County), a mid-sized city with a health-conscious culture and relatively strong healthcare infrastructure, surrounded by rural mountain counties with very different demographic and economic profiles. This urban-rural contrast within a compact geography is exactly the kind of disparity that gets lost in state-level statistics."""),

    (31, """### Regional Comparison: WNC vs. North Carolina vs. National

We aggregate all measures to three geographic levels — WNC counties, all North Carolina counties, and all U.S. counties — to see where the region stands relative to state and national benchmarks."""),

    (34, """### County-Level Heatmap

The heatmap shows every WNC county across every measure, with colors normalized to the full national range (0 = best nationally, 1 = worst nationally). This makes it easy to spot which counties face the greatest challenges and on which specific measures — the kind of actionable detail that drives resource allocation decisions."""),

    (35, """### WNC Regional Map

A zoomed choropleth focusing specifically on WNC counties, colored by diabetes prevalence. This visualization demonstrates the ability to move between national-scale and regional-scale analysis within the same pipeline."""),

    (36, """### Key Findings Summary

A structured comparison of WNC against state and national benchmarks, with directional indicators (▲/▼) showing where the region performs above or below the national average. We also identify the highest-need counties within WNC — those exceeding state averages on both diabetes and poverty."""),
]

# Load notebook
with open(NOTEBOOK_PATH, 'r') as f:
    nb = json.load(f)

cells = nb['cells']

def make_md_cell(source_text):
    """Create a properly formatted Jupyter markdown cell."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source_text.strip().split("\n")]
    }

# Insert in reverse order so indices remain valid
for idx, content in sorted(NARRATIVE_CELLS, key=lambda x: x[0], reverse=True):
    md_cell = make_md_cell(content)
    cells.insert(idx, md_cell)

nb['cells'] = cells

# Save
with open(NOTEBOOK_PATH, 'w') as f:
    json.dump(nb, f, indent=1)

code_count = sum(1 for c in nb['cells'] if c['cell_type'] == 'code')
md_count = sum(1 for c in nb['cells'] if c['cell_type'] == 'markdown')
print(f"✅ Narrative injected into {NOTEBOOK_PATH}")
print(f"   Code cells: {code_count}")
print(f"   Markdown cells: {md_count}")
print(f"   Total cells: {len(nb['cells'])}")