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
import cv2 as cv
import os


def patch_cut(img, x_grid, y_grid, d, scale, filename, patch_destination_path):
    # Pad the image with d pixels
    img = cv.cvtColor(img, cv.COLOR_RGB2RGBA)
    img = cv.copyMakeBorder(
        img,
        int(d / 2),
        int(d / 2),
        int(d / 2),
        int(d / 2),
        cv.BORDER_CONSTANT,
        value=(255, 255, 255, -255),
    )
    for i, (y, x) in enumerate(zip(y_grid, x_grid)):
        # Crop the image
        lx = int(np.round(x)) + int(d / 2) - int(d / 2)
        rx = int(np.round(x)) + int(d / 2) + int(d / 2)
        ly = int(np.round(y)) + int(d / 2) - int(d / 2)
        ry = int(np.round(y)) + int(d / 2) + int(d / 2)
        crop_img = img[lx:rx, ly:ry, :]
        # Define the mask
        mask = np.zeros(crop_img.shape[:2], dtype="uint8")
        cv.circle(mask, (int(d / 2), int(d / 2)), int(d / 2), 255, -1)
        masked = cv.bitwise_and(crop_img, crop_img, mask=mask)
        # Create a transparency layer
        rgba = cv.cvtColor(masked, cv.COLOR_RGB2RGBA)
        # Then assign the mask to the last channel of the image
        os.makedirs(
            patch_destination_path + "/qualtrics/patch_stimuli/" + scale, exist_ok=True
        )
        cv.imwrite(
            patch_destination_path
            + "/qualtrics/patch_stimuli/"
            + scale
            + "/"
            + filename
            + str(i + 1)
            + ".png",
            rgba,
        )
