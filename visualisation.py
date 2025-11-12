"""
Visualisation functions for the facade panel movement joint calculator.
Creates Plotly figures with proper dimensions and annotations.
"""

import plotly.graph_objects as go
import numpy as np
from deflection_calculations import generate_slab_edge_coordinates


def get_frame_color(frame_type):
    """Get color based on frame type."""
    return '#808080' if frame_type == 'concrete' else '#B7410E'


def create_dimension_arrow(x1, y1, x2, y2, text, offset=200):
    """
    Create dimension arrow with text.
    
    Parameters:
    -----------
    x1, y1 : float
        Start coordinates
    x2, y2 : float
        End coordinates
    text : str
        Dimension text
    offset : float
        Offset from the measured line
    
    Returns:
    --------
    list
        List of plotly traces for the dimension
    """
    traces = []
    
    # Calculate perpendicular offset direction
    dx = x2 - x1
    dy = y2 - y1
    length = np.sqrt(dx**2 + dy**2)
    
    if length == 0:
        return traces
    
    # Unit perpendicular vector
    if abs(dx) < 0.1:  # Vertical line
        offset_x = offset
        offset_y = 0
    elif abs(dy) < 0.1:  # Horizontal line
        offset_x = 0
        offset_y = -offset
    else:
        perp_x = -dy / length
        perp_y = dx / length
        offset_x = perp_x * offset
        offset_y = perp_y * offset
    
    # Offset start and end points
    x1_off = x1 + offset_x
    y1_off = y1 + offset_y
    x2_off = x2 + offset_x
    y2_off = y2 + offset_y
    
    # Main dimension line
    traces.append(go.Scatter(
        x=[x1_off, x2_off],
        y=[y1_off, y2_off],
        mode='lines',
        line=dict(color='black', width=2),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Extension lines
    extension_length = abs(offset) * 0.3
    traces.append(go.Scatter(
        x=[x1, x1_off + (offset_x * 0.2)],
        y=[y1, y1_off + (offset_y * 0.2)],
        mode='lines',
        line=dict(color='black', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    traces.append(go.Scatter(
        x=[x2, x2_off + (offset_x * 0.2)],
        y=[y2, y2_off + (offset_y * 0.2)],
        mode='lines',
        line=dict(color='black', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Arrowheads using annotations
    mid_x = (x1_off + x2_off) / 2
    mid_y = (y1_off + y2_off) / 2
    
    return traces, (mid_x, mid_y, x2_off - x1_off, y2_off - y1_off)

def create_facade_figure(span_width, floor_height, u_max, frame_type, support_type,
                         panel_geometries, column_thickness=150, slab_thickness=300):
    """
    Create the main facade visualization figure.
    
    Parameters:
    -----------
    span_width : float
        Single span width (in mm)
    floor_height : float
        Floor height (in mm)
    u_max : float
        Maximum deflection (in mm)
    frame_type : str
        'concrete' or 'steel'
    support_type : str
        'top_hung' or 'bottom_supported'
    panel_geometries : list
        List of panel geometry dictionaries
    column_thickness : float
        Thickness of columns (in mm)
    slab_thickness : float
        Thickness of slab edges (in mm)
    
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()
    
    frame_color = get_frame_color(frame_type)
    total_span = span_width * 2
    
    # Extension beyond bounds
    extension = span_width * 0.1
    
    # Calculate vertical positions based on support type
    if support_type == 'top_hung':
        # Deflected edge at top (where panels hang from)
        deflected_edge_base = floor_height
        straight_edge_base = 0
    else:  # bottom_supported
        # Deflected edge at bottom (where panels sit on)
        deflected_edge_base = 0
        straight_edge_base = floor_height
    
    # Create columns (3 columns) - extend beyond bounds
    column_positions = [0, span_width, total_span]
    column_bottom = -extension
    column_top = floor_height + extension
    
    for x_pos in column_positions:
        fig.add_trace(go.Scatter(
            x=[x_pos - column_thickness/2, x_pos + column_thickness/2, 
               x_pos + column_thickness/2, x_pos - column_thickness/2, x_pos - column_thickness/2],
            y=[column_bottom, column_bottom, column_top, column_top, column_bottom],
            fill='toself',
            fillcolor=frame_color,
            line=dict(color=frame_color, width=0),
            mode='lines',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Create deflected slab edges for both spans
    num_points = 401
    for span_num in range(2):
        x_coords, y_deflection = generate_slab_edge_coordinates(
            span_width, u_max, frame_type, num_points
        )
        x_offset = span_num * span_width

        # bring coordinates into global x-space
        x_global = x_coords + x_offset
        y_global = y_deflection + deflected_edge_base

        # --- Add flat outer extension on the left for span 0 and on the right for span 1 ---
        # keep the deflection value at the nearest edge for the flat extension
        if span_num == 0:
            # prepend a flat point at x = -extension
            x_global = np.concatenate((np.array([-extension]), x_global))
            y_global = np.concatenate((np.array([y_global[0]]), y_global))
        if span_num == 1:
            # append a flat point at x = total_span + extension
            x_global = np.concatenate((x_global, np.array([total_span + extension])))
            y_global = np.concatenate((y_global, np.array([y_global[-1]])))

        # Create thick slab edge by making a filled polygon (top then bottom reversed)
        x_edge = np.concatenate([x_global, x_global[::-1]])
        y_edge_top = y_global + slab_thickness/2
        y_edge_bottom = y_global - slab_thickness/2
        y_edge = np.concatenate([y_edge_top, y_edge_bottom[::-1]])

        fig.add_trace(go.Scatter(
            x=x_edge,
            y=y_edge,
            fill='toself',
            fillcolor=frame_color,
            line=dict(color=frame_color, width=0),
            showlegend=False,
            hoverinfo='skip',
            mode='lines'
        ))
    
    # Create straight slab edges (solid thick line)
    x_straight = np.array([-extension, total_span + extension])
    y_straight_center = straight_edge_base * np.ones_like(x_straight)
    
    fig.add_trace(go.Scatter(
        x=np.concatenate([x_straight, x_straight[::-1]]),
        y=np.concatenate([y_straight_center + slab_thickness/2, 
                         (y_straight_center - slab_thickness/2)[::-1]]),
        fill='toself',
        fillcolor=frame_color,
        line=dict(color=frame_color, width=0),
        mode='lines',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add panels
    for i, geom in enumerate(panel_geometries):
        tl = geom['top_left']
        tr = geom['top_right']
        br = geom['bottom_right']
        bl = geom['bottom_left']
        
        # Add vertical offset based on support type
        if support_type == 'top_hung':
            y_offset = deflected_edge_base
        else:
            y_offset = deflected_edge_base
        
        fig.add_trace(go.Scatter(
            x=[tl[0], tr[0], br[0], bl[0], tl[0]],
            y=[tl[1] + y_offset, tr[1] + y_offset, 
               br[1] + y_offset, bl[1] + y_offset, tl[1] + y_offset],
            fill='toself',
            fillcolor='rgba(173, 216, 230, 0.5)',
            line=dict(color='steelblue', width=2),
            mode='lines',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Add dimensions
    dimension_data = []
    
    # Height dimension (on the left)
    height_traces, height_info = create_dimension_arrow(
        -extension/2, 0, -extension/2, floor_height,
        f"{floor_height} mm", offset=-300
    )
    for trace in height_traces:
        fig.add_trace(trace)
    dimension_data.append({
        'x': height_info[0],
        'y': height_info[1],
        'text': f"{floor_height} mm",
        'angle': 90
    })
    
    # Span width dimension (on top or bottom depending on support type)
    if support_type == 'top_hung':
        dim_y = floor_height + extension/2
    else:
        dim_y = -extension/2
    
    span_traces, span_info = create_dimension_arrow(
        0, dim_y, span_width, dim_y,
        f"{span_width} mm", offset=300 if support_type == 'bottom_supported' else -300
    )
    for trace in span_traces:
        fig.add_trace(trace)
    dimension_data.append({
        'x': span_info[0],
        'y': span_info[1],
        'text': f"{span_width} mm",
        'angle': 0
    })
    
    # Update layout - no axes, no grid, plain background
    fig.update_layout(
        showlegend=False,
        hovermode=False,
        height=700,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False,
            range=[-extension - 500, total_span + extension + 500]
        ),
        yaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False,
            scaleanchor="x",
            scaleratio=1,
            range=[-extension - 500, floor_height + extension + 500]
        ),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    # Add dimension text as annotations
    for dim in dimension_data:
        fig.add_annotation(
            x=dim['x'],
            y=dim['y'],
            text=dim['text'],
            showarrow=False,
            font=dict(size=12, color='black'),
            textangle=dim['angle'],
            bgcolor='white',
            borderpad=4
        )
    
    return fig
