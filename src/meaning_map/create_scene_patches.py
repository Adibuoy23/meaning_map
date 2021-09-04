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
from tqdm import tqdm
import os
import cv2 as cv
import numpy as np
from . import patch_cut
import tkinter
from tkinter import filedialog, messagebox


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


def get_info(prompt):

    root = tkinter.Tk()
    root.withdraw()  # use to hide tkinter window
    response = messagebox.askyesno("Question", prompt)
    if response:
        answer = 1
    else:
        answer = 0
    return answer


def create_scene_patches():
    """
    This code creates scene patches from given images.

    Args:
        scene_image_path (string): Location where the scene images are saved

        patch_destination_path (string) : Location where the generated patches
        are going to be saved

    Returns:
        type: None

    Raises:
        Exception: If the images are not [768, 1024]

    """

    # %% 010: Get the image file names
    list_of_files = []
    # path = "../"  # Moves one folder up
    print(patch_cut)
    scene_image_path = search_for_file_path(
        "Please select the directory containing scene images"
    )
    print(scene_image_path)

    patch_destination_path = search_for_file_path(
        "Please select the directory to save the generated patches"
    )
    print(patch_destination_path)
    for root, dirs, files in os.walk(scene_image_path):
        for file in files:  # Get all the filenames into this list
            list_of_files.append(os.path.join(root, file))
    included_extensions = ["jpg", "jpeg", "png"]
    list_of_files = [
        fn
        for fn in list_of_files
        if any(fn.endswith(ext) for ext in included_extensions)
    ]
    # %% 020: Define patch related parameters
    patch = {}
    patch["img_size"] = [768, 1024]  # resolution of the input image
    # parameter for controlling size of the
    patch["scale"] = ["fine", "coarse"]
    # patch 0 = patch only, 1 = patch in the context of the scene
    patch["scene_context"] = get_info("Generate patches with context?")
    # generate catch patches
    patch["catch"] = patch["scene_context"]
    # color used to highlight the patch.
    patch["context_color"] = [57, 255, 20]
    # Include low meaning patches to keep subjects
    patch["catch_trials"] = 1
    # attentive. Only used in context free study
    # Patch diameter - Fine patches have smaller sizes
    patch["diameter"] = [87, 205]
    patch["density"] = [300, 108]  # Number of pixels per patch

    # Define the grid
    x_grid = {}
    y_grid = {}

    # %% 030: Define and display fine and coarse grid as a sanity check.

    # Illustrate how the grid templates look
    for i, d in enumerate(patch["density"]):
        # Create the gray image background
        gray_img = np.ones([patch["img_size"][0], patch["img_size"][1]]) * 128
        # Determine pixel frequency to create a grid of patches
        freq = np.round(
            np.sqrt(patch["img_size"][0] * patch["img_size"][1]) / np.sqrt(d)
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
        r = patch["diameter"][i] / 2
        x_grid[d] = x - offset_x
        y_grid[d] = y - offset_y

        x_grid[d] = x_grid[d].flatten()
        y_grid[d] = y_grid[d].flatten()

        # Draw circles on the gray image
        for en, (y, x) in enumerate(zip(x_grid[d], y_grid[d])):
            # Draw the circles at each grid point
            cv.circle(gray_img, (int(x), int(y)), int(r), (0, 0, 0), 1)
            cv.circle(gray_img, (int(x), int(y)), 0, (0, 0, 0), 2)
            cv.putText(
                gray_img,
                str(en + 1),
                (int(x) - 10, int(y) + 15),
                cv.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                thickness=1,
                lineType=cv.LINE_AA,
            )
        os.makedirs(
            patch_destination_path + "/qualtrics/patch_template/", exist_ok=True
        )
        cv.imwrite(
            patch_destination_path
            + "/qualtrics/patch_template/"
            + patch["scale"][i]
            + ".png",
            gray_img,
        )

    # %% 040: Cut patches from each scene and store images
    for i, d in enumerate(patch["density"]):
        r = int(patch["diameter"][i] / 2)  # Radius to be drawn
        print("Scale: " + patch["scale"][i])
        for k in tqdm(list_of_files, desc="Image"):
            # Read the image
            img = cv.imread(k, cv.IMREAD_UNCHANGED)
            if list(img.shape[:2]) != patch["img_size"]:
                Warning(
                    "Image dimensions :"
                    + str(img.shape[:2])
                    + "Resizing it to [768, 1024]"
                )
                img = cv.resize(img, [768, 1024], interpolation=cv.INTER_AREA)
            # Extract the file name.
            filename = k.split("/")[-1].split(".")[0]
            # Extract the circular patches from the image
            if patch["scene_context"]:  # if context is specified
                for en, (y, x) in enumerate(zip(x_grid[d], y_grid[d])):
                    temp = img.copy()
                    # Draw the circles at each grid point
                    cv.circle(temp, (int(x), int(y)), int(r), (0, 255, 0), 2)
                    os.makedirs(
                        patch_destination_path
                        + "/qualtrics/patch_stimuli/"
                        + patch["scale"][i],
                        exist_ok=True,
                    )
                    cv.imwrite(
                        patch_destination_path
                        + "/qualtrics/patch_stimuli/"
                        + patch["scale"][i]
                        + "/"
                        + filename
                        + str(en + 1)
                        + "_context.png",
                        temp,
                    )
            else:
                # patch_cut is available in utils
                # utils is called in the main function
                patch_cut.patch_cut(
                    img,
                    x_grid[d],
                    y_grid[d],
                    patch["diameter"][i],
                    patch["scale"][i],
                    filename,
                    patch_destination_path,
                )
            # Generate the default catch patches
            if not patch["catch"]:
                os.makedirs(
                    patch_destination_path + "/qualtrics/patch_stimuli/catch/default/",
                    exist_ok=True,
                )
                for ix in range(20):
                    # Create an image array with increasing intensity
                    # over 20 iterations
                    img = np.ones((2 * r, 2 * r, 3), dtype="uint8") * (13 * ix)
                    mask = np.zeros(img.shape[:2], dtype="uint8")
                    cv.circle(mask, (int(r), int(r)), int(r), 255, -1)
                    masked = cv.bitwise_and(img, img, mask=mask)
                    masked = cv.cvtColor(masked, cv.COLOR_RGB2BGRA)
                    masked[:, :, 3] = mask
                    cv.imwrite(
                        patch_destination_path
                        + "/qualtrics/patch_stimuli/catch/default/"
                        + patch["scale"][i]
                        + str(ix + 1)
                        + ".png",
                        masked,
                    )
    if patch["scene_context"]:
        os.makedirs(
            patch_destination_path + "/qualtrics/patch_stimuli/catch/custom/",
            exist_ok=True,
        )
        # Add a message window asking user to add the custom catch patch csv file
        root = tkinter.Tk()
        root.withdraw()  # use to hide tkinter window
        messagebox.showinfo(
            "Information",
            "Make sure to save a copy of the catch_patches.csv in the following directory:\n\n"
            + patch_destination_path
            + "/qualtrics/patch_stimuli/catch/custom/",
        )
