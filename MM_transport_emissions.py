import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import Dict, List, Tuple

class MultimodalCarbonFootprintCalculator:
    def __init__(self):
        # Updated emission factors (2024 values) in kg CO2 per tonne-km
        self.emission_factors: Dict[str, float] = {
            'car': 0.158,          # Personal car/van (EV adoption impact)
            'truck': 0.088,        # Heavy duty truck (improved efficiency)
            'mini_truck': 0.122,   # Medium duty truck
            'railway': 0.023,      # Electric train (renewable energy mix)
            'seaway': 0.007,       # Container ship (slow steaming optimization)
            'air': 0.805,          # Air freight (new addition)
            'barge': 0.035         # Inland waterways (new addition)
        }
        
        # Modern color palette with accessibility considerations
        self.mode_colors: Dict[str, str] = {
            'car': '#FF6B6B',        # Coral
            'truck': '#4ECDC4',      # Turquoise
            'mini_truck': '#1A535C',  # Dark teal
            'railway': '#FFD166',     # Yellow
            'seaway': '#EF476F',      # Pink
            'air': '#118AB2',         # Blue
            'barge': '#073B4C'        # Navy
        }
        
        # Enhanced mode groupings
        self.mode_groups: Dict[str, List[str]] = {
            'road': ['car', 'truck', 'mini_truck'],
            'rail': ['railway'],
            'maritime': ['seaway', 'barge'],
            'air': ['air']
        }
        
        # Mode display names for UI
        self.mode_display_names = {
            'car': 'Car/Van',
            'truck': 'Heavy Truck',
            'mini_truck': 'Medium Truck',
            'railway': 'Train',
            'seaway': 'Cargo Ship',
            'air': 'Air Freight',
            'barge': 'River Barge'
        }
        
        # Create reverse mapping for display names to internal keys
        self.display_to_internal = {v: k for k, v in self.mode_display_names.items()}

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
            'display_name': self.mode_display_names.get(transport_mode, transport_mode),
            'transport_group': transport_group,
            'weight_kg': weight_kg,
            'distance_km': distance_km,
            'total_emissions_kg': emissions,
            'efficiency_kg_per_tonne_km': efficiency
        }

def dynamic_supply_chain_diagram(segments: List[Dict], calculator: MultimodalCarbonFootprintCalculator) -> go.Figure:
    """Create an interactive supply chain visualization"""
    fig = go.Figure()
    x, y = 0, 0
    node_positions = []
    total_emissions = 0
    
    # Calculate positions and emissions
    for idx, segment in enumerate(segments):
        result = calculator.calculate_emissions(
            segment['weight'], segment['distance'], segment['mode']
        )
        total_emissions += result['total_emissions_kg']
        
        # Create curved paths for visual interest
        next_x = x + 1
        next_y = y + (0.5 if idx % 2 == 0 else -0.5)  # Alternating curve direction
        
        # Store node positions for labels
        node_positions.append((x, y, segment['mode']))
        node_positions.append((next_x, next_y, segment['mode']))
        
        # Create curved line
        fig.add_trace(go.Scatter(
            x=[x, (x+next_x)/2, next_x],
            y=[y, (y+next_y)/2 + (0.3 if idx % 2 == 0 else -0.3), next_y],
            mode='lines',
            line=dict(
                color=calculator.mode_colors[segment['mode']],
                width=8,
                shape='spline'
            ),
            hoverinfo='none',
            showlegend=False
        ))
        
        # Add mode marker
        fig.add_trace(go.Scatter(
            x=[(x+next_x)/2],
            y=[(y+next_y)/2 + (0.3 if idx % 2 == 0 else -0.3)],
            mode='markers+text',
            marker=dict(
                size=25,
                color=calculator.mode_colors[segment['mode']],
                line=dict(width=2, color='white')
            ),
            text=[calculator.mode_display_names.get(segment['mode'], segment['mode'])],
            textposition='middle center',
            textfont=dict(color='white', size=10),
            hoverinfo='none',
            showlegend=False
        ))
        
        # Add distance label
        fig.add_annotation(
            x=(x+next_x)/2,
            y=(y+next_y)/2 + (0.5 if idx % 2 == 0 else -0.5),
            text=f"{segment['distance']} km",
            showarrow=False,
            font=dict(size=10, color='white'),
            bgcolor='rgba(0,0,0,0.7)',
            bordercolor='white',
            borderwidth=1
        )
        
        x, y = next_x, next_y
    
    # Add start and end nodes
    fig.add_trace(go.Scatter(
        x=[0, x],
        y=[0, y],
        mode='markers',
        marker=dict(size=30, color=['#6A994E', '#BC4749']),
        text=['Start', 'End'],
        textposition='middle center',
        textfont=dict(color='white', size=12),
        hoverinfo='none',
        showlegend=False
    ))
    
    # Add emissions summary
    fig.add_annotation(
        x=0.5,
        y=1.1,
        xref="paper",
        yref="paper",
        text=f"<b>Total Emissions: {total_emissions:.1f} kg CO₂</b>",
        showarrow=False,
        font=dict(size=16, color='white'),
        align="center",
        bgcolor='rgba(40, 40, 40, 0.8)',
        bordercolor='white',
        borderwidth=1
    )
    
    # Configure layout
    fig.update_layout(
        title="Dynamic Supply Chain Route Visualization",
        xaxis=dict(visible=False, range=[-0.5, len(segments)+0.5]),
        yaxis=dict(visible=False, range=[min(-1, y-1), max(1, y+1)]),
        height=500,
        showlegend=False,
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        margin=dict(t=80, b=20, l=20, r=20)
    )
    
    return fig

