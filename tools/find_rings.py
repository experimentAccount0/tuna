"""
The scope of this module is to find rings within 3D FP spectrographs.
"""

import IPython
import logging
import math
import numpy
import tuna

class rings_finder ( object ):
    """
    The responsibility of this class is to find all rings contained in a data cube.
    """
    def __init__ ( self, array ):
        self.log = logging.getLogger ( __name__ )
        self.__version__ = '0.1.0'
        self.changelog = {
            '0.1.0' : "Initial version." }
        self.plot_log = True
        if self.plot_log:
            self.ipython = IPython.get_ipython()
            self.ipython.magic("matplotlib qt")

        self.chosen_plane = 1
        self.ridge_threshold = 2
        self.upper_percentile = 90

            
        self.array = array
        
        self.result = { }
        
    def execute ( self ):
        """
        1. segment the image in ring and non-ring regions.
        2. Create a separate array for each individual ring.
        3. Calculate the center and the average radius.
        """
        self.segment ( )
        #self.find_continuous_regions ( )
        #self.accumulate_traces ( )
        #self.hough_circles ( )
        self.get_statistics ( )
        self.log.debug ( "rings_finder finished." )
        
    def segment ( self ):
        if len ( self.array.shape ) != 3:
            self.log.info ( "This procedure expects a 3D numpy ndarray as input." )
        
        gradients = numpy.gradient ( self.array )
        if self.plot_log:
            tuna.tools.plot ( gradients [ 0 ] [ self.chosen_plane ], "gradients [ 0 ] [ {} ]".format (
                self.chosen_plane ), self.ipython )
            #tuna.tools.plot ( gradients [ 1 ], "Col gradients", self.ipython )
            #tuna.tools.plot ( gradients [ 2 ], "Row gradients", self.ipython )
        self.result [ 'gradients' ] = gradients
            
        gradient = gradients [ 0 ] [ self.chosen_plane ]
        self.result [ 'gradient' ] = gradient
            
        upper_percentile_value = numpy.percentile ( gradient, self.upper_percentile ) 
        upper_dep_gradient = numpy.where ( gradient > upper_percentile_value, 1, 0 )
        if self.plot_log:
            tuna.tools.plot ( upper_dep_gradient, "({}) upper_dep_gradient".format (
                self.upper_percentile ), self.ipython )

        lower_percentile = tuna.tools.find_lowest_nonnull_percentile ( gradient )
        lower_percentile_value = numpy.percentile ( gradient, lower_percentile )
        lower_percentile_regions = numpy.where ( gradient < lower_percentile_value, 1, 0 )
        if self.plot_log:
            tuna.tools.plot ( lower_percentile_regions, "({}) lower_percentile_regions".format (
                lower_percentile ), self.ipython )
        self.result [ 'lower_percentile_regions' ] = lower_percentile_regions

        ridge = numpy.zeros ( shape = gradient.shape )
        for col in range ( ridge.shape [ 0 ] ):
            for row in range ( ridge.shape [ 1 ] ):
                ridge [ col ] [ row ] = self.ridgeness ( upper_dep_gradient,
                                                         lower_percentile_regions,
                                                         col, row, threshold = self.ridge_threshold )
        if self.plot_log:
            tuna.tools.plot ( ridge, "ridge ", self.ipython )
        
        self.log.debug ( "ridge found" )    
        self.result [ 'ridge' ] = ridge

    def ridgeness ( self, upper, lower, col, row, threshold = 1 ):
        """
        Returns 1 if point at col, row has threshold neighbours that is 1 in both upper and lower arrays.
        """
        neighbours = tuna.tools.get_pixel_neighbours ( ( col, row ), upper )
        upper_neighbour = 0
        lower_neighbour = 0
        for neighbour in neighbours:
            if ( upper_neighbour >= threshold and
                 lower_neighbour >= threshold ):
                return 1
            if upper [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] == 1:
                upper_neighbour += 1
            if lower [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] == 1:
                lower_neighbour += 1
        if ( upper_neighbour >= threshold and
             lower_neighbour >= threshold ):
            return 1
        return 0    

    def find_continuous_regions ( self ):
        ridge = self.result [ 'ridge' ]
        painted = numpy.copy ( ridge )
        color = 1
        for col in range ( ridge.shape [ 0 ] ):
            self.log.debug ( "painted creation: col {}.".format ( col ) )
            for row in range ( ridge.shape [ 1 ] ):
                if painted [ col ] [ row ] != 0:
                    continue
                color += 1
                to_paint = [ ( col, row ) ]
                while ( len ( to_paint ) > 0 ):
                    here = to_paint.pop ( )
                    painted [ here [ 0 ] ] [ here [ 1 ] ] = color
                    neighbours = tuna.tools.get_pixel_neighbours ( here, ridge )
                    for neighbour in neighbours:
                        if painted [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] != 0:
                            continue
                        to_paint.append ( neighbour )
        if self.plot_log:
            tuna.tools.plot ( painted, "painted", self.ipython )
        self.result [ 'painted' ] = painted
        return
        color = 0
        continuous = painted - ridge
        for col in range ( continuous.shape [ 0 ] ):
            self.log.debug ( "continuous creation: col {}.".format ( col ) )
            for row in range ( continuous.shape [ 1 ] ):
                if continuous [ col ] [ row ] != 0:
                    color = continuous [ col ] [ row ]
                    continue
                to_paint = [ ( col, row ) ]
                while ( len ( to_paint ) > 0 ):
                    here = to_paint.pop ( )
                    painted [ here [ 0 ] ] [ here [ 1 ] ] = color
                    neighbours = tuna.tools.get_pixel_neighbours ( here, continuous )
                    for neighbour in neighbours:
                        if continuous [ neighbour [ 0 ] ] [ neighbour [ 1 ] ] != 0:
                            continue
                        to_paint.append ( neighbour )
        if self.plot_log:
            tuna.tools.plot ( continuous, "continuous", self.ipython )
        self.result [ 'continuous' ] = continuous

    def accumulate_traces ( self ):
        """
        From a zeroes array where ones mean existing points, create a new array where each existing point is connected to each other, and pixels in this line segment accumulate the value 1.
        """
        array = self.result [ 'ridge' ]
        accumulated = numpy.zeros ( shape = array.shape )
        points = [ ]
        thetas = [ ]
        for col in range ( array.shape [ 0 ] ):
            for row in range ( array.shape [ 1 ] ):
                if array [ col ] [ row ] == 1:
                    points.append ( ( col, row ) )
        unconsidered = points
        while ( len ( unconsidered ) > 0 ):
            here = unconsidered.pop ( )
            there = self.find_most_distant_pair ( here, points )
            if there in unconsidered:
                unconsidered.remove ( there )
            if there in points:
                points.remove ( there )
            self.add_trace ( accumulated, here, there, thetas, array )
        if self.plot_log:
            tuna.tools.plot ( accumulated, "accumulated", self.ipython )
        self.result [ 'accumulated' ] = accumulated

    def find_most_distant_pair ( self, origin, points ):
        max_distance = 0
        max_point = origin
        for point in points:
            distance = math.sqrt ( ( origin [ 0 ] - point [ 0 ] ) ** 2 +
                                   ( origin [ 1 ] - point [ 1 ] ) ** 2 )
            if distance >= max_distance:
                max_distance = distance
                max_point = point
        return max_point
        
    def add_trace ( self, array, origin, destiny, thetas, borders ):
        """
        Add 1 to each pixel in the line segment between origin and destiny.
        """
        diff_col = origin [ 0 ] - destiny [ 0 ]
        diff_row = origin [ 1 ] - destiny [ 1 ]
        if diff_col == 0:
            # not sure
            return
        theta = math.atan ( diff_row / diff_col )
        weight = 1
        if round ( theta, 2 ) in thetas:
            weight = 0.1
        thetas.append ( round ( theta, 2 ) )
        col_zero_crossing = origin [ 1 ] - theta * origin [ 0 ]
        border_latest = 0
        border_crossings = 0
        carry = 0
        temp = numpy.zeros ( shape = array.shape )
        for col in range ( array.shape [ 0 ] ):
            row = theta * col + col_zero_crossing
            if ( row < 0 or row > array.shape [ 1 ] ):
                continue
            #distance_origin = math.sqrt ( ( origin [ 0 ] - col ) ** 2 +
            #                              ( origin [ 1 ] - row ) ** 2 )
            #distance_destiny = math.sqrt ( ( destiny [ 0 ] - col ) ** 2 +
            #                               ( destiny [ 1 ] - row ) ** 2 )
            #distance = round ( abs ( distance_origin - distance_destiny ) )
            #array [ col ] [ row ] += distance
            temp [ col ] [ row ] += weight * carry
            carry += 1
            if borders [ col ] [ row ] == 1:
                if border_latest == 0:
                    border_crossings += 1
                    carry = 0
                    border_latest = 1
            else:
                border_latest = 0
        if border_crossings % 2 == 0:
            self.log.info ( "theta = {}".format ( theta ) )
            array += temp                

    def hough_circles ( self ):
        array = self.result [ 'ridge' ]
        for col in range ( array.shape [ 0 ] ):
            for row in range ( array.shape [ 1 ] ):
                circle = self.get_circle ( ( col, row ), 100, array.shape )
                diff = numpy.sum ( numpy.where ( array == circle, 1, 0 ) )
                self.log.info ( "({}, {}) diff = {}".format ( col, row, diff ) )
                
        #if self.plot_log:
        #    tuna.tools.plot ( circle, "circle", self.ipython )       
            
    def get_circle ( self, center, radius, shape ):
        result = numpy.zeros ( shape = shape )
        for col in range ( shape [ 0 ] ):
            for row in range ( shape [ 1 ] ):
                if round ( tuna.tools.calculate_distance ( center, ( col, row ) ) ) == round ( radius ):
                    result [ col ] [ row ] = 1
        return result

    def get_statistics ( self ):
        array = self.result [ 'ridge' ]
        max_col_crossings = 0
        max_col_cross = -1
        for col in range ( array.shape [ 0 ] ):
            border_latest = 0
            border_crossings = 0
            for row in range ( array.shape [ 1 ] ):
                if array [ col ] [ row ] == 1:
                    if border_latest == 0:
                        border_crossings += 1
                        if border_crossings > max_col_crossings:
                            max_col_crossings = border_crossings
                            max_col_cross = col                        
                        border_latest = 1
                else:
                    border_latest = 0
        self.log.info ( "row {} has {} max border crossings.".format ( max_col_cross, max_col_crossings ) )
        max_row_crossings = 0
        for row in range ( array.shape [ 1 ] ):
            border_latest = 0
            border_crossings = 0
            for col in range ( array.shape [ 0 ] ):
                if array [ col ] [ row ] == 1:
                    if border_latest == 0:
                        border_crossings += 1
                        if border_crossings > max_row_crossings:
                            max_row_crossings = border_crossings
                            max_row_cross = row
                        border_latest = 1
                else:
                    border_latest = 0
        self.log.info ( "col {} has {} max border crossings.".format ( max_row_cross, max_row_crossings ) )
    
def find_rings ( array ):
    """
    Attempts to find rings contained in a 3D numpy ndarray input.
    Returns a list of dicts, with the following keys:
    'array'  : 2D numpy.ndarray where pixels in the ring have value 1 and other pixels have value 0.
    'center' : a tuple of 2 floats, where the first is the column and the second is the row of the most probable locations for the center of that ring.
    'plane'  : A non-negative integer that corresponds to the index of the plane where this ring is in the original cube.
    'radius' : a float with the average value of the distance of the ring pixels to its center.
    """

    finder = rings_finder ( array )
    finder.execute ( )
    return finder.result

