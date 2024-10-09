import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Cricket Analysis - BPI Calculator",
    page_icon="🏏",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1 {
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sample data for demonstration
@st.cache_data
def load_sample_data():
    return pd.DataFrame({
        'Player': ['MS Dhoni', 'Chris Gayle', 'AB de Villiers', 'Virat Kohli', 'Rohit Sharma'],
        'Average': [37.60, 27.92, 37.05, 52.73, 32.32],
        'Strike_Rate': [126.13, 137.50, 151.68, 138.43, 139.02],
        'Fifties': [2, 14, 22, 37, 29],
        'Hundreds': [0, 2, 1, 1, 4],
        'Boundary_Percentage': [47.99, 72.46, 58.32, 54.76, 62.18],
        'Not_Outs': [41, 7, 11, 15, 12]
    })

# Function to calculate BPI
def calculate_bpi(row):
    return (
        (row['Strike_Rate'] * 0.3) +
        (row['Not_Outs'] * 0.1) +
        (row['Hundreds'] * 0.05) +
        (row['Fifties'] * 0.15) +
        (row['Average'] * 0.2) +
        (row['Boundary_Percentage'] * 0.2)
    )

# Function to calculate DPPI
def calculate_dppi(avg, sr):
    return (avg * sr) / 100

# Main app layout
def main():
    st.title("Cricket Analysis - Batsman Performance Index (BPI)")
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "BPI Calculator", "Player Comparison", "About"])
    
    if page == "Home":
        show_home()
    elif page == "BPI Calculator":
        show_bpi_calculator()
    elif page == "Player Comparison":
        show_player_comparison()
    else:
        show_about()

def show_home():
    st.header("Welcome to Cricket Analysis")
    st.write("""
    This application implements the research findings on the Batsman Performance Index (BPI),
    a sophisticated metric for evaluating cricket batsmen's performance in T20 International matches.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Key Features")
        st.write("""
        - Calculate BPI for any player
        - Compare players across different eras
        - Visualize performance metrics
        - Analyze fan engagement correlation
        """)
    
    with col2:
        st.subheader("Why BPI?")
        st.write("""
        Traditional metrics like batting average and strike rate don't tell the complete story.
        BPI incorporates multiple factors to provide a more comprehensive evaluation of a batsman's impact.
        """)
    
    st.subheader("Sample BPI Analysis")
    data = load_sample_data()
    data['BPI'] = data.apply(calculate_bpi, axis=1)
    
    fig = px.bar(data, x='Player', y='BPI', title='BPI Comparison of Top Players')
    st.plotly_chart(fig)

def show_bpi_calculator():
    st.header("BPI Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        player_name = st.text_input("Player Name")
        avg = st.number_input("Batting Average", min_value=0.0, max_value=100.0, value=30.0)
        sr = st.number_input("Strike Rate", min_value=0.0, max_value=200.0, value=120.0)
    
    with col2:
        fifties = st.number_input("Number of Fifties", min_value=0, max_value=100, value=10)
        hundreds = st.number_input("Number of Hundreds", min_value=0, max_value=50, value=1)
        boundary_percent = st.number_input("Boundary Percentage", min_value=0.0, max_value=100.0, value=50.0)
        not_outs = st.number_input("Number of Not Outs", min_value=0, max_value=100, value=5)
    
    if st.button("Calculate BPI"):
        bpi = calculate_bpi(pd.Series({
            'Average': avg,
            'Strike_Rate': sr,
            'Fifties': fifties,
            'Hundreds': hundreds,
            'Boundary_Percentage': boundary_percent,
            'Not_Outs': not_outs
        }))
        
        dppi = calculate_dppi(avg, sr)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("BPI Score", f"{bpi:.2f}")
        with col2:
            st.metric("DPPI Score", f"{dppi:.2f}")
        
        st.write("### Performance Breakdown")
        metrics = {
            'Strike Rate Contribution': sr * 0.3,
            'Not Outs Contribution': not_outs * 0.1,
            'Hundreds Contribution': hundreds * 0.05,
            'Fifties Contribution': fifties * 0.15,
            'Average Contribution': avg * 0.2,
            'Boundary % Contribution': boundary_percent * 0.2
        }
        
        fig = px.pie(values=list(metrics.values()), names=list(metrics.keys()),
                     title=f'BPI Components for {player_name if player_name else "Player"}')
        st.plotly_chart(fig)

def show_player_comparison():
    st.header("Player Comparison")
    
    data = load_sample_data()
    data['BPI'] = data.apply(calculate_bpi, axis=1)
    data['DPPI'] = data.apply(lambda x: calculate_dppi(x['Average'], x['Strike_Rate']), axis=1)
    
    selected_players = st.multiselect("Select players to compare", data['Player'].tolist(),
                                      default=data['Player'].tolist()[:2])
    
    if len(selected_players) > 0:
        comparison_data = data[data['Player'].isin(selected_players)]
        
        # Radar chart
        categories = ['Average', 'Strike_Rate', 'Fifties', 'Hundreds', 'Boundary_Percentage', 'Not_Outs']
        
        fig = go.Figure()
        for player in selected_players:
            player_data = comparison_data[comparison_data['Player'] == player]
            values = player_data[categories].values.flatten().tolist()
            values += values[:1]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name=player
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max(data[categories].max())])),
            showlegend=True,
            title="Player Statistics Comparison"
        )
        
        st.plotly_chart(fig)
        
        # Bar chart comparison
        st.subheader("BPI vs DPPI Comparison")
        fig_bar = go.Figure(data=[
            go.Bar(name='BPI', x=comparison_data['Player'], y=comparison_data['BPI']),
            go.Bar(name='DPPI', x=comparison_data['Player'], y=comparison_data['DPPI'])
        ])
        fig_bar.update_layout(barmode='group')
        st.plotly_chart(fig_bar)
        
        # Detailed stats table
        st.subheader("Detailed Statistics")
        st.dataframe(comparison_data)

def show_about():
    st.header("About This Project")
    st.write("""
    This application is based on the research paper "AI-Driven Analytics for Batsman Performance
    Index in T20I Cricket: A New Era of Evaluation" by Dr. Anil V Turukmane, Rahul Bharadwaj, Pranav Pendyala, Aryan Shinde, Digvijay Patil
    
    ### Key Concepts
    
    The Batsman Performance Index (BPI) is calculated using the formula:
    
    BPI = (SR × 0.3) + (Not Outs × 0.1) + (100s × 0.05) + (50s × 0.15) + (Avg × 0.2) + (Boundary% × 0.2)
    
    where:
    - SR: Strike Rate
    - Not Outs: Number of times the batsman remained not out
    - 100s: Number of centuries scored
    - 50s: Number of half-centuries scored
    - Avg: Batting average
    - Boundary%: Percentage of runs scored in boundaries
    
    ### Future Scope
    
    - Impact Player Identification
    - Injury Risk Prediction
    - Enhanced Fan Engagement Analysis
    - Integration with Fantasy Sports
    """)

if __name__ == "__main__":
    main()