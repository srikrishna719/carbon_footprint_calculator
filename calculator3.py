import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import Dict, List

class MultimodalCarbonFootprintCalculator:
    def __init__(self):
        # Simplified emission factors in kg CO2 per tonne-km
        self.emission_factors: Dict[str, float] = {
            'car': 0.171,          # Personal car/van
            'truck': 0.096,        # Heavy duty truck
            'mini_truck': 0.137,   # Medium duty truck
            'railway': 0.028,      # Electric train average
            'seaway': 0.008        # Container ship average
        }
        
        # Define bold and bright colors for each transport mode
        self.mode_colors: Dict[str, str] = {
            'car': '#FF1E1E',          # Bright Red
            'truck': '#00FF00',        # Lime Green
            'mini_truck': '#1E90FF',   # Bright Blue
            'railway': '#FFD700',      # Gold
            'seaway': '#FF1493'        # Deep Pink
        }
        
        # Group modes for easier analysis
        self.mode_groups: Dict[str, List[str]] = {
            'roadways': ['car', 'truck', 'mini_truck'],
            'railways': ['railway'],
            'seaways': ['seaway']
        }

    def calculate_emissions(self, weight_kg: float, distance_km: float, transport_mode: str) -> Dict[str, any]:
        """Calculate carbon emissions for a shipment segment"""
        weight_tonnes = weight_kg / 1000
        emission_factor = self.emission_factors.get(transport_mode.lower())
        
        if not emission_factor:
            raise ValueError(f"Invalid transport mode. Choose from: {list(self.emission_factors.keys())}")
        
        emissions = weight_tonnes * distance_km * emission_factor
        efficiency = emissions / (weight_tonnes * distance_km)
        
        transport_group = next((group for group, modes in self.mode_groups.items() 
                             if transport_mode.lower() in modes), 'other')
        
        return {
            'timestamp': datetime.now(),
            'transport_mode': transport_mode,
            'transport_group': transport_group,
            'weight_kg': weight_kg,
            'distance_km': distance_km,
            'total_emissions_kg': emissions,
            'efficiency_kg_per_tonne_km': efficiency
        }

def delete_segment(index):
    st.session_state.route_segments.pop(index)
    st.success("✅ Segment deleted successfully!")

