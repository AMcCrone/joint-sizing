"""
Calculations module for facade panel movement joints.
Handles deflection shape calculations for different frame types.
"""

import numpy as np


def deflection_shape(x, u_max, L, shape='fixed-fixed'):
    """
    Calculate deflection u(x) for given u_max at midspan and span L.
    
    Parameters:
    -----------
    x : array-like
        Position along the span (in mm)
    u_max : float
        Maximum deflection at midspan (in mm)
    L : float
        Span length (in mm)
    shape : str
        Shape type: 'fixed-fixed' (concrete) or 'quadratic' (steel)
    
    Returns:
    --------
    array-like
        Deflection values at each x position
    """
    xi = x / L
    
    if shape == 'fixed-fixed':
        # Concrete frame: exact quartic normalized shape
        phi = 16.0 * xi**2 * (1.0 - xi)**2
    elif shape == 'quadratic':
        # Steel frame: simple parabola normalized to u_max
        phi = 4.0 * xi * (1.0 - xi)
    else:
        raise ValueError("Unknown shape. Use 'fixed-fixed' or 'quadratic'.")
    
    return u_max * phi


def generate_slab_edge_coordinates(span, u_max, frame_type, support_type, num_points=401):
    """
    Generate coordinates for the deflected slab edge.
    
    Parameters:
    -----------
    span : float
        Span length between columns (in mm)
    u_max : float
        Maximum deflection (in mm)
    frame_type : str
        'concrete' or 'steel'
    support_type : str
        'top_hung' or 'bottom_supported'
    num_points : int
        Number of points to generate along the span
    
    Returns:
    --------
    tuple
        (x_coords, y_deflected, y_straight)
    """
    x = np.linspace(0, span, num_points)
    
    # Select shape based on frame type
    shape = 'fixed-fixed' if frame_type == 'concrete' else 'quadratic'
    
    # Calculate deflection
    deflection = deflection_shape(x, u_max, span, shape)
    
    # Apply support type (top hung: deflection goes down; bottom supported: deflection goes up)
    if support_type == 'top_hung':
        y_deflected = -deflection
    else:  # bottom_supported
        y_deflected = deflection
    
    # Straight edge is at y=0
    y_straight = np.zeros_like(x)
    
    return x, y_deflected, y_straight


def calculate_panel_positions(span, num_panels, joint_width=5):
    """
    Calculate the positions of panels along the span.
    
    Parameters:
    -----------
    span : float
        Total span length (in mm)
    num_panels : int
        Number of panels
    joint_width : float
        Width of joints between panels (in mm)
    
    Returns:
    --------
    list of tuples
        List of (x_start, x_end) for each panel
    """
    total_joint_width = (num_panels - 1) * joint_width
    available_span = span - total_joint_width
    panel_width = available_span / num_panels
    
    panels = []
    current_x = 0
    
    for i in range(num_panels):
        x_start = current_x
        x_end = x_start + panel_width
        panels.append((x_start, x_end))
        current_x = x_end + joint_width
    
    return panels


def get_panel_corner_deflections(panels, span, u_max, frame_type, support_type):
    """
    Calculate deflection at each panel corner.
    
    Parameters:
    -----------
    panels : list of tuples
        List of (x_start, x_end) for each panel
    span : float
        Total span length (in mm)
    u_max : float
        Maximum deflection (in mm)
    frame_type : str
        'concrete' or 'steel'
    support_type : str
        'top_hung' or 'bottom_supported'
    
    Returns:
    --------
    dict
        Dictionary with panel indices as keys and corner deflections as values
    """
    shape = 'fixed-fixed' if frame_type == 'concrete' else 'quadratic'
    
    panel_deflections = {}
    
    for i, (x_start, x_end) in enumerate(panels):
        # Calculate deflection at panel corners
        deflection_start = deflection_shape(x_start, u_max, span, shape)
        deflection_end = deflection_shape(x_end, u_max, span, shape)
        
        # Apply support type
        if support_type == 'top_hung':
            deflection_start = -deflection_start
            deflection_end = -deflection_end
        
        panel_deflections[i] = {
            'x_start': x_start,
            'x_end': x_end,
            'deflection_start': deflection_start,
            'deflection_end': deflection_end
        }
    
    return panel_deflections
