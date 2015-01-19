#!/bin/env python3

# Import all modules and classes relevant to a user:
import tuna

# Start the backend processes, such as the 0MQ proxy and the log server:
tuna_daemons = tuna.console.backend ( ) 
tuna_daemons.start ( )

# User-specific code would go here.
def g092 ( ):
    g092 = tuna.io.adhoc ( file_name = 'examples/G092.AD3' )
    g092_phase_map = tuna.tools.phase_map_creation.high_resolution_Fabry_Perot_phase_map_creation ( file_object = g092 )

    fits_object = tuna.io.fits ( image_ndarray = g092_phase_map.get_max_channel_map ( ) )
    fits_object.write ( file_name = 'g092_1_max_channel_map.fits' )

    fits_object = tuna.io.fits ( image_ndarray = g092_phase_map.get_binary_noise_map ( ) )
    fits_object.write ( file_name = 'g092_2_binary_noise_map.fits' )

    fits_object = tuna.io.fits ( image_ndarray = g092_phase_map.get_ring_borders_map ( ) )
    fits_object.write ( file_name = 'g092_3_ring_borders_map.fits' )

    fits_object = tuna.io.fits ( image_ndarray = g092_phase_map.get_regions_map ( ) )
    fits_object.write ( file_name = 'g092_4_regions_map.fits' )

    fits_object = tuna.io.fits ( image_ndarray = g092_phase_map.get_order_map ( ) )
    fits_object.write ( file_name = 'g092_5_order_map.fits' )

    fits_object = tuna.io.fits ( image_ndarray = g092_phase_map.get_unwrapped_phases_map ( ) )
    fits_object.write ( file_name = 'g092_6_unwrapped_phases_map.fits' )

def g093 ( ):
    g093 = tuna.io.read ( file_name = '/home/nix/cloud_fpdata1/2014-11-05_Benoit_ngc772/G093/G093.ADT' )
    tuna.io.write ( file_name   = 'g093_fits_file.fits',
	            array       = g093.get_array    ( ), 
		    metadata    = g093.get_metadata ( ),
		    file_format = 'fits' )
    g093b = tuna.io.read ( file_name = 'g093_fits_file.fits' )
    print ( "Queensgate constant = %s." % ( g093b.get_metadata ( )['Queensgate constant'] ) )

def g094 ( ):
    #g094_can = tuna.io.read ( file_name = 'examples/G094.AD3' )
    #g094_barycenter_array = tuna.tools.phase_map_creation.create_barycenter_array ( array = g094_can.get_array ( ) )
    #tuna.io.write ( file_name   = 'g094_fits_file.fits',
#	             array       = g094_barycenter_array,
#                    file_format = 'fits' )
    g094_can = tuna.io.read ( file_name = 'g094_fits_file.fits' )  
    g094_binary_noise_map = tuna.tools.phase_map_creation.create_binary_noise_map ( array = g094_can.get_array ( ) )
    tuna.io.write (  file_name   = 'g094_binary_noise_map.fits',
	             array       = g094_binary_noise_map,
		     file_format = 'fits' )
#g092 ( )
#g093 ( )
g094 ( )

# This call is required to close the daemons gracefully:
tuna_daemons.finish ( )