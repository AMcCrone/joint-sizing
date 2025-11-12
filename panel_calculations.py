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
    Calculate the geometry of a single panel including corners and rotation.
    Panel maintains rectangular shape (90-degree corners) by rotating about support edge.
    
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
    panel_height : float
        Height of the panel (in mm) - typically same as floor height
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
    
    # Get deflections at panel edges
    deflection_start = get_deflection_at_position(x_local_start, u_max, single_span, frame_type)
    deflection_end = get_deflection_at_position(x_local_end, u_max, single_span, frame_type)
    
    # Calculate panel width
    panel_width = x_end - x_start
    
    # Calculate differential deflection and rotation angle
    deflection_diff = deflection_end - deflection_start
    
    if support_type == 'bottom_supported':
        # For bottom supported: rotation based on bottom edge differential
        # Bottom edge deflects, panel rotates from bottom
        rotation_angle = np.arcsin(-deflection_diff / panel_width)
        
        # Bottom corners are on the deflected edge
        bottom_left = (x_start, deflection_start)
        bottom_right = (x_end, deflection_end)
        
        # Panel maintains rectangular shape by rotating
        # Calculate rotation matrix components
        cos_theta = np.cos(rotation_angle)
        sin_theta = np.sin(rotation_angle)
        
        # Top corners: offset by panel_height perpendicular to bottom edge
        # In rotated coordinate system, this is just +H in y-direction
        # Then rotate back to global coordinates
        top_left = (
            bottom_left[0] - panel_height * sin_theta,
            bottom_left[1] + panel_height * cos_theta
        )
        top_right = (
            bottom_right[0] - panel_height * sin_theta,
            bottom_right[1] + panel_height * cos_theta
        )
        
    else:  # top_hung
        # For top hung: rotation based on top edge differential
        # Top edge deflects, panel rotates from top
        rotation_angle = np.arcsin(-deflection_diff / panel_width)
        
        # Top corners are on the deflected edge
        top_left = (x_start, deflection_start)
        top_right = (x_end, deflection_end)
        
        # Calculate rotation matrix components
        cos_theta = np.cos(rotation_angle)
        sin_theta = np.sin(rotation_angle)
        
        # Bottom corners: offset by panel_height perpendicular to top edge
        # In rotated coordinate system, this is just -H in y-direction
        # Then rotate back to global coordinates
        bottom_left = (
            top_left[0] + panel_height * sin_theta,
            top_left[1] - panel_height * cos_theta
        )
        bottom_right = (
            top_right[0] + panel_height * sin_theta,
            top_right[1] - panel_height * cos_theta
        )
    
    return {
        'top_left': top_left,
        'top_right': top_right,
        'bottom_left': bottom_left,
        'bottom_right': bottom_right,
        'rotation_angle': rotation_angle,
        'rotation_degrees': np.degrees(rotation_angle),
        'deflection_start': deflection_start,
        'deflection_end': deflection_end,
        'deflection_diff': deflection_diff
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
