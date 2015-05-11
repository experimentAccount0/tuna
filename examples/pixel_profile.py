#!/bin/env ipython3

# Import all modules and classes relevant to a user:
import tuna

file_name = "/home/nix/sync/tuna/sample_data/G094.AD3"
file_name_unpathed = file_name.split ( "/" ) [ -1 ]
file_name_prefix = file_name_unpathed.split ( "." ) [ 0 ]

can = tuna.io.read ( file_name )
high_res = tuna.tools.phase_map.high_resolution_pipeline ( beam = 450,
                                                           calibration_wavelength = 6598.953125,
                                                           finesse = 15.,
                                                           focal_length = 0.1,
                                                           free_spectral_range = 8.36522123894,
                                                           gap = 1904,
                                                           interference_order = 791,
                                                           interference_reference_wavelength = 6562.7797852,
                                                           channel_threshold = 1, 
                                                           bad_neighbours_threshold = 7, 
                                                           noise_mask_radius = 10,
                                                           scanning_wavelength = 6616.89,
                                                           tuna_can = can )

tuna.write ( file_name   = file_name_prefix + '_00_original.fits',
             array       = can.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_01_continuum.fits',
             array       = high_res.continuum.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_02_discontinuum.fits',
             array       = high_res.discontinuum.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_03_wrapped_phase_map.fits',
             array       = high_res.wrapped_phase_map.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_04_noise.fits',
             array       = high_res.noise.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_05_borders_to_center_distances.fits',
             array       = high_res.borders_to_center_distances.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_06_order_map.fits',
             array       = high_res.order_map.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_07_unwrapped_phase_map.fits',
             array       = high_res.unwrapped_phase_map.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_08_parabolic_fit.fits',
             array       = high_res.parabolic_fit.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_09_airy_fit.fits',
             array       = high_res.airy_fit.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_09_airy_fit_residue.fits',
             array       = high_res.airy_fit_residue.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_10_substituted_channels.fits',
             array       = high_res.substituted_channels.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_11_wavelength_calibrated.fits',
             array       = high_res.wavelength_calibrated.array,
             file_format = 'fits' )    

print ( "Profile for pixel 200, 200:" )
profile = tuna.tools.phase_map.profile_processing_history ( high_res, ( 200, 200 ) )
for key in profile.keys ( ):
    print ( "step %2d: %s" % ( key, str ( profile [ key ] ) ) )