#!/usr/bin/python3
# default python version used : 3.9
# follow this link to change your python version if you have
# a different version installed
# https://stackoverflow.com/questions/52584907/how-to-downgrade-python-from-3-7-to-3-6

# ######################################
# #############  Notes #################
# ######################################

# Adapted for Python by SAUpadhyayula
# Originally written by TRHayes for Matlab

# 1.0.0 2021-07-23 : SAUpadhyayula wrote it
# 2.1.0 2020-01-17 : OSF release updated for TRHayes's matlab code

# ######################################

import numpy as np
from math import hypot


def patch_stitch(dat, scene, scale):
    """
    Compiles the patch ratings and stitches them together.

    This takes in the patch ratings for each patch across all participants,
    computes the average rating, and stores the average ratings for all such
    patches into an array of shape [width x height]. It does it for each of
    the specified scales.

    Args:
        dat (dict): The input dict file is a dictionary of dicts.
        It should containg the following fields: {scene}.
        Scene field contains  a dict {name of the image:scale} key value pair.
        Scale contains another dictionary with key
        value pairs as {scale_name: patch_ids}. Scale name is:
        ["coarse", "fine"].
        patch_ids correspond to the number in the grid that was used to
        generate the patches.
        Refer to patch_cut.py and create_scene_patches.py for more
        information.

        scene (string): Name of the image file to be processed.

        scale (string): Scale at which the image should be processed.

    Returns:
        dict: Returns a dictionary of dictionaries. It would contain the
        following fields: {scene}. Scene field contains another dict with
        {name of the image: scale} key value pair. Scale contains another
        dictionary with {scale_name: rating_array} as a key value pair.
        Rating array is a numpy array with dimensions [width X height]

    Raises:
        Exception: description

    """

    # %% 010: Define image related parameters
    patch = {}
    patch["img_size"] = [768, 1024]  # resolution of the input image
    # Patch diameter - Fine patches have smaller sizes
    patch["diameter"] = [87, 205]
    patch["density"] = [300, 108]  # Number of pixels per patch
    patch["scale"] = ["fine", "coarse"]

    # %% 020: Create the image grid

    # Define the grid
    x_grid = {}
    y_grid = {}

    # Illustrate how the grid templates look
    for i, d in enumerate(patch["scale"]):
        density = patch["density"][i]
        # Determine pixel frequency to create a grid of patches
        freq = np.round(
            np.sqrt(patch["img_size"][0] * patch["img_size"][1]) / np.sqrt(density)
        )
        [y, x] = np.meshgrid(
            np.arange(freq, patch["img_size"][1], freq),
            np.arange(freq, patch["img_size"][0], freq),
        )

        # Center grid on images
        offset_x = freq - (patch["img_size"][0] - np.max(x) + freq) / 2
        offset_y = freq - (patch["img_size"][1] - np.max(y) + freq) / 2

        # Draw circle patch grid on the gray image
        # th = np.arange(0, 2 * np.pi + 1, np.pi / 50)
        x_grid[d] = x - offset_x
        y_grid[d] = y - offset_y

        x_grid[d] = x_grid[d].flatten()
        y_grid[d] = y_grid[d].flatten()

    # %% 030: Create the output rating_array
    xdim = patch["img_size"][0]
    ydim = patch["img_size"][1]
    rating_array = [[[] for i in range(ydim)] for i in range(xdim)]

    # %% 040: Fill in the array with patch ratings
    # Get the patch diameter
    if scale == "fine":
        d = patch["diameter"][0]
    elif scale == "coarse":
        d = patch["diameter"][1]

    for en, (x, y) in enumerate(zip(x_grid[scale], y_grid[scale])):
        # Get the corresponding pixels of the patch location in the image
        lx = max(int(np.round(x)) - int(d / 2), 0)
        rx = min(int(np.round(x)) + int(d / 2), xdim)
        ly = max(int(np.round(y)) - int(d / 2), 0)
        ry = min(int(np.round(y)) + int(d / 2), ydim)

        for i in range(lx, rx):
            for j in range(ly, ry):
                if hypot(i - x, j - y) <= int(d / 2):
                    rating_array[i][j].extend(dat[scene][scale][en + 1])

    return rating_array
