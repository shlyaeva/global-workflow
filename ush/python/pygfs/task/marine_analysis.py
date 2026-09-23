#!/usr/bin/env python3

from datetime import datetime, timedelta
from logging import getLogger
import os
from pygfs.jedi import Jedi
from pygfs.task.analysis import Analysis
from pygfs.utils.marine_da_utils import test_hist_date
from wxflow import (AttrDict, FileHandler,
                    to_timedelta, to_fv3time, to_isotime,
                    parse_j2yaml, parse_j2tmpl,
                    logit)

logger = getLogger(__name__.split('.')[-1])


class MarineAnalysis(Analysis):
    """
    Class for global marine analysis tasks
    """
    def __init__(self, config):
        """Constructor for global marine analysis

        This method will construct a marine analysis task
        This includes:
        - extending the task_config attribute AttrDict to include parameters required for this task
        - loading the task configuration YAML
        - instantiating the dictionary of Jedi objects for each JEDI application

        Parameters
        ----------
        config: Dict
            dictionary object containing task configuration

        Returns
        ----------
        None
        """

        super().__init__(config)

        # Create a local dictionary that is repeatedly used across this class
        self.task_config.update(marine_task_config(self.task_config))

        # Extend task_config with content of config yaml for this task
        self.task_config.update(parse_j2yaml(self.task_config.TASK_CONFIG_YAML, self.task_config))

        # Construct dictionary of JEDI objects, one for each JEDI application need for the analysis
        expected_keys = ['var', 'soca_incpostproc', 'soca_diag_stats']
        self.jedi_dict = Jedi.get_jedi_dict(self.task_config.jedi_config, self.task_config, expected_keys)

    @logit(logger)
    def initialize(self) -> None:
        """Initialize the marine analysis task

        This method will initialize the marine analysis.
        This includes:
        - staging input files from COM and create output directories
        - staging observation files
        - preparing the namelists for deterministic MOM6 and analysis geometry
        - asserting that dates of the history files are correct
        - initializing all the JEDI applications required for the marine analysis
        - initialize obs stats application

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """

        # stage files from COM
        logger.info(f"Staging files from COM and creating input/output directories")
        FileHandler(self.task_config.data_in).sync()

        # Stage observation files
        logger.info(f"Staging observations")
        self.jedi_dict['var'].stage_obsdatain(self.task_config.COMIN_OBS)

        # prepare the MOM6 namelists
        marine_prep_input_nml(self.task_config)

        # assert that dates of the history files are correct
        test_hist_date('./INPUT/MOM.res.nc', self.task_config.WINDOW_BEGIN)
        for state in self.task_config.marine_pseudo_model_states:
            test_hist_date(state['basename'] + state['ocn_filename'],
                           datetime.strptime(state['date'], '%Y-%m-%dT%H:%M:%SZ'))

        # initialize JEDI applications
        logger.info(f"Initializing JEDI applications")
        self.jedi_dict['var'].initialize(clean_empty_obsspaces=True)
        self.jedi_dict['soca_incpostproc'].initialize()

        # This method is a bit of a hack that will be removed in the future when the anlstat
        # job fully replaces the SOCA obs_diag_stats application
        try:
            self.initialize_obs_stats()
        except Exception as e:
            logger.warning(f"Failed to initialize observation statistics: {e}")

    @logit(logger)
    def execute(self, jedi_dict_key: str) -> None:
        """Execute JEDI application of marine analysis

        Parameters
        ----------
        jedi_dict_key
            key specifying particular Jedi object in self.jedi_dict

        Returns
        ----------
        None
        """

        self.jedi_dict[jedi_dict_key].execute()

    @logit(logger)
    def finalize(self) -> None:
        """Finalize a global marine analysis

        This method will finalize a global marine analysis.
        This includes:
        - Saving output files to COM
        - Archiving, compressing, and saving diag files in COM directory
        - Saving (legacy) observation statistics to COM

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """

        # Save files from COM
        logger.info(f"Saving files to COM")
        FileHandler(self.task_config.data_out).sync()

        # Archive, compress, and save diag files in COM directory
        logger.info(f"Saving observation diag files to COM")
        self.jedi_dict['var'].save_obsdataout(self.task_config.COMOUT_OCEAN_ANALYSIS,
                                              f"{self.task_config.APREFIX}marine_analysis.ioda_hofx")

        # Save obs diag statistics to COM (this is for legacy obs monitoring)
        marine_save_obs_stats(self.jedi_dict['soca_diag_stats'],
                              self.task_config.DATA,
                              self.task_config.COMOUT_OCEAN_ANALYSIS)

    @logit(logger)
    def initialize_obs_stats(self) -> None:
        """Initialize the observation statistics

        This method will initialize the observation statistics
        This includes:
        - ...

        Parameters
        ----------
        None

        Returns
        ----------
        None
        """

        marine_initialize_obs_stats(self.jedi_dict['var'],
                                    self.jedi_dict['soca_diag_stats'],
                                    self.task_config)


