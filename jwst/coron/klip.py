"""
    Python implementation of the KLIP algorithm based on the
    Mathematica script from Remi Soummer.

:Authors: Mihai Cara

:License: `<http://www.stsci.edu/resources/software_hardware/pyraf/LICENSE>`_
"""

from __future__ import division

import logging
import numpy as np

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def klip(target_model, refs_model, truncate):

    """
    Parameters
    ----------
    target_model : ImageModel
        The input image of the target

    refs_model : CubeModel
        The input cube of reference images

    truncate : int
        Indicates how many rows to keep in the Karhunen-Loeve transform.
    """

    # Initialize the output models as copies of the input target model
    output_target = target_model.copy()
    output_psf = target_model.copy()

    # Load the target data array and flatten it from 2-D to 1-D
    target = target_model.data
    target = target.astype(np.float64)
    tshape = target.shape
    target = target.reshape(-1)

    # Load the reference psf arrays and flatten them from 3-D to 2-D
    refs = refs_model.data
    refs = refs.astype(np.float64)
    rshape = refs.shape
    nrefs = rshape[0]
    refs = refs.reshape(nrefs, rshape[1]*rshape[2])

    # Make each ref image have zero mean
    for k in range(nrefs):
        refs[k] -= np.mean(refs[k], dtype=np.float64)

    # Compute Karhunen-Loeve transform of ref images and normalize vectors
    klvect, eigval, eigvect = KarhunenLoeveTransform(refs, normalize=True)

    # Truncate the Karhunen-Loeve vectors
    klvect = klvect[:truncate]

    # Compute the PSF fit to the target image
    psfimg = np.dot(klvect.T, np.dot(target, klvect.T))

    # Subtract the PSF fit from the target image
    outimg = target - np.mean(target, dtype=np.float64)
    outimg = outimg - psfimg

    # Unflatten the PSF and subtracted target images from 1-D to 2-D
    psfimg = psfimg.reshape(tshape)
    output_psf.data = psfimg
    outimg = outimg.reshape(tshape)
    output_target.data = outimg

    # Compute the ERR for the fitted target image:
    # the ERR is taken as the std-dev of the KLIP results for all of the
    # PSF reference images.
    #
    # First, apply the PSF fit to each PSF reference image
    refs_fit = refs * 0.0
    for k in range(nrefs):
        refs_fit[k] = refs[k] - np.dot(klvect.T, np.dot(refs[k], klvect.T))
    # Now take the standard deviation of the results
    output_target.err = np.std(refs_fit, 0).reshape(tshape)

    return (output_target, output_psf)


def KarhunenLoeveTransform(m, normalize=False):
    """
    Returns Karhunen-Loeve Transform of the input, eigenvalues, and
    a matrix of eigenvectors.

    """
    eigval, eigvect = np.linalg.eigh(np.cov(m))

    # Sort eigenvalues (replicate Mathematica's behaviour):
    idx = eigval.argsort()[::-1]
    eigval = eigval[idx]
    eigvect = eigvect[:, idx]

    # Compute Karhunen-Loeve transform:
    klvect = np.dot(eigvect.T, m)

    if normalize:
        for k in range(len(klvect)):
            klvect[k] /= np.linalg.norm(klvect[k])

    return klvect, eigval, eigvect
