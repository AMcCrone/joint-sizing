"""
Streamlit app for facade panel movement joint calculations and visualization.
Main application file.
"""

import streamlit as st
import pandas as pd
from deflection_calculations import generate_slab_edge_coordinates
from panel_calculations import calculate_panel_positions, get_all_panel_geometries
from visualisation import create_facade_figure


# Page configuration
st.set_page_config(
    page_title="Facade Panel Movement Joints",
    page_icon="🏢",
    layout="wide"
)

st.title("Facade Panel Movement Joint Calculator")
st.markdown("Calculate and visualize facade panel movement joints with slab edge deflection")

# Sidebar for inputs
st.sidebar.header("Input Parameters")

# Frame type selection
frame_type = st.sidebar.selectbox(
    "Frame Type",
    options=["concrete", "steel"],
    format_func=lambda x: "Concrete Frame" if x == "concrete" else "Steel Frame"
)

# Support type selection
support_type = st.sidebar.selectbox(
    "Panel Support Type",
    options=["top_hung", "bottom_supported"],
    format_func=lambda x: "Top Hung" if x == "top_hung" else "Bottom Supported"
)

# Numerical inputs
floor_height = st.sidebar.number_input(
    "Floor Height (mm)",
    min_value=100,
    max_value=10000,
    value=3000,
    step=100
)

span_width = st.sidebar.number_input(
    "Span Width Between Columns (mm)",
    min_value=1000,
    max_value=20000,
    value=6000,
    step=100
)

max_deflection = st.sidebar.number_input(
    "Maximum Deflection (mm)",
    min_value=0.1,
    max_value=500.0,
    value=10.0,
    step=0.5,
    format="%.1f",
    help="Deflection is always downward (negative direction)"
)

num_panels = st.sidebar.number_input(
    "Number of Panels (Total across both spans)",
    min_value=1,
    max_value=40,
    value=4,
    step=1
)

joint_width = st.sidebar.number_input(
    "Joint Width (mm)",
    min_value=1.0,
    max_value=50.0,
    value=5.0,
    step=1.0
)

st.sidebar.markdown("---")
st.sidebar.subheader("Structural Elements")

column_thickness = st.sidebar.number_input(
    "Column Thickness (mm)",
    min_value=50,
    max_value=1000,
    value=150,
    step=10
)

slab_thickness = st.sidebar.number_input(
    "Slab Thickness (mm)",
    min_value=50,
    max_value=1000,
    value=300,
    step=10
)

# Calculate total span
total_span = span_width * 2

# Calculate panel positions and geometries
panels = calculate_panel_positions(total_span, num_panels, joint_width)

panel_geometries = get_all_panel_geometries(
    panels, span_width, slab_thickness, max_deflection, 
    frame_type, support_type
)

# Create visualization
fig = create_facade_figure(
    span_width, floor_height, max_deflection, frame_type, support_type,
    panel_geometries, column_thickness, slab_thickness
)

# Display the plot
st.plotly_chart(fig, use_container_width=True)

# Display calculations
st.header("System Information")

col1, col2, col3, col4 = st.columns(4)

with col1:
    frame_name = "Concrete Frame" if frame_type == "concrete" else "Steel Frame"
    st.metric("Frame Type", frame_name)
    st.metric("Support Type", support_type.replace('_', ' ').title())

with col2:
    st.metric("Single Span Width", f"{span_width} mm")
    st.metric("Total Span Width", f"{total_span} mm")

with col3:
    st.metric("Floor Height", f"{floor_height} mm")
    st.metric("Maximum Deflection", f"{max_deflection} mm")

with col4:
    st.metric("Number of Panels", num_panels)
    deflection_ratio = span_width / max_deflection if max_deflection > 0 else 0
    st.metric("Span/Deflection Ratio", f"L/{deflection_ratio:.0f}")

# Panel geometry details table
st.subheader("Panel Geometry Details")

