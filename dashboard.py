#!/usr/bin/env python3
"""
GitHub Copilot Analytics Dashboard

Interactive Streamlit dashboard for visualizing GitHub Copilot usage metrics.
Designed for the actual GitHub Copilot API data structure.

Author: Enderson Menezes
Created: 2025-06-24
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from pathlib import Path
from datetime import datetime
import numpy as np

# =====================================================================
# PAGE CONFIGURATION
# =====================================================================

st.set_page_config(
    page_title="GitHub Copilot Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# DATA LOADING
# =====================================================================

@st.cache_data
def load_data_from_file(uploaded_file):
    """Load and cache the processed Copilot data from uploaded file."""
    try:
        df = pd.read_parquet(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

@st.cache_data
def load_data_local():
    """Load data from local file (for development)."""
    parquet_file = Path("data.parquet")
    
    if parquet_file.exists():
        df = pd.read_parquet(parquet_file)
        return df
    else:
        return None

def extract_language_metrics(df):
    """Extract language-specific metrics from the nested data structure."""
    language_data = []
    
    for _, row in df.iterrows():
        date = row['date']
        org = row['organization']
        
        # Extract code completions data
        if 'copilot_ide_code_completions' in row and row['copilot_ide_code_completions']:
            completions = row['copilot_ide_code_completions']
            
            # Check if it has editors
            if 'editors' in completions:
                for editor in completions['editors']:
                    editor_name = editor.get('name', 'unknown')
                    
                    if 'models' in editor:
                        for model in editor['models']:
                            if 'languages' in model:
                                for lang in model['languages']:
                                    language_data.append({
                                        'date': date,
                                        'organization': org,
                                        'editor': editor_name,
                                        'language': lang.get('name', 'unknown'),
                                        'total_engaged_users': lang.get('total_engaged_users', 0),
                                        'total_code_acceptances': lang.get('total_code_acceptances', 0),
                                        'total_code_suggestions': lang.get('total_code_suggestions', 0),
                                        'total_code_lines_accepted': lang.get('total_code_lines_accepted', 0),
                                        'total_code_lines_suggested': lang.get('total_code_lines_suggested', 0),
                                        'feature_type': 'code_completions'
                                    })
    
    return pd.DataFrame(language_data)

def extract_chat_metrics(df):
    """Extract chat-specific metrics from the nested data structure."""
    chat_data = []
    
    for _, row in df.iterrows():
        date = row['date']
        org = row['organization']
        
        # Extract IDE chat data
        if 'copilot_ide_chat' in row and row['copilot_ide_chat']:
            chat = row['copilot_ide_chat']
            
            if 'editors' in chat:
                for editor in chat['editors']:
                    editor_name = editor.get('name', 'unknown')
                    
                    if 'models' in editor:
                        for model in editor['models']:
                            chat_data.append({
                                'date': date,
                                'organization': org,
                                'editor': editor_name,
                                'feature_type': 'ide_chat',
                                'total_engaged_users': model.get('total_engaged_users', 0),
                                'total_chats': model.get('total_chats', 0),
                                'total_chat_copy_events': model.get('total_chat_copy_events', 0),
                                'total_chat_insertion_events': model.get('total_chat_insertion_events', 0)
                            })
        
        # Extract dotcom chat data
        if 'copilot_dotcom_chat' in row and row['copilot_dotcom_chat']:
            dotcom_chat = row['copilot_dotcom_chat']
            
            total_chats = 0
            if 'models' in dotcom_chat and dotcom_chat['models'] and len(dotcom_chat['models']) > 0:
                total_chats = dotcom_chat['models'][0].get('total_chats', 0)
            
            chat_data.append({
                'date': date,
                'organization': org,
                'editor': 'github.com',
                'feature_type': 'dotcom_chat',
                'total_engaged_users': dotcom_chat.get('total_engaged_users', 0),
                'total_chats': total_chats,
                'total_chat_copy_events': 0,
                'total_chat_insertion_events': 0
            })
    
    return pd.DataFrame(chat_data)

# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================

def format_number(num):
    """Format numbers with appropriate suffixes."""
    if pd.isna(num) or num == 0:
        return "0"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(int(num))

def calculate_acceptance_rate(lang_df):
    """Calculate code acceptance rate."""
    if lang_df.empty:
        return 0
    
    total_suggestions = lang_df['total_code_suggestions'].sum()
    total_acceptances = lang_df['total_code_acceptances'].sum()
    
    return (total_acceptances / total_suggestions * 100) if total_suggestions > 0 else 0

# =====================================================================
# DASHBOARD FUNCTIONS
# =====================================================================

def render_overview(df):
    """Render the overview section."""
    st.header("📊 Overview")
    
    # Get latest metrics
    latest_date = df['date'].max()
    latest_data = df[df['date'] == latest_date].iloc[0]
    
    # Show data context
    st.info(f"📅 **Latest Data:** {latest_date.strftime('%B %d, %Y')} | **Organization:** {latest_data.get('organization', 'N/A')}")
    st.caption("💡 Overview metrics show the most recent data available for your selected organization and date range")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Active Users",
            format_number(latest_data.get('total_active_users', 0)),
            help="Total number of users with GitHub Copilot licenses on the latest available date"
        )
    
    with col2:
        st.metric(
            "Total Engaged Users", 
            format_number(latest_data.get('total_engaged_users', 0)),
            help="Users who actively used GitHub Copilot features on the latest available date"
        )
    
    with col3:
        engagement_rate = (latest_data.get('total_engaged_users', 0) / latest_data.get('total_active_users', 1)) * 100
        st.metric(
            "Engagement Rate",
            f"{engagement_rate:.1f}%",
            help="Percentage of licensed users who actively used Copilot on the latest available date"
        )
    
    with col4:
        data_points = len(df)
        date_range = (df['date'].max() - df['date'].min()).days + 1 if len(df) > 1 else 1
        st.metric(
            "Data Coverage",
            f"{date_range} days",
            help=f"Total time span covered by {data_points} data records in your current selection"
        )

def render_trends(df):
    """Render the trends section."""
    st.header("📈 Usage Trends")
    
    # Time series chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['total_active_users'],
        mode='lines+markers',
        name='Active Users',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['total_engaged_users'],
        mode='lines+markers',
        name='Engaged Users',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title="User Engagement Over Time",
        xaxis_title="Date",
        yaxis_title="Number of Users",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True, key="trends_users_over_time")
    st.caption("📈 Track user engagement patterns and growth over time across all organizations")

def render_language_analysis(lang_df):
    """Render language analysis."""
    st.header("💻 Programming Languages")
    
    if lang_df.empty:
        st.warning("No language data available")
        return
    
    # Period filter for language analysis
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        period_option = st.selectbox(
            "Select Period View",
            ["Last 7 days", "Last 14 days", "Last 30 days", "All time"],
            index=2,  # Default to Last 30 days for languages
            key="lang_period_filter"
        )
    
    with col2:
        compare_previous = st.checkbox(
            "Compare with Previous Period",
            value=False,
            key="lang_compare_filter"
        )
    
    # Filter data based on period selection
    filtered_lang_df = lang_df.copy()
    previous_lang_df = pd.DataFrame()
    
    if period_option != "All time":
        max_date = lang_df['date'].max()
        if period_option == "Last 7 days":
            days = 7
            start_date = max_date - pd.Timedelta(days=days-1)
        elif period_option == "Last 14 days":
            days = 14
            start_date = max_date - pd.Timedelta(days=days-1)
        elif period_option == "Last 30 days":
            days = 30
            start_date = max_date - pd.Timedelta(days=days-1)
        
        filtered_lang_df = lang_df[lang_df['date'] >= start_date]
        
        # Calculate previous period if comparison is enabled
        if compare_previous:
            prev_start = start_date - pd.Timedelta(days=days)
            prev_end = start_date - pd.Timedelta(days=1)
            previous_lang_df = lang_df[(lang_df['date'] >= prev_start) & (lang_df['date'] <= prev_end)]
    
    # Language popularity over time
    lang_summary = filtered_lang_df.groupby(['date', 'language']).agg({
        'total_engaged_users': 'sum',
        'total_code_acceptances': 'sum',
        'total_code_suggestions': 'sum'
    }).reset_index()
    
    # Top languages by engaged users
    top_languages = lang_summary.groupby('language')['total_engaged_users'].sum().sort_values(ascending=False).head(10)
    
    # Calculate previous period data if comparison is enabled
    prev_lang_summary = pd.DataFrame()
    if compare_previous and not previous_lang_df.empty:
        prev_lang_summary = previous_lang_df.groupby(['date', 'language']).agg({
            'total_engaged_users': 'sum',
            'total_code_acceptances': 'sum',
            'total_code_suggestions': 'sum'
        }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if compare_previous and not prev_lang_summary.empty:
            # Compare current vs previous period
            current_totals = lang_summary.groupby('language')['total_engaged_users'].sum()
            prev_totals = prev_lang_summary.groupby('language')['total_engaged_users'].sum()
            
            # Combine data for comparison
            comparison_data = pd.DataFrame({
                'Current Period': current_totals,
                'Previous Period': prev_totals
            }).fillna(0).reset_index()
            
            # Get top languages from current period for consistent ordering
            top_langs = comparison_data.set_index('language').loc[top_languages.index[:10]].reset_index()
            
            fig = px.bar(
                top_langs.melt(id_vars='language', var_name='Period', value_name='Engaged Users'),
                x='Engaged Users',
                y='language',
                color='Period',
                orientation='h',
                title=f"Top Languages Comparison ({period_option} vs Previous)",
                labels={'Engaged Users': 'Total Engaged Users', 'language': 'Language'},
                color_discrete_map={'Current Period': '#1f77b4', 'Previous Period': '#ff7f0e'},
                barmode='group'
            )
        else:
            fig = px.bar(
                x=top_languages.values,
                y=top_languages.index,
                orientation='h',
                title=f"Top Languages by Engaged Users ({period_option})",
                labels={'x': 'Total Engaged Users', 'y': 'Language'}
            )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key="lang_top_by_users")
        st.caption("🏆 Most popular programming languages based on user engagement")
    
    with col2:
        # Acceptance rates by language
        lang_rates = lang_summary.groupby('language').apply(
            lambda x: (x['total_code_acceptances'].sum() / x['total_code_suggestions'].sum() * 100) 
            if x['total_code_suggestions'].sum() > 0 else 0
        ).sort_values(ascending=False).head(10)
        
        if compare_previous and not prev_lang_summary.empty:
            # Compare acceptance rates
            prev_rates = prev_lang_summary.groupby('language').apply(
                lambda x: (x['total_code_acceptances'].sum() / x['total_code_suggestions'].sum() * 100) 
                if x['total_code_suggestions'].sum() > 0 else 0
            )
            
            # Combine rates for comparison
            rates_comparison = pd.DataFrame({
                'Current Period': lang_rates,
                'Previous Period': prev_rates
            }).fillna(0).reset_index()
            
            # Get top languages from current period for consistent ordering
            top_rates = rates_comparison.set_index('language').loc[lang_rates.index[:10]].reset_index()
            
            fig = px.bar(
                top_rates.melt(id_vars='language', var_name='Period', value_name='Acceptance Rate'),
                x='Acceptance Rate',
                y='language',
                color='Period',
                orientation='h',
                title=f"Acceptance Rate Comparison ({period_option} vs Previous)",
                labels={'Acceptance Rate': 'Acceptance Rate (%)', 'language': 'Language'},
                color_discrete_map={'Current Period': '#2ca02c', 'Previous Period': '#d62728'},
                barmode='group'
            )
        else:
            fig = px.bar(
                x=lang_rates.values,
                y=lang_rates.index,
                orientation='h',
                title=f"Acceptance Rate by Language ({period_option})",
                labels={'x': 'Acceptance Rate (%)', 'y': 'Language'}
            )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key="lang_acceptance_rates")
        st.caption("✅ Languages with highest acceptance rates - shows where Copilot suggestions are most helpful")

def render_editor_analysis(lang_df, chat_df):
    """Render editor analysis."""
    st.header("🖥️ Editor Usage")
    
    # Period filter for daily view
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        period_option = st.selectbox(
            "Select Period View",
            ["Last 7 days", "Last 14 days", "Last 30 days", "All time"],
            index=0,
            key="editor_period_filter"
        )
    
    with col2:
        compare_previous = st.checkbox(
            "Compare with Previous Period",
            value=False,
            key="editor_compare_filter"
        )
    
    # Filter data based on period selection
    filtered_lang_df = lang_df.copy()
    filtered_chat_df = chat_df.copy()
    previous_lang_df = pd.DataFrame()
    
    if not lang_df.empty and period_option != "All time":
        max_date = lang_df['date'].max()
        if period_option == "Last 7 days":
            days = 7
            start_date = max_date - pd.Timedelta(days=days-1)
        elif period_option == "Last 14 days":
            days = 14
            start_date = max_date - pd.Timedelta(days=days-1)
        elif period_option == "Last 30 days":
            days = 30
            start_date = max_date - pd.Timedelta(days=days-1)
        
        filtered_lang_df = lang_df[lang_df['date'] >= start_date]
        if not chat_df.empty:
            filtered_chat_df = chat_df[chat_df['date'] >= start_date]
        
        # Calculate previous period if comparison is enabled
        if compare_previous:
            prev_start = start_date - pd.Timedelta(days=days)
            prev_end = start_date - pd.Timedelta(days=1)
            previous_lang_df = lang_df[(lang_df['date'] >= prev_start) & (lang_df['date'] <= prev_end)]
    
    # Daily usage by editor (not accumulated)
    if not filtered_lang_df.empty:
        # Group by date and editor to show daily patterns
        daily_editor = filtered_lang_df.groupby(['date', 'editor']).agg({
            'total_engaged_users': 'mean',  # Use mean to avoid double counting
            'total_code_acceptances': 'sum'
        }).reset_index()
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["📊 Daily Engaged Users", "📈 Editor Summary"])
        
        with tab1:
            if len(daily_editor['editor'].unique()) > 0:
                fig = px.bar(
                    daily_editor,
                    x='date',
                    y='total_engaged_users',
                    color='editor',
                    title=f"Daily Engaged Users by Editor ({period_option})",
                    labels={'total_engaged_users': 'Engaged Users', 'date': 'Date'}
                )
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True, key="editor_daily_users")
            else:
                st.info("No editor data available for the selected period")
        
        with tab2:
            # Summary view by editor
            editor_summary = filtered_lang_df.groupby('editor').agg({
                'total_engaged_users': 'mean',  # Average daily users
                'total_code_acceptances': 'sum',
                'total_code_suggestions': 'sum'
            }).reset_index()
            
            # Calculate acceptance rate
            editor_summary['acceptance_rate'] = (
                editor_summary['total_code_acceptances'] / 
                editor_summary['total_code_suggestions'] * 100
            ).fillna(0)
            
            # Calculate previous period data if comparison is enabled
            prev_editor_summary = pd.DataFrame()
            if compare_previous and not previous_lang_df.empty:
                prev_editor_summary = previous_lang_df.groupby('editor').agg({
                    'total_engaged_users': 'mean',
                    'total_code_acceptances': 'sum',
                    'total_code_suggestions': 'sum'
                }).reset_index()
                prev_editor_summary['acceptance_rate'] = (
                    prev_editor_summary['total_code_acceptances'] / 
                    prev_editor_summary['total_code_suggestions'] * 100
                ).fillna(0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if compare_previous and not prev_editor_summary.empty:
                    # Compare current vs previous period
                    current_users = editor_summary.set_index('editor')['total_engaged_users']
                    prev_users = prev_editor_summary.set_index('editor')['total_engaged_users']
                    
                    # Combine data for comparison
                    users_comparison = pd.DataFrame({
                        'Current Period': current_users,
                        'Previous Period': prev_users
                    }).fillna(0).reset_index()
                    
                    fig = px.bar(
                        users_comparison.melt(id_vars='editor', var_name='Period', value_name='Engaged Users'),
                        x='Engaged Users',
                        y='editor',
                        color='Period',
                        orientation='h',
                        title=f"Avg Daily Users Comparison ({period_option} vs Previous)",
                        labels={'Engaged Users': 'Avg Daily Engaged Users', 'editor': 'Editor'},
                        color_discrete_map={'Current Period': '#1f77b4', 'Previous Period': '#ff7f0e'},
                        barmode='group'
                    )
                else:
                    fig = px.bar(
                        editor_summary.sort_values('total_engaged_users', ascending=True),
                        x='total_engaged_users',
                        y='editor',
                        orientation='h',
                        title=f"Average Daily Engaged Users by Editor ({period_option})",
                        labels={'total_engaged_users': 'Avg Daily Engaged Users', 'editor': 'Editor'}
                    )
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True, key="editor_avg_users")
            
            with col2:
                if compare_previous and not prev_editor_summary.empty:
                    # Compare acceptance rates
                    current_rates = editor_summary.set_index('editor')['acceptance_rate']
                    prev_rates = prev_editor_summary.set_index('editor')['acceptance_rate']
                    
                    # Combine rates for comparison
                    rates_comparison = pd.DataFrame({
                        'Current Period': current_rates,
                        'Previous Period': prev_rates
                    }).fillna(0).reset_index()
                    
                    fig = px.bar(
                        rates_comparison.melt(id_vars='editor', var_name='Period', value_name='Acceptance Rate'),
                        x='Acceptance Rate',
                        y='editor',
                        color='Period',
                        orientation='h',
                        title=f"Acceptance Rate Comparison ({period_option} vs Previous)",
                        labels={'Acceptance Rate': 'Acceptance Rate (%)', 'editor': 'Editor'},
                        color_discrete_map={'Current Period': '#2ca02c', 'Previous Period': '#d62728'},
                        barmode='group'
                    )
                else:
                    fig = px.bar(
                        editor_summary.sort_values('acceptance_rate', ascending=True),
                        x='acceptance_rate',
                        y='editor',
                        orientation='h',
                        title=f"Code Acceptance Rate by Editor ({period_option})",
                        labels={'acceptance_rate': 'Acceptance Rate (%)', 'editor': 'Editor'}
                    )
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True, key="editor_acceptance_rates")
    
    else:
        st.info("No editor data available for analysis")

def render_chat_interactions(df):
    """Render chat interaction analysis (copy/paste events)."""
    st.header("💬 Chat Interactions")
    
    if df.empty:
        st.warning("No data available")
        return
    
    # Extract chat copy/insertion events
    chat_events = []
    for _, row in df.iterrows():
        try:
            ide_chat = row['copilot_ide_chat']
            if isinstance(ide_chat, dict) and 'editors' in ide_chat:
                for editor in ide_chat['editors']:
                    if 'models' in editor and len(editor['models']) > 0:
                        for model in editor['models']:
                            chat_events.append({
                                'date': row['date'],
                                'organization': row['organization'],
                                'editor': editor['name'],
                                'model': model['name'],
                                'copy_events': model.get('total_chat_copy_events', 0),
                                'insertion_events': model.get('total_chat_insertion_events', 0),
                                'total_chats': model.get('total_chats', 0),
                                'engaged_users': model.get('total_engaged_users', 0)
                            })
        except Exception as e:
            continue
    
    if not chat_events:
        st.info("No chat interaction data available")
        return
    
    chat_df = pd.DataFrame(chat_events)
    
    # Period filter for chat interactions
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        period_option = st.selectbox(
            "Select Period View",
            ["Last 7 days", "Last 14 days", "Last 30 days", "All time"],
            index=1,  # Default to Last 14 days for chat
            key="chat_period_filter"
        )
    
    with col2:
        compare_previous = st.checkbox(
            "Compare with Previous Period",
            value=False,
            key="chat_compare_filter"
        )
    
    # Filter data based on period selection
    filtered_chat_df = chat_df.copy()
    previous_chat_df = pd.DataFrame()
    
    if period_option != "All time":
        max_date = chat_df['date'].max()
        if period_option == "Last 7 days":
            days = 7
            start_date = max_date - pd.Timedelta(days=days-1)
        elif period_option == "Last 14 days":
            days = 14
            start_date = max_date - pd.Timedelta(days=days-1)
        elif period_option == "Last 30 days":
            days = 30
            start_date = max_date - pd.Timedelta(days=days-1)
        
        filtered_chat_df = chat_df[chat_df['date'] >= start_date]
        
        # Calculate previous period if comparison is enabled
        if compare_previous:
            prev_start = start_date - pd.Timedelta(days=days)
            prev_end = start_date - pd.Timedelta(days=1)
            previous_chat_df = chat_df[(chat_df['date'] >= prev_start) & (chat_df['date'] <= prev_end)]
    
    # Metrics overview
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate previous period metrics for comparison
    prev_total_copy = previous_chat_df['copy_events'].sum() if compare_previous and not previous_chat_df.empty else 0
    prev_total_insertion = previous_chat_df['insertion_events'].sum() if compare_previous and not previous_chat_df.empty else 0
    prev_total_chats = previous_chat_df['total_chats'].sum() if compare_previous and not previous_chat_df.empty else 0
    
    with col1:
        total_copy = filtered_chat_df['copy_events'].sum()
        delta_copy = total_copy - prev_total_copy if compare_previous else None
        st.metric(
            "Total Copy Events", 
            f"{total_copy:,}",
            delta=f"{delta_copy:+,}" if delta_copy is not None else None,
            help="Number of times users copied code suggestions from Copilot Chat"
        )
    
    with col2:
        total_insertion = filtered_chat_df['insertion_events'].sum()
        delta_insertion = total_insertion - prev_total_insertion if compare_previous else None
        st.metric(
            "Total Insertion Events", 
            f"{total_insertion:,}",
            delta=f"{delta_insertion:+,}" if delta_insertion is not None else None,
            help="Number of times code was directly inserted from Copilot Chat into the editor"
        )
    
    with col3:
        total_chats = filtered_chat_df['total_chats'].sum()
        delta_chats = total_chats - prev_total_chats if compare_previous else None
        st.metric(
            "Total IDE Chats", 
            f"{total_chats:,}",
            delta=f"{delta_chats:+,}" if delta_chats is not None else None,
            help="Total number of chat interactions with Copilot in IDEs"
        )
    
    with col4:
        avg_copy_rate = (total_copy / total_chats * 100) if total_chats > 0 else 0
        prev_copy_rate = (prev_total_copy / prev_total_chats * 100) if prev_total_chats > 0 else 0
        delta_rate = avg_copy_rate - prev_copy_rate if compare_previous else None
        st.metric(
            "Copy Rate", 
            f"{avg_copy_rate:.1f}%",
            delta=f"{delta_rate:+.1f}%" if delta_rate is not None else None,
            help="Percentage of chat interactions that resulted in code being copied. Higher rates indicate users find chat suggestions valuable"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily chat interactions
        daily_events = filtered_chat_df.groupby('date').agg({
            'copy_events': 'sum',
            'insertion_events': 'sum',
            'total_chats': 'sum'
        }).reset_index()
        
        fig = px.line(
            daily_events,
            x='date',
            y=['copy_events', 'insertion_events'],
            title=f"Daily Chat Copy/Insertion Events ({period_option})",
            labels={'value': 'Events', 'date': 'Date'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key="chat_daily_events")
        st.caption("📈 Track daily chat interactions to identify usage patterns and peaks")
    
    with col2:
        # Events by editor
        editor_events = filtered_chat_df.groupby('editor').agg({
            'copy_events': 'sum',
            'insertion_events': 'sum'
        }).reset_index()
        
        fig = px.bar(
            editor_events,
            x='editor',
            y=['copy_events', 'insertion_events'],
            title=f"Chat Events by Editor ({period_option})",
            labels={'value': 'Events', 'editor': 'Editor'},
            barmode='group'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key="chat_events_by_editor")
        st.caption("🔧 Compare how different editors facilitate chat-to-code workflows")

def render_github_dotcom_usage(df):
    """Render GitHub.com (web) usage analysis."""
    st.header("🌐 GitHub.com Usage")
    
    if df.empty:
        st.warning("No data available")
        return
    
    # Extract GitHub.com data
    dotcom_data = []
    for _, row in df.iterrows():
        try:
            # Dotcom Chat
            dotcom_chat = row['copilot_dotcom_chat']
            if isinstance(dotcom_chat, dict) and 'models' in dotcom_chat:
                for model in dotcom_chat['models']:
                    dotcom_data.append({
                        'date': row['date'],
                        'organization': row['organization'],
                        'feature': 'Web Chat',
                        'model': model['name'],
                        'is_custom': model.get('is_custom_model', False),
                        'total_chats': model.get('total_chats', 0),
                        'engaged_users': model.get('total_engaged_users', 0)
                    })
            
            # Dotcom Pull Requests
            dotcom_pr = row['copilot_dotcom_pull_requests']
            if isinstance(dotcom_pr, dict):
                dotcom_data.append({
                    'date': row['date'],
                    'organization': row['organization'],
                    'feature': 'Pull Requests',
                    'model': 'default',
                    'is_custom': False,
                    'total_chats': 0,  # Not applicable
                    'engaged_users': dotcom_pr.get('total_engaged_users', 0)
                })
        except Exception as e:
            continue
    
    if not dotcom_data:
        st.info("No GitHub.com usage data available")
        return
    
    dotcom_df = pd.DataFrame(dotcom_data)
    
    # Period filter for GitHub.com usage
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        period_option = st.selectbox(
            "Select Period View",
            ["Last 7 days", "Last 14 days", "Last 30 days", "All time"],
            index=1,  # Default to Last 14 days for dotcom
            key="dotcom_period_filter"
        )
    
    with col2:
        compare_previous = st.checkbox(
            "Compare with Previous Period",
            value=False,
            key="dotcom_compare_filter"
        )
    
    # Filter data based on period selection
    filtered_dotcom_df = dotcom_df.copy()
    previous_dotcom_df = pd.DataFrame()
    
    if period_option != "All time":
        max_date = dotcom_df['date'].max()
        if period_option == "Last 7 days":
            days = 7
            start_date = max_date - pd.Timedelta(days=days-1)
        elif period_option == "Last 14 days":
            days = 14
            start_date = max_date - pd.Timedelta(days=days-1)
        elif period_option == "Last 30 days":
            days = 30
            start_date = max_date - pd.Timedelta(days=days-1)
        
        filtered_dotcom_df = dotcom_df[dotcom_df['date'] >= start_date]
        
        # Calculate previous period if comparison is enabled
        if compare_previous:
            prev_start = start_date - pd.Timedelta(days=days)
            prev_end = start_date - pd.Timedelta(days=1)
            previous_dotcom_df = dotcom_df[(dotcom_df['date'] >= prev_start) & (dotcom_df['date'] <= prev_end)]
    
    # Metrics overview
    col1, col2, col3 = st.columns(3)
    
    # Calculate previous period metrics for comparison
    prev_web_chats = previous_dotcom_df[previous_dotcom_df['feature'] == 'Web Chat']['total_chats'].sum() if compare_previous and not previous_dotcom_df.empty else 0
    prev_web_users = previous_dotcom_df[previous_dotcom_df['feature'] == 'Web Chat']['engaged_users'].sum() if compare_previous and not previous_dotcom_df.empty else 0
    prev_pr_users = previous_dotcom_df[previous_dotcom_df['feature'] == 'Pull Requests']['engaged_users'].sum() if compare_previous and not previous_dotcom_df.empty else 0
    
    with col1:
        web_chats = filtered_dotcom_df[filtered_dotcom_df['feature'] == 'Web Chat']['total_chats'].sum()
        delta_chats = web_chats - prev_web_chats if compare_previous else None
        st.metric(
            "Total Web Chats", 
            f"{web_chats:,}",
            delta=f"{delta_chats:+,}" if delta_chats is not None else None,
            help="Total number of chat interactions on GitHub.com web interface"
        )
    
    with col2:
        web_users = filtered_dotcom_df[filtered_dotcom_df['feature'] == 'Web Chat']['engaged_users'].sum()
        delta_web_users = web_users - prev_web_users if compare_previous else None
        st.metric(
            "Web Chat Users", 
            f"{web_users:,}",
            delta=f"{delta_web_users:+,}" if delta_web_users is not None else None,
            help="Number of unique users who interacted with Copilot chat on GitHub.com"
        )
    
    with col3:
        pr_users = filtered_dotcom_df[filtered_dotcom_df['feature'] == 'Pull Requests']['engaged_users'].sum()
        delta_pr_users = pr_users - prev_pr_users if compare_previous else None
        st.metric(
            "PR Feature Users", 
            f"{pr_users:,}",
            delta=f"{delta_pr_users:+,}" if delta_pr_users is not None else None,
            help="Number of users who used Copilot features in Pull Requests on GitHub.com"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily usage trends
        daily_usage = filtered_dotcom_df.groupby(['date', 'feature']).agg({
            'engaged_users': 'sum'
        }).reset_index()
        
        fig = px.line(
            daily_usage,
            x='date',
            y='engaged_users',
            color='feature',
            title=f"Daily GitHub.com Feature Usage ({period_option})",
            labels={'engaged_users': 'Engaged Users', 'date': 'Date'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key="dotcom_daily_usage")
        st.caption("🌐 Monitor web-based Copilot feature adoption across GitHub.com")
    
    with col2:
        # Model usage (custom vs default)
        if 'model' in filtered_dotcom_df.columns:
            model_usage = filtered_dotcom_df.groupby(['model', 'is_custom']).agg({
                'engaged_users': 'sum'
            }).reset_index()
            
            fig = px.bar(
                model_usage,
                x='model',
                y='engaged_users',
                color='is_custom',
                title=f"Model Usage ({period_option})",
                labels={'engaged_users': 'Engaged Users', 'model': 'Model'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, key="dotcom_model_usage")
            st.caption("🤖 Compare usage between custom and default models on GitHub.com")

def render_data_insights(df):
    """Render data freshness and collection insights."""
    st.header("📈 Data Insights")
    
    if df.empty:
        st.warning("No data available")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Data freshness
        latest_download = df['download_timestamp'].max()
        hours_ago = (pd.Timestamp.now(tz=latest_download.tz) - latest_download).total_seconds() / 3600
        st.metric(
            "Data Freshness", 
            f"{hours_ago:.1f}h ago",
            help="Time elapsed since the most recent data collection. Fresher data means more current insights."
        )
    
    with col2:
        # Data coverage
        date_range = (df['date'].max() - df['date'].min()).days + 1
        st.metric(
            "Data Coverage", 
            f"{date_range} days",
            help="Total time span covered by the collected data. Longer coverage enables better trend analysis."
        )
    
    with col3:
        # Collection consistency
        org_coverage = df.groupby('organization')['date'].nunique()
        if len(org_coverage) > 1 and org_coverage.mean() > 0:
            consistency_variance = (org_coverage.std() / org_coverage.mean() * 100)
            if pd.isna(consistency_variance):
                consistency_score = 100.0
            else:
                consistency_score = max(0, 100 - consistency_variance)
        else:
            consistency_score = 100.0
        
        st.metric(
            "Collection Consistency", 
            f"{consistency_score:.1f}%",
            help="Measures how evenly data is collected across organizations. Higher scores indicate more balanced data collection"
        )
    
    # Download patterns
    col1, col2 = st.columns(2)
    
    with col1:
        # Downloads by organization
        download_counts = df.groupby('organization')['download_timestamp'].nunique().reset_index()
        download_counts.columns = ['organization', 'download_sessions']
        
        fig = px.bar(
            download_counts,
            x='organization',
            y='download_sessions',
            title="Download Sessions by Organization",
            labels={'download_sessions': 'Download Sessions', 'organization': 'Organization'}
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True, key="data_download_sessions")
        st.caption("📊 Track data collection activity across different organizations")
    
    with col2:
        # Data collection timeline
        timeline = df.groupby('download_timestamp').size().reset_index()
        timeline.columns = ['download_timestamp', 'records_collected']
        
        fig = px.line(
            timeline,
            x='download_timestamp',
            y='records_collected',
            title="Data Collection Timeline",
            labels={'records_collected': 'Records Collected', 'download_timestamp': 'Download Time'}
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True, key="data_collection_timeline")
        st.caption("⏰ Monitor when data collection occurs and how much data is gathered")

# =====================================================================
# MAIN FUNCTION
# =====================================================================

def main():
    st.title("🤖 GitHub Copilot Analytics Dashboard")
    st.markdown("📊 **Open-source insights into GitHub Copilot usage across your organization**")
    
    # File upload section
    st.sidebar.header("📁 Data Source")
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload your Copilot data (Parquet file)",
        type=['parquet'],
        help="Upload the .parquet file generated by the data collection script"
    )
    
    df = None
    
    if uploaded_file is not None:
        with st.spinner("Loading uploaded data..."):
            df = load_data_from_file(uploaded_file)
            if df is not None:
                st.sidebar.success(f"✅ Loaded: {uploaded_file.name}")
                st.sidebar.info(f"📊 {len(df)} records loaded")
    else:
        # Try to load local file for development
        local_df = load_data_local()
        if local_df is not None:
            df = local_df
            st.sidebar.info("🔧 Using local development data")
        else:
            # Welcome screen for new users
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.markdown("""
                <div style="text-align: center; padding: 2rem; background-color: #f0f2f6; border-radius: 10px; margin: 2rem 0;">
                    <h2>👋 Welcome to GitHub Copilot Analytics!</h2>
                    <p style="font-size: 1.1em; color: #666;">
                        Analyze your GitHub Copilot usage with beautiful, interactive charts
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### 🚀 Getting Started")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                #### 📊 Collect Your Data
                1. **Install GitHub CLI** and authenticate
                2. **Clone this repository** to your local machine
                3. **Run the collection script**:
                   ```bash
                   ./collect_metrics.sh --org your-organization
                   ```
                4. **Process the data**:
                   ```bash
                   python main.py
                   ```
                """)
            
            with col2:
                st.markdown("""
                #### 📈 Analyze Your Data
                1. **Upload your file** using the sidebar ⬅️
                2. **Explore interactive charts** showing:
                   - Usage trends over time
                   - Programming language preferences
                   - Editor usage statistics
                   - Chat interaction patterns
                   - User engagement metrics
                """)
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                #### 🔒 Privacy First
                - All data stays on your machine
                - No data stored in the cloud
                - Session-only processing
                """)
            
            with col2:
                st.markdown("""
                #### 🌟 Open Source
                - MIT Licensed
                - Community driven
                - Easy to customize
                """)
            
            with col3:
                st.markdown("""
                #### 📚 Documentation
                - [Setup Guide](https://github.com/codaqui/copilot-dashboard)
                - [API Reference](https://docs.github.com/en/rest/copilot)
                - [Deployment Guide](https://github.com/codaqui/copilot-dashboard/blob/main/README.md)
                """)
            
            st.info("👆 **Ready to start?** Upload your `.parquet` file using the sidebar to begin analyzing your Copilot data!")
            st.stop()
    
    if df is None or df.empty:
        st.error("Could not load data. Please check your file and try again.")
        st.stop()
    
    # Process data
    lang_df = extract_language_metrics(df)
    chat_df = extract_chat_metrics(df)
    
    # Sidebar filters
    st.sidebar.header("📋 Filters")
    
    # Date range filter
    if not df.empty:
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
            lang_df = lang_df[(lang_df['date'].dt.date >= start_date) & (lang_df['date'].dt.date <= end_date)]
            chat_df = chat_df[(chat_df['date'].dt.date >= start_date) & (chat_df['date'].dt.date <= end_date)]
    
    # Organization filter
    if 'organization' in df.columns:
        orgs = df['organization'].unique()
        if len(orgs) > 1:
            selected_org = st.sidebar.selectbox("Select Organization", orgs)
            df = df[df['organization'] == selected_org]
            lang_df = lang_df[lang_df['organization'] == selected_org]
            chat_df = chat_df[chat_df['organization'] == selected_org]
    
    # Render dashboard sections
    if not df.empty:
        render_overview(df)
        st.divider()
        render_trends(df)
        st.divider()
        render_language_analysis(lang_df)
        st.divider()
        render_editor_analysis(lang_df, chat_df)
        st.divider()
        render_chat_interactions(df)
        st.divider()
        render_github_dotcom_usage(df)
        st.divider()
        render_data_insights(df)
    else:
        st.warning("No data available for the selected filters")
    
    # Footer
    st.divider()
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 10px;">
            <p style="margin: 0; color: #666;">
                🤖 <strong>GitHub Copilot Analytics Dashboard</strong><br>
                Open-source tool for analyzing GitHub Copilot usage data<br>
                <a href="https://github.com/your-repo" target="_blank">📖 Documentation</a> | 
                <a href="https://github.com/your-repo/issues" target="_blank">🐛 Report Issues</a> | 
                <a href="https://github.com/your-repo" target="_blank">⭐ Star on GitHub</a>
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
