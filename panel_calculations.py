# panel_calculations.py
"""
Panel positioning and geometry calculations for facade panels.
Handles panel division, corner positions, and rotations.
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
                            slab_thickness, u_max, frame_type, support_type):
    """
    Calculate the geometry of a single panel including corners and rotation.
    
    Parameters:
    -----------
    x_start : float
        Starting x position of panel (in mm)
    x_end : float
        Ending x position of panel (in mm)
    span_number : int
        Which span (0 or 1)
    single_span : float
        Length of a single span (in mm)
    slab_thickness : float
        Thickness of the slab (in mm)
    u_max : float
        Maximum deflection (in mm)
    frame_type : str
        'concrete' or 'steel'
    support_type : str
        'top_hung' or 'bottom_supported'
    
    Returns:
    --------
    dict
        Dictionary containing panel corner coordinates and rotation angle
    """
    # Convert global x to local x within the span
    span_offset = span_number * single_span
    x_local_start = x_start - span_offset
    x_local_end = x_end - span_offset
    
    # Get deflections at panel support points
    deflection_start = get_deflection_at_position(x_local_start, u_max, single_span, frame_type)
    deflection_end = get_deflection_at_position(x_local_end, u_max, single_span, frame_type)
    
    # Calculate rotation angle (in radians)
    panel_width = x_end - x_start
    rotation_angle = np.arctan2(deflection_end - deflection_start, panel_width)
    
    # Calculate panel corners based on support type
    if support_type == 'top_hung':
        # Top edge follows deflected shape, bottom edge is offset by slab thickness
        # Top corners (support points on deflected edge)
        top_left = (x_start, deflection_start)
        top_right = (x_end, deflection_end)
        
        # Bottom corners - offset perpendicular to top edge by slab thickness
        dx = -slab_thickness * np.sin(rotation_angle)
        dy = slab_thickness * np.cos(rotation_angle)
        
        bottom_left = (top_left[0] + dx, top_left[1] + dy)
        bottom_right = (top_right[0] + dx, top_right[1] + dy)
        
    else:  # bottom_supported
        # Bottom edge follows deflected shape, top edge is offset by slab thickness
        # Bottom corners (support points on deflected edge)
        bottom_left = (x_start, deflection_start)
        bottom_right = (x_end, deflection_end)
        
        # Top corners - offset perpendicular to bottom edge by slab thickness
        dx = -slab_thickness * np.sin(rotation_angle)
        dy = -slab_thickness * np.cos(rotation_angle)
        
        top_left = (bottom_left[0] + dx, bottom_left[1] + dy)
        top_right = (bottom_right[0] + dx, bottom_right[1] + dy)
    
    return {
        'top_left': top_left,
        'top_right': top_right,
        'bottom_left': bottom_left,
        'bottom_right': bottom_right,
        'rotation_angle': rotation_angle,
        'rotation_degrees': np.degrees(rotation_angle),
        'deflection_start': deflection_start,
        'deflection_end': deflection_end
    }


def get_all_panel_geometries(panels, single_span, slab_thickness, u_max, 
                            frame_type, support_type):
    """
    Calculate geometries for all panels.
    
    Parameters:
    -----------
    panels : list of tuples
        List of (x_start, x_end, span_number) for each panel
    single_span : float
        Length of a single span (in mm)
    slab_thickness : float
        Thickness of the slab (in mm)
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
            slab_thickness, u_max, frame_type, support_type
        )
        geometry['x_start'] = x_start
        geometry['x_end'] = x_end
        geometry['span_number'] = span_number
        panel_geometries.append(geometry)
    
    return panel_geometries
