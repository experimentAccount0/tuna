import logging
from math import sqrt
import numpy
import threading
import time
import tuna

class ring_border_detector ( threading.Thread ):
    """
    This class is responsible for detecting the "borders" of the rings contained in a interferogram. 

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.

    Its constructor expects the following parameters:

    - data, a numpy.ndarray;
    - center, a tuple of 2 integers;
    - noise, a :ref:`tuna_io_can_label` containing the noise map for data;
    - rings, a dictionary, such as the one produced by  :ref:`tuna_tools_find_rings_2d_label` or equivalent. ;
    - log_level, a valid :ref:`logging_label` level.
    """
    def __init__ ( self, data, center, noise, rings, log_level = logging.INFO ):
        self.__version__ = '0.1.1'
        self.changelog = {
            '0.1.1' : "Improved dosctrings for Sphinx documentation.",
            '0.1.0' : "Adapted to use find_ring."
            }
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( log_level )
        super ( self.__class__, self ).__init__ ( )

        self.data = data
        self.center = center
        self.noise = noise.array
        self.rings = rings

        self.borders = None
        self.discontinuities = None
        self.discontinuities_distances = None
        self.distances = None

        self.start ( )

    def run ( self ):
        """
        Method required by :ref:`threading_label`, which allows parallel exection in a separate thread.
        
        First, this tool will aggregate all circles contained in the input rings dictionary. Then, it will map the distances from each pixel in the borders to the center of the rings structure. This is saved as the distances numpy.ndarray.
        """
        start = time.time ( )

        self.log.debug ( "self.center = {}".format ( self.center ) )
        self.aggregate_fits_into_borders ( )
        self.map_distances_onto_borders ( )
        self.distances = tuna.io.can ( self.borders )

        self.log.debug ( "ring_border_detector took %ds." % ( time.time ( ) - start ) )

    def aggregate_fits_into_borders ( self ):
        """
        This method begins creating a zero-filled numpy.ndarray of the same shape as the input data. Then each ring_fit in the input rings dictionary is added to this numpy.ndarray, which is saved as self.borders.
        """
        self.borders = numpy.zeros ( shape = self.data.shape )
        for index in self.rings [ 'concentric_rings' ] [ 2 ]:
            self.borders += self.rings [ 'ring_fit' ] [ index ]
            
    def map_distances_onto_borders ( self ):
        """
        This method will map the pixels belonging to the border with the value of the radius of its nearest ring. Essentially, the objective is to have every pixel that belongs to a certain "border" to have the same non-zero value, and for different ring borders to have different values.
        """
        for ring in self.rings [ 'ring_fit_parameters' ]:
            try:
                radii.append ( ring [ 2 ] )
            except:
                radii = [ ring [ 2 ] ]
        for col in range ( self.borders.shape [ 0 ] ):
            for row in range ( self.borders.shape [ 1 ] ):
                if self.borders [ col ] [ row ] == 0:
                    continue
                distance = tuna.tools.calculate_distance ( self.center, ( col, row ) )
                nearest_ring = 0
                nearest_distance = abs ( distance - radii [ 0 ] )
                for entry in range ( len ( radii ) ):
                    entry_distance = abs ( distance - radii [ entry ] )
                if entry_distance < nearest_distance:
                    nearest_distance = entry_distance
                    nearest_ring = entry
                self.borders [ col ] [ row ] = radii [ nearest_ring ]
        
    def detect_discontinuities_old ( self ):
        """
        From an unwrapped map and a noise map, create a map where pixels have 1 if they are noisy or have neighbours with a channel more distant than the channel distance threshold, 0 otherwise.
        """
        self.log.debug ( "Producing ring borders map." )
        ring_borders_map = numpy.zeros ( shape = self.data.array.shape )
        max_x = self.data.array.shape [ 0 ]
        max_y = self.data.array.shape [ 1 ]
        max_channel = numpy.amax ( self.data.array )
        threshold = max_channel / 2
        for x in range ( max_x ):
            for y in range ( max_y ):
                if self.noise.array [ x ] [ y ] == 1:
                    ring_borders_map [ x ] [ y ] = 1
                    continue
                neighbours = tuna.tools.get_pixel_neighbours ( ( x, y ), ring_borders_map )
                for neighbour in neighbours:
                    if self.noise.array [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] == 0:
                        distance = self.data.array [ x ] [ y ] - \
                                   self.data.array [ neighbour [ 0 ] ] [ neighbour [ 1 ] ]
                        if distance > threshold:
                            ring_borders_map [ x ] [ y ] = 1
                            break

        self.discontinuities = ring_borders_map
