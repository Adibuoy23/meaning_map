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
from tqdm import tqdm
import os
import errno
import pandas as pd
import numpy as np
from re import match
import shutil
import tkinter
from tkinter import filedialog, messagebox, simpledialog


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
    file = filedialog.askopenfilename(
        parent=root,
        initialdir=currdir,
        title=prompt,
        filetypes=[("text files", ".txt")],
    )

    return file


def get_url(prompt):
    root = tkinter.Tk()
    root.withdraw()  # use to hide tkinter window
    url = ()  # Create an empty tuple for the url
    url_len = any(map(len, url))  # Initialize the url_len to 0
    while not url_len:
        url = simpledialog.askstring("Input", prompt, parent=root)
        try:
            url_len = any(map(len, url))
        except TypeError:
            url_len = 1
    return url


def message(prompt):

    root = tkinter.Tk()
    root.withdraw()  # use to hide tkinter window
    messagebox.showinfo("Information", prompt)


def get_info(prompt):

    root = tkinter.Tk()
    root.withdraw()  # use to hide tkinter window
    response = messagebox.askyesno("Question", prompt)
    if response:
        answer = 1
    else:
        answer = 0
    return answer


def create_qualtrics_surveys():
    print("Please select the qualtrics folder containing patch_stimuli\n")
    qualtrics_path = search_for_file_path(
        "Please select the qualtrics folder containing patch_stimuli"
    )
    print("You selected: " + qualtrics_path)
    survey = dict()  # Create an empty survey dict object

    # Define path parameters
    survey["patch_dir"] = [
        os.path.abspath(qualtrics_path + "/patch_stimuli/fine/"),
        os.path.abspath(qualtrics_path + "/patch_stimuli/coarse/"),
    ]

    # Create the survey_out directory if it doesn't exist
    os.makedirs(qualtrics_path + "/survey_jobs/fine/", exist_ok=True)
    os.makedirs(qualtrics_path + "/survey_jobs/coarse/", exist_ok=True)

    survey["survey_out"] = [
        os.path.abspath(qualtrics_path + "/survey_jobs/fine/"),
        os.path.abspath(qualtrics_path + "/survey_jobs/coarse/"),
    ]

    # Create the instructions directory if it doesn't exist
    os.makedirs(qualtrics_path + "/survey_jobs/rating_instructions/", exist_ok=True)

    # %% 010: Define survey parameters
    # 0 = patch only, 1 = patch in context
    print("Scene context enabled?\n")
    survey["scene_context"] = get_info("Scene context?")
    survey["patch_scale"] = ["fine", "coarse"]  # Patch scales

    # number of ratings per job not including catch trials
    survey["job_ratings"] = 300
    survey["page_items"] = 10  # Number of ratings per page

    # String listed above the likert scale
    survey["rating_type"] = "Meaning Rating\n"

    # Catch trial parameters are dependent on scene context
    if survey["scene_context"]:
        survey["catch_path"] = os.path.abspath(
            qualtrics_path + "/patch_stimuli/catch/custom/catch_patches.csv"
        )
        if not os.path.exists(survey["catch_path"]):
            message(
                """Scene context is set to true, but I can't find the custom
                catchfile.\n Check for catch_patches.csv here:"""
                + survey["catch_path"]
            )
            print("Context is set to true, but I can't find custom catchfile")
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), survey["catch_path"]
            )
        survey["instructions_path"] = os.path.abspath(
            qualtrics_path
            + "/survey_jobs/rating_instructions/"
            + "PatchOnly_instruction_template.txt"
        )
    else:
        survey["catch_path"] = os.path.abspath(
            qualtrics_path + "/patch_stimuli/catch/default/"
        )
        survey["instructions_path"] = os.path.abspath(
            qualtrics_path
            + "/survey_jobs/rating_instructions/"
            + "PatchOnly_instruction_template.txt"
        )
    print("\n")
    print("Enter the url where the image patches are hosted:")
    survey["hosting"] = get_url("Enter the url where the image patches are hosted:")

    message(
        """Make sure the catch_patches.csv file has the same\n
            specified url, in case you are using custom catch patches"""
    )

    # Look if the instructions file is present
    exists = os.path.exists(survey["instructions_path"])

    if not exists:
        print("\n")
        print("Please select the 'instructions.txt' file for the survey:")
        files = get_file("Please provide the instructions file for the survey:")
        for f in list(files):
            shutil.copy(f, survey["instructions_path"])

    # %% 020: Define catch trials (default or user-specified)

    # Check if the catch patches are user defined (used for in context rating)
    # Note: Number of custom patches must be divisible by survey["page_items"]
    catch_urls = dict()
    if survey["scene_context"]:
        df_cpatches = pd.read_csv(survey["catch_path"])
        for i, scale in enumerate(survey["patch_scale"]):
            catch_urls[scale] = list(
                df_cpatches["full_url"][df_cpatches["scale"].isin([scale])]
            )
    else:
        catch_patch_names = os.listdir(survey["catch_path"])
        for i, scale in enumerate(survey["patch_scale"]):
            file_names = list(filter(lambda v: match(scale, v), catch_patch_names))
            catch_urls[scale] = [
                survey["hosting"] + "catch/default/" + name for name in file_names
            ]

    # %% 030: Define patch urls

    # For each patch scale get patch names
    patch_urls = dict()
    total_ratings = dict()
    for i, scale in enumerate(survey["patch_scale"]):
        patch_urls[scale] = []
        patch_names = os.listdir(survey["patch_dir"][i])
        patch_names = [i for i in patch_names if "context" not in i]
        total_ratings[scale] = len(patch_names)
        # For each patch define a unique url
        for name in patch_names:
            patch_urls[scale].append(survey["hosting"] + scale + name)
        assert len(patch_urls[scale]) == total_ratings[scale]

    # %% 040: Randomly sample patches to create survey jobs
    run_samples = dict()
    jobs = dict()
    final_jobs = dict()
    # For each patch scale
    for i, scale in enumerate(survey["patch_scale"]):

        # Perform random sampling without replacement (aka shuffle)
        run_samples[scale] = np.arange(total_ratings[scale])
        np.random.shuffle(run_samples[scale])

        # Build an array for maximum job size
        full_jobs = np.ceil(total_ratings[scale] / survey["job_ratings"])
        nan_array = np.array(
            [None] * (int(survey["job_ratings"]) * int(full_jobs)), dtype=object
        )[:, np.newaxis]
        # Add patch urls and separate into survey jobs
        nan_array[: len(run_samples[scale])] = np.array(patch_urls[scale])[
            run_samples[scale][:, np.newaxis]
        ]

        jobs[scale] = np.reshape(
            nan_array, (int(survey["job_ratings"]), int(full_jobs)), order="F"
        )
        final_jobs[scale] = dict()
        # Define current survey job in pages format
        for k in range(jobs[scale].shape[1]):
            # Get current job
            curr_job = jobs[scale][:, k]
            curr_job = list(filter(None, curr_job))
            curr_job.extend(catch_urls[scale])
            # Build an array for maximum page size
            f_pgs = np.ceil(len(curr_job) / survey["page_items"])
            dims = int(f_pgs) * int(survey["page_items"])
            n_pgs = np.array([None] * dims, dtype=object)[:, np.newaxis]

            # Turn job into surveys in page format
            n_pgs[: len(curr_job)] = np.array(curr_job)[:, np.newaxis]
            final_jobs[scale][k] = np.reshape(
                n_pgs, (int(survey["page_items"]), int(f_pgs)), order="F"
            ).transpose()
    # %% 050: Write text file jobs in Qualtrics pseudo-code

    # For each patch scale
    for i, scale in enumerate(
        tqdm(survey["patch_scale"], desc="Patch survey generation at scale:")
    ):
        for k in range(len(final_jobs[scale])):
            fname = survey["survey_out"][i] + "/survey" + str(k + 1) + ".txt"
            shutil.copy(survey["instructions_path"], fname)
            with open(fname, "a") as f:
                f.write("[[PageBreak]]\n\n")
                f.write("[[Block:BL01]]\n\n")

                # Get current patch survey
                survey_patches = final_jobs[scale][k]
                # Write page by page questions
                for page in range(survey_patches.shape[0]):
                    temp = list(survey_patches[page, :])
                    # Account for incomplete pages<S.page_items, nans
                    curr_page_patches = list(filter(None, temp))
                    # If scene context is active, define scene context images
                    if survey["scene_context"]:
                        current_page_contexts = []
                        for curr in curr_page_patches:
                            # Get the current patch name
                            cname, ext = curr.split("/")[-1].split(".")
                            current_page_contexts.extend(
                                [survey["hosting"] + scale + cname + "_context." + ext]
                            )
                        # print(current_page_contexts)
                    if page == int(np.round(survey_patches.shape[0]) / 2):
                        f.write("[[Block:BL02]]\n\n")

                    # For each item on current page
                    for c in range(len(curr_page_patches)):
                        I_patch = curr_page_patches[c]
                        if survey["scene_context"]:
                            I_context = current_page_contexts[c]

                        # Write qualtrics matrix question commands to File
                        f.write("[[Question:Matrix]]\n")

                        # Display image html to file (PATCH ONLY)
                        if not survey["scene_context"]:
                            f.write("<div style = 'text-align: center;'>\n")
                            f.write("<a><img src='" + I_patch + "' /></a\n")
                            f.write("></div>\n\n")
                        else:
                            f.write("<div style='text-align: center;'>\n")
                            f.write(
                                "<a><img src='"
                                + I_context
                                + "'></a>&nbsp;&nbsp;&nbsp;&nbsp;"
                                + "<img src='"
                                + I_patch
                                + "'"
                            )
                            f.write("></div>\n\n")

                        # Write qualtrics choices = matrix statement
                        f.write("[[Choices]]\n")
                        f.write(survey["rating_type"])

                        # Write qualtrics answers = Likert scale Choices
                        f.write("[[Answers]]\n")
                        f.write("Very Low 1\n")
                        f.write("Low 2\n")
                        f.write("Somewhat Low 3\n")
                        f.write("Somewhat High 4\n")
                        f.write("High 5\n")
                        f.write("Very High 6\n\n")

                    # Write Qualtrics pagebreak command to file
                    f.write("[[PageBreak]]\n\n")
                    f.write("\n")

                    # Write Qualtrics pagebreak command to file
                    f.write("[[PageBreak]]\n\n")
                    f.write("\n")
                    f.write("[[PageBreak]]\n\n")
                    f.write("\n")