def delete_segment(index: int):
    st.session_state.route_segments.pop(index)
    st.toast("✅ Segment deleted successfully!", icon="✅")

def reset_session():
    st.session_state.route_segments = []
    st.toast("🧹 All segments cleared!", icon="🧹")

def main():
    # Modern page configuration
    st.set_page_config(
        layout="wide", 
        page_title="EcoRoute Carbon Calculator",
        page_icon="🌿",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for modern styling
    st.markdown("""
    <style>
    /* Main page styling */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #ffffff;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(15, 32, 39, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid #2c5364;
    }
    
    /* Card styling */
    .segment-card {
        background: rgba(20, 30, 48, 0.7) !important;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #2c5364;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .segment-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        border: 1px solid #4ECDC4;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #4ECDC4, #2a9d8f) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background: rgba(20, 30, 48, 0.7) !important;
        border: 1px solid #2c5364 !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    
    /* Tab styling */
    [data-baseweb="tab-list"] {
        gap: 10px !important;
    }
    
    [data-baseweb="tab"] {
        background: rgba(20, 30, 48, 0.7) !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        margin: 0 5px !important;
        border: 1px solid #2c5364 !important;
        transition: all 0.3s ease !important;
    }
    
    [data-baseweb="tab"]:hover {
        border-color: #4ECDC4 !important;
    }
    
    [aria-selected="true"] {
        background: linear-gradient(135deg, #4ECDC4, #2a9d8f) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize calculator
    calculator = MultimodalCarbonFootprintCalculator()
    
    # Initialize session state
    if 'route_segments' not in st.session_state:
        st.session_state.route_segments = []
    
    # Sidebar configuration
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2455/2455300.png", width=80)
        st.title("🌱 EcoRoute Calculator")
        st.caption("Multimodal Carbon Footprint Analysis")
        st.divider()
        
        st.header("📝 Add Segment")
        weight = st.number_input("Cargo Weight (kg)", min_value=0.1, value=1000.0, step=50.0)
        mode = st.selectbox("Transport Mode", 
                          options=list(calculator.emission_factors.keys()),
                          format_func=lambda x: calculator.mode_display_names.get(x, x))
        distance = st.number_input("Distance (km)", min_value=0.1, value=100.0, step=10.0)
        
        if st.button("➕ Add Segment", use_container_width=True):
            segment = {'mode': mode, 'distance': distance, 'weight': weight}
            st.session_state.route_segments.append(segment)
            st.toast(f"✅ {calculator.mode_display_names.get(mode, mode)} segment added!", icon="✅")
        
        st.divider()
        
        if st.button("🧹 Clear All Segments", use_container_width=True, on_click=reset_session):
            pass
        
        st.divider()
        st.caption("🔍 Emission factors based on 2024 IEA data")
        st.caption("💡 Tip: Add at least 2 segments for optimal visualization")
    
    # Main content
    st.title("🌍 EcoRoute: Multimodal Carbon Footprint Analyzer")
    st.caption("Optimize your supply chain sustainability with real-time emissions tracking")
    
    # Display current segments
    if st.session_state.route_segments:
        st.header("🚚 Current Route Segments")
        for idx, segment in enumerate(st.session_state.route_segments):
            display_name = calculator.mode_display_names.get(segment['mode'], segment['mode'])
            col1, col2, col3, col4 = st.columns([0.4, 0.2, 0.2, 0.2])
            
            with col1:
                st.markdown(
                    f"<div class='segment-card'>"
                    f"<h4 style='color:{calculator.mode_colors[segment['mode']]}; margin-bottom:0;'>"
                    f"{display_name}</h4></div>", 
                    unsafe_allow_html=True
                )
            
            with col2:
                st.metric("Distance", f"{segment['distance']} km")
            
            with col3:
                st.metric("Weight", f"{segment['weight']} kg")
            
            with col4:
                st.button("🗑️", key=f"delete_{idx}", on_click=delete_segment, 
                         args=(idx,), use_container_width=True)
    
    # Calculate emissions
    results = []
    total_emissions = 0
    total_distance = 0
    total_weight = 0
    
    for segment in st.session_state.route_segments:
        result = calculator.calculate_emissions(
            segment['weight'],
            segment['distance'],
            segment['mode']
        )
        results.append(result)
        total_emissions += result['total_emissions_kg']
        total_distance += segment['distance']
        total_weight += segment['weight']
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🌐 Supply Chain", "📋 Detailed Report"])
    
    with tab1:
        if st.session_state.route_segments:
            # Key metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Emissions", f"{total_emissions:.1f} kg CO₂", 
                         delta=f"{total_emissions/1000:.2f} tonnes")
            with col2:
                st.metric("Total Distance", f"{total_distance:.1f} km")
            with col3:
                st.metric("Total Cargo", f"{total_weight:.1f} kg")
            
            # Emissions breakdown
            st.subheader("🔎 Emissions Breakdown")
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('By Transport Mode', 'By Transport Category'),
                specs=[[{"type": "pie"}, {"type": "pie"}]],
                column_widths=[0.5, 0.5]
            )
            
            # Mode pie chart - FIXED: Use internal mode keys for colors
            mode_emissions = {}
            for r in results:
                display_name = r['display_name']
                # Map display name back to internal mode key
                internal_mode = calculator.display_to_internal.get(display_name, r['transport_mode'])
                mode_emissions[internal_mode] = mode_emissions.get(internal_mode, 0) + r['total_emissions_kg']
            
            fig.add_trace(
                go.Pie(
                    labels=[calculator.mode_display_names[m] for m in mode_emissions.keys()],
                    values=list(mode_emissions.values()),
                    hole=0.4,
                    marker=dict(colors=[calculator.mode_colors[m] for m in mode_emissions.keys()]),
                    textinfo='percent+label',
                    hoverinfo='label+value+percent',
                    name="By Mode"
                ),
                row=1, col=1
            )
            
            # Category pie chart
            category_emissions = {}
            for r in results:
                category_emissions[r['transport_group']] = category_emissions.get(r['transport_group'], 0) + r['total_emissions_kg']
            
            fig.add_trace(
                go.Pie(
                    labels=[g.capitalize() for g in category_emissions.keys()],
                    values=list(category_emissions.values()),
                    hole=0.4,
                    textinfo='percent+label',
                    hoverinfo='label+value+percent',
                    name="By Category"
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                height=400,
                showlegend=False,
                margin=dict(t=50, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Efficiency metrics
            st.subheader("🚀 Transport Efficiency Comparison")
            efficiency_data = []
            for mode, factor in calculator.emission_factors.items():
                efficiency_data.append({
                    'Mode': calculator.mode_display_names.get(mode, mode),
                    'Emission Factor': factor,
                    'Color': calculator.mode_colors[mode]
                })
            
            efficiency_df = pd.DataFrame(efficiency_data).sort_values('Emission Factor')
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=efficiency_df['Mode'],
                y=efficiency_df['Emission Factor'],
                marker_color=efficiency_df['Color'],
                text=efficiency_df['Emission Factor'].round(3),
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Factor: %{y:.3f} kg CO₂/tonne-km<extra></extra>'
            ))
            
            fig.update_layout(
                height=400,
                yaxis_title="kg CO₂ per tonne-km",
                xaxis_title="Transport Mode",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                hoverlabel=dict(bgcolor='rgba(30, 30, 30, 0.8)')
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if st.session_state.route_segments:
            st.subheader("🌐 Supply Chain Visualization")
            fig = dynamic_supply_chain_diagram(st.session_state.route_segments, calculator)
            st.plotly_chart(fig, use_container_width=True)
            
            if len(st.session_state.route_segments) < 2:
                st.warning("Add more segments to enhance the visualization")
        else:
            st.info("Add segments to visualize your supply chain")
    
    with tab3:
        if st.session_state.route_segments:
            st.subheader("📋 Detailed Emissions Report")
            
            # Create detailed report dataframe
            report_data = []
            for r in results:
                report_data.append({
                    'Segment': r['display_name'],
                    'Category': r['transport_group'].capitalize(),
                    'Distance (km)': r['distance_km'],
                    'Weight (kg)': r['weight_kg'],
                    'Emissions (kg CO₂)': r['total_emissions_kg'],
                    'Efficiency (kg CO₂/tonne-km)': r['efficiency_kg_per_tonne_km']
                })
            
            report_df = pd.DataFrame(report_data)
            st.dataframe(
                report_df.style.format({
                    'Emissions (kg CO₂)': '{:.1f}',
                    'Efficiency (kg CO₂/tonne-km)': '{:.4f}'
                }).background_gradient(cmap='viridis'),
                use_container_width=True
            )
            
            # Download button
            csv = report_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Download Report (CSV)",
                data=csv,
                file_name="carbon_footprint_report.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("Add segments to generate a detailed report")
    
    # Empty state messaging
    if not st.session_state.route_segments:
        st.markdown("""
        <div style="text-align: center; padding: 50px 20px; border-radius: 15px; 
                    background: rgba(20, 30, 48, 0.7); border: 2px dashed #2c5364;">
            <h3>🚀 Get Started</h3>
            <p>Add your first route segment using the sidebar to begin calculating emissions</p>
            <p>👉 Select a transport mode, enter weight and distance</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
