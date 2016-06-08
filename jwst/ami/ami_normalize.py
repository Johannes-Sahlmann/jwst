from __future__ import division

#
#  Module for normalizing the LG results for a science target by 
#  the LG results for a reference target
#

import logging
from jwst import datamodels

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def normalize_LG (target_model, reference_model):
    """
    Short Summary
    -------------
    Normalizes the LG results for a science target by the
    LG results for a reference target

    Parameters
    ----------
    target_model: AmiLgModel data model
        The target data to be normalized

    reference_model: AmiLgModel data model
        The reference data

    Returns
    -------
    output_model: AmiLgModel data model
        Normalized fringe data for the target

    """
 
    # Create the ouput model as a copy of the input target model
    output_model = target_model.copy()

    # Apply the normalizations to the target data
    #output_model.fit_image = 
    #output_model.resid_image = 
    #output_model.closure_amp_table['coeffs'] = 
    output_model.closure_phase_table['coeffs'] -= reference_model.closure_phase_table['coeffs']
    output_model.fringe_amp_table['coeffs'] /= reference_model.fringe_amp_table['coeffs']
    #output_model.fringe_phase_table['coeffs'] = 
    #output_model.pupil_phase_table['coeffs'] = 
    #output_model.solns_table['coeffs'] = 

    # Return the normalized target model
    return output_model

