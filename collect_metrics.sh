#!/bin/bash

# GitHub Copilot Metrics Collector
# Uses GitHub CLI to collect Copilot usage metrics and organize them in the required directory structure
#
# Author: Enderson Menezes
# Created: 2025-06-24

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# Check if gh CLI is installed and authenticated
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed. Please install it first:"
        log_error "https://cli.github.com/"
        exit 1
    fi
    
    if ! gh auth status &> /dev/null; then
        log_error "GitHub CLI is not authenticated. Please run 'gh auth login' first."
        exit 1
    fi
    
    log_info "GitHub CLI is installed and authenticated ✓"
}

# Show usage information
show_usage() {
    echo "GitHub Copilot Metrics Collector"
    echo "Usage: $0 --org <organization> [OPTIONS]"
    echo ""
    echo "Required:"
    echo "  --org <org>           GitHub organization name"
    echo ""
    echo "Options:"
    echo "  --data-dir <dir>      Data directory (default: ./data)"
    echo "  --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --org codaqui"
    echo "  $0 --org codaqui --data-dir /path/to/data"
    echo ""
    echo "Prerequisites:"
    echo "  - GitHub CLI (gh) must be installed and authenticated"
    echo "  - Organization must have Copilot enabled"
    echo "  - User must have appropriate permissions to read Copilot metrics"
}

# Parse command line arguments
parse_args() {
    ORG=""
    DATA_DIR="./data"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --org)
                ORG="$2"
                shift 2
                ;;
            --data-dir)
                DATA_DIR="$2"
                shift 2
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    if [[ -z "$ORG" ]]; then
        log_error "Organization name is required. Use --org <organization>"
        show_usage
        exit 1
    fi
}

# Create directory structure for a specific date
create_date_dir() {
    local date="$1"
    local org="$2"
    local year=$(echo "$date" | cut -d'-' -f1)
    local month=$(echo "$date" | cut -d'-' -f2)
    local day=$(echo "$date" | cut -d'-' -f3)
    
    local dir_path="${DATA_DIR}/year=${year}/month=${month}"
    mkdir -p "$dir_path"
    echo "${dir_path}/${day}-${org}.json"
}

# Fetch Copilot metrics using GitHub CLI
fetch_copilot_metrics() {
    local org="$1"
    
    log_info "Fetching Copilot metrics for organization: $org"
    
    # Create temporary files
    local temp_output=$(mktemp)
    local temp_error=$(mktemp)
    
    # Use curl instead of gh to have more control over output
    local token=$(gh auth token 2>/dev/null)
    if [[ -z "$token" ]]; then
        log_error "Failed to get GitHub token from gh auth"
        rm -f "$temp_output" "$temp_error"
        return 1
    fi
    
    # Make API call with curl
    if curl -s -H "Authorization: Bearer $token" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "https://api.github.com/orgs/$org/copilot/metrics" \
        > "$temp_output" 2> "$temp_error"; then
        
        # Check if response is valid JSON
        if jq empty < "$temp_output" 2>/dev/null; then
            log_info "Successfully fetched Copilot metrics"
            cat "$temp_output"
            rm -f "$temp_output" "$temp_error"
        else
            log_error "Invalid JSON response from API"
            log_debug "Response content:"
            cat "$temp_output" | head -c 500
            rm -f "$temp_output" "$temp_error"
            return 1
        fi
    else
        local error_content=$(cat "$temp_error" 2>/dev/null)
        local response_content=$(cat "$temp_output" 2>/dev/null)
        
        log_error "Failed to fetch Copilot metrics"
        
        if [[ -n "$response_content" ]]; then
            # Parse error from API response
            local message=$(echo "$response_content" | jq -r '.message // empty' 2>/dev/null)
            if [[ -n "$message" && "$message" != "null" ]]; then
                log_error "API error: $message"
            else
                log_error "Response: $response_content"
            fi
        fi
        
        if [[ -n "$error_content" ]]; then
            log_error "Network error: $error_content"
        fi
        
        # Check for common issues
        if echo "$response_content" | grep -q "Not Found"; then
            log_error "Organization '$org' not found or Copilot not enabled"
        elif echo "$response_content" | grep -q "Forbidden"; then
            log_error "Access denied. Check if you have permissions to read Copilot metrics for '$org'"
        elif echo "$response_content" | grep -q "rate limit"; then
            log_error "API rate limit exceeded. Try again later."
        fi
        
        rm -f "$temp_output" "$temp_error"
        
        return 1
    fi
}