data = []
for i, geom in enumerate(panel_geometries):
    span_num = geom['span_number'] + 1
    panel_width = geom['x_end'] - geom['x_start']
    
    data.append({
        'Panel': i + 1,
        'Span': span_num,
        'Start (mm)': f"{geom['x_start']:.1f}",
        'End (mm)': f"{geom['x_end']:.1f}",
        'Width (mm)': f"{panel_width:.1f}",
        'Start Deflection (mm)': f"{geom['deflection_start']:.3f}",
        'End Deflection (mm)': f"{geom['deflection_end']:.3f}",
        'Differential (mm)': f"{abs(geom['deflection_end'] - geom['deflection_start']):.3f}",
        'Rotation (°)': f"{geom['rotation_degrees']:.3f}"
    })

df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True, hide_index=True)

# Panel corner coordinates
with st.expander("Panel Corner Coordinates"):
    corner_data = []
    for i, geom in enumerate(panel_geometries):
        corner_data.append({
            'Panel': i + 1,
            'Top Left': f"({geom['top_left'][0]:.1f}, {geom['top_left'][1]:.2f})",
            'Top Right': f"({geom['top_right'][0]:.1f}, {geom['top_right'][1]:.2f})",
            'Bottom Left': f"({geom['bottom_left'][0]:.1f}, {geom['bottom_left'][1]:.2f})",
            'Bottom Right': f"({geom['bottom_right'][0]:.1f}, {geom['bottom_right'][1]:.2f})"
        })
    
    corner_df = pd.DataFrame(corner_data)
    st.dataframe(corner_df, use_container_width=True, hide_index=True)

# Formula information
with st.expander("Deflection Formulas"):
    if frame_type == 'concrete':
        st.markdown("""
        **Concrete Frame (Fixed-Fixed Beam):**
        
        Exact quartic normalized shape:
        ```
        u(x) = -u_max × 16 × (x/L)² × (1 - x/L)²
        ```
        
        This represents the deflection of a uniformly loaded beam with fixed ends.
        The negative sign indicates downward deflection.
        """)
    else:
        st.markdown("""
        **Steel Frame (Simple Support):**
        
        Quadratic parabolic approximation:
        ```
        u(x) = -u_max × 4 × (x/L) × (1 - x/L)
        ```
        
        This represents a simplified parabolic deflection shape.
        The negative sign indicates downward deflection.
        """)

# System description
with st.expander("System Description"):
    st.markdown(f"""
    ### Support Configuration: {support_type.replace('_', ' ').title()}
    
    {'**Top Hung Panels:**' if support_type == 'top_hung' else '**Bottom Supported Panels:**'}
    
    {'''- Panels are supported at their top edge along the deflected slab edge
    - The deflected edge is at the top of the columns (floor level)
    - Panels hang downward from the deflected edge
    - The straight (undeflected) reference edge is at the bottom of the columns
    - Each panel rotates to maintain contact with the deflected support edge''' if support_type == 'top_hung' else 
    '''- Panels are supported at their bottom edge along the deflected slab edge
    - The deflected edge is at the bottom of the columns (ground level)
    - Panels rest on the deflected edge
    - The straight (undeflected) reference edge is at the top of the columns
    - Each panel rotates to maintain contact with the deflected support edge'''}
    
    ### Deflection Behavior:
    - All deflections are **downward** (negative direction)
    - Maximum deflection occurs at midspan: **{max_deflection} mm**
    - The deflection shape depends on the frame type:
      - **Concrete Frame**: Fixed-fixed beam (quartic curve)
      - **Steel Frame**: Simple support (parabolic curve)
    
    ### Panel Behavior:
    - Panels remain as **perfect rectangles**
    - Each panel rotates based on the deflection at its support points
    - Panel rotation angle is calculated from the slope of the deflected edge
    - Joints between panels accommodate differential movement
    """)

# Footer
st.markdown("---")
st.caption("Facade Panel Movement Joint Calculator | Built with Streamlit and Plotly")
