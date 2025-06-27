sh# GitHub Copilot Analytics

An open-source tool to collect, process, and visualize GitHub Copilot usage data for any organization. Features a web-based dashboard for interactive analytics and supports data privacy by keeping all data local.

## 🌟 Features

- **🔒 Privacy-First**: All data stays local - no cloud dependencies
- **📊 Interactive Dashboard**: Beautiful Streamlit web interface
- **🔄 Multi-Organization**: Collect data from multiple GitHub organizations
- **📈 Rich Analytics**: Usage trends, language breakdowns, editor statistics
- **🚀 Easy Deployment**: Deploy dashboard to Streamlit Community Cloud
- **🛡️ Secure**: Uses GitHub CLI authentication - no token management

## 🛠️ Components Overview

This project consists of three main components that work together in sequence:

### 1. `collect_metrics.sh` (Data Collection)
- **Purpose**: Bash script that collects GitHub Copilot usage metrics
- **What it does**: Uses GitHub CLI to fetch raw metrics data from GitHub's API
- **Output**: Organizes JSON files in `data/year=YYYY/month=MM/DD-org.json` structure
- **Usage**: `./collect_metrics.sh --org <organization>`

### 2. `main.py` (Data Processing) 
- **Purpose**: Python script that processes collected JSON data
- **What it does**: Converts JSON files into a consolidated Parquet file for analysis
- **Output**: Generates `data.parquet` file ready for visualization
- **Usage**: `python main.py`

### 3. `dashboard.py` (Data Visualization)
- **Purpose**: Streamlit web application for interactive analytics
- **What it does**: Generates charts, graphs and insights from the processed data
- **Output**: Interactive web dashboard with multiple visualizations
- **Usage**: `streamlit run dashboard.py`

## 📋 Prerequisites

- **GitHub CLI (gh)**: Must be installed and authenticated
- **Python 3.8+**: For data processing and dashboard
- **jq**: For JSON processing in the bash script

### Installing Prerequisites

```bash
# Install GitHub CLI (if not already installed)
# On macOS
brew install gh

# On Ubuntu/Debian
sudo apt update && sudo apt install gh

# On other systems, see: https://cli.github.com/

# Install jq (if not already installed)
# On macOS
brew install jq

# On Ubuntu/Debian
sudo apt install jq

# Authenticate with GitHub CLI
gh auth login

# Install Python dependencies
pip install -r requirements.txt
```

## 🚀 Quick Start

### Step 1: Collect Metrics Data
```bash
# Collect metrics for your organization
./collect_metrics.sh --org your-organization-name

# Optional: specify custom data directory
./collect_metrics.sh --org your-org --data-dir ./custom-data-dir
```

**Requirements:**
- You must be authenticated with GitHub CLI (`gh auth login`)
- Your account needs appropriate permissions to read Copilot metrics for the organization
- The organization must have GitHub Copilot enabled

### Step 2: Process Data into Parquet Format
```bash
# Process collected JSON files into consolidated parquet
python main.py

# Optional: specify custom directories
python main.py --data-dir ./custom-data-dir --output-dir ./custom-output
```

**What happens:**
- Reads all JSON files from the data directory
- Cleans and validates the data
- Combines data from multiple organizations and dates
- Outputs `data.parquet` file ready for analysis

### Step 3: Launch Interactive Dashboard
```bash
# Run the dashboard locally with your data
streamlit run dashboard.py
```

**Dashboard features:**
- Interactive charts and graphs
- Date range filtering
- Organization comparison
- Language usage breakdown
- Editor statistics
- User engagement metrics

## 📊 Data Structure

The processed data includes the following key metrics:

- **Code Completions**: Suggestions, acceptances, lines of code by language and editor
- **Chat Interactions**: Usage of Copilot chat features
- **User Engagement**: Active vs engaged users over time
- **Editor Breakdown**: Usage statistics by IDE (VS Code, JetBrains, etc.)
- **Language Statistics**: Most used programming languages
- **Pull Request Summaries**: GitHub.com integration metrics

## 🔒 Privacy & Security

### Data Privacy
- **Local Processing**: All data stays on your machine
- **No Cloud Storage**: No data is sent to external services
- **Organization Control**: You control what data to collect and analyze

### Data Anonymization
- The project automatically anonymizes organization names in public deployments
- Sensitive data files are ignored by git (see `.gitignore`)
- Raw API responses are cleaned up after processing

### What's Safe to Commit
- ✅ Source code (`*.py`, `*.sh`)
- ✅ Configuration files (`requirements.txt`, etc.)
- ✅ Documentation (`README.md`)
- ❌ Data files (`data/`, `*.parquet`, `*.csv`)
- ❌ Raw API responses (`raw_response_*.json`)

## 🌐 Online Deployment

### Deploy Your Own Dashboard
1. Fork this repository to your GitHub account
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Create a new app pointing to your fork
4. Set main file path to `dashboard.py`
5. Deploy!

The deployed dashboard will:
- Show an upload interface for users to upload their `.parquet` files
- Process data securely in the browser session only
- Display interactive analytics without storing any data on the server
- Clear all data when the session ends

### Security in Cloud Deployment
- **No Data Persistence**: Cloud dashboard never stores user data
- **Session-Only Processing**: Data exists only during the browser session
- **Client-Side Analytics**: All processing happens in the user's browser
- **Zero Server Storage**: No data is saved on deployment servers

## 🛠️ Development

### Project Structure
```
copilot-dashboard/
├── collect_metrics.sh      # Data collection script
├── main.py                # Data processing script  
├── dashboard.py           # Streamlit dashboard
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules (includes data files)
├── README.md             # This documentation
└── data/                 # Local data storage (git-ignored)
    └── year=YYYY/
        └── month=MM/
            └── DD-org.json
```

### Adding New Organizations
Simply run the collection script with different `--org` parameters:
```bash
./collect_metrics.sh --org organization-1
./collect_metrics.sh --org organization-2
./collect_metrics.sh --org organization-3
```

Then reprocess the data:
```bash
python main.py
```

## 📈 Example Insights

The dashboard provides insights such as:
- **Adoption Trends**: How Copilot usage grows over time
- **Language Preferences**: Which programming languages benefit most from Copilot
- **Editor Usage**: VS Code vs JetBrains vs other IDEs
- **Feature Usage**: Code completions vs chat features
- **Team Engagement**: Active users vs engaged users ratios

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**"GitHub CLI not authenticated"**
- Run `gh auth login` and follow the prompts

**"Access denied" when collecting metrics**
- Ensure your GitHub account has permissions to read Copilot metrics for the organization
- Contact your organization admin to grant appropriate access

**"No data found to process"**
- Check that the data collection step completed successfully
- Verify that JSON files exist in the `data/` directory structure

**"Invalid JSON response"**
- This usually indicates API rate limiting or authentication issues
- Wait a few minutes and try again
- Check your GitHub CLI authentication status

### Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review the console output for specific error messages
3. Ensure all prerequisites are properly installed
4. Open an issue on GitHub with detailed error information

This script uses GitHub CLI to fetch Copilot usage data and organize it automatically.

```bash
# Navigate to the script directory
cd copilot-dashboard

# Install Python dependencies (if not already done)
pip install -r requirements.txt

# Run the collection script
./collect_metrics.sh --org <organization> [--data-dir ./data]
```

*   You need to be authenticated with GitHub CLI (`gh auth login`)
*   Your account must have appropriate permissions to read Copilot metrics for the organization
*   Specify the `--org` to collect data for
*   The default data directory is `./data`
*   The script will automatically organize data in the `year=YYYY/month=MM/DD.json` structure

## 2. Processing Data and Generating Reports

After collecting the `.json` files, run `main.py` to process them.

```bash
# Ensure you are in the copilot-dashboard directory
cd copilot-dashboard

# Run the main processing script
python main.py [--data-dir ./data] [--output-dir .]
```

*   This script reads JSON files from the `data` directory.
*   It cleans, merges, and enriches the data.
*   It generates aggregated `data.parquet` and `data.csv` files.

## 3. Running the Dashboard

### Option A: Local Dashboard (with your data)
```bash
# Run the dashboard locally with your generated data
streamlit run dashboard.py
```

