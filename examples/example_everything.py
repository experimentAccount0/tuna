#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna.init ( )

# User-specific code would go here.
def compare_barycenter ( ):
    o_barycenter_file      = tuna.io.read ( file_name = '2_wrapped.fits' )
    a_barycenter           = o_barycenter_file.get_array ( )
    o_barycenter_gold_file = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/g094_compever_bru.ad2' )
    a_barycenter_gold      = o_barycenter_gold_file.get_array ( )

    import numpy
    a_comparison = numpy.ndarray ( shape = a_barycenter.shape )
    for i_row in range ( a_comparison.shape[0] ):
        for i_col in range ( a_comparison.shape[1] ):
            a_comparison [ i_row ] [ i_col ] = ( a_barycenter_gold [ i_row ] [ i_col ] - 
                                                 a_barycenter [ i_row ] [ i_col ] )

    tuna.io.write ( file_name   = '2_wrapped_residue.fits',
                    array       = a_comparison,
                    file_format = 'fits' )
    
def unwrap_phase_map ( ):
    o_raw_file = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G094.AD3' )
    a_raw      = o_raw_file.get_array ( )
    o_high_res = tuna.tools.phase_map.high_resolution ( f_airy_max_distance = 1904.325,
                                                        f_airy_min_distance = 1904,
                                                        array = a_raw,
                                                        f_calibration_wavelength = 6598.950,
                                                        f_free_spectral_range = 1,
                                                        wrapped_phase_map_algorithm = tuna.tools.phase_map.create_barycenter_array, 
                                                        channel_threshold = 1, 
                                                        bad_neighbours_threshold = 7, 
                                                        noise_mask_radius = 7,
                                                        f_scanning_wavelength = 6616.895 )

    a_continuum              = o_high_res.get_continuum_array ( )
    a_wrapped                = o_high_res.get_wrapped_phase_map_array ( )
    a_noise                  = o_high_res.get_binary_noise_array ( )
    a_distances              = o_high_res.get_borders_to_center_distances ( )
    a_FSRs                   = o_high_res.get_order_array ( )
    a_unwrapped              = o_high_res.get_unwrapped_phase_map_array ( )
    a_parabolic_model        = o_high_res.get_parabolic_Polynomial2D_model ( )
    a_airy                   = o_high_res.get_airy ( )
    a_wavelength             = o_high_res.get_wavelength_calibrated ( )

    tuna.io.write ( file_name   = '0_raw.fits',
                    array       = a_raw,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '1_continuum.fits',
                    array       = a_continuum,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '2_wrapped.fits',
                    array       = a_wrapped,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '3_noise.fits',
                    array       = a_noise,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '4_distances.fits',
                    array       = a_distances,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '5_FSRs.fits',
                    array       = a_FSRs,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '6_unwrapped.fits',
                    array       = a_unwrapped,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '7_parabolic_model.fits',
                    array       = a_parabolic_model,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '8_airy_model.fits',
                    array       = a_airy,
                    file_format = 'fits' )    
    tuna.io.write ( file_name   = '9_wavelength_calibrated.fits',
                    array       = a_wavelength,
                    file_format = 'fits' )    

    #t_parabolic_coefficients = o_high_res.get_parabolic_Polynomial2D_coefficients ( )
    #print ( "Parabolic model coefficients = %s" % str ( t_parabolic_coefficients ) )

def wavelength_residue ( ):
    o_wavelength = tuna.io.read ( file_name = '9_wavelength_calibrated.fits' )
    o_unwrapped  = tuna.io.read ( file_name = '6_unwrapped.fits' )
    a_wavelength = o_wavelength.get_array ( )
    a_unwrapped  = o_unwrapped .get_array ( )

    import numpy
    a_comparison = numpy.ndarray ( shape = a_unwrapped.shape )
    a_comparison = a_unwrapped - a_wavelength

    tuna.io.write ( file_name   = '9_wavelength_calibrated_residue.fits',
                    array       = a_comparison,
                    file_format = 'fits' )
    
def compile_raw_data_from_ADAs ( ):
    o_file = tuna.io.read ( file_name = '/home/nix/sync/tuna/sample_data/G093/G093.ADT' )
    a_raw = o_file.get_array ( )

    tuna.io.write ( file_name   = 'raw.fits',
                    array       = a_raw, 
                    metadata    = o_file.get_metadata ( ),
                    file_format = 'fits',
                    d_photons   = o_file.get_photons ( ) )

compile_raw_data_from_ADAs ( )
unwrap_phase_map ( )
compare_barycenter ( )
wavelength_residue ( )

# This call is required to close the daemons gracefully:
tuna.finish ( )