@logit(logger)
def marine_task_config(task_config: AttrDict) -> AttrDict:
    """Compute the marine-specific entries of a JEDI analysis task configuration

    These are the SOCA background error selection, restart dates and pseudo model states
    that any task assimilating the ocean and sea ice needs. Kept separate from
    MarineAnalysis so that a coupled analysis can pick them up alongside another
    component's entries.

    Parameters
    ----------
    task_config: AttrDict
        Attribute-dictionary of task configuration, as prepared by Analysis

    Returns
    ----------
    AttrDict of marine-specific task configuration entries
    """

    # compute the relative path from task_config.DATA to task_config.DATAens
    if task_config.NMEM_ENS > 0:
        _enspert_relpath = os.path.relpath(task_config.DATAens, task_config.DATA)
    else:
        _enspert_relpath = None

    # Determine background error model
    if task_config.NMEM_ENS >= 2:
        _berror_model = 'marine_background_error_hybrid_diffusion_diffusion'
    else:
        _berror_model = 'marine_background_error_static_diffusion'

    # Get restart date
    if task_config.DOIAU:
        _rst_date = to_fv3time(task_config.WINDOW_BEGIN)
        _cice_rst_date = to_fv3time(task_config.WINDOW_BEGIN)
    else:
        _rst_date = to_fv3time(task_config.current_cycle)
        _cice_rst_date = to_fv3time(task_config.current_cycle)

    # Generate list of pseudo model states
    dt_pseudo = 3
    fcst_hour_list = list(range(6, 10, dt_pseudo))
    _marine_pseudo_model_states = []
    bkg_date = task_config.WINDOW_BEGIN
    for fcst_hour in fcst_hour_list:
        bkg_date = bkg_date + timedelta(hours=dt_pseudo)
        _marine_pseudo_model_states.append({'date': to_isotime(bkg_date),
                                            'basename': './bkg/',
                                            'ocn_filename': f"ocean.bkg.f{str(fcst_hour).zfill(3)}.nc",
                                            'ice_filename': f"ice.bkg.f{str(fcst_hour).zfill(3)}.nc",
                                            'read_from_file': 1})

    return AttrDict(
        {
            'PARMmarine': os.path.join(task_config.PARMglobal, 'gdas', 'marine'),
            'ENSPERT_RELPATH': _enspert_relpath,
            'berror_model': _berror_model,
            'rst_date': _rst_date,
            'cice_rst_date': _cice_rst_date,
            'marine_pseudo_model_states': _marine_pseudo_model_states
        }
    )


@logit(logger)
def marine_prep_input_nml(task_config: AttrDict) -> None:
    """Write the MOM6 namelists a marine JEDI analysis runs against

    One for the deterministic background geometry and one for the analysis geometry.
    Kept separate from MarineAnalysis so that a coupled analysis can prepare the same
    two namelists.

    Parameters
    ----------
    task_config: AttrDict
        Attribute-dictionary of task configuration

    Returns
    ----------
    None
    """

    logger.info(f"Preparing deterministic MOM6 input namelist")
    parse_j2tmpl(os.path.join(task_config.PARMmarine, 'mom_input.nml.j2'),
                 task_config,
                 output_file="mom_input.nml")

    logger.info(f"Preparing analysis geometry input namelist")
    parse_j2tmpl(os.path.join(task_config.PARMmarine, 'mom_input_anlgeom.nml.j2'),
                 task_config,
                 output_file="./anl_geom/mom_input.nml")


@logit(logger)
def marine_initialize_obs_stats(jedi_var: Jedi, jedi_obs_stats: Jedi, task_config: AttrDict) -> None:
    """Initialize the SOCA observation statistics application

    The observation spaces it reports on are whichever ones survived in the variational
    application's input configuration, so this has to run after that has been initialized.

    Parameters
    ----------
    jedi_var: Jedi
        the initialized variational Jedi object to take the observation spaces from
    jedi_obs_stats: Jedi
        the observation statistics Jedi object to initialize
    task_config: AttrDict
        Attribute-dictionary of task configuration; the observation names and variables
        are added to it

    Returns
    ----------
    None
    """

    cleaned_observations = []
    obs_variables = {}
    for obs_space in jedi_var.jedi_config.input_config['cost function']['observations']['observers']:
        name = obs_space['obs space']['name']
        variable = obs_space['obs space']['simulated variables'][0]

        cleaned_observations.append(name)
        obs_variables[name] = variable

    # Update the task_config with the observation variables
    task_config['cleaned_observations'] = cleaned_observations
    task_config['obs_variables'] = obs_variables

    # Initialize the observation statistics
    logger.info(f"Initializing JEDI SOCA observation statistics application")
    jedi_obs_stats.initialize(task_config)


@logit(logger)
def marine_save_obs_stats(jedi_obs_stats: Jedi, data: str, comout: str) -> None:
    """Copy the (legacy) SOCA observation statistics to COM

    Parameters
    ----------
    jedi_obs_stats: Jedi
        the observation statistics Jedi object
    data: str
        path to the run directory, for logging
    comout: str
        path to the COM output directory, for logging

    Returns
    ----------
    None
    """

    logger.info(f"Copy (legacy) observation statistics from {data} to {comout}")
    try:
        diags_list = jedi_obs_stats.render_jcb_template(algorithm_in='soca_diags_finalize')
    except Exception as e:
        logger.warning(f"Failed to render JCB template, 'soca_diags_finalize': {e}")
        return

    FileHandler(diags_list).sync()
