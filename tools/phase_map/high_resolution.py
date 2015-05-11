import logging
from math import floor, sqrt
import numpy
import threading
import time
import tuna

class high_resolution ( threading.Thread ):
    """
    Creates and stores an unwrapped phase map, taking as input a raw data cube.
    Intermediary products are the binary noise, the ring borders, the regions and orders maps.
    """
    def __init__ ( self, 
                   beam,
                   calibration_wavelength,
                   finesse,
                   focal_length,
                   free_spectral_range,
                   gap,
                   interference_order,
                   interference_reference_wavelength,
                   scanning_wavelength,
                   tuna_can,
                   bad_neighbours_threshold = 7, 
                   channel_subset = [ ],
                   channel_threshold = 1, 
                   continuum_to_FSR_ratio = 0.125,
                   noise_mask_radius = 1 ):

        """
        Creates the phase map from raw data obtained with a Fabry-Perot instrument.

        Parameters:
        ---
        - array : the raw data. Must be a 3D numpy.ndarray.
        - bad_neighbours_threshold : how many neighbouring pixels can have a value above the threshold before the pixel itself is conidered noise.
        - channel_threshold : the distance, in "channels", that a neighbouring pixel' value can have before being considered noise.
        - noise_mas_radius : the distance from a noise pixel that will be marked as noise also (size of a circle around each noise pixel).
        """
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.DEBUG )

        super ( high_resolution, self ).__init__ ( )
        self.zmq_client = tuna.zeromq.zmq_client ( )

        self.log.info ( "Starting high_resolution pipeline." )

        """inputs:"""
        self.bad_neighbours_threshold = bad_neighbours_threshold
        self.beam = beam
        self.calibration_wavelength = calibration_wavelength
        self.channel_subset = channel_subset
        self.channel_threshold = channel_threshold
        self.continuum_to_FSR_ratio = continuum_to_FSR_ratio
        self.finesse = finesse
        self.focal_length = focal_length
        self.free_spectral_range = free_spectral_range
        self.gap = gap
        self.interference_order = interference_order
        self.interference_reference_wavelength = interference_reference_wavelength
        self.noise_mask_radius = noise_mask_radius
        self.scanning_wavelength = scanning_wavelength
        self.tuna_can = tuna_can

        """outputs:"""
        self.airy_fit = None
        self.airy_fit_residue = None
        self.borders_to_center_distances = None
        self.continuum = None
        self.discontinuum = None
        self.fsr_map = None
        self.noise = None
        self.order_map = None
        self.parabolic_fit = None
        self.parabolic_model = None
        self.rings_center = None
        self.substituted_channels = None
        self.unwrapped_phase_map = None
        self.wavelength_calibrated = None
        self.wrapped_phase_map = None

    def run ( self ):
        self.continuum = tuna.tools.phase_map.detect_continuum ( array = self.tuna_can.array, 
                                                                 continuum_to_FSR_ratio = self.continuum_to_FSR_ratio )

        self.discontinuum = tuna.io.can ( array = numpy.ndarray ( shape = self.tuna_can.shape ) )
        for plane in range ( self.tuna_can.planes ):
            self.discontinuum.array [ plane, : , : ] = numpy.abs ( self.tuna_can.array [ plane, : , : ] - self.continuum.array )

        self.wrapped_phase_map = tuna.tools.phase_map.detect_barycenters ( array = self.discontinuum.array )

        find_center = tuna.tools.phase_map.find_image_center_by_arc_segmentation
        self.rings_center = find_center ( wrapped = self.wrapped_phase_map )

        self.noise = tuna.tools.phase_map.detect_noise ( array = self.wrapped_phase_map.array, 
                                                         bad_neighbours_threshold = self.bad_neighbours_threshold, 
                                                         channel_threshold = self.channel_threshold, 
                                                         noise_mask_radius = self.noise_mask_radius )

        map_distances = tuna.tools.phase_map.create_borders_to_center_distances
        self.borders_to_center_distances = map_distances ( array = self.wrapped_phase_map.array,
                                                           center = self.rings_center,
                                                           noise_array = self.noise.array )

        self.fsr_map = tuna.tools.phase_map.create_fsr_map ( distances = self.borders_to_center_distances.array,
                                                             center = self.rings_center,
                                                             wrapped = self.wrapped_phase_map.array )

        self.order_map = tuna.io.can ( array = self.fsr_map.astype ( dtype = numpy.float64 ) )

        self.create_unwrapped_phase_map ( )

        polynomial_fit = tuna.tools.models.fit_parabolic_model_by_Polynomial2D
        self.parabolic_model, self.parabolic_fit = polynomial_fit ( center = self.rings_center, 
                                                                    noise = self.noise.array, 
                                                                    unwrapped = self.unwrapped_phase_map.array )
        self.verify_parabolic_model ( )

        self.airy_fit = tuna.tools.models.fit_airy ( beam = self.beam,
                                                     center = self.rings_center,
                                                     discontinuum = self.discontinuum,
                                                     finesse = self.finesse,
                                                     focal_length = self.focal_length,
                                                     gap = self.gap )

        airy_fit_residue = numpy.abs ( self.tuna_can.array - self.airy_fit.array )
        self.airy_fit_residue = tuna.io.can ( array = airy_fit_residue )

        substituted_channels = numpy.copy ( self.tuna_can.array )
        for channel in range ( self.tuna_can.planes ):
            if channel in self.channel_subset:
                substituted_channels [ plane ] = numpy.copy ( self.airy_fit.array [ plane ] )
        self.substituted_channels = tuna.io.can ( array = substituted_channels )

        wavelength = tuna.tools.wavelength.calibration
        self.wavelength_calibrated = wavelength ( self.rings_center,
                                                  calibration_wavelength = self.calibration_wavelength,
                                                  free_spectral_range = self.free_spectral_range,
                                                  interference_order = self.interference_order,
                                                  interference_reference_wavelength = self.interference_reference_wavelength,
                                                  scanning_wavelength = self.scanning_wavelength,
                                                  unwrapped_phase_map = self.unwrapped_phase_map )
        
    def create_unwrapped_phase_map ( self ):
        """
        Unwraps the phase map according using the order array constructed.
        """
        start = time.time ( )

        max_x = self.wrapped_phase_map.array.shape[0]
        max_y = self.wrapped_phase_map.array.shape[1]
        max_channel = numpy.amax ( self.wrapped_phase_map.array )
        min_channel = numpy.amin ( self.wrapped_phase_map.array )

        unwrapped_phase_map = numpy.zeros ( shape = self.wrapped_phase_map.shape )
        self.log ( "debug: unwrapped_phase_map.ndim == %d" % unwrapped_phase_map.ndim )

        self.log ( "info: phase map 0% unwrapped." )
        last_percentage_logged = 0
        for x in range ( max_x ):
            percentage = 10 * int ( x / max_x * 10 )
            if percentage > last_percentage_logged:
                last_percentage_logged = percentage
                self.log ( "info: phase map %d%% unwrapped." % percentage )
            for y in range ( max_y ):
                unwrapped_phase_map [ x ] [ y ] = self.wrapped_phase_map.array [ x ] [ y ] + \
                                                  max_channel * float ( self.order_map.array [ x ] [ y ] )
        self.log ( "info: phase map 100% unwrapped." )

        self.unwrapped_phase_map = tuna.io.can ( log = self.log,
                                                 array = unwrapped_phase_map )

        self.log ( "info: create_unwrapped_phase_map() took %ds." % ( time.time ( ) - start ) )

    def verify_parabolic_model ( self ):
        self.log ( "info: Ratio between 2nd degree coefficients is: %f" % ( self.parabolic_model [ 'x2y0' ] / 
                                                                            self.parabolic_model [ 'x0y2' ] ) )

