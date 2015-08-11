
"""
Plot the numpy array using matplotlib.
"""

import IPython
import math
import matplotlib.pyplot as plt
import numpy

def log ( message ):
    debug = False
    if debug:
        print ( message )

def plot ( data, title = "", ipython = None ):
    """
    Function that attempts to plot a numpy ndarray argument.
    Will plot a mosaic if data is 3D, a simple plot if 2D.
    """
    if not ipython:
        ipython = IPython.get_ipython()
        ipython.magic("matplotlib qt")

    if len ( data.shape ) == 3:
        subplots = data.shape [ 0 ]
        log ( "subplots = {}".format ( subplots ) )

        dimensions = math.ceil ( math.sqrt ( subplots ) )
        log ( "should create mosaic of {} x {} slots.".format ( dimensions, dimensions ) )

        figure, axes = plt.subplots ( dimensions, dimensions, sharex='col', sharey='row' )

        figure.suptitle ( title )
        
        for plane in range ( data.shape [ 0 ] ):
            image = axes.flat [ plane ] .imshow ( data [ plane ], cmap = 'Greys' )

        figure.subplots_adjust( right = 0.8 )
        
        colorbar_axe = figure.add_axes ( [ 0.85, 0.15, 0.05, 0.7 ] )
        figure.colorbar ( image, cax=colorbar_axe )
            
        return

    if len ( data.shape ) == 2:
        fig = plt.figure ( )
        plt.imshow ( data, cmap='Greys')
        plt.colorbar ( orientation="horizontal" )
        plt.title ( title )

def plot_high_res ( high_res ):
    """
    Expects a high_res object.
    Will plot each of the intermediary products.
    """
    
    ipython = IPython.get_ipython()
    ipython.magic("matplotlib qt")

    plot ( high_res.continuum.array, title = "continuum", ipython = ipython )
    plot ( high_res.wrapped_phase_map.array, title = "wrapped phase map", ipython = ipython )
    plot ( high_res.noise.array, title = "noise", ipython = ipython )
    ring_counter = 0
    for ring in high_res.rings_center [ 'rings' ]:
        plot ( ring, title = "ring {}".format ( ring_counter ), ipython = ipython )
        ring_counter += 1
    plot ( high_res.borders_to_center_distances.array, title = "borders to center distances", ipython = ipython )
    plot ( high_res.order_map.array, title = "order map", ipython = ipython )
    plot ( high_res.unwrapped_phase_map.array, title = "unwrapped phase map", ipython = ipython )
    if high_res.parabolic_fit:
        plot ( high_res.parabolic_fit.array, title = "parabolic fit", ipython = ipython )
    plot ( high_res.discontinuum.array, title = "discontinuum", ipython = ipython )
    if high_res.airy_fit:
        plot ( high_res.airy_fit.array, title = "airy fit", ipython = ipython )
        plot ( high_res.airy_fit_residue.array, title = "airy fit residue", ipython = ipython )
    plot ( high_res.substituted_channels.array, title = "substituted channels", ipython = ipython )
    plot ( high_res.wavelength_calibrated.array, title = "wavelength calibrated", ipython = ipython )
