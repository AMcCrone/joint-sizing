"""
Deflection calculations for facade panel movement joints.
Handles deflection shape calculations for different frame types.
"""

import numpy as np


def deflection_shape(x, u_max, L, shape='fixed-fixed'):
    """
    Calculate deflection u(x) for given u_max at midspan and span L.
    Note: Deflection is always downward (negative direction).
    
    Parameters:
    -----------
    x : array-like
        Position along the span (in mm)
    u_max : float
        Maximum deflection at midspan (in mm, always treated as downward)
    L : float
        Span length (in mm)
    shape : str
        Shape type: 'fixed-fixed' (concrete) or 'quadratic' (steel)
    
    Returns:
    --------
    array-like
        Deflection values at each x position (negative/downward)
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
    
    # Always return negative (downward) deflection
    return -abs(u_max) * phi


def get_deflection_at_position(x, u_max, L, frame_type):
    """
    Get deflection at a specific position.
    
    Parameters:
    -----------
    x : float
        Position along the span (in mm)
    u_max : float
        Maximum deflection at midspan (in mm)
    L : float
        Span length (in mm)
    frame_type : str
        'concrete' or 'steel'
    
    Returns:
    --------
    float
        Deflection at position x (negative/downward)
    """
    shape = 'fixed-fixed' if frame_type == 'concrete' else 'quadratic'
    return deflection_shape(x, u_max, L, shape)


def generate_slab_edge_coordinates(span, u_max, frame_type, num_points=401):
    """
    Generate coordinates for the deflected slab edge.
    
    Parameters:
    -----------
    span : float
        Span length between columns (in mm)
    u_max : float
        Maximum deflection (in mm, always downward)
    frame_type : str
        'concrete' or 'steel'
    num_points : int
        Number of points to generate along the span
    
    Returns:
    --------
    tuple
        (x_coords, y_deflection) - deflection is negative (downward)
    """
    x = np.linspace(0, span, num_points)
    shape = 'fixed-fixed' if frame_type == 'concrete' else 'quadratic'
    y_deflection = deflection_shape(x, u_max, span, shape)
    
    return x, y_deflection
