from .file_reader import file_reader
import numpy
from os import listdir
from os.path import dirname, isfile, join
import re

class ada ( file_reader ):
    """
    Class for reading files in ADHOC format ADA.

    The ADHOC file formats were developed for use with the ADHOC software solution,
    developed at LAM by Jacques Boulesteix.
    """

    def __init__ ( self, array = None, log = print, file_name = None ):
        super ( ada, self ).__init__ ( )
        self.__file_name = file_name
        self.__array = array
        self.__metadata = { }
        self.log = log

    def get_array ( self ):
        return self.__array

    def get_metadata ( self ):
        return self.__metadata

    def read ( self ):
        if self.__file_name != None:
            if ( self.__file_name.startswith ( ".ADT", -4 ) or
                 self.__file_name.startswith ( ".adt", -4 ) ):
                self.read_adt ( )
        else:
            self.log ( "File name %s does not have .ADT or .adt suffix, aborting." % ( self.__file_name ) )

    def read_adt ( self ):
        self.__file_path = dirname ( self.__file_name )
        self.log ( "self.__file_path = %s." % ( self.__file_path ) )
        
        self.read_adt_metadata ( )

        adt = open ( self.__file_name, "r" )
               
        number_of_channels = int ( self.__metadata['Number of channels'] )
        self.log ( "number_of_channels = %s." % ( number_of_channels ) )

        for line in adt:
            if line.startswith ( "X and Y dimensions : 00512 00512" ):
                dimensions_string = line.split ( " : " )[1]
                dimensions = [ int ( dimensions_string.split ( " " )[0] ),
                               int ( dimensions_string.split ( " " )[1] ) ]
                break
        self.log ( "dimensions = %s." % ( dimensions ) )
       
        data_files = 0
        adt.seek ( 0 )
        for line in adt:
            if line.startswith ( "==>" ):
                data_files += 1
        self.log ( "data_files = %d." % ( data_files ) )

        photon_files = []
        file_list = listdir ( self.__file_path )
        for file_name in file_list:
            if isfile ( join ( self.__file_path, file_name ) ):
                if ( file_name.startswith ( ".ADA", -4 ) or
                     file_name.startswith ( ".ada", -4 ) ):
                    photon_files.append ( file_name )

        photon_files.sort ( )
        self.log ( "len ( photon_files ) = %d." % ( len ( photon_files ) ) )

        
        self.__array = numpy.zeros ( shape = ( number_of_channels,
                                                       dimensions[0], 
                                                       dimensions[1] ) )
        files_processed = 0
        last_printed = 0
        for element in range ( len ( photon_files ) ):
            file_name_entry = photon_files[element]
            channel = element % number_of_channels
            percentage_done = int ( 100 * files_processed / len ( photon_files ) )
            if last_printed < percentage_done:
                self.log ( "Adding photon counts into numpy array: %3d" % ( percentage_done ) + '%')
                last_printed = percentage_done

            file_result = self.read_ada ( file_name = file_name_entry, channel = channel )
            files_processed += 1
                
    def read_ada ( self, channel = -1, file_name = None ):
        """
        Attempts to read an ADHOC .ADA file containing photon counts.

        Returns a two-dimensional numpy array.

        Originally developed by Benoît Epinat, modified by Renato Borges.
        """
        
        if channel == -1:
            return

        if file_name == None:
            return
        
        file_path = join ( self.__file_path, file_name )
        photon_positions = numpy.fromfile ( file_path, dtype = numpy.int16 )
        # We know the file is organized with y,x,y,x,y,x... 
        # So the file will have size / 2 photons.
        photon_hits = photon_positions.reshape ( photon_positions.size / 2, 2 )
        for photon in range ( photon_hits.shape[0] ):
            x = photon_hits[photon][0]
            y = photon_hits[photon][1]
            self.__array[channel][x][y] += 1                
        #it seems that the first frame is duplicated
        #it would be nice to be able to display the creation of the image photon by photon

    def read_adt_metadata ( self ):
        adt = open ( self.__file_name, "r" )

        adt_header_lines = []
        for line in adt:
            if line.startswith ( "-----------------------------------------------------------------------------" ):
                break
            adt_header_lines.append ( line )

        adt_notes_lines = []
        for line in adt:
            if line.startswith ( "==>" ):
                break
            adt_notes_lines.append ( line )

        adt_parameters = { }
        for line in adt_header_lines:
            pair_regex = re.search ( "=", line )
            if pair_regex != None:
                pair = line.split ( "=" )
                key = pair[0].replace ( "\n", "" ).strip ( )
                value = pair[1].replace ( "\n", "" ).strip ( )
                adt_parameters[key] = value
                #self.log ( "...............%s" % ( line ) )
                #self.log ( "adt_parameters[%s] = %s" % ( key, adt_parameters[key] ) )
            else:
                adt_parameters[line] = ""

        adt_notes = ""
        for line in adt_notes_lines:
            adt_notes += line.strip ( ).replace ( "\n", "" )

        if "ADT notes" not in adt_parameters.keys ( ):
            adt_parameters["ADT notes"] = adt_notes

        acquisition_index = 0
        adt.seek ( 0 )
        for line in adt:
            if line.startswith ( "==>" ):                
                split_1 = line.split ( "==>  Beginning channel=" )
                split_2 = split_1[1].split ( " at " )
                acquisition_channel = split_2[0]
                acquisition_start_time = split_2[1]
                next_line = adt.readline ( )
                split_1 = next_line.split ( "Was acquired at " )
                split_2 = split_1[1].split ( ": ch=" )
                acquisition_end_time = split_2[0]
                split_3 = split_2[1].split ( "  cy=" )
                #acquisition_channel = split_3[0]
                split_4 = split_3[1].split ( " QGval=" )
                acquisition_cycle = split_4[0]
                split_5 = split_4[1].split ( "  ph=" )
                acquisition_queensgate_value = split_5[0]
                split_6 = split_5[1].split ( "  fr=" )
                acquisition_photon_count = split_6[0]
                acquisition_fr = split_6[1]

                next_line = adt.readline ( )
                split_1 = next_line.split ( "Cumulated exp=" )
                split_2 = split_1[1].split ( "  phot=" )
                acquisition_cumulated_exposure = split_2[0]
                split_3 = split_2[1].split ( " efficiency=" )
                acquisition_cumulated_photons = split_3[0]
                split_4 = split_3[1].split ( " %  disk=" )
                acquisition_efficiency = split_4[0]
                split_5 = split_4[1].split ( " Mb" )
                acquisition_disk_usage = split_5[1]

                next_line = adt.readline ( )
                split_1 = next_line.split ( "THT=" )
                split_2 = split_1[1].split ( "v  shutter=" )
                acquisition_THT = split_2[0]
                split_3 = split_2[1].split ( "  discri=" )
                acquisition_shutter = split_3[0]
                split_4 = split_3[1].split ( " BlackLevel=" )
                acquisition_discri = split_4[0]
                split_5 = split_4[1].split ( " Whitelevel=" )
                acquisition_blacklevel = split_5[0]
                acquisition_whitelevel = split_5[1]

                acquisition_index += 1
                prefix = "Acquisition " + str ( acquisition_index ) + " "
                adt_parameters[prefix + "channel"] = acquisition_channel.strip ( )
                adt_parameters[prefix + "start time"] = acquisition_start_time.strip ( )
                adt_parameters[prefix + "end time"] = acquisition_end_time.strip ( )
                adt_parameters[prefix + "cycle"] = acquisition_cycle.strip ( )
                adt_parameters[prefix + "Queensgate value"] = acquisition_queensgate_value.strip ( )
                adt_parameters[prefix + "photon count"] = acquisition_photon_count.strip ( )
                adt_parameters[prefix + "fr"] = acquisition_fr.strip ( )
                adt_parameters[prefix + "cumulated exposure"] = acquisition_cumulated_exposure.strip ( )
                adt_parameters[prefix + "cumulated photons"] = acquisition_cumulated_photons.strip ( )
                adt_parameters[prefix + "efficiency"] = acquisition_efficiency.strip ( )
                adt_parameters[prefix + "disk usage"] = acquisition_disk_usage.strip ( )
                adt_parameters[prefix + "THT"] = acquisition_THT.strip ( )
                adt_parameters[prefix + "shutter"] = acquisition_shutter.strip ( )
                adt_parameters[prefix + "discri"] = acquisition_discri.strip ( )
                adt_parameters[prefix + "blacklevel"] = acquisition_blacklevel.strip ( )
                adt_parameters[prefix + "whitelevel"] = acquisition_whitelevel.strip ( )

        self.__metadata = adt_parameters
