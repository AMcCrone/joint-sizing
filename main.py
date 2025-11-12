"""
Streamlit app for facade panel movement joint calculations and visualization.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from calculations import (
    generate_slab_edge_coordinates,
    calculate_panel_positions,
    get_panel_corner_deflections
)


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
    max_value=100.0,
    value=10.0,
    step=0.5,
    format="%.1f"
)

num_panels = st.sidebar.number_input(
    "Number of Panels",
    min_value=1,
    max_value=20,
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

# Calculate data
x_coords, y_deflected, y_straight = generate_slab_edge_coordinates(
    span_width, max_deflection, frame_type, support_type
)

panels = calculate_panel_positions(span_width, num_panels, joint_width)
panel_deflections = get_panel_corner_deflections(
    panels, span_width, max_deflection, frame_type, support_type
)

# Create Plotly figure
fig = go.Figure()

# Color scheme based on frame type
frame_color = '#808080' if frame_type == 'concrete' else '#B7410E'
frame_name = "Concrete Frame" if frame_type == 'concrete' else "Steel Frame"

# Add columns (3 columns)
column_width = span_width * 0.02  # 2% of span width
column_positions = [0, span_width, span_width * 2]

for i, x_pos in enumerate(column_positions):
    fig.add_trace(go.Scatter(
        x=[x_pos - column_width/2, x_pos + column_width/2, 
           x_pos + column_width/2, x_pos - column_width/2, x_pos - column_width/2],
        y=[0, 0, floor_height, floor_height, 0],
        fill='toself',
        fillcolor=frame_color,
        line=dict(color=frame_color, width=2),
        name=f'Column {i+1}' if i == 0 else '',
        showlegend=(i == 0),
        hoverinfo='skip'
    ))

# Add slab edges for both spans
for span_num in range(2):
    x_offset = span_num * span_width
    
    # Deflected slab edge
    fig.add_trace(go.Scatter(
        x=x_coords + x_offset,
        y=y_deflected + floor_height,
        mode='lines',
        line=dict(color=frame_color, width=3),
        name=f'Deflected Edge (Span {span_num+1})' if span_num == 0 else '',
        showlegend=(span_num == 0),
        hovertemplate='x: %{x:.0f} mm<br>y: %{y:.2f} mm<extra></extra>'
    ))
    
    # Straight slab edge (reference)
    fig.add_trace(go.Scatter(
        x=x_coords + x_offset,
        y=y_straight + floor_height,
        mode='lines',
        line=dict(color='gray', width=2, dash='dash'),
        name='Straight Edge' if span_num == 0 else '',
        showlegend=(span_num == 0),
        hovertemplate='x: %{x:.0f} mm<br>y: %{y:.2f} mm<extra></extra>'
    ))

# Add panels for both spans
for span_num in range(2):
    x_offset = span_num * span_width
    
    for i, (x_start, x_end) in enumerate(panels):
        # Create panel rectangle
        panel_height = floor_height * 0.8  # Panels are 80% of floor height
        
        # Calculate deflection at panel edges
        x_points = np.array([x_start, x_end])
        shape = 'fixed-fixed' if frame_type == 'concrete' else 'quadratic'
        
        from calculations import deflection_shape
        deflection_at_points = deflection_shape(x_points, max_deflection, span_width, shape)
        
        if support_type == 'top_hung':
            y_top_start = floor_height - deflection_at_points[0]
            y_top_end = floor_height - deflection_at_points[1]
            y_bottom_start = y_top_start - panel_height
            y_bottom_end = y_top_end - panel_height
        else:
            y_bottom_start = deflection_at_points[0]
            y_bottom_end = deflection_at_points[1]
            y_top_start = y_bottom_start + panel_height
            y_top_end = y_bottom_end + panel_height
        
        fig.add_trace(go.Scatter(
            x=[x_start + x_offset, x_end + x_offset, 
               x_end + x_offset, x_start + x_offset, x_start + x_offset],
            y=[y_bottom_start, y_bottom_end, y_top_end, y_top_start, y_bottom_start],
            fill='toself',
            fillcolor='rgba(173, 216, 230, 0.3)',
            line=dict(color='steelblue', width=1),
            name=f'Panel {i+1}' if (i == 0 and span_num == 0) else '',
            showlegend=(i == 0 and span_num == 0),
            hovertemplate=f'Panel {i+1}<br>Span {span_num+1}<extra></extra>'
        ))

# Update layout
fig.update_layout(
    title=f"{frame_name} - {support_type.replace('_', ' ').title()} Panels",
    xaxis_title="Horizontal Distance (mm)",
    yaxis_title="Vertical Distance (mm)",
    hovermode='closest',
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ),
    height=600,
    plot_bgcolor='white',
    xaxis=dict(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='black'
    ),
    yaxis=dict(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        scaleanchor="x",
        scaleratio=1,
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='black'
    )
)

# Display the plot
st.plotly_chart(fig, use_container_width=True)

# Display calculations
st.header("Deflection Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Frame Type", frame_name)
    st.metric("Support Type", support_type.replace('_', ' ').title())

with col2:
    st.metric("Total Span Width", f"{span_width} mm")
    st.metric("Maximum Deflection", f"{max_deflection} mm")

with col3:
    st.metric("Number of Panels", num_panels)
    deflection_ratio = span_width / max_deflection if max_deflection > 0 else 0
    st.metric("Span/Deflection Ratio", f"L/{deflection_ratio:.0f}")

# Panel corner deflections table
st.subheader("Panel Corner Deflections (Per Span)")

import pandas as pd

data = []
for i, deflections in panel_deflections.items():
    data.append({
        'Panel': i + 1,
        'Start Position (mm)': f"{deflections['x_start']:.1f}",
        'End Position (mm)': f"{deflections['x_end']:.1f}",
        'Start Deflection (mm)': f"{deflections['deflection_start']:.2f}",
        'End Deflection (mm)': f"{deflections['deflection_end']:.2f}",
        'Differential (mm)': f"{abs(deflections['deflection_end'] - deflections['deflection_start']):.2f}"
    })

df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True, hide_index=True)

# Formula information
with st.expander("Deflection Formulas"):
    if frame_type == 'concrete':
        st.markdown("""
        **Concrete Frame (Fixed-Fixed Beam):**
        
        Exact quartic normalized shape:
        ```
        u(x) = u_max × 16 × (x/L)² × (1 - x/L)²
        ```
        
        This represents the deflection of a uniformly loaded beam with fixed ends.
        """)
    else:
        st.markdown("""
        **Steel Frame (Simple Support):**
        
        Quadratic parabolic approximation:
        ```
        u(x) = u_max × 4 × (x/L) × (1 - x/L)
        ```
        
        This represents a simplified parabolic deflection shape.
        """)

# Footer
st.markdown("---")
st.caption("Facade Panel Movement Joint Calculator | Built with Streamlit and Plotly")