def main():
    # Set page config for wider layout
    st.set_page_config(layout="wide", page_title="Carbon Footprint Calculator")
    
    # Custom CSS for styling
    st.markdown("""
        <style>
        .stMetric {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
        }
        .stMetric:hover {
            background-color: #e0e2e6;
        }
        .stDataFrame {
            border: 1px solid #e0e2e6;
            border-radius: 10px;
        }
        .segment-box {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e0e2e6;
            margin: 10px 0;
        }
        .delete-button {
            color: #FF1E1E;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🌍 Multimodal Carbon Footprint Calculator")
    
    # Initialize calculator
    calculator = MultimodalCarbonFootprintCalculator()
    
    # Initialize session state for storing segments
    if 'route_segments' not in st.session_state:
        st.session_state.route_segments = []
    
    # Input section with improved styling
    st.header("📝 Add Route Segment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        weight = st.number_input("Cargo Weight (kg)", min_value=0.1, value=1000.0)
    
    with col2:
        mode = st.selectbox("Transport Mode", options=list(calculator.emission_factors.keys()))
    
    with col3:
        distance = st.number_input("Distance (km)", min_value=0.1, value=100.0)
    
    # Add segment button with styling
    if st.button("➕ Add Segment", key="add_segment"):
        segment = {
            'mode': mode,
            'distance': distance,
            'weight': weight
        }
        st.session_state.route_segments.append(segment)
        st.success("✅ Segment added successfully!")
    
    # Display current segments with delete buttons
    if st.session_state.route_segments:
        st.header("🚦 Current Route Segments")
        
        for idx, segment in enumerate(st.session_state.route_segments):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 3, 3, 1])
                
                with col1:
                    st.markdown(f"**Mode:** {segment['mode'].title()}")
                with col2:
                    st.markdown(f"**Distance:** {segment['distance']} km")
                with col3:
                    st.markdown(f"**Weight:** {segment['weight']} kg")
                with col4:
                    st.button("🗑️", key=f"delete_{idx}", on_click=delete_segment, args=(idx,))
        
        # Calculate emissions
        results = []
        total_emissions = 0
        total_distance = 0
        
        for segment in st.session_state.route_segments:
            result = calculator.calculate_emissions(
                segment['weight'],
                segment['distance'],
                segment['mode']
            )
            results.append(result)
            total_emissions += result['total_emissions_kg']
            total_distance += segment['distance']
        
        # Display total emissions with improved styling
        st.header("📊 Emissions Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Emissions", f"{total_emissions:.2f} kg CO₂", 
                     delta=f"{total_emissions/1000:.2f} tonnes CO₂")
        with col2:
            st.metric("Total Distance", f"{total_distance:.2f} km", 
                     delta=f"{total_distance/1000:.2f} thousand km")
        
        # Create visualization with enhanced colors
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('📈 Emissions by Segment', '🎯 Percentage Contribution'),
            specs=[[{"type": "bar"}],
                  [{"type": "pie"}]],
            vertical_spacing=0.3
        )
        
        # Add bar chart with custom colors
        bar_colors = [calculator.mode_colors[r['transport_mode']] for r in results]
        fig.add_trace(
            go.Bar(
                x=[f"{r['transport_mode']} ({r['distance_km']} km)" for r in results],
                y=[r['total_emissions_kg'] for r in results],
                name="Emissions",
                marker_color=bar_colors,
                marker_line_color='rgb(8,48,107)',
                marker_line_width=1.5,
                opacity=0.9,
                hovertemplate="<b>%{x}</b><br>" +
                             "Emissions: %{y:.2f} kg CO₂<br>" +
                             "<extra></extra>"
            ),
            row=1, col=1
        )
        
        # Add pie chart with custom colors
        fig.add_trace(
            go.Pie(
                labels=[f"{r['transport_mode']} ({r['distance_km']} km)" for r in results],
                values=[r['total_emissions_kg'] for r in results],
                name="Contribution",
                marker=dict(colors=bar_colors),
                hole=0.4,
                textinfo='label+percent',
                textposition='outside',
                hovertemplate="<b>%{label}</b><br>" +
                             "Emissions: %{value:.2f} kg CO₂<br>" +
                             "Percentage: %{percent}<br>" +
                             "<extra></extra>"
            ),
            row=2, col=1
        )
        
        # Update layout with enhanced styling and black hover labels
        fig.update_layout(
            height=800,
            title_text="Multimodal Route Analysis",
            showlegend=False,
            template="plotly_white",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            title=dict(
                font=dict(size=24)
            ),
            hoverlabel=dict(
                bgcolor="black",
                font_size=16,
                font_family="Rockwell",
                font_color="white",
                bordercolor="black"
            )
        )
        
        # Update axes styling
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)',
                        tickangle=45, title_font=dict(size=14))
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)',
                        title_font=dict(size=14))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed breakdown with improved styling
        st.header("📋 Detailed Breakdown")
        for r in results:
            with st.expander(f"🔍 {r['transport_mode'].title()} Segment Details"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Distance", f"{r['distance_km']} km")
                with col2:
                    st.metric("Emissions", f"{r['total_emissions_kg']:.2f} kg CO₂")
                with col3:
                    st.metric("Efficiency", f"{r['efficiency_kg_per_tonne_km']:.4f} kg CO₂/tonne-km")
        
        # Clear button with styling
        if st.button("🗑️ Clear All Segments", key="clear_segments"):
            st.session_state.route_segments = []
            st.experimental_rerun()

if __name__ == "__main__":
    main()