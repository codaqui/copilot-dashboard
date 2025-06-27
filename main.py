#!/usr/bin/env python3
"""
GitHub Copilot Data Processor

This script processes GitHub Copilot usage data from JSON files and generates
aggregated reports in Parquet format.

Author: Enderson Menezes
Created: 2025-06-24
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import argparse


def load_json_files(data_dir="./data"):
    """Load all JSON files from the data directory structure."""
    data_path = Path(data_dir)
    all_data = []
    
    if not data_path.exists():
        print(f"Data directory {data_dir} does not exist")
        return pd.DataFrame()
    
    # Walk through year=YYYY/month=MM/ structure
    for year_dir in data_path.glob("year=*"):
        for month_dir in year_dir.glob("month=*"):
            for json_file in month_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Extract organization from filename if not in data
                        if 'organization' not in data:
                            # Extract from filename: DD-<org>.json
                            filename = json_file.stem  # filename without extension
                            if '-' in filename:
                                org_from_filename = filename.split('-', 1)[1]  # Get everything after first dash
                                data['organization'] = org_from_filename
                        
                        all_data.append(data)
                        print(f"📄 Loaded {json_file}")
                except Exception as e:
                    print(f"❌ Error loading {json_file}: {e}")
    
    if not all_data:
        print("No data files found")
        return pd.DataFrame()
    
    print(f"✅ Loaded {len(all_data)} data files")
    return pd.DataFrame(all_data)


def process_data(df):
    """Process and clean the data."""
    if df.empty:
        return df
    
    # Convert date column to datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    # Add derived columns
    if 'download_timestamp' in df.columns:
        df['download_timestamp'] = pd.to_datetime(df['download_timestamp'])
    
    # Sort by date
    if 'date' in df.columns:
        df = df.sort_values('date')
    
    print(f"📊 Processed {len(df)} records")
    return df


def save_reports(df, output_dir="."):
    """Save processed data to single consolidated Parquet file."""
    if df.empty:
        print("No data to save")
        return
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save as single consolidated Parquet file
    parquet_file = output_path / "data.parquet"
    df.to_parquet(parquet_file, index=False)
    print(f"💾 Saved consolidated Parquet file: {parquet_file}")
    
    # Show organizations included
    if 'organization' in df.columns:
        organizations = df['organization'].unique()
        print(f"� Organizations included: {', '.join(organizations)}")
        for org in organizations:
            org_count = len(df[df['organization'] == org])
            print(f"   - {org}: {org_count} records")


def print_summary(df):
    """Print a summary of the data."""
    if df.empty:
        print("No data to summarize")
        return
    
    print("\n📈 Data Summary:")
    print(f"Total records: {len(df)}")
    
    if 'date' in df.columns:
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    
    if 'organization' in df.columns:
        orgs = df['organization'].unique()
        print(f"Organizations ({len(orgs)}): {', '.join(orgs)}")
        
        # Show summary per organization
        for org in orgs:
            org_df = df[df['organization'] == org]
            print(f"\n  📊 {org}:")
            print(f"    Records: {len(org_df)}")
            
            if 'total_active_users' in org_df.columns:
                latest_active = org_df['total_active_users'].iloc[-1] if len(org_df) > 0 else 'N/A'
                print(f"    Latest active users: {latest_active}")
            
            if 'total_engaged_users' in org_df.columns:
                latest_engaged = org_df['total_engaged_users'].iloc[-1] if len(org_df) > 0 else 'N/A'
                print(f"    Latest engaged users: {latest_engaged}")
    else:
        if 'total_active_users' in df.columns:
            print(f"Total active users (latest): {df['total_active_users'].iloc[-1] if len(df) > 0 else 'N/A'}")
        
        if 'total_engaged_users' in df.columns:
            print(f"Total engaged users (latest): {df['total_engaged_users'].iloc[-1] if len(df) > 0 else 'N/A'}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Process GitHub Copilot usage data")
    parser.add_argument("--data-dir", default="./data", help="Directory containing JSON data files")
    parser.add_argument("--output-dir", default=".", help="Directory to save output files")
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()
    
    print("🚀 Starting GitHub Copilot data processing...")
    
    # Load data
    df = load_json_files(args.data_dir)
    
    if df.empty:
        print("❌ No data found to process")
        return
    
    # Process data
    df = process_data(df)
    
    # Save reports
    save_reports(df, args.output_dir)
    
    # Print summary
    print_summary(df)
    
    print("✅ Data processing completed successfully!")


if __name__ == "__main__":
    main()
