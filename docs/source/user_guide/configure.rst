=============
Configure Run
=============

The GW configs contain switches that change how the system runs. Many defaults are set initially. Users wishing to run with different settings should adjust their $EXPDIR configs and then rerun the ``setup_workflow.py`` script since some configuration settings/switches change the workflow/xml ("Adjusts XML" column value is "YES").

+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| Switch           | What                             | Default       | Adjusts XML | More Details                                      |
+==================+==================================+===============+=============+===================================================+
| APP              | Model application                | ATM           | YES         | See case block in config.base for options         |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DEBUG_POSTSCRIPT | Debug option for PBS scheduler   | NO            | YES         | Sets debug=true for additional logging            |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DOIAU            | Enable 4DIAU for control         | YES           | NO          | Turned off for cold-start first half cycle        |
|                  | with 3 increments                |               |             |                                                   |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DOHYBVAR         | Run EnKF                         | YES           | YES         | Don't recommend turning off                       |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DONST            | Run NSST                         | YES           | NO          | If YES, turns on NSST in anal/fcst steps, and     |
|                  |                                  |               |             | turn off rtgsst                                   |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_AWIPS         | Run jobs to produce AWIPS        | NO            | YES         | downstream processing, ops only                   |
|                  | products                         |               |             |                                                   |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_BUFRSND       | Run job to produce BUFR          | NO            | YES         | downstream processing                             |
|                  | sounding products                |               |             |                                                   |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_GEMPAK        | Run job to produce GEMPAK        | NO            | YES         | downstream processing, ops only                   |
|                  | products                         |               |             |                                                   |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_FIT2OBS       | Run FIT2OBS job                  | YES           | YES         | Whether to run the FIT2OBS job                    |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_TRACKER       | Run tracker job                  | YES           | YES         | Whether to run the tracker job                    |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_GENESIS       | Run genesis job                  | YES           | YES         | Whether to run the genesis job                    |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_GENESIS_FSU   | Run FSU genesis job              | YES           | YES         | Whether to run the FSU genesis job                |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_VERFOZN       | Run GSI monitor ozone job        | YES           | YES         | Whether to run the GSI monitor ozone job          |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_VERFRAD       | Run GSI monitor radiance job     | YES           | YES         | Whether to run the GSI monitor radiance job       |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_VMINMON       | Run GSI monitor minimization job | YES           | YES         | Whether to run the GSI monitor minimization job   |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_ANLSTAT       | Run analysis statistics job      | NO            | YES         | Whether to run the analysis statistics job.       |
|                  |                                  |               |             | Automatically set to YES for JEDI-based           |
|                  |                                  |               |             | experiments (DO_JEDIATMVAR, DO_AERO,              |
|                  |                                  |               |             | DO_JEDIOCNVAR, or DO_JEDISNOWDA).                 |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_GSI_ANLSTAT   | Run GSI analysis statistics job  | NO            | NO          | Whether to include GSI-based atmospheric analysis |
|                  |                                  |               |             | statistics when running the anlstat job. Only     |
|                  |                                  |               |             | relevant when DO_ANLSTAT=YES and using GSI (not   |
|                  |                                  |               |             | JEDI) for atmospheric data assimilation.          |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_METP          | Run METplus jobs                 | YES           | YES         | One cycle spinup                                  |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| EXP_WARM_START   | Is experiment starting warm      | .false.       | NO          | Impacts IAU settings for initial cycle. Can also  |
|                  | (.true.) or cold (.false)?       |               |             | be set when running ``setup_expt.py`` script with |
|                  |                                  |               |             | the ``--start`` flag (e.g. ``--start warm``)      |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| DO_ARCHCOM       | Archive COM                      | YES/NO        | YES         | Whether to archive the COM structure.  Defaults   |
|                  |                                  |               |             | are machine-specific.                             |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| ARCHCOM_TO       | Where to archive COM             | hpss, local,  | YES         | If DO_ARCHCOM is YES, then this variable indicates|
|                  |                                  | or globus_hpss|             | where the COM structure tarballs should be saved. |
|                  |                                  |               |             | Choices are 'hpss', 'local', or 'globus_hpss'.    |
|                  |                                  |               |             | HPSS archiving requires a direct connection.      |
|                  |                                  |               |             | Globus-HPSS archiving uses Mercury as a server to |
|                  |                                  |               |             | archiving to HPSS.  This is currently only        |
|                  |                                  |               |             | supported on Hercules.  Defaults are machine      |
|                  |                                  |               |             | specific.                                         |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| ARCH_EXPDIR      | Archive the EXPDIR               | NO            | NO          | Whether to create a tarball of the EXPDIR.        |
|                  |                                  |               |             | ARCH_HASHES and ARCH_DIFFS generate text files    |
|                  |                                  |               |             | of git output that are archived with the EXPDIR.  |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| QUILTING         | Use I/O quilting                 | .true.        | NO          | If .true. choose OUTPUT_GRID as cubed_sphere_grid |
|                  |                                  |               |             | in netcdf or gaussian_grid                        |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| CAT_MPMD_LOGS    | Write MPMD logs back to the      | YES           | NO          | If YES, the contents of the MPMD logs will be     |
|                  | parent log.                      |               |             | written to the parent log file.                   |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| WRITE_DOPOST     | Run inline post                  | .true.        | NO          | If .true. produces master post output in forecast |
|                  |                                  |               |             | job                                               |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+
| USE_BUILD_GSINFO | Build the GSI info files         | YES           | NO          | If YES, the GSI analysis jobs will build the      |
|                  |                                  |               |             | satinfo, cnvinfo, and ozinfo files dynamically.   |
|                  |                                  |               |             | If NO, static versions located in the GSI FIX     |
|                  |                                  |               |             | directory will be used.                           |
+------------------+----------------------------------+---------------+-------------+---------------------------------------------------+

JEDI model interface selection
------------------------------

When running the JEDI-based deterministic variational analyses, the model interface used by the
variational solver can be selected per component (defaults reproduce the current system):

* ``JEDI_ATM_INTERFACE`` (``atmanl`` section of the defaults YAML): ``fv3jedi`` (default) or
  ``ijedi``. With ``ijedi``, the ``atmanlvar`` step runs ``gdas_ijedi.x var`` on the i-jedi FV3
  geometry. Requires GDASApp built with ``BUILD_IJEDI=ON``, ``STATICB_TYPE=identity`` (no
  gsibec/Control2Analysis support in i-jedi yet) and ``LEVS=128`` (the only ak/bk table ported
  to i-jedi so far). CRTM radiance observations are not supported yet, because i-jedi cannot
  produce the GeoVaLs they need.
* ``JEDI_MARINE_INTERFACE`` (``marineanl`` section): ``soca`` (default) or ``ijedi``. With
  ``ijedi``, the marine variational step runs ``gdas_ijedi.x var`` on the i-jedi MOM6 geometry.
  The analysis is ocean only (no sea-ice increment) and is supported only at 5 degree ocean
  resolution (``OCNRES=500``). The MPI layout of the i-jedi MOM6 geometry is derived from the
  ``marineanlvar`` task count in ``config.resources``. The background error is identity until
  the B-matrix jobs can calibrate i-jedi diffusion parameters (soca's cannot be read by i-jedi);
  the B-matrix and increment post-processing steps remain soca-based.

These switches live in the experiment configs (``config.atmanl``/``config.marineanl``), so
changing them requires re-running ``setup_expt.py``; they do not adjust the XML.
