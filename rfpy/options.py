# Copyright 2019 Pascal Audet
#
# This file is part of RfPy.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""

Module containing the main utility functions used in the `RfPy` scripts
that accompany this package.

"""

# -*- coding: utf-8 -*-

def get_calc_options():
    """
    Get Options from :class:`~optparse.OptionParser` objects.

    This function is used for data processing on-the-fly (requires web connection)

    """

    from optparse import OptionParser, OptionGroup
    from os.path import exists as exist
    from obspy import UTCDateTime
    from numpy import nan

    parser = OptionParser(
        usage="Usage: %prog [options] <station database>",
        description="Script used to download and pre-process " +
        "three-component (Z, N, and E), seismograms for individual " +
        "events and calculate teleseismic P-wave receiver functions" +
        "This version requests data on the fly for a given date " +
        "range. Data are requested from the internet using the " +
        "client services framework. The stations are processed one " +
        "by one and the data are stored to disk.")

    # General Settings
    parser.add_option(
        "--keys",
        action="store",
        type=str,
        dest="stkeys",
        default="",
        help="Specify a comma separated list of station keys for " +
        "which to perform the analysis. These must be " +
        "contained within the station database. Partial keys will " +
        "be used to match against those in the dictionary. For " +
        "instance, providing IU will match with all stations in " +
        "the IU network [Default processes all stations in the database]")
    parser.add_option(
        "-v", "-V", "--verbose",
        action="store_true",
        dest="verb",
        default=False,
        help="Specify to increase verbosity.")
    parser.add_option(
        "-O", "--overwrite",
        action="store_true",
        dest="ovr",
        default=False,
        help="Force the overwriting of pre-existing data. " +
        "[Default False]")

    # Server Settings
    ServerGroup = OptionGroup(
        parser,
        title="Server Settings",
        description="Settings associated with which "
        "datacenter to log into.")
    ServerGroup.add_option(
        "-S", "--Server",
        action="store",
        type=str,
        dest="Server",
        default="IRIS",
        help="Specify the server to connect to. Options include: " +
        "BGR, ETH, GEONET, GFZ, INGV, IPGP, IRIS, KOERI, " +
        "LMU, NCEDC, NEIP, NERIES, ODC, ORFEUS, RESIF, SCEDC, USGS, USP. " +
        "[Default IRIS]")
    ServerGroup.add_option(
        "-U", "--User-Auth",
        action="store",
        type=str,
        dest="UserAuth",
        default="",
        help="Enter your IRIS Authentification Username and Password " +
        "(--User-Auth='username:authpassword') to " +
        "access and download restricted data. " +
        "[Default no user and password]")

    # Database Settings
    DataGroup = OptionGroup(
        parser,
        title="Local Data Settings",
        description="Settings associated with defining " +
        "and using a local data base of pre-downloaded " +
        "day-long SAC files.")
    DataGroup.add_option(
        "--local-data",
        action="store",
        type=str,
        dest="localdata",
        default=None,
        help="Specify a comma separated list of paths containing " +
        "day-long sac files of data already downloaded. " +
        "If data exists for a seismogram is already present on disk, " +
        "it is selected preferentially over downloading " +
        "the data using the Client interface")
    DataGroup.add_option(
        "--no-data-zero",
        action="store_true",
        dest="ndval",
        default=False,
        help="Specify to force missing data to be set as zero, rather " +
        "than default behaviour which sets to nan.")
    DataGroup.add_option(
        "--no-local-net",
        action="store_false",
        dest="useNet",
        default=True,
        help="Specify to prevent using the Network code in the " +
        "search for local data (sometimes for CN stations " +
        "the dictionary name for a station may disagree with that " +
        "in the filename. [Default Network used]")

    # Event Selection Criteria
    EventGroup = OptionGroup(
        parser,
        title="Event Settings",
        description="Settings associated with refining " +
        "the events to include in matching event-station pairs")
    EventGroup.add_option(
        "--start",
        action="store",
        type=str,
        dest="startT",
        default="",
        help="Specify a UTCDateTime compatible string representing " +
        "the start time for the event search. This will override any " +
        "station start times. [Default start date of station]")
    EventGroup.add_option(
        "--end",
        action="store",
        type=str,
        dest="endT",
        default="",
        help="Specify a UTCDateTime compatible string representing " +
        "the end time for the event search. This will override any " +
        "station end times [Default end date of station]")
    EventGroup.add_option(
        "--reverse", "-R",
        action="store_true",
        dest="reverse",
        default=False,
        help="Reverse order of events. Default behaviour starts at " +
        "oldest event and works towards most recent. Specify reverse " +
        "order and instead the program will start with the most recent " +
        "events and work towards older")
    EventGroup.add_option(
        "--minmag",
        action="store",
        type=float,
        dest="minmag",
        default=6.0,
        help="Specify the minimum magnitude of event for which to search. " +
        "[Default 6.0]")
    EventGroup.add_option(
        "--maxmag",
        action="store",
        type=float,
        dest="maxmag",
        default=9.0,
        help="Specify the maximum magnitude of event for which to search. " +
        "[Default None, i.e. no limit]")

    # Geometry Settings
    PhaseGroup = OptionGroup(
        parser,
        title="Geometry Settings",
        description="Settings associatd with the "
        "event-station geometries for the specified phase")
    PhaseGroup.add_option(
        "--phase",
        action="store",
        type=str,
        dest="phase",
        default='P',
        help="Specify the phase name to use. Be careful with the distance. "+
        "setting. Options are 'P' or 'PP'. [Default 'P']")
    PhaseGroup.add_option(
        "--mindist",
        action="store",
        type=float,
        dest="mindist",
        default=None,
        help="Specify the minimum great circle distance (degrees) between " +
        "the station and event. [Default depends on phase]")
    PhaseGroup.add_option(
        "--maxdist",
        action="store",
        type=float,
        dest="maxdist",
        default=None,
        help="Specify the maximum great circle distance (degrees) between " +
        "the station and event. [Default depends on phase]")

    # Constants Settings
    ConstGroup = OptionGroup(
        parser,
        title='Parameter Settings',
        description="Miscellaneous default values and settings")
    ConstGroup.add_option(
        "--sampling-rate",
        action="store",
        type=float,
        dest="new_sampling_rate",
        default=10.,
        help="Specify new sampling rate in Hz. [Default 10.]")
    ConstGroup.add_option(
        "--dts",
        action="store",
        type=float,
        dest="dts",
        default=150.,
        help="Specify the window length in sec (symmetric about arrival " +
        "time). [Default 150.]")
    ConstGroup.add_option(
        "--align",
        action="store",
        type=str,
        dest="align",
        default=None,
        help="Specify component alignment key. Can be either " +
        "ZRT, LQT, or PVH. [Default ZRT]")
    ConstGroup.add_option(
        "--vp",
        action="store",
        type=float,
        dest="vp",
        default=6.0,
        help="Specify near-surface Vp to use with --align=PVH (km/s). "+
        "[Default 6.0]")
    ConstGroup.add_option(
        "--vs",
        action="store",
        type=float,
        dest="vs",
        default=3.5,
        help="Specify near-surface Vs to use with --align=PVH (km/s). "+
        "[Default 3.5]")
    ConstGroup.add_option(
        "--dt-snr",
        action="store",
        type=float,
        dest="dt_snr",
        default=30.,
        help="Specify the window length over which to calculate " +
        "the SNR in sec. [Default 30.]")
    ConstGroup.add_option(
        "--pre-filt",
        action="store",
        type=str,
        dest="pre_filt",
        default=None,
        help="Specify two floats with low and high frequency corners for "+
        "pre-filter (before deconvolution). [Default None]")
    ConstGroup.add_option(
        "--fmin",
        action="store",
        type=float,
        dest="fmin",
        default=0.05,
        help="Specify the minimum frequency corner for SNR and CC " +
        "filter (Hz). [Default 0.05]")
    ConstGroup.add_option(
        "--fmax",
        action="store",
        type=float,
        dest="fmax",
        default=1.0,
        help="Specify the maximum frequency corner for SNR and CC " +
        "filter (Hz). [Default 1.0]")

    # Constants Settings
    DeconGroup = OptionGroup(
        parser,
        title='Deconvolution Settings',
        description="Parameters for deconvolution")
    DeconGroup.add_option(
        "--method",
        action="store",
        dest="method",
        type=str,
        default="wiener",
        help="Specify the deconvolution method. Available methods " +
        "include 'wiener', 'water' and 'multitaper'. [Default 'wiener']")
    DeconGroup.add_option(
        "--gfilt",
        action="store",
        dest="gfilt",
        type=float,
        default=None,
        help="Specify the Gaussian filter width in Hz. " +
        "[Default None]")
    DeconGroup.add_option(
        "--wlevel",
        action="store",
        dest="wlevel",
        type=float,
        default=0.01,
        help="Specify the water level, used in the 'water' method. "+
        "[Default 0.01]")



    parser.add_option_group(ServerGroup)
    parser.add_option_group(DataGroup)
    parser.add_option_group(EventGroup)
    parser.add_option_group(PhaseGroup)
    parser.add_option_group(ConstGroup)
    parser.add_option_group(DeconGroup)

    (opts, args) = parser.parse_args()

    # Check inputs
    if len(args) != 1:
        parser.error("Need station database file")
    indb = args[0]
    if not exist(indb):
        parser.error("Input file " + indb + " does not exist")

    # create station key list
    if len(opts.stkeys) > 0:
        opts.stkeys = opts.stkeys.split(',')

    # construct start time
    if len(opts.startT) > 0:
        try:
            opts.startT = UTCDateTime(opts.startT)
        except:
            parser.error(
                "Cannot construct UTCDateTime from start time: " +
                opts.startT)
    else:
        opts.startT = None

    # construct end time
    if len(opts.endT) > 0:
        try:
            opts.endT = UTCDateTime(opts.endT)
        except:
            parser.error(
                "Cannot construct UTCDateTime from end time: " +
                opts.endT)
    else:
        opts.endT = None

    # Parse User Authentification
    if not len(opts.UserAuth) == 0:
        tt = opts.UserAuth.split(':')
        if not len(tt) == 2:
            parser.error(
                "Error: Incorrect Username and Password " +
                "Strings for User Authentification")
        else:
            opts.UserAuth = tt
    else:
        opts.UserAuth = []

    # Parse Local Data directories
    if opts.localdata is not None:
        opts.localdata = opts.localdata.split(',')
    else:
        opts.localdata = []

    # Check NoData Value
    if opts.ndval:
        opts.ndval = 0.0
    else:
        opts.ndval = nan

    # Check distances for selected phase
    if opts.phase not in ['P', 'PP', 'S', 'SKS']:
        parser.error(
            "Error: choose between 'P', 'PP', 'S' and 'SKS'.")
    if opts.phase == 'P':
        if not opts.mindist:
            opts.mindist = 30.
        if not opts.maxdist:
            opts.maxdist = 100.
        if opts.mindist < 30. or opts.maxdist > 100.:
            parser.error(
                "Distances should be between 30 and 100 deg. for "+
                "teleseismic 'P' waves.")
    elif opts.phase == 'PP':
        if not opts.mindist:
            opts.mindist = 100.
        if not opts.maxdist:
            opts.maxdist = 180.
        if opts.mindist < 100. or opts.maxdist > 180.:
            parser.error(
                "Distances should be between 100 and 180 deg. for "+
                "teleseismic 'PP' waves.")
    elif opts.phase == 'S':
        if not opts.mindist:
            opts.mindist = 55.
        if not opts.maxdist:
            opts.maxdist = 85.
        if opts.mindist < 55. or opts.maxdist > 85.:
            parser.error(
                "Distances should be between 55 and 85 deg. for "+
                "teleseismic 'S' waves.")
    elif opts.phase == 'SKS':
        if not opts.mindist:
            opts.mindist = 85.
        if not opts.maxdist:
            opts.maxdist = 115.
        if opts.mindist < 85. or opts.maxdist > 115.:
            parser.error(
                "Distances should be between 85 and 115 deg. for "+
                "teleseismic 'SKS' waves.")

    if opts.pre_filt is not None:
        opts.pre_filt = [float(val) for val in opts.pre_filt.split(',')]
        opts.pre_filt = sorted(opts.pre_filt)
        if (len(opts.pre_filt)) != 2:
            parser.error(
                "Error: --pre-filt should contain 2 " +
                "comma-separated floats")

    # Check alignment options
    if opts.align is None:
        opts.align = 'ZRT'
    elif opts.align not in ['ZRT', 'LQT', 'PVH']:
        parser.error(
            "Error: Incorrect alignment specifier. Should be " +
            "either 'ZRT', 'LQT', or 'PVH'.")

    if opts.dt_snr > opts.dts:
        opts.dt_snr = opts.dts - 10.
        print("SNR window > data window. Defaulting to data " +
              "window minus 10 sec.")

    if opts.method not in ['wiener', 'water', 'multitaper']:
        parser.error(
            "Error: 'method' should be either 'wiener', 'water' or " +
            "'multitaper'")

    return (opts, indb)


def get_recalc_options():
    """
    Get Options from :class:`~optparse.OptionParser` objects.

    This function is used for data processing on-the-fly (requires web connection)

    """

    from optparse import OptionParser, OptionGroup
    from os.path import exists as exist
    from obspy import UTCDateTime
    from numpy import nan

    parser = OptionParser(
        usage="Usage: %prog [options] <station database>",
        description="Script used to download and pre-process " +
        "three-component (Z, N, and E), seismograms for individual " +
        "events and calculate teleseismic P-wave receiver functions" +
        "This version requests data on the fly for a given date " +
        "range. Data are requested from the internet using the " +
        "client services framework. The stations are processed one " +
        "by one and the data are stored to disk.")

    # General Settings
    parser.add_option(
        "--keys",
        action="store",
        type=str,
        dest="stkeys",
        default="",
        help="Specify a comma separated list of station keys for " +
        "which to perform the analysis. These must be " +
        "contained within the station database. Partial keys will " +
        "be used to match against those in the dictionary. For " +
        "instance, providing IU will match with all stations in " +
        "the IU network [Default processes all stations in the database]")
    parser.add_option(
        "-v", "-V", "--verbose",
        action="store_true",
        dest="verb",
        default=False,
        help="Specify to increase verbosity.")

    # Constants Settings
    ConstGroup = OptionGroup(
        parser,
        title='Parameter Settings',
        description="Miscellaneous default values and settings")
    ConstGroup.add_option(
        "--phase",
        action="store",
        type=str,
        dest="phase",
        default='allP',
        help="Specify the phase name to use. Be careful with the distance. "+
        "setting. Options are 'P', 'PP', 'allP', 'S', 'SKS' or 'allS'. "+
        "[Default 'allP']")
    ConstGroup.add_option(
        "--align",
        action="store",
        type=str,
        dest="align",
        default=None,
        help="Specify component alignment key. Can be either " +
        "ZRT, LQT, or PVH. [Default ZRT]")
    ConstGroup.add_option(
        "--vp",
        action="store",
        type=float,
        dest="vp",
        default=6.0,
        help="Specify near-surface Vp to use with --align=PVH (km/s). "+
        "[Default 6.0]")
    ConstGroup.add_option(
        "--vs",
        action="store",
        type=float,
        dest="vs",
        default=3.5,
        help="Specify near-surface Vs to use with --align=PVH (km/s). "+
        "[Default 3.5]")
    ConstGroup.add_option(
        "--dt-snr",
        action="store",
        type=float,
        dest="dt_snr",
        default=30.,
        help="Specify the window length over which to calculate " +
        "the SNR in sec. [Default 30.]")
    ConstGroup.add_option(
        "--pre-filt",
        action="store",
        type=str,
        dest="pre_filt",
        default=None,
        help="Specify two floats with low and high frequency corners for "+
        "pre-filter (before deconvolution). [Default None]")
    ConstGroup.add_option(
        "--fmin",
        action="store",
        type=float,
        dest="fmin",
        default=0.05,
        help="Specify the minimum frequency corner for SNR " +
        "filter (Hz). [Default 0.05]")
    ConstGroup.add_option(
        "--fmax",
        action="store",
        type=float,
        dest="fmax",
        default=1.0,
        help="Specify the maximum frequency corner for SNR " +
        "filter (Hz). [Default 1.0]")

    # Constants Settings
    DeconGroup = OptionGroup(
        parser,
        title='Deconvolution Settings',
        description="Parameters for deconvolution")
    DeconGroup.add_option(
        "--method",
        action="store",
        dest="method",
        type=str,
        default="wiener",
        help="Specify the deconvolution method. Available methods " +
        "include 'wiener', 'water' and 'multitaper'. [Default 'wiener']")
    DeconGroup.add_option(
        "--gfilt",
        action="store",
        dest="gfilt",
        type=float,
        default=None,
        help="Specify the Gaussian filter width in Hz. " +
        "[Default None]")
    DeconGroup.add_option(
        "--wlevel",
        action="store",
        dest="wlevel",
        type=float,
        default=0.01,
        help="Specify the water level, used in the 'water' method. "+
        "[Default 0.01]")

    parser.add_option_group(ConstGroup)
    parser.add_option_group(DeconGroup)

    (opts, args) = parser.parse_args()

    # Check inputs
    if len(args) != 1:
        parser.error("Need station database file")
    indb = args[0]
    if not exist(indb):
        parser.error("Input file " + indb + " does not exist")

    # create station key list
    if len(opts.stkeys) > 0:
        opts.stkeys = opts.stkeys.split(',')

    if opts.phase not in ['P', 'PP', 'allP', 'S', 'SKS', 'allS']:
        parser.error(
            "Error: choose between 'P', 'PP', 'allP', 'S', 'SKS' and 'allS'.")
    if opts.phase == 'allP':
        opts.listphase = ['P', 'PP']
    elif opts.phase == 'allS':
        opts.listphase = ['S', 'SKS']
    else:
        opts.listphase = [opts.phase]    

    if opts.align is None:
        opts.align = 'ZRT'
    elif opts.align not in ['ZRT', 'LQT', 'PVH']:
        parser.error(
            "Error: Incorrect alignment specifier. Should be " +
            "either 'ZRT', 'LQT', or 'PVH'.")

    if opts.method not in ['wiener', 'water', 'multitaper']:
        parser.error(
            "Error: 'method' should be either 'wiener', 'water' or " +
            "'multitaper'")

    if opts.pre_filt is not None:
        opts.pre_filt = [float(val) for val in opts.pre_filt.split(',')]
        opts.pre_filt = sorted(opts.pre_filt)
        if (len(opts.pre_filt)) != 2:
            parser.error(
                "Error: --pre-filt should contain 2 " +
                "comma-separated floats")


    return (opts, indb)


def get_hk_options():
    """
    Get Options from :class:`~optparse.OptionParser` objects.

    This function is used for data processing on-the-fly (requires web connection)

    """

    from optparse import OptionParser, OptionGroup
    from os.path import exists as exist
    from obspy import UTCDateTime
    from numpy import nan

    parser = OptionParser(
        usage="Usage: %prog [options] <station database>",
        description="Script used to process receiver function data " +
        "for H-k stacking.")

    # General Settings
    parser.add_option(
        "--keys",
        action="store",
        type=str,
        dest="stkeys",
        default="",
        help="Specify a comma separated list of station keys for " +
        "which to perform the analysis. These must be " +
        "contained within the station database. Partial keys will " +
        "be used to match against those in the dictionary. For " +
        "instance, providing IU will match with all stations in " +
        "the IU network [Default processes all stations in the database]")
    parser.add_option(
        "-v", "-V", "--verbose",
        action="store_true",
        dest="verb",
        default=False,
        help="Specify to increase verbosity.")
    parser.add_option(
        "-O", "--overwrite",
        action="store_true",
        dest="ovr",
        default=False,
        help="Force the overwriting of pre-existing data. " +
        "[Default False]")

    # Event Selection Criteria
    TimeGroup = OptionGroup(
        parser,
        title="Time Settings",
        description="Settings associated with refining " +
        "the times to include in searching for receiver function data")
    TimeGroup.add_option(
        "--start",
        action="store",
        type=str,
        dest="startT",
        default="",
        help="Specify a UTCDateTime compatible string representing " +
        "the start time for the search. This will override any " +
        "station start times. [Default start date of station]")
    TimeGroup.add_option(
        "--end",
        action="store",
        type=str,
        dest="endT",
        default="",
        help="Specify a UTCDateTime compatible string representing " +
        "the end time for the search. This will override any " +
        "station end times [Default end date of station]")

    PreGroup = OptionGroup(
        parser,
        title='Pre-processing Settings',
        description="Options for pre-processing of receiver function " +
        "data prior to H-k stacking")
    PreGroup.add_option(
        "--bp",
        action="store",
        type=str,
        dest="bp",
        default=None,
        help="Specify the corner frequencies for the bandpass filter. " +
        "[Default 0.05,0.5]")
    PreGroup.add_option(
        "--nbaz",
        action="store",
        dest="nbaz",
        type=int,
        default=36,
        help="Specify integer number of back-azimuth bins to consider. " +
        "[Default 36]")
    PreGroup.add_option(
        "--nslow",
        action="store",
        dest="nslow",
        type=int,
        default=40,
        help="Specify integer number of slowness bins to consider. " +
        "[Default 40]")
    PreGroup.add_option(
        "--snr",
        action="store",
        type=float,
        dest="snr",
        default=-9999.,
        help="Specify the SNR threshold for extracting receiver functions. " +
        "[Default None]")
    PreGroup.add_option(
        "--snrh",
        action="store",
        type=float,
        dest="snrh",
        default=-9999,
        help="Specify the horizontal component SNR threshold for "+
        "extracting receiver functions. [Default None]")
    PreGroup.add_option(
        "--cc",
        action="store",
        type=float,
        dest="cc",
        default=-1.,
        help="Specify the CC threshold for extracting receiver functions. " +
        "[Default None]")
    PreGroup.add_option(
        "--no-outlier",
        action="store_true",
        dest="no_outl",
        default=False,
        help="Set this option to delete outliers based on the MAD "+
        "on the variance. [Default False]")
## JMG ##
    PreGroup.add_option(
         "--slowbound",
         action="store",
        dest="slowbound",
        type=str,
        default=None,
        help="Specify a list of two floats with minimum and maximum" +
        "bounds on slowness (s/km). [Default [0.04, 0.08]]")
    PreGroup.add_option(
        "--bazbound",
        action="store",
        dest="bazbound",
        type=str,
        default=None,
        help="Specify a list of two floats with minimum and maximum" +
        "bounds on back azimuth (degrees). [Default [0, 360]]")
## JMG ##
    PreGroup.add_option(
        "--copy",
        action="store_true",
        dest="copy",
        default=False,
        help="Set this option to use a copy of the radial component " +
        "filtered at different corners for the Pps and Pss phases. " +
        "[Default False]")
    PreGroup.add_option(
        "--bp-copy",
        action="store",
        dest="bp_copy",
        type=str,
        default=None,
        help="Specify a list of two floats with minimum and maximum" +
        "frequency for the copies stream (Hz). [Default [0.05, 0.35]]")

    HKGroup = OptionGroup(
        parser,
        title='Settings for H-k Stacking',
        description="Specify parameters of H-k search, including" +
        "bounds on search, weights, type of stacking, etc.")
    HKGroup.add_option(
        "--hbound",
        action="store",
        type=str,
        dest="hbound",
        default=None,
        help="Specify a list of two floats with minimum and maximum" +
        "bounds on Moho depth (H, in km). [Default [20., 50.]]")
    HKGroup.add_option(
        "--dh",
        action="store",
        type=float,
        dest="dh",
        default=0.5,
        help="Specify search interval for H (km). [Default 0.5]")
    HKGroup.add_option(
        "--kbound",
        action="store",
        type=str,
        dest="kbound",
        default=None,
        help="Specify a list of two floats with minimum and maximum" +
        "bounds on Vp/Vs (k). [Default [1.56, 2.1]]")
    HKGroup.add_option(
        "--dk",
        action="store",
        type=float,
        dest="dk",
        default=0.02,
        help="Specify search interval for k. [Default 0.02]")
    HKGroup.add_option(
        "--weights",
        action="store",
        type=str,
        dest="weights",
        default=None,
        help="Specify a list of three floats with for Ps, Pps and Pass " +
        "weights in final stack. [Default [0.5, 2., -1.]]")
    HKGroup.add_option(
        "--type",
        action="store",
        type=str,
        dest="typ",
        default="sum",
        help="Specify type of final stacking. Options are: 'sum' for " +
        "a weighted average (using weights), or 'prod' for the product " +
        "of positive values in stacks. [Default 'sum']")
    HKGroup.add_option(
        "--save",
        action="store_true",
        dest="save",
        default=False,
        help="Set this option to save the HkStack object to file. "+
        "[Default doesn't save]")

    # Constants Settings
    ModelGroup = OptionGroup(
        parser,
        title='Model Settings',
        description="Miscellaneous default values and settings")
    ModelGroup.add_option(
        "--vp",
        action="store",
        type=float,
        dest="vp",
        default=6.0,
        help="Specify mean crustal Vp (km/s). [Default 6.0]")
    ModelGroup.add_option(
        "--strike",
        action="store",
        type=float,
        dest="strike",
        default=None,
        help="Specify the strike of dipping Moho. [Default None]")
    ModelGroup.add_option(
        "--dip",
        action="store",
        type=float,
        dest="dip",
        default=None,
        help="Specify the dip of dipping Moho. [Default None]")

    PlotGroup = OptionGroup(
        parser,
        title='Settings for plotting results',
        description="Specify parameters for plotting the H-k stacks.")
    PlotGroup.add_option(
        "--plot",
        action="store_true",
        dest="plot",
        default=False,
        help="Set this option to produce a plot of the stacks [Default " +
        "does not produce plot]")
    PlotGroup.add_option(
        "--save-plot",
        action="store_true",
        dest="save_plot",
        default=False,
        help="Set this option to save the plot [Default doesn't save]")
    PlotGroup.add_option(
        "--title",
        action="store",
        type=str,
        dest="title",
        default="",
        help="Specify plot title [Default has no title]")
    PlotGroup.add_option(
        "--format",
        action="store",
        type=str,
        dest="form",
        default="png",
        help="Specify format of figure. Can be any one of the valid" +
        "matplotlib formats: 'png', 'jpg', 'eps', 'pdf'. [Default 'png']")

    parser.add_option_group(TimeGroup)
    parser.add_option_group(PreGroup)
    parser.add_option_group(HKGroup)
    parser.add_option_group(ModelGroup)
    parser.add_option_group(PlotGroup)

    (opts, args) = parser.parse_args()

    # Check inputs
    if len(args) != 1:
        parser.error("Need station database file")
    indb = args[0]
    if not exist(indb):
        parser.error("Input file " + indb + " does not exist")

    # create station key list
    if len(opts.stkeys) > 0:
        opts.stkeys = opts.stkeys.split(',')

    # construct start time
    if len(opts.startT) > 0:
        try:
            opts.startT = UTCDateTime(opts.startT)
        except:
            parser.error(
                "Cannot construct UTCDateTime from start time: " +
                opts.startT)
    else:
        opts.startT = None

    # construct end time
    if len(opts.endT) > 0:
        try:
            opts.endT = UTCDateTime(opts.endT)
        except:
            parser.error(
                "Cannot construct UTCDateTime from end time: " +
                opts.endT)
    else:
        opts.endT = None

    if opts.strike is None and opts.dip is None:
        opts.calc_dip = False
        opts.nbaz = None
    elif opts.strike is None or opts.dip is None:
        parser.error("Specify both strike and dip for this type " +
                     "of analysis")
    else:
        opts.calc_dip = True

    if opts.bp is None:
        opts.bp = [0.05, 0.5]
    else:
        opts.bp = [float(val) for val in opts.bp.split(',')]
        opts.bp = sorted(opts.bp)
        if (len(opts.bp)) != 2:
            parser.error(
                "Error: --bp should contain 2 " +
                "comma-separated floats")

## JMG ##
    if opts.slowbound is None:
        opts.slowbound = [0.04, 0.08]
    else:
        opts.slowbound = [float(val) for val in opts.slowbound.split(',')]
        opts.slowbound = sorted(opts.slowbound)
        if (len(opts.slowbound)) != 2:
            parser.error(
                "Error: --slowbound should contain 2 " +
                "comma-separated floats")
    
    if opts.bazbound is None:
        opts.bazbound = [0.0, 360.0]
    else:
        opts.bazbound = [float(val) for val in opts.bazbound.split(',')]
        opts.bazbound = sorted(opts.bazbound)
        if (len(opts.bazbound)) != 2:
            parser.error(
                "Error: --bazbound should contain 2 " +
                "comma-separated floats")
## JMG ##

    if opts.copy:
        if opts.bp_copy is None:
            opts.bp_copy = [0.05, 0.35]
        else:
            opts.bp_copy = [float(val)
                               for val in opts.bp_copy.split(',')]
            opts.bp_copy = sorted(opts.bp_copy)
            if (len(opts.bp_copy)) != 2:
                parser.error(
                    "Error: --bp_copy should contain 2 " +
                    "comma-separated floats")

    if opts.hbound is None:
        opts.hbound = [20., 50.]
    else:
        opts.hbound = [float(val) for val in opts.hbound.split(',')]
        opts.hbound = sorted(opts.hbound)
        if (len(opts.hbound)) != 2:
            parser.error(
                "Error: --hbound should contain 2 " +
                "comma-separated floats")

    if opts.kbound is None:
        opts.kbound = [1.56, 2.1]
    else:
        opts.kbound = [float(val) for val in opts.kbound.split(',')]
        opts.kbound = sorted(opts.kbound)
        if (len(opts.kbound)) != 2:
            parser.error(
                "Error: --kbound should contain 2 " +
                "comma-separated floats")

    if opts.weights is None:
        opts.weights = [0.5, 2.0, -1.0]
    else:
        opts.weights = [float(val) for val in opts.weights.split(',')]
        opts.weights = sorted(opts.weights)
        if (len(opts.weights)) != 3:
            parser.error(
                "Error: --weights should contain 3 " +
                "comma-separated floats")

    return (opts, indb)


def get_harmonics_options():
    """
    Get Options from :class:`~optparse.OptionParser` objects.

    This function is used for data processing on-the-fly (requires web connection)

    """

    from optparse import OptionParser, OptionGroup
    from os.path import exists as exist
    from obspy import UTCDateTime
    from numpy import nan

    parser = OptionParser(
        usage="Usage: %prog [options] <station database>",
        description="Script used to process receiver function data " +
        "for harmonic decomposition.")

    # General Settings
    parser.add_option(
        "--keys",
        action="store",
        type=str,
        dest="stkeys",
        default="",
        help="Specify a comma separated list of station keys for " +
        "which to perform the analysis. These must be " +
        "contained within the station database. Partial keys will " +
        "be used to match against those in the dictionary. For " +
        "instance, providing IU will match with all stations in " +
        "the IU network [Default processes all stations in the database]")
    parser.add_option(
        "-v", "-V", "--verbose",
        action="store_true",
        dest="verb",
        default=False,
        help="Specify to increase verbosity.")
    parser.add_option(
        "-O", "--overwrite",
        action="store_true",
        dest="ovr",
        default=False,
        help="Force the overwriting of pre-existing data. " +
        "[Default False]")

    # Event Selection Criteria
    TimeGroup = OptionGroup(
        parser,
        title="Time Settings",
        description="Settings associated with refining " +
        "the times to include in searching for receiver function data")
    TimeGroup.add_option(
        "--start",
        action="store",
        type=str,
        dest="startT",
        default="",
        help="Specify a UTCDateTime compatible string representing " +
        "the start time for the search. This will override any " +
        "station start times. [Default start date of station]")
    TimeGroup.add_option(
        "--end",
        action="store",
        type=str,
        dest="endT",
        default="",
        help="Specify a UTCDateTime compatible string representing " +
        "the end time for the search. This will override any " +
        "station end times [Default end date of station]")

    PreGroup = OptionGroup(
        parser,
        title='Pre-processing Settings',
        description="Options for pre-processing of receiver function " +
        "data prior to harmonic decomposition")
    PreGroup.add_option(
        "--bp",
        action="store",
        type=str,
        dest="bp",
        default=None,
        help="Specify the corner frequencies for the bandpass filter. " +
        "[Default 0.05,0.5]")
    PreGroup.add_option(
        "--bin",
        action="store",
        dest="nbin",
        type=int,
        default=None,
        help="Specify integer number of back-azimuth bins to consider " +
        "(typically 36 or 72). [Default does not bin data]")
    PreGroup.add_option(
        "--snr",
        action="store",
        type=float,
        dest="snr",
        default=-9999.,
        help="Specify the SNR threshold for extracting receiver functions. " +
        "[Default None]")
    PreGroup.add_option(
        "--snrh",
        action="store",
        type=float,
        dest="snrh",
        default=-9999,
        help="Specify the horizontal component SNR threshold for "+
        "extracting receiver functions. [Default None]")
    PreGroup.add_option(
        "--cc",
        action="store",
        type=float,
        dest="cc",
        default=-1.,
        help="Specify the CC threshold for extracting receiver functions. " +
        "[Default None]")
    PreGroup.add_option(
        "--no-outlier",
        action="store_true",
        dest="no_outl",
        default=False,
        help="Set this option to delete outliers based on the MAD "+
        "on the variance. [Default False]")

    HarmonicGroup = OptionGroup(
        parser,
        title='Settings for harmonic decomposition',
        description="Specify parameters for the decomposition, e.g. " +
        "a fixed azimuth, depth range for finding the optimal azimuth, etc.")
    HarmonicGroup.add_option(
        "--azim",
        action="store",
        type=float,
        dest="azim",
        default=None,
        help="Specify the azimuth angle along with to perform the " +
        "decomposition. [Default 0.]")
    HarmonicGroup.add_option(
        "--find-azim",
        action="store_true",
        dest="find_azim",
        default=False,
        help="Set this option to calculate the optimal azimuth. [Default " +
        "uses the '--azim' value]")
    HarmonicGroup.add_option(
        "--trange",
        action="store",
        type=str,
        dest="trange",
        default=None,
        help="Specify a list of two floats with minimum and maximum" +
        "bounds on time range for finding the optimal azimuth (sec). " +
        "[Default [0., 10.] when '--find-azim' is set]")
    HarmonicGroup.add_option(
        "--save",
        action="store_true",
        dest="save",
        default=False,
        help="Set this option to save the Harmonics object " +
        "to a pickled file. [Default does not save object]")

    PlotGroup = OptionGroup(
        parser,
        title='Settings for plotting results',
        description="Specify parameters for plotting the back-azimuth " +
        "harmonics.")
    PlotGroup.add_option(
        "--plot",
        action="store_true",
        dest="plot",
        default=False,
        help="Set this option to produce a plot of the back-azimuth harmonics")
    PlotGroup.add_option(
        "--ymax",
        action="store",
        type=float,
        dest="ymax",
        default=30.,
        help="Specify the maximum y axis value for the plot in units of the" +
        "dependent variable (e.g., sec). [Default 30.]")
    PlotGroup.add_option(
        "--scale",
        action="store",
        type=float,
        dest="scale",
        default=30.,
        help="Specify the scaling value that multiplies the amplitude " +
        "of the harmonic components. [Default 10.]")
    PlotGroup.add_option(
        "--save-plot",
        action="store_true",
        dest="save_plot",
        default=False,
        help="Set this option to save the plot [Default doesn't save]")
    PlotGroup.add_option(
        "--title",
        action="store",
        type=str,
        dest="title",
        default="",
        help="Specify plot title [Default has no title]")
    PlotGroup.add_option(
        "--format",
        action="store",
        type=str,
        dest="form",
        default="png",
        help="Specify format of figure. Can be any one of the valid" +
        "matplotlib formats: 'png', 'jpg', 'eps', 'pdf'. [Default 'png']")

    parser.add_option_group(TimeGroup)
    parser.add_option_group(PreGroup)
    parser.add_option_group(HarmonicGroup)
    parser.add_option_group(PlotGroup)

    (opts, args) = parser.parse_args()

    # Check inputs
    if len(args) != 1:
        parser.error("Need station database file")
    indb = args[0]
    if not exist(indb):
        parser.error("Input file " + indb + " does not exist")

    # create station key list
    if len(opts.stkeys) > 0:
        opts.stkeys = opts.stkeys.split(',')

    # construct start time
    if len(opts.startT) > 0:
        try:
            opts.startT = UTCDateTime(opts.startT)
        except:
            parser.error(
                "Cannot construct UTCDateTime from start time: " +
                opts.startT)
    else:
        opts.startT = None

    # construct end time
    if len(opts.endT) > 0:
        try:
            opts.endT = UTCDateTime(opts.endT)
        except:
            parser.error(
                "Cannot construct UTCDateTime from end time: " +
                opts.endT)
    else:
        opts.endT = None

    if opts.bp is None:
        opts.bp = [0.05, 0.5]
    else:
        opts.bp = [float(val) for val in opts.bp.split(',')]
        opts.bp = sorted(opts.bp)
        if (len(opts.bp)) != 2:
            parser.error(
                "Error: --bp should contain 2 " +
                "comma-separated floats")

    if opts.azim is not None and opts.find_azim:
        print("Warning: Setting both '--azim' and '--find-azim' is " +
              "conflictual. Ignoring '--find-azim'")
        opts.find_azim = False
    elif opts.azim is None and not opts.find_azim:
        opts.azim = 0.
    if opts.find_azim:
        if opts.trange is None:
            opts.trange = [0., 10.]
        else:
            print(opts.trange.split(','))
            opts.trange = [float(val) for val in opts.trange.split(',')]
            opts.trange = sorted(opts.trange)
            if (len(opts.trange)) != 2:
                parser.error(
                    "Error: --trange should contain 2 " +
                    "comma-separated floats")

    return (opts, indb)


def get_ccp_options():
    """
    Get Options from :class:`~optparse.OptionParser` objects.

    This function is used for data processing on-the-fly (requires web connection)

    """

    from optparse import OptionParser, OptionGroup
    from os.path import exists as exist
    from obspy import UTCDateTime
    from numpy import nan

    parser = OptionParser(
        usage="Usage: %prog [options] <station database>",
        description="Script used to process receiver function data " +
        "for common-conversion-point (CCP) imaging.")

    # General Settings
    parser.add_option(
        "--keys",
        action="store",
        type=str,
        dest="stkeys",
        default="",
        help="Specify a comma separated list of station keys for " +
        "which to perform the analysis. These must be " +
        "contained within the station database. Partial keys will " +
        "be used to match against those in the dictionary. For " +
        "instance, providing IU will match with all stations in " +
        "the IU network [Default processes all stations in the database]")
    parser.add_option(
        "-v", "-V", "--verbose",
        action="store_true",
        dest="verb",
        default=False,
        help="Specify to increase verbosity.")
    parser.add_option(
        "-O", "--overwrite",
        action="store_true",
        dest="ovr",
        default=False,
        help="Force the overwriting of pre-existing data. " +
        "[Default False]")

    LineGroup = OptionGroup(
        parser,
        title='Line Geometry Settings',
        description="Options for defining the line along which to " +
        "produce the CCP image")
    LineGroup.add_option(
        "--start",
        action="store",
        type=str,
        dest="coord_start",
        default=None,
        help="Specify a list of two floats with the latitude and longitude " +
        "of the start point, in this respective order. [Exception raised " +
        "if not specified]")
    LineGroup.add_option(
        "--end",
        action="store",
        dest="coord_end",
        type=str,
        default=None,
        help="Specify a list of two floats with the latitude and longitude" +
        "of the end point, in this respective order. [Exception raised " +
        "if not specified]")
    LineGroup.add_option(
        "--dz",
        action="store",
        dest="dz",
        type=int,
        default=1.,
        help="Specify vertical cell size in km. " +
        "[Default 1.]")
    LineGroup.add_option(
        "--dx",
        action="store",
        dest="dx",
        type=float,
        default=2.5,
        help="Specify horizontal cell size in km. " +
        "[Default 2.5]")

    PreGroup = OptionGroup(
        parser,
        title='Pre-processing Settings',
        description="Options for pre-processing of receiver function " +
        "data for CCP stacking")
    PreGroup.add_option(
        "--snr",
        action="store",
        type=float,
        dest="snr",
        default=-9999.,
        help="Specify the SNR threshold for extracting receiver functions. " +
        "[Default None]")
    PreGroup.add_option(
        "--snrh",
        action="store",
        type=float,
        dest="snrh",
        default=-9999,
        help="Specify the horizontal component SNR threshold for "+
        "extracting receiver functions. [Default None]")
    PreGroup.add_option(
        "--cc",
        action="store",
        type=float,
        dest="cc",
        default=-1.,
        help="Specify the CC threshold for extracting receiver functions. " +
        "[Default None]")
    PreGroup.add_option(
        "--no-outlier",
        action="store_true",
        dest="no_outl",
        default=False,
        help="Set this option to delete outliers based on the MAD "+
        "on the variance. [Default False]")
    PreGroup.add_option(
        "--f1",
        action="store",
        type=float,
        dest="f1",
        default=0.05,
        help="Specify the low frequency corner for the bandpass filter " +
        "for all phases (Hz). [Default [0.05]]")
    PreGroup.add_option(
        "--f2ps",
        action="store",
        type=float,
        dest="f2ps",
        default=0.75,
        help="Specify the high frequency corner for the bandpass filter " +
        "for the Ps phase (Hz). [Default [0.75]]")
    PreGroup.add_option(
        "--f2pps",
        action="store",
        type=float,
        dest="f2pps",
        default=0.36,
        help="Specify the high frequency corner for the bandpass filter " +
        "for the Pps phase (Hz). [Default [0.36]]")
    PreGroup.add_option(
        "--f2pss",
        action="store",
        type=float,
        dest="f2pss",
        default=0.3,
        help="Specify the high frequency corner for the bandpass filter " +
        "for the Pss phase (Hz). [Default [0.3]]")
    PreGroup.add_option(
        "--nbaz",
        action="store",
        dest="nbaz",
        type=int,
        default=36,
        help="Specify integer number of back-azimuth bins to consider. " +
        "[Default 36]")
    PreGroup.add_option(
        "--nslow",
        action="store",
        dest="nslow",
        type=int,
        default=40,
        help="Specify integer number of slowness bins to consider. " +
        "[Default 40]")
    PreGroup.add_option(
        "--wlen",
        action="store",
        dest="wlen",
        type=float,
        default=35.,
        help="Specify wavelength of P-wave as sensitivity (km). " +
        "[Default 35.]")

    CCPGroup = OptionGroup(
        parser,
        title='CCP Settings',
        description="Options for specifying the type of CCP stacking " +
        "to perform")
    CCPGroup.add_option(
        "--load",
        action="store_true",
        dest="load",
        default=False,
        help="Step 1. Set this option to load rfstreams into CCPimage "+
        "object. [Default False]")
    CCPGroup.add_option(
        "--prep",
        action="store_true",
        dest="prep",
        default=False,
        help="Step 2. Set this option to prepare CCPimage before "+
        "pre-stacking. [Default False]")
    CCPGroup.add_option(
        "--prestack",
        action="store_true",
        dest="prestack",
        default=False,
        help="Step 3. Set this option to prestack all phases before "+
        "CCP averaging. [Default False]")
    CCPGroup.add_option(
        "--ccp",
        action="store_true",
        dest="ccp",
        default=False,
        help="Step 4a. Set this option for standard CCP stacking with "+
        "multiples. [Default False]")
    CCPGroup.add_option(
        "--gccp",
        action="store_true",
        dest="gccp",
        default=False,
        help="Step 4b. Set this option for Gaussian-weighted "+
        "CCP stacking with multiples. [Default False]")
    CCPGroup.add_option(
        "--linear",
        action="store_true",
        dest="linear",
        default=False,
        help="Step 5a. Set this option to produce a linear, weighted "+
        "stack for the final [G]CCP image. [Default True unless "+
        "--phase is set]")
    CCPGroup.add_option(
        "--phase",
        action="store_true",
        dest="phase",
        default=False,
        help="Step 5b. Set this option to produce a phase weighted stack "+
        "for the final [G]CCP image. [Default False]")

    FigGroup = OptionGroup(
        parser,
        title='Figure Settings',
        description="Options for specifying the settings for the final figure")
    FigGroup.add_option(
        "--figure",
        action="store_true",
        dest="ccp_figure",
        default=False,
        help="Set this option to plot the final [G]CCP figure. " +
        "[Default False]")
    FigGroup.add_option(
        "--cbound",
        action="store",
        dest="cbound",
        type=float,
        default=None,
        help="Set the maximum value for the color palette. "+
        "[Default 0.05 for --ccp or 0.015 for --gccp]")
    FigGroup.add_option(
        "--save-fig",
        action="store_true",
        dest="save_figure",
        default=False,
        help="Set this option to save the final [G]CCP figure. "+
        "This option can only be set if --figure is also set." +
        "[Default False]")
    FigGroup.add_option(
        "--title",
        action="store",
        dest="title",
        type=str,
        default="",
        help="Set Figure title. [Default None]")
    FigGroup.add_option(
        "--format",
        action="store",
        dest="fmt",
        type=str,
        default='png',
        help="Set format of figure. You can choose among "+
        "'png', 'jpg', 'eps', 'pdf'. [Default 'png']")

    parser.add_option_group(LineGroup)
    parser.add_option_group(PreGroup)
    parser.add_option_group(CCPGroup)
    parser.add_option_group(FigGroup)

    (opts, args) = parser.parse_args()

    # Check inputs
    if len(args) != 1:
        parser.error("Need station database file")
    indb = args[0]
    if not exist(indb):
        parser.error("Input file " + indb + " does not exist")

    # create station key list
    if len(opts.stkeys) > 0:
        opts.stkeys = opts.stkeys.split(',')

    if opts.load and opts.coord_start is None:
        parser.error("--start=lon,lat is required")
    elif opts.load and opts.coord_start is not None:
        opts.coord_start = [float(val) for val in opts.coord_start.split(',')]
        if (len(opts.coord_start)) != 2:
            parser.error(
                "Error: --start should contain 2 " +
                "comma-separated floats")

    if opts.load and opts.coord_end is None:
        parser.error("--end=lon,lat is required")
    elif opts.load and opts.coord_end is not None:
        opts.coord_end = [float(val) for val in opts.coord_end.split(',')]
        if (len(opts.coord_end)) != 2:
            parser.error(
                "Error: --end should contain 2 " +
                "comma-separated floats")

    if not (opts.load or opts.prep or opts.prestack or opts.ccp
            or opts.gccp):
        parser.error(
            "Error: needs at least one CCP Setting (--load, --prep, " +
            "--prestack, --ccp or --gccp")

    if opts.linear and opts.phase:
        parser.error(
            "Error: cannot use --linear and --phase at the same time")

    if opts.ccp and not opts.linear and not opts.phase:
        opts.linear = True
    if opts.gccp and not opts.linear and not opts.phase:
        opts.phase = True

    if opts.ccp or opts.gccp:
        if (opts.save_figure or opts.cbound or opts.fmt) and not opts.ccp_figure:
            print("Warning: Figure will not be produced since --figure "+
                "has not been set.")

    if opts.ccp_figure and not (opts.ccp or opts.gccp):
        parser.error(
            "Error: Cannot produce Figure without specifying the "+
            "type of stacking [--ccp or --gccp].")

    if not opts.cbound and opts.gccp:
        opts.cbound = 0.015
    elif not opts.cbound and opts.ccp:
        opts.cbound = 0.05

    return (opts, indb)


def get_plot_options():
    """
    Get Options from :class:`~optparse.OptionParser` objects.

    This function is used for data processing on-the-fly (requires web connection)

    """

    from optparse import OptionParser, OptionGroup
    from os.path import exists as exist
    from obspy import UTCDateTime
    from numpy import nan

    parser = OptionParser(
        usage="Usage: %prog [options] <station database>",
        description="Script used to plot receiver function data ")

    # General Settings
    parser.add_option(
        "--keys",
        action="store",
        type=str,
        dest="stkeys",
        default="",
        help="Specify a comma separated list of station keys for " +
        "which to perform the analysis. These must be " +
        "contained within the station database. Partial keys will " +
        "be used to match against those in the dictionary. For " +
        "instance, providing IU will match with all stations in " +
        "the IU network [Default processes all stations in the database]")
    parser.add_option(
        "-v", "-V", "--verbose",
        action="store_true",
        dest="verb",
        default=False,
        help="Specify to increase verbosity.")
    parser.add_option(
        "-O", "--overwrite",
        action="store_true",
        dest="ovr",
        default=False,
        help="Force the overwriting of pre-existing figures. " +
        "[Default False]")

    PreGroup = OptionGroup(
        parser,
        title='Pre-processing Settings',
        description="Options for pre-processing of receiver function " +
        "data before plotting")
    PreGroup.add_option(
        "--snr",
        action="store",
        type=float,
        dest="snr",
        default=-9999.,
        help="Specify the vertical component SNR threshold for extracting receiver functions. " +
        "[Default 5.]")
    PreGroup.add_option(
        "--snrh",
        action="store",
        type=float,
        dest="snrh",
        default=-9999.,
        help="Specify the horizontal component SNR threshold for extracting receiver functions. " +
        "[Default None]")
    PreGroup.add_option(
        "--cc",
        action="store",
        type=float,
        dest="cc",
        default=-1.,
        help="Specify the CC threshold for extracting receiver functions. " +
        "[Default None]")
    PreGroup.add_option(
        "--no-outlier",
        action="store_true",
        dest="no_outl",
        default=False,
        help="Set this option to delete outliers based on the MAD "+
        "on the variance. [Default False]")
    PreGroup.add_option(
         "--binlim",
         action="store",
         type=float,
         dest="binlim",
         default=0,
         help="Specify the minimum threshold for the number RFs needed before bin is "+
         "plotted. [Default 0]")
    PreGroup.add_option(
        "--bp",
        action="store",
        type=str,
        dest="bp",
        default=None,
        help="Specify the corner frequencies for the bandpass filter. " +
        "[Default no filtering]")
    PreGroup.add_option(
        "--pws",
        action="store_true",
        dest="pws",
        default=False,
        help="Set this option to use phase-weighted stacking during binning "+
        " [Default False]")
    PreGroup.add_option(
        "--nbaz",
        action="store",
        dest="nbaz",
        type=int,
        default=None,
        help="Specify integer number of back-azimuth bins to consider " +
        "(typically 36 or 72). If not None, the plot will show receiver " +
        "functions sorted by back-azimuth values. [Default None]")
    PreGroup.add_option(
        "--nslow",
        action="store",
        dest="nslow",
        type=int,
        default=None,
        help="Specify integer number of slowness bins to consider " +
        "(typically 20 or 40). If not None, the plot will show receiver " +
        "functions sorted by slowness values. [Default None]")
## JMG ##
    PreGroup.add_option(
        "--slowbound",
        action="store",
        dest="slowbound",
        type=str,
        default=None,
        help="Specify a list of two floats with minimum and maximum" +
        "bounds on slowness (s/km). [Default [0.04, 0.08]]")
    PreGroup.add_option(
        "--bazbound",
        action="store",
        dest="bazbound",
        type=str,
        default=None,
        help="Specify a list of two floats with minimum and maximum" +
        "bounds on back azimuth (degrees). [Default [0, 360]]")
    PreGroup.add_option(
        "--phase",
        action="store",
        type=str,
        dest="phase",
        default=None,
        help="Specify the phase name to plot.  "+
        "Options are 'P', 'PP', 'allP', 'S', 'SKS' or 'allS'. "+
        "[Default 'allP']")
## JMG ##

    PlotGroup = OptionGroup(
        parser,
        title='Plot Settings',
        description="Options for plot format")
    PlotGroup.add_option(
        "--scale",
        action="store",
        dest="scale",
        default=None,
        type=float,
        help="Specify the scaling factor for the amplitude of the "+
        "receiver functions in the wiggle plots. [Default 100. for "+
        "a back-azimuth plot, 0.02 for a slowness plot]")
    PlotGroup.add_option(
        "--normalize",
        action="store_true",
        dest="norm",
        default=False,
        help="Set this option to produce receiver functions normalized "+
        "by the max amplitude of stacked RFs. [Default False]")
    PlotGroup.add_option(
        "--trange",
        action="store",
        default=None,
        type=str,
        dest="trange",
        help="Specify the time range for the x-axis (sec). Negative times "+
        "are allowed [Default 0., 30.]")
    PlotGroup.add_option(
        "--stacked",
        action="store_true",
        dest="stacked",
        default=False,
        help="Set this option to plot a stack of all traces in top panel. "+
        "[Default does not plot stacked traces]")
    PlotGroup.add_option(
        "--save",
        action="store_true",
        dest="saveplot",
        default=False,
        help="Set this option if you wish to save the figure. [Default " +
        "does not save figure]")
    PlotGroup.add_option(
        "--title",
        action="store",
        dest="titleplot",
        type=str,
        default='',
        help="Specify title of figure. [Default None]")
    PlotGroup.add_option(
        "--format",
        action="store",
        type=str,
        dest="form",
        default="png",
        help="Specify format of figure. Can be any one of the valid" +
        "matplotlib formats: 'png', 'jpg', 'eps', 'pdf'. [Default 'png']")

    parser.add_option_group(PreGroup)
    parser.add_option_group(PlotGroup)

    (opts, args) = parser.parse_args()

    # Check inputs
    if len(args) != 1:
        parser.error("Need station database file")
    indb = args[0]
    if not exist(indb):
        parser.error("Input file " + indb + " does not exist")

## JMG ##
    if opts.slowbound is None:
        opts.slowbound = [0.04, 0.08]
    else:
        opts.slowbound = [float(val) for val in opts.slowbound.split(',')]
        opts.slowbound = sorted(opts.slowbound)
        if (len(opts.slowbound)) != 2:
            parser.error(
                "Error: --slowbound should contain 2 " +
                "comma-separated floats")
    
    if opts.bazbound is None:
        opts.bazbound = [0.0, 360.0]
    else:
        opts.bazbound = [float(val) for val in opts.bazbound.split(',')]
        opts.bazbound = sorted(opts.bazbound)
        if (len(opts.bazbound)) != 2:
            parser.error(
                "Error: --bazbound should contain 2 " +
                "comma-separated floats")
## JMG ##

    if opts.phase not in ['P', 'PP', 'allP', 'S', 'SKS', 'allS']:
        parser.error(
            "Error: choose between 'P', 'PP', 'allP', 'S', 'SKS' and 'allS'.")
    if opts.phase == 'allP':
        opts.listphase = ['P', 'PP']
    elif opts.phase == 'allS':
        opts.listphase = ['S', 'SKS']
    else:
        opts.listphase = [opts.phase]    


    if opts.bp is not None:
        opts.bp = [float(val) for val in opts.bp.split(',')]
        opts.bp = sorted(opts.bp)
        if (len(opts.bp)) != 2:
            parser.error(
                "Error: --bp should contain 2 " +
                "comma-separated floats")

    if opts.trange is None:
        opts.tmin = 0.
        opts.tmax = 30.
    if opts.trange is not None:
        opts.trange = [float(val) for val in opts.trange.split(',')]
        opts.trange = sorted(opts.trange)
        if (len(opts.trange)) != 2:
            parser.error(
                "Error: --trange should contain 2 " +
                "comma-separated floats")

    # create station key list
    if len(opts.stkeys) > 0:
        opts.stkeys = opts.stkeys.split(',')

    if opts.nbaz is None and opts.nslow is None:
        parser.error("Specify at least one of --nbaz or --nslow")
    elif opts.nbaz is not None and opts.nslow is not None:
        parser.error("Specify only one of --nbaz or --nslow")

    return (opts, indb)