def high_resolution_pipeline ( beam,
                               calibration_wavelength,
                               finesse,
                               focal_length,
                               free_spectral_range,
                               gap,
                               interference_order,
                               interference_reference_wavelength,
                               scanning_wavelength,
                               tuna_can,
                               bad_neighbours_threshold = 7, 
                               channel_subset = [ ],
                               channel_threshold = 1, 
                               continuum_to_FSR_ratio = 0.125,
                               noise_mask_radius = 1,
                               log = print ):
    
    if not isinstance ( tuna_can, tuna.io.can ):
        log ( "info: array must be a numpy.ndarray or derivative object." )
        return
    try:
        if tuna_can.ndim != 3:
            self.log ( "warning: Image does not have 3 dimensions, aborting." )
            return
    except AttributeError as e:
        self.log ( "warning: %s, aborting." % str ( e ) )
        return

    high_resolution_pipeline = high_resolution ( beam,
                                                 calibration_wavelength,
                                                 finesse,
                                                 focal_length,
                                                 free_spectral_range,
                                                 gap,
                                                 interference_order,
                                                 interference_reference_wavelength,
                                                 scanning_wavelength,
                                                 tuna_can,
                                                 bad_neighbours_threshold, 
                                                 channel_subset,
                                                 channel_threshold, 
                                                 continuum_to_FSR_ratio,
                                                 noise_mask_radius )
    high_resolution_pipeline.start ( )
    high_resolution_pipeline.join ( )

    return high_resolution_pipeline

def profile_processing_history ( high_resolution, pixel ):
    profile = { }

    profile [ 0 ] = ( 'Original data', high_resolution.tuna_can.array [ :, pixel [ 0 ], pixel [ 1 ] ] )
    profile [ 1 ] = ( 'Discontinuum', high_resolution.discontinuum.array [ :, pixel [ 0 ], pixel [ 1 ] ] )
    profile [ 2 ] = ( 'Wrapped phase map', high_resolution.wrapped_phase_map.array [ pixel [ 0 ] ] [ pixel [ 1 ] ] )
    profile [ 3 ] = ( 'Order map', high_resolution.order_map.array [ pixel [ 0 ] ] [ pixel [ 1 ] ] )
    profile [ 4 ] = ( 'Unwrapped phase map', high_resolution.unwrapped_phase_map.array [ pixel [ 0 ] ] [ pixel [ 1 ] ] )
    profile [ 5 ] = ( 'Parabolic fit', high_resolution.parabolic_fit.array [ pixel [ 0 ] ] [ pixel [ 1 ] ] )
    profile [ 6 ] = ( 'Airy fit', high_resolution.airy_fit.array [ :, pixel [ 0 ], pixel [ 1 ] ] )
    profile [ 7 ] = ( 'Wavelength', high_resolution.wavelength_calibrated.array [ pixel [ 0 ] ] [ pixel [ 1 ] ] )

    return profile
