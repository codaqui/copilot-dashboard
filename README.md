# GitHub Copilot Analytics

Collect, process and visualize GitHub Copilot usage metrics for one or more GitHub organizations. Everything runs locally: a shell script downloads the metrics, a Python script consolidates them into a single Parquet file, and a Streamlit dashboard renders the charts.

> **⚠️ API status (April 2026):** `collect_metrics.sh` calls the legacy endpoint `GET /orgs/{org}/copilot/metrics`, which GitHub [closed down on April 2, 2026](https://github.blog/changelog/2026-01-29-closing-down-notice-of-legacy-copilot-metrics-apis/). Collecting new data from the live API fails until the script is migrated to the [Copilot usage metrics endpoints](https://docs.github.com/en/rest/copilot/copilot-usage-metrics). Processing and the dashboard keep working with JSON files collected earlier and with the example data shipped in this repository.

## How it works

```
collect_metrics.sh ──▶ data/year=YYYY/month=MM/DD-<org>.json ──▶ main.py ──▶ data.parquet ──▶ dashboard.py
```

| Step | File | What it does |
|------|------|--------------|
| 1. Collect | `collect_metrics.sh` | Downloads the daily metrics of an organization and saves one JSON file per day. |
| 2. Process | `main.py` | Reads every JSON file and writes a single consolidated `data.parquet`. |
| 3. Visualize | `dashboard.py` | Streamlit app that loads a `.parquet` file and renders the charts. |

Steps 2 and 3 are the ones you will usually touch when developing. Step 1 rarely needs changes and requires API access, so the repository ships example data to let you work without it.

## Requirements

- Python 3.13 (pinned in `.python-version`) and the packages in `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```
- Only for collecting data: [GitHub CLI](https://cli.github.com/) authenticated with `gh auth login`, plus `curl`, `jq` and GNU `date` (the script runs on Linux; on macOS it needs GNU coreutils).

## Try it locally with the example data

`data_example/` contains 82 days of real metrics of the `codaqui` organization (2025-05-01 to 2025-07-21), already in the layout produced by the collector. `output_example/data.parquet` is the result of processing them.

Run the processing step against the example data:

```bash
python main.py --data-dir ./data_example --output-dir output_example
```

Expected output (abridged):

```
✅ Loaded 82 data files
📊 Processed 82 records
💾 Saved consolidated Parquet file: output_example/data.parquet
📈 Data Summary:
Total records: 82
Date range: 2025-05-01 00:00:00 to 2025-07-21 00:00:00
Organizations (1): codaqui
```

`output_example/data.parquet` is tracked in git and the run rewrites it. The content stays the same, but the bytes change with the pandas/pyarrow version, so `git status` will show it as modified. Restore it with `git checkout -- output_example/data.parquet` unless you intend to update the example.

To open the dashboard with the example data, write the Parquet file to the current directory and start Streamlit:

```bash
python main.py --data-dir ./data_example --output-dir .
streamlit run dashboard.py
```

Alternatively, start `streamlit run dashboard.py` and upload `output_example/data.parquet` through the sidebar.

## Using your own data

### 1. Collect metrics

```bash
./collect_metrics.sh --org <organization> [--data-dir ./data]
```

- Uses the token from `gh auth token`; your account needs permission to read Copilot metrics for the organization, and the organization must have the Copilot metrics policy enabled.
- Saves one file per day as `data/year=YYYY/month=MM/DD-<organization>.json`, adding `organization` and `download_timestamp` to each record. Running again overwrites the files of the days returned by the API.
- Writes a temporary `raw_response_*.json` and deletes it once every record has been saved.
- For several organizations, run the script once per organization. The organization name in the file name keeps them apart.

See the API status note at the top: this step does not work against the live API until the script is migrated.

### 2. Process into Parquet

```bash
python main.py [--data-dir ./data] [--output-dir .]
```

- Reads every `year=*/month=*/*.json` under `--data-dir`. If a record has no `organization` field, it is taken from the file name (`DD-<org>.json`).
- Parses `date` and `download_timestamp`, sorts by date and writes a single `data.parquet` to `--output-dir` (one row per organization per day; the nested metrics are kept as nested columns).
- Prints a per-organization summary.

### 3. Run the dashboard

```bash
streamlit run dashboard.py
```

The dashboard picks its data in this order:

1. A `.parquet` file uploaded through the sidebar.
2. A `data.parquet` file in the current working directory.
3. Otherwise it shows a welcome screen with the setup instructions.

Sidebar filters: date range and, when the file contains more than one organization, an organization selector. Sections: Overview, Usage Trends, Programming Languages, Editor Usage, Chat Interactions, GitHub.com Usage and Data Insights.

## Data layout

```
data/
└── year=2025/
    ├── month=05/
    │   ├── 01-codaqui.json
    │   ├── 02-codaqui.json
    │   └── ...
    └── month=06/
        └── ...
data.parquet
```

Each JSON file is one day of the API response. `data.parquet` has these columns:

| Column | Content |
|--------|---------|
| `date` | Day of the metrics |
| `organization` | GitHub organization |
| `total_active_users`, `total_engaged_users` | Daily totals |
| `copilot_ide_code_completions` | Completions by editor, model and language |
| `copilot_ide_chat` | IDE chat usage by editor and model |
| `copilot_dotcom_chat` | GitHub.com chat usage |
| `copilot_dotcom_pull_requests` | Pull request summaries on GitHub.com |
| `download_timestamp` | When the record was collected |

## Deploying the dashboard

1. Fork this repository.
2. Create an app at [share.streamlit.io](https://share.streamlit.io) pointing to your fork with `dashboard.py` as the main file.

Without a `data.parquet` in the deployed repository, visitors see the welcome screen and upload their own file. The uploaded file is kept only in the memory of that browser session and is discarded when the session ends; nothing is written to disk.

Collected data must never be committed. `.gitignore` already excludes `data/`, `*.parquet`, `*.csv` and `raw_response_*.json`; the only tracked Parquet file is `output_example/data.parquet`.

## Troubleshooting

- **`Not Found` when collecting:** the legacy endpoint is closed (see the API status note). GitHub also answers 404 when the organization does not exist or your account cannot read its metrics.
- **`Skipping record ... with invalid date` for every record:** the script uses GNU `date -d`. Run it on Linux or with GNU coreutils on `PATH`.
- **`No data found to process`:** check that `--data-dir` contains the `year=YYYY/month=MM/*.json` layout.
- **The dashboard only shows the welcome screen:** no file was uploaded and there is no `data.parquet` in the directory where `streamlit run` was started.
- **`use_container_width` deprecation warnings** printed by recent Streamlit versions are harmless.

## Contributing

Open an issue or a pull request at [codaqui/copilot-dashboard](https://github.com/codaqui/copilot-dashboard). Use the example data to test changes to `main.py` and `dashboard.py` before submitting.

## License

MIT. See [LICENSE](LICENSE).