### Option B: Upload to Online Dashboard
1. Visit our hosted dashboard: [GitHub Copilot Analytics](https://your-app.streamlit.app) 
2. Upload your generated `.parquet` file using the sidebar
3. Explore your analytics instantly!

> **🔒 Privacy Note**: When using the online dashboard, your data is processed in your browser session only and is never stored on our servers.

The dashboard provides:
*   Interactive charts showing Copilot usage trends
*   User engagement metrics
*   Language and editor breakdowns
*   Chat usage statistics
*   Pull request summary metrics

## Data Structure

The data is stored in the following format:
```
data/
├── year=2025/
│   ├── month=01/
│   │   ├── 01.json
│   │   ├── 02.json
│   │   └── ...
│   ├── month=02/
│   │   ├── 01.json
│   │   └── ...
```

Each JSON file contains the raw response from the GitHub Copilot metrics API for a specific day.

## Environment Variables

*   No specific environment variables are required
*   Authentication is handled through GitHub CLI (`gh auth login`)

## API Reference

This tool uses the GitHub REST API endpoint through GitHub CLI:
- `GET /orgs/{org}/copilot/metrics`

For more information, see the [GitHub API documentation](https://docs.github.com/en/rest/copilot/copilot-usage).

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Complete guide for deploying to Streamlit Community Cloud
- **[DATA_STRUCTURE.md](DATA_STRUCTURE.md)**: Data schema and troubleshooting guide
- **[README.md](README.md)**: This file - getting started guide

## Quick Start

```bash
# 1. Install and authenticate GitHub CLI
gh auth login

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Collect metrics for your organization
./collect_metrics.sh --org your-organization

# 4. Process data into analytics format
python main.py

# 5A. Run dashboard locally
streamlit run dashboard.py

# 5B. Or upload data.parquet to our hosted dashboard
# Visit: https://your-app.streamlit.app
```

## 🌐 Deployment Options

### Local Development
- Run `streamlit run dashboard.py` for local development
- All data stays on your machine

### Streamlit Community Cloud
- Fork this repository
- Deploy to [Streamlit Community Cloud](https://streamlit.io/cloud)
- Users upload their own data files
- No sensitive data stored in the cloud

## 🎯 Open Source Workflow

This project is designed to be privacy-first and cloud-ready:

### 🔧 Data Collection (Local)
1. **Data Collection**: `collect_metrics.sh` uses GitHub CLI to collect raw data via API
2. **Data Processing**: `main.py` processes the raw JSON files into a Parquet file
3. **Local Storage**: All data files are automatically excluded from git commits

### 🌐 Data Visualization (Cloud-Ready)
4. **Local Dashboard**: Run `streamlit run dashboard.py` for local analysis
5. **Cloud Dashboard**: Upload your `.parquet` file to our hosted Streamlit app
6. **Privacy**: Your data never leaves your control - upload only for analysis

### Key Benefits:
- ✅ **Privacy-First**: Data collection and storage happens locally
- ✅ **Cloud-Ready**: Dashboard can be deployed to Streamlit Community Cloud
- ✅ **User Upload**: Users upload their own data for analysis
- ✅ **No Data Persistence**: Cloud dashboard doesn't store any user data
- ✅ **GitHub CLI Authentication**: No token management needed
- ✅ **Multi-Organization Support**: Collect from multiple GitHub orgs

### Data Structure:
```
data/
├── year=2025/
│   ├── month=04/
│   │   ├── 11-stone-payments.json
│   │   ├── 12-stone-payments.json
│   │   ├── 11-other-org.json
│   │   └── ...
│   └── month=05/
│       ├── 01-stone-payments.json
│       └── ...
├── data-stone-payments.parquet (single org)
├── data-other-org.parquet (single org)
└── data-combined.parquet (all orgs)
```

### Multi-Organization Support:
- Collect data for different organizations: `./collect_metrics.sh --org org1` and `./collect_metrics.sh --org org2`
- Files are saved as `DD-<organization>.json` to avoid conflicts
- Processing creates separate Parquet files per organization plus a combined file
- Dashboard allows selecting which organization to analyze

## 🤝 Contributing

We welcome contributions to make this tool even better! Here's how you can help:

### Ways to Contribute
- 🐛 **Report bugs** via GitHub Issues
- 💡 **Suggest features** for new analytics or visualizations
- 📖 **Improve documentation** with clearer examples
- 🔧 **Submit code** via Pull Requests
- ⭐ **Star the repository** to show your support

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/copilot-dashboard
cd copilot-dashboard

# Install development dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest

# Run the dashboard locally
streamlit run dashboard.py
```

### Guidelines
- Follow existing code style and conventions
- Add documentation for new features
- Test your changes thoroughly
- Ensure data privacy and security best practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check [DEPLOYMENT.md](DEPLOYMENT.md) and [DATA_STRUCTURE.md](DATA_STRUCTURE.md)
- **Issues**: Report problems via [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/your-repo/discussions)
- **Community**: Connect with other users and contributors

## 🙏 Acknowledgments

- GitHub for providing the Copilot API
- Streamlit team for the amazing framework
- Open-source community for contributions and feedback

---

**Ready to analyze your GitHub Copilot usage?** Start collecting data and upload to the dashboard! 🚀
