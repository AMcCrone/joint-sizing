# panel_calculations.py
"""
Panel positioning and geometry calculations for facade panels.
Handles panel division, corner positions, and rotations while maintaining rectangular geometry.
"""

import numpy as np
from deflection_calculations import get_deflection_at_position


def calculate_panel_positions(total_span, num_panels, joint_width=5):
    """
    Calculate the positions of panels across the total span (2 spans between 3 columns).
    
    Parameters:
    -----------
    total_span : float
        Total span across all columns (in mm) - this is 2x single span
    num_panels : int
        Total number of panels across all spans
    joint_width : float
        Width of joints between panels (in mm)
    
    Returns:
    --------
    list of tuples
        List of (x_start, x_end, span_number) for each panel
        span_number: 0 for first span, 1 for second span
    """
    single_span = total_span / 2
    total_joint_width = (num_panels - 1) * joint_width
    available_span = total_span - total_joint_width
    panel_width = available_span / num_panels
    
    panels = []
    current_x = 0
    
    for i in range(num_panels):
        x_start = current_x
        x_end = x_start + panel_width
        
        # Determine which span this panel is in
        span_number = 0 if x_start < single_span else 1
        
        panels.append((x_start, x_end, span_number))
        current_x = x_end + joint_width
    
    return panels


def calculate_panel_geometry(x_start, x_end, span_number, single_span,
                             panel_height, u_max, frame_type, support_type):
    """
    Calculate rectangular panel corners by using the support edge tangent
    and a perpendicular offset (unit normal). This preserves 90° corners.
    """
    # Convert global x to local x within the span
    span_offset = span_number * single_span
    x_local_start = x_start - span_offset
    x_local_end = x_end - span_offset

    # Get deflections at panel edges (vertical values)
    deflection_start = get_deflection_at_position(x_local_start, u_max, single_span, frame_type)
    deflection_end = get_deflection_at_position(x_local_end, u_max, single_span, frame_type)

    # Panel horizontal projection (adjacent)
    dx = (x_end - x_start)
    dy = (deflection_end - deflection_start)  # vertical difference along the support edge

    # Edge length (actual length of the support edge across the panel)
    edge_length = np.hypot(dx, dy)
    if edge_length == 0:
        # Degenerate panel — return a vertical rectangle of zero width
        bottom_left = bottom_right = top_left = top_right = (x_start, deflection_start)
        rotation_angle = 0.0
        return {
            'top_left': top_left, 'top_right': top_right,
            'bottom_left': bottom_left, 'bottom_right': bottom_right,
            'rotation_angle': rotation_angle,
            'rotation_degrees': 0.0,
            'deflection_start': deflection_start,
            'deflection_end': deflection_end,
            'deflection_diff': dy
        }

    # Unit tangent vector along the deflected support edge (from left -> right)
    tx = dx / edge_length
    ty = dy / edge_length

    # Unit normal (pointing "up" relative to the edge). Choose convention:
    # normal = (-ty, tx) produces a normal rotated +90° from the tangent.
    nx = -ty
    ny = tx

    # If top-hung, the deflected edge is the top; otherwise it's the bottom.
    if support_type == 'bottom_supported':
        # Bottom edge coordinates (on deflected support)
        bottom_left = (x_start, deflection_start)
        bottom_right = (x_end, deflection_end)

        # Offset top edge by +panel_height along the unit normal
        top_left = (bottom_left[0] + nx * panel_height, bottom_left[1] + ny * panel_height)
        top_right = (bottom_right[0] + nx * panel_height, bottom_right[1] + ny * panel_height)

        # rotation angle of the support edge relative to horizontal:
        rotation_angle = np.arctan2(dy, dx)

    else:  # 'top_hung'
        # Top edge coordinates (on deflected support)
        top_left = (x_start, deflection_start)
        top_right = (x_end, deflection_end)

        # Offset bottom edge by -panel_height along the unit normal (downwards)
        bottom_left = (top_left[0] - nx * panel_height, top_left[1] - ny * panel_height)
        bottom_right = (top_right[0] - nx * panel_height, top_right[1] - ny * panel_height)

        rotation_angle = np.arctan2(dy, dx)

    return {
        'top_left': top_left,
        'top_right': top_right,
        'bottom_left': bottom_left,
        'bottom_right': bottom_right,
        'rotation_angle': rotation_angle,
        'rotation_degrees': np.degrees(rotation_angle),
        'deflection_start': deflection_start,
        'deflection_end': deflection_end,
        'deflection_diff': dy
    }


def get_all_panel_geometries(panels, single_span, panel_height, u_max, 
                            frame_type, support_type):
    """
    Calculate geometries for all panels.
    
    Parameters:
    -----------
    panels : list of tuples
        List of (x_start, x_end, span_number) for each panel
    single_span : float
        Length of a single span (in mm)
    panel_height : float
        Height of the panel (in mm)
    u_max : float
        Maximum deflection (in mm)
    frame_type : str
        'concrete' or 'steel'
    support_type : str
        'top_hung' or 'bottom_supported'
    
    Returns:
    --------
    list of dict
        List of panel geometry dictionaries
    """
    panel_geometries = []
    
    for x_start, x_end, span_number in panels:
        geometry = calculate_panel_geometry(
            x_start, x_end, span_number, single_span,
            panel_height, u_max, frame_type, support_type
        )
        geometry['x_start'] = x_start
        geometry['x_end'] = x_end
        geometry['span_number'] = span_number
        panel_geometries.append(geometry)
    
    return panel_geometries
