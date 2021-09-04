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

# 1.0.0 2021-07-27 : SAUpadhyayula wrote it
# 2.1.0 2020-01-17 : OSF release updated for TRHayes's matlab code

# ######################################
import numpy as np
import cv2 as cv
import pickle
import matplotlib.pyplot as plt
import os
from . import HeatMap
import tkinter
from tkinter import filedialog
from tqdm import tqdm


# Define functions here


def search_for_file_path(prompt):

    root = tkinter.Tk()
    root.withdraw()  # use to hide tkinter window
    currdir = os.getcwd()
    file_dir = filedialog.askdirectory(
        parent=root,
        initialdir=currdir,
        title=prompt,
        mustexist=True,
    )

    return file_dir


def get_file(prompt):

    root = tkinter.Tk()
    root.withdraw()  # use to hide tkinter window
    currdir = os.getcwd()
    files = filedialog.askopenfilenames(
        parent=root,
        initialdir=currdir,
        title=prompt,
        filetypes=[("Pickle files", ".pkl")],
    )

    return files


def transparent_cmap(cmap, N=255):
    "Copy colormap and set alpha values"

    mycmap = cmap
    mycmap._init()
    mycmap._lut[:, -1] = np.linspace(0, 1.0, N + 4)
    return mycmap


def build_meaning_map():
    """
    Generates a meaning map

    Based on the aggregated likert patch data from the fine and coarse
    spatial scales.


    Args:
        rating_array (list): List of dimensions [Image Height x Width x 2]
        2 is for the two spatial scales (coarse and fine).

        For each spatial scale (i.e., fine and coarse) the corresponding rating
        array contains the patch Likert ratings assigned to each pixel in the
        scene image aggregated across all raters (3 unique raters per patch).
        Note due to the overlap between patches most pixels will contain more
        than 3 unique ratings. See meaning_map_example.mat for an instance of a
        rating_array and corresponding scene.

        scene_image [optional] (ndarray): Image array [Height x Width x 3]
        If scene image is included then it will overlay the meaning map on
        the image array and plot the overlaid image and the original image side
        by side.


    Returns:
        None: It saves the meaning map as a '.png' file.

    Raises:
        Exception: description

    """
    save_path = search_for_file_path(
        "select the folder where you want to save the heatmaps: "
    )
    img_save_path = os.path.join(save_path, "img")
    pkl_save_path = os.path.join(save_path, "smooth_pkl")
    os.makedirs(img_save_path, exist_ok=True)
    os.makedirs(pkl_save_path, exist_ok=True)
    meaning_files = get_file(
        "Select the meaning mapped pkl files to generate heatmaps:"
    )
    m_files = tqdm(list(meaning_files))
    for mfile in m_files:
        m_files.set_description(f"Building meaning map for {os.path.basename(mfile)}")
        with open(mfile, "rb") as file:
            # Call load method to deserialze
            data = pickle.load(file)
        fname = os.path.basename(mfile)
        rating_array = data["rating_array"]
        scene_image = data["scene"]
        file_name = fname[:-4]
        # %%010: Sanity-check input rating cell array

        # Check that both spatial scare patch ratings are present
        # assert rating_array.shape[2] == 2, (
        #     "Rating array should be an [H x W x 2]" + "cell array"
        # )
        #
        # if scene_image:
        #     print(scene_image.shape[:1], rating_array.shape[:1])
        #     assert np.array_equal(
        #         scene_image.shape[:1], rating_array.shape[:1]
        #     ), "Scene and rating array should have same dimensions"

        # Check that all values match set of possible Likert rating scale
        likert_set = [1, 2, 3, 4, 5, 6]
        for i in range(len(rating_array)):
            for j in range(len(rating_array[0])):
                for k in range(len(rating_array[0][0])):
                    if any(rating_array[i][j][k]) not in likert_set:
                        raise ValueError(
                            "Rating array contains elements outside likert scale"
                        )
                    else:
                        continue

        # %%020: Generate meaning map from aggregated patch ratings

        # First average ratings at each pixel within each spatial scale
        height = len(rating_array[0])
        width = len(rating_array[0][0])
        spatial_average_map = np.zeros((height, width, 2))
        for k in range(len(rating_array)):
            for i in range(len(rating_array[0])):
                for j in range(len(rating_array[0][0])):
                    spatial_average_map[i][j][k] = np.mean(rating_array[k][i][j])

        # Second average the two spatial scale maps together so each is equally
        # weighted
        average_meaning_map = spatial_average_map.mean(axis=2)

        # Third smooth the map a little to reduce the patch size artifacts.
        sigma = 10
        kernel = (int(2 * np.ceil(2 * sigma) + 1), int(2 * np.ceil(2 * sigma) + 1))
        meaning_map = cv.GaussianBlur(average_meaning_map, kernel, sigma)
        # Use base cmap to create transparent
        hm = HeatMap.HeatMap(scene_image, meaning_map)
        hm.save(
            os.path.join(img_save_path, file_name),
            "png",
            transparency=0.6,
            color_map="seismic",
            show_axis=False,
            show_original=True,
            show_colorbar=True,
            width_pad=5,
        )
        with open(os.path.join(pkl_save_path, file_name + ".pkl"), "wb") as f:

            # write the python object (dict) to pickle file
            pickle.dump(average_meaning_map, f)