# Quiet version of fetch function that doesn't log during execution
fetch_copilot_metrics_quiet() {
    local org="$1"
    
    # Create temporary files
    local temp_output=$(mktemp)
    local temp_error=$(mktemp)
    
    # Use curl instead of gh to have more control over output
    local token=$(gh auth token 2>/dev/null)
    if [[ -z "$token" ]]; then
        rm -f "$temp_output" "$temp_error"
        return 1
    fi
    
    # Make API call with curl
    if curl -s -H "Authorization: Bearer $token" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "https://api.github.com/orgs/$org/copilot/metrics" \
        > "$temp_output" 2> "$temp_error"; then
        
        # Check if response is valid JSON
        if jq empty < "$temp_output" 2>/dev/null; then
            cat "$temp_output"
            rm -f "$temp_output" "$temp_error"
        else
            rm -f "$temp_output" "$temp_error"
            return 1
        fi
    else
        rm -f "$temp_output" "$temp_error"
        return 1
    fi
}

# Process and save metrics data
process_metrics() {
    local org="$1"
    local metrics_json="$2"
    
    log_info "Processing metrics data..."
    
    # Save raw response
    local raw_file="${DATA_DIR}/raw_response_$(date +%Y%m%d_%H%M%S).json"
    echo "$metrics_json" > "$raw_file"
    log_info "Raw API response saved to $raw_file"
    
    # Check if response is valid JSON
    if ! jq empty < "$raw_file" 2>/dev/null; then
        log_error "Invalid JSON response from API"
        log_error "Response content (first 500 chars):"
        head -c 500 "$raw_file"
        return 1
    fi
    
    # Get array length for progress
    local total_records=$(jq 'length' < "$raw_file" 2>/dev/null || echo "0")
    log_info "Found $total_records records to process"
    
    if [[ "$total_records" -eq 0 ]]; then
        log_warn "No records found in API response"
        return 1
    fi
    
    # Process each record using jq directly
    local count=0
    for i in $(seq 0 $((total_records - 1))); do
        log_debug "Processing record $i of $((total_records - 1))"
        
        # Extract record and date
        local day_record=$(jq ".[$i]" < "$raw_file")
        local date=$(echo "$day_record" | jq -r '.date // empty')
        
        if [[ -z "$date" || "$date" == "null" ]]; then
            log_warn "Skipping record $i without date field"
            continue
        fi
        
        # Validate date format
        if ! date -d "$date" &>/dev/null; then
            log_warn "Skipping record $i with invalid date: $date"
            continue
        fi
        
        log_debug "Creating directory for date: $date"
        # Create directory and file path
        local file_path=$(create_date_dir "$date" "$org")
        
        log_debug "Saving to file: $file_path"
        # Add metadata and save
        echo "$day_record" | jq --arg org "$org" --arg timestamp "$(date -Iseconds)" \
            '. + {organization: $org, download_timestamp: $timestamp}' > "$file_path"
        
        log_info "[$((count + 1))/$total_records] Saved metrics for $date"
        count=$((count + 1))
    done
    
    log_info "✅ Processed $count/$total_records records successfully"
    
    # Clean up raw file if all records processed successfully
    if [[ $count -eq $total_records ]]; then
        rm -f "$raw_file"
        log_info "Cleaned up temporary files"
    fi
}

# Main function
main() {
    echo "🤖 GitHub Copilot Metrics Collector"
    echo "=================================="
    
    # Parse arguments
    parse_args "$@"
    
    # Check prerequisites
    check_gh_cli
    
    # Create data directory
    mkdir -p "$DATA_DIR"
    log_info "Using data directory: $DATA_DIR"
    
    # Fetch metrics
    log_info "Starting metrics collection for organization: $ORG"
    
    log_info "Fetching Copilot metrics for organization: $ORG"
    local metrics_json
    if metrics_json=$(fetch_copilot_metrics_quiet "$ORG"); then
        log_info "Successfully fetched Copilot metrics"
        # Process and save metrics
        process_metrics "$ORG" "$metrics_json"
        
        log_info "✅ Metrics collection completed successfully!"
        log_info "Data saved to: $DATA_DIR"
        log_info ""
        log_info "Next steps:"
        log_info "1. Run 'python main.py' to process the data"
        log_info "2. Run 'streamlit run dashboard.py' to view the dashboard"
    else
        log_error "❌ Failed to collect metrics"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
