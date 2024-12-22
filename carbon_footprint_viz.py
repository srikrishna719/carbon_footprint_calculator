import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List

class MultimodalCarbonFootprintCalculator:
    def __init__(self):
        self.emission_factors = {
            'car': 0.171,
            'truck': 0.096,
            'mini_truck': 0.137,
            'railway': 0.028,
            'seaway': 0.008
        }
        
        # Bold and bright colors for each transport mode
        self.mode_colors = {
            'car': '#FF4500',          # Bright Orange Red
            'truck': '#32CD32',        # Lime Green
            'mini_truck': '#1E90FF',   # Dodger Blue
            'railway': '#FFD700',      # Gold
            'seaway': '#FF1493'        # Deep Pink
        }
    
    def calculate_emissions(self, weight_kg: float, distance_km: float, transport_mode: str) -> Dict[str, any]:
        weight_tonnes = weight_kg / 1000
        emission_factor = self.emission_factors.get(transport_mode.lower())
        emissions = weight_tonnes * distance_km * emission_factor
        return {
            'transport_mode': transport_mode,
            'weight_kg': weight_kg,
            'distance_km': distance_km,
            'total_emissions_kg': emissions
        }

def dynamic_supply_chain_diagram(segments, mode_colors, calculator):
    fig = go.Figure()
    x, y = 0, 0  # Initial coordinates for the first node
    total_distance = sum(segment['distance'] for segment in segments)
    total_emissions = sum(
        segment['weight'] / 1000 * segment['distance'] * calculator.emission_factors[segment['mode']]
        for segment in segments
    )

    for idx, segment in enumerate(segments):
        mode = segment['mode']
        distance = segment['distance']
        weight = segment['weight']
        
        current_position = (x, y)
        next_position = (x + 1, y)

        # Draw line with a bold color
        fig.add_trace(go.Scatter(
            x=[current_position[0], next_position[0]],
            y=[current_position[1], next_position[1]],
            mode='lines+markers+text',
            line=dict(color=mode_colors[mode], width=4),
            marker=dict(size=18, color=mode_colors[mode]),
            text=[f"{mode.title()} ({distance} km)"],
            textposition="top center",
            hovertemplate=f"<b>{mode.title()}</b><br>Distance: {distance} km<br>Weight: {weight} kg<extra></extra>"
        ))

        # Add annotations with a background color for better visibility
        emissions_info = f"{mode.title()} - {distance} km, {weight} kg"
        fig.add_annotation(
            x=next_position[0],
            y=next_position[1],
            text=emissions_info,
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            ax=20,
            ay=-30,
            font=dict(color="white"),
            bgcolor=mode_colors[mode],
            bordercolor="black",
            borderwidth=1
        )
        
        x += 1  # Move horizontally to the next node

    # Add total distance and emissions in the top right corner
    fig.add_annotation(
        x=0.95,
        y=1.05,
        xref="paper",
        yref="paper",
        text=f"Total Distance: {total_distance:.2f} km<br>Total Emissions: {total_emissions:.2f} kg CO₂",
        showarrow=False,
        font=dict(size=12, color="white"),
        align="right",
        bordercolor="white",
        borderwidth=1,
        borderpad=5,
        bgcolor="rgba(50, 50, 50, 0.8)"
    )

    # Add a legend
    fig.update_layout(
        legend=dict(
            title="Transport Modes",
            itemsizing="constant",
            font=dict(size=12, color="white"),
            bgcolor="rgba(50, 50, 50, 0.8)"
        )
    )

    fig.update_layout(
        title="Dynamic Supply Chain Route Diagram",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600,
        showlegend=True,
        plot_bgcolor="black",   # Set plot background to black
        paper_bgcolor="black",  # Set entire paper background to black
        font=dict(color="white"),  # Set font color to white for visibility on black
        hoverlabel=dict(
            bgcolor="black",       # Set hover label background to black
            font_color="white"     # Set hover text color to white for contrast
        )
    )

    return fig

def delete_segment(index):
    st.session_state.route_segments.pop(index)
    st.success("✅ Segment deleted successfully!")

def main():
    st.set_page_config(layout="wide", page_title="Carbon Footprint Calculator")
    st.title("🌍 Multimodal Carbon Footprint Calculator")
    
    calculator = MultimodalCarbonFootprintCalculator()
    
    if 'route_segments' not in st.session_state:
        st.session_state.route_segments = []
    
    st.header("📝 Add Route Segment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        weight = st.number_input("Cargo Weight (kg)", min_value=0.1, value=1000.0)
    
    with col2:
        mode = st.selectbox("Transport Mode", options=list(calculator.emission_factors.keys()))
    
    with col3:
        distance = st.number_input("Distance (km)", min_value=0.1, value=100.0)
    
    if st.button("➕ Add Segment", key="add_segment"):
        segment = {
            'mode': mode,
            'distance': distance,
            'weight': weight
        }
        st.session_state.route_segments.append(segment)
        st.success("✅ Segment added successfully!")
    
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
        
        # Display dynamic route diagram
        st.header("🚗 Dynamic Supply Chain Route Diagram")
        fig = dynamic_supply_chain_diagram(st.session_state.route_segments, calculator.mode_colors, calculator)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()