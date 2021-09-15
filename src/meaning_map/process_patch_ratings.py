#!/usr/bin/python3
# default python version used : 3.9
# follow this link to change your python version if you have
# a different version installed
# https://stackoverflow.com/questions/52584907/how-to-downgrade-python-from-3-7-to-3-6

# ######################################
# #############  Notes #################
# ######################################

# Edited by SAUpadhyayula (Added patch_stitch.py function)
# Originally written by Gwen Rehrig

# 1.0.0 2021-08-09 : SAUpadhyayula wrote it

# ######################################

# 010: Import necessary modules

import os
from scipy.io import savemat
from . import patch_stitch
import cv2 as cv
import numpy as np
import pickle
import tkinter
import re
from tkinter import filedialog, messagebox
from tqdm import tqdm


# 020: Define functions


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


def parse_test_survey(fname, catch_key, scale):
    # Parses all survey questions to associate patch image names with data
    imgs = catch_key[scale]

    tmp = open(fname, "r").readlines()
    tmp = tmp[0]
    tmp = tmp.split('"questionType"')

    # Identify and exclude catch patches
    survey = {}
    survey["scenes"] = []
    survey["catch"] = {}
    for row in tmp:
        for i in imgs:
            if i in row:
                urls = re.findall(r'src=\\"(.*?)\\"', row)
                img = os.path.basename(urls[0])
                qid = row.split('"questionName":"')[1].split('","')[0]
                existing = [survey["catch"][e] for e in list(survey["catch"].keys())]
                if img not in existing:
                    survey["catch"][qid] = img

    # Identify and store test patches
    survey["test"] = {}
    for row in tmp:
        urls = re.findall(r'src=\\"(.*?)\\"', row)
        # Check whether the current row includes a patch image
        if len(urls) > 0:
            if scale in urls[0]:  # Change string to a string in the URL for
                # patch images only (e.g., folder name)

                img = os.path.basename(urls[0])
                # Get the ID of the survey question (QID) for the current row
                qid = row.split('"questionName":"')[1].split('","')[0]
                if qid not in list(survey["catch"].keys()):
                    survey["test"][qid] = img
                    img_scene = img.split(
                        "_"
                    )  # Strip the scene image name from the patch image name
                    if (
                        len(img_scene) > 2
                    ):  # Account for image names that include an underscore
                        # Modify if any your scene names have more
                        # than one underscore
                        img_scene = "_".join(img_scene[:-1])
                    else:
                        img_scene = img_scene[0]
                    if (
                        img_scene not in survey["scenes"]
                    ):  # If the scene doesn't already have data in the dict,
                        # add it
                        survey["scenes"].append(img_scene)

    return survey


def save_struct(
    scene_path, meaning_path, scale_rating_array, scene, task, use_mat=True
):
    # Store patch data for each scene at each scale as a Matlab structure
    # Arguments:
    # 	- dat is the data dictionary constructed in 050
    # 	- scene is a string identifying the scene (e.g., bell)
    #   - scale is a string identifying the grid scale (fine or coarse)
    # 	- task is a string naming the subfolder to save data

    # Make a dictionary to store:
    struct = {}
    scene_file = os.path.join(scene_path, scene + ".jpg")
    scene_image = cv.imread(scene_file, cv.IMREAD_UNCHANGED)
    struct["scene"] = scene_image
    if use_mat:
        struct["rating_array"] = np.stack(scale_rating_array, axis=2)
    else:
        struct["rating_array"] = scale_rating_array
    # Package in another structure so Matlab interprets it properly
    if use_mat:
        save_path = os.path.join(meaning_path, task, "mat")
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)
        savemat(os.path.join(save_path, scene + ".mat"), struct)
    else:
        save_path = os.path.join(meaning_path, task, "raw_data_pkl")
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)
        # create a binary pickle file
        f = open(os.path.join(save_path, scene + ".pkl"), "wb")

        # write the python object (dict) to pickle file
        pickle.dump(struct, f)

        # close file
        f.close()


# 030: Define relevant file paths
# Relative path for this python script
# (assumes it's located in the folder named in the task string)


def process_patch_ratings():
    print("Select the qualtrics folder: \n")
    relpath = search_for_file_path("Select the qualtrics folder:")
    print("You selected: " + relpath + "\n")
    # Folder name for task, if applicable
    #   Remove or change as needed
    task = "meaning_maps"

    # Move up one directory to get catch patch .csv file
    catch_in = os.path.join(relpath, "patch_stimuli", "catch", "custom")

    # Directory for survey .qsf files
    surveys_in = os.path.join(relpath, "survey_jobs", "from_qualtrics")
    # Directory for processed survey data
    data_in = os.path.join(relpath, "processed_data")

    # 040: Put together catch patch key from .csv file to pass to parse_test_survey

    # Build catch key (need to parse surveys)
    catch_key = {}
    catch_key["values"] = [1, 2]
    try:
        catch_tmp = open(os.path.join(catch_in, os.listdir(catch_in)[0]), "r").readlines()
        catch_tmp = catch_tmp[1:]

        for row in catch_tmp:
            try:
                catch_key[row.split(",")[3]].append(row.split(",")[0])
            except KeyError:
                catch_key[row.split(",")[3]] = []
                catch_key[row.split(",")[3]].append(row.split(",")[0])
    except IndexError:
        raise Warning("No catch files found! I will assume that there were no catch patches used")

    # 050: Combine data across surveys into a data dictionary

    # Populate list of scene images
    print("Select the directory containing image scenes:\n")
    scene_image_path = search_for_file_path(
        "Select the directory containing the image scenes:"
    )
    print("You chose: " + scene_image_path + "\n")
    meaning_map_path = os.path.dirname(relpath)
    scenes = [
        s.replace(".jpg", "") for s in os.listdir(scene_image_path) if ".jpg" in s
    ]

    dat = {}
    for scene in scenes:
        # Initialize dictionary for each scene
        dat[scene] = {}
        dat[scene]["fine"] = {}
        dat[scene]["coarse"] = {}

    for file in os.listdir(data_in):
        # Parse scene and survey number information from file name
        scale = file.split("_")[0]
        num = file.split("_")[1].replace(".csv", "")

        # Parse .qsf survey into QIDs to pair patch numbers to data
        this_survey = parse_test_survey(
            os.path.join(surveys_in, "RM03_Inv_" + scale + num + ".txt"),
            catch_key,
            scale,
        )

        # Read in each survey's data
        tmp = open(os.path.join(data_in, file), "r").readlines()
        for j in range(0, len(tmp)):
            tmp[j] = tmp[j].split(",")
        del j

        cols = tmp[0]
        cols = [c.replace("_1", "") for c in cols]

        # Get data corresponding to each question
        for qid in list(this_survey["test"].keys()):
            patch = this_survey["test"][qid].replace(".png", "")
            patch_split = "_".join(patch.split("_")[:-1])
            patch_num = int(patch.split("_")[-1])
            scene = [s for s in this_survey["scenes"] if s == patch_split][0]

            c_ind = cols.index(qid)
            for j in range(1, len(tmp)):
                if tmp[j][c_ind]:
                    val = int(tmp[j][c_ind])
                    try:
                        dat[scene][scale][patch_num].append(val)

                    except KeyError:
                        dat[scene][scale][patch_num] = []
                        dat[scene][scale][patch_num].append(val)
                else:
                    continue

        del tmp

    # 060: (Optional) Make sure each patch has at least 3 ratings
    # 	   If each patch has enough ratings, nothing will happen
    for scene in scenes:
        for scale in ["coarse", "fine"]:
            for patch in list(dat[scene][scale].keys()):
                if (
                    len(dat[scene][scale][patch]) < 3
                ):  # Is the length of the rating array at least 3 entries long?
                    print(
                        "Too few! Too few of you have returned! "
                        + scene
                        + " "
                        + scale
                        + " "
                        + patch
                    )

    # 070: Save dictionary structure for each scene and scale
    list_of_scenes = tqdm(list(dat.keys()))
    for scene in list_of_scenes:
        scale_rating_array = []
        for scale in list(dat[scene].keys()):
            rating_array = patch_stitch(dat, scene, scale)
            scale_rating_array.append(rating_array)
        save_struct(
            scene_image_path,
            meaning_map_path,
            scale_rating_array,
            scene,
            "meaning",
            use_mat=False,
        )
        list_of_scenes.set_description((f"Processed: {scene}"))
