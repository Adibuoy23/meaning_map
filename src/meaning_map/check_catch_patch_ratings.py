#!/usr/bin/python3
# default python version used : 3.9
# follow this link to change your python version if you have
# a different version installed
# https://stackoverflow.com/questions/52584907/how-to-downgrade-python-from-3-7-to-3-6

# ######################################
# #############  Notes #################
# ######################################

# Originally written by Gwen Rehrig

# 1.0.0 2021-08-05 : SAUpadhyayula edited it
import os
import pandas as pd
from collections import defaultdict
import tkinter
from tkinter import filedialog, messagebox, simpledialog


# %% 010: Define functions here


def get_info(prompt):

    root = tkinter.Tk()
    root.withdraw()  # use to hide tkinter window
    response = messagebox.askyesno("Question", prompt)
    if response:
        answer = 1
    else:
        answer = 0
    return answer


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


def str_together(a_list, sep):
    # Function to concatenate a list to a string
    #   Adds a new line character when separator is a tab or comma (for writing to files)
    make_str = ""
    for i in range(0, len(a_list)):
        if i < (len(a_list)) - 1:
            make_str = make_str + str(a_list[i]) + sep
        elif sep in ["\t", ","]:
            make_str = make_str + str(a_list[i]) + "\n"
        else:
            make_str = make_str + str(a_list[i])
    return make_str


def parse_survey(filename, catch_key, scale):
    imgs = catch_key[scale]
    tmp = open(filename, "r").readlines()
    tmp = tmp[0]
    tmp = tmp.split('"questionType"')
    parsed_survey = defaultdict()
    for row in tmp:
        for i in imgs:
            if i in row:
                qid = row.split('"questionName":"')[1].split('","')[0]
                parsed_survey[qid] = i
    return parsed_survey


def get_catch(catch_key, scale, parsed_survey):
    catches = catch_key[scale]
    IDs = []
    vals = []
    for key in parsed_survey.keys():
        if parsed_survey[key] in catches and parsed_survey[key] not in vals:
            IDs.append(key)
            vals.append(parsed_survey[key])
    if len(catches) == len(IDs):
        return IDs
    else:
        assert len(catches) != len(IDs), "Not enough catch patches in the survey"


def check_catch_patch_ratings():

    # %% 020: Define input parameters
    scales = ["coarse", "fine"]
    # Get the qualtrics path
    print("Select the qualtrics folder:\n")
    relpath = search_for_file_path("Select the qualtrics folder:")
    print("You selected: " + relpath+"\n")
    # Directory containing .csv with catch patches
    # Catch patch condition
    print("Do the surveys have custom catch patches?\n")
    custom_catch = get_info("Do the surveys have custom catch patches?")
    print("You said: " + custom_catch + "\n")

    if custom_catch:
        catch_condition = "custom"
    else:
        catch_condition = "default"

    catch_in = os.path.join(relpath, "patch_stimuli", "catch", catch_condition)
    # Directory where survey files are stored
    surveys_in = os.path.join(relpath, "survey_jobs", "from_qualtrics")

    # Define catch keys. These contain the correct ratings participants should
    # respond with. These will be used to validate the catch patch ratings later.
    catch_key = defaultdict(list)
    catch_key["values"] = [1, 2]  # Only lowest part of the scale is correct
    task_surveys = defaultdict(list)

    # Get the catch files information
    if catch_condition == "custom":
        catch_csv = pd.read_csv(catch_in + "/catch_patches.csv")
        catch_file_list = catch_csv["patch"]
        catch_key[scales[0]].extend([i for i in catch_file_list if scales[0] in i])
        catch_key[scales[1]].extend([i for i in catch_file_list if scales[1] in i])
    else:
        catch_file_list = os.listdir(catch_in)
        catch_key[scales[0]].extend([i for i in catch_file_list if scales[0] in i])
        catch_key[scales[1]].extend([i for i in catch_file_list if scales[1] in i])
    # Get survey files information
    for file in os.listdir(surveys_in):
        if scales[0] in file:
            scale = scales[0]
        elif scales[1] in file:
            scale = scales[1]
        num = re.findall(r'\d+', file)  # Store survey number
        print(num)
        parsed_survey = parse_survey(os.path.join(surveys_in, file), catch_key, scale)
        catch_IDs = get_catch(catch_key, scale, parsed_survey)
        try:
            task_surveys[scale][num] = catch_IDs
        except TypeError:
            task_surveys[scale] = defaultdict(list)
            task_surveys[scale][num] = catch_IDs

    # %% 050: Define the survey_data output file locations
    data_in = os.path.join(relpath, "patch_data")
    # Initialize dictionary to store subject data
    sbj_data = {}

    for scale in scales:
        for d in os.listdir(os.path.join(data_in, scale)):  # For each data file
            # Strip information from the file name
            scale_num = re.findall(scale+"[0-9]{3}", d)  # Survey scale + number
            num = scale_num[-3:]  # Survey number

            data = open(
                os.path.join(data_in, scale, d), "r"
            ).readlines()  # Read data file

            cols = data[0]  # Get column names from first row
            # Strip Qualtrics garbage from column names
            cols = [c.replace("_1", "") for c in cols.split(",")]
            inds = [
                cols.index(e) for e in task_surveys[scale][num]
            ]  # Get indices for column names
            # Strip first two rows of Qualtrics header garbage
            data = data[2:]
            try:
                sbj_data[scale][num] = {}
            except KeyError:
                sbj_data[scale] = {}
                sbj_data[scale][num] = {}

            sbj_data[scale][num]["subject"] = {}
            sbj_data[scale][num]["subject"]["id"] = []
            sbj_data[scale][num]["subject"]["catch"] = {}
            sbj_data[scale][num]["correct"] = []
            sbj_data[scale][num]["skips"] = []
            sbj_data[scale][num]["status"] = ""

            # Define the full Likert scale to make sure each question was answered
            full_scale = [1, 2, 3, 4, 5, 6]

            for row in data:  # For each subject
                count = 0  # Keep track of correct responses on catch questions
                catch_resps = {}
                this_row = row.split(",")  # The current subject's data
                if int(
                    this_row[6]
                ):  # Sanity check to make sure survey progress is complete
                    for ind in inds:
                        # Did the subject give the correct response?
                        if int(this_row[ind]) in catch_key["values"]:
                            count = count + 1  # If yes, increment the count variable
                        # Store actual response for sanity checks
                        catch_resps[cols[ind]] = this_row[ind]
                    sbj_data[scale][num]["correct"].append(
                        count
                    )  # Store n correct responses
                    sbj_data[scale][num]["subject"]["id"].append(
                        this_row[-1].replace("\n", "")
                    )  # Store subject ID number
                    sbj_data[scale][num]["subject"]["catch"][
                        str(this_row[-1].replace("\n", ""))
                    ] = catch_resps  # Store actual responses
                    del count

                    # Make sure each response is a valid response on the Likert scale (e.g., no questions were skipped)
                    skips = 0
                    # Consider only patch ratings (not other information, e.g., subject id)
                    for i in range(18, len(cols) - 1):
                        # If the response isn't a response on the scale, count as skipped
                        if int(this_row[i]) not in full_scale:
                            skips = skips + 1
                            print(this_row[-1].replace("\n") + " skipped responses!")
                    if skips:
                        sbj_data[scale][num]["skips"].append("yes")
                    else:
                        sbj_data[scale][num]["skips"].append("no")

            # Count subjects with 80% or higher accuracy as done
            threshold_check = [1 for val in sbj_data[scale][num]["correct"] if val >= 8]
            if sum(threshold_check) >= 3:
                # Done if there are at least 3 subjects who pass the accuracy threshold
                sbj_data[scale][num]["status"] = "done"
            else:
                # If not done, how many more subjects need to beat threshold
                sbj_data[scale][num]["status"] = (
                    str(3 - sum(threshold_check)) + " remaining"
                )

            del threshold_check
    # 070: Print status (complete or not complete) of each survey
    done = ["\tdone: "]
    not_done = ["\tnot done: "]

    for scale in list(sbj_data.keys()):
        for num in list(sbj_data[scale].keys()):
            if sbj_data[scale][num]["status"] == "done":
                done.append(scale + num)
            else:
                not_done.append(scale + num)
    print(str_together(done, "\t"))
    print(str_together(not_done, "\t"))

    # 080: Rewrite data files to exclude catch trials and bad subjects

    # First: Go through sbj_data and
    #  (1) determine which subjects failed the catch trials
    #  (2) record which columns correspond to catch trials

    exclude = {}
    for scale in list(sbj_data.keys()):
        exclude[scale] = {}
        for num in list(sbj_data[scale].keys()):
            exclude[scale][num] = {}
            # Store excluded subject IDs to skip them in later writing steps
            exclude[scale][num]["subjects"] = [
                n
                for n in sbj_data[scale][num]["subject"]["id"]
                if sbj_data[scale][num]["correct"][
                    sbj_data[scale][num]["subject"]["id"].index(n)
                ]
                < 8
            ]
            # Store QIDs for catch trials to exclude them in processed data
            exclude[scale][num]["QIDs"] = list(
                sbj_data[scale][num]["subject"]["catch"][
                    sbj_data[scale][num]["subject"]["id"][0]
                ].keys()
            )

    # For each survey:
    #  (1) Import survey data file
    #  (2) Get header row(s)
    #  (3) Get inds of catch trials (to exclude)
    #  (4) Write rows corresponding to good subjects to new data file in data_out path

    os.makedirs(os.path.join(relpath, "processed_data"), exist_ok=True)
    data_out = os.path.join(relpath, "processed_data")  # Output directory

    for scale in scales:
        for d in os.listdir(os.path.join(data_in, scale)):

            # Repeating some lines from earlier
            s = d.split("_")[2]
            num = s[-3:]
            s = s[0:-3]

            data = open(os.path.join(data_in, scale, d), "r").readlines()

            headers = data[0:1]  # Retain first two header rows
            cols = headers[0]
            cols = [c.replace("_1", "") for c in cols.split(",")]

            catch_inds = [
                cols.index(i) for i in cols if i in exclude[scale][num]["QIDs"]
            ]

            data = data[2:]
            with open(
                os.path.join(data_out, scale + "_" + num + ".csv"), "w"
            ) as outfile:
                for h in headers:
                    tmp = [
                        h.split(",")[t]
                        for t in range(0, len(h.split(",")))
                        if t not in catch_inds
                    ]
                    tmp[-1] = tmp[-1].replace("\n", "")
                    outfile.write(str_together(tmp, ","))
                    del tmp

                for row in data:
                    tmp = [
                        row.split(",")[t]
                        for t in range(0, len(row.split(",")))
                        if t not in catch_inds
                    ]
                    tmp[-1] = tmp[-1].replace("\n", "")
                    if len(exclude[scale][num]["subjects"]):
                        if tmp[-1] not in exclude[scale][num]["subjects"]:
                            outfile.write(str_together(tmp, ","))
                            del tmp
                    else:
                        outfile.write(str_together(tmp, ","))
                        del tmp
            outfile.close()

    # 070: Print status (complete or not complete) of each survey
    done = ["\tdone: "]
    not_done = ["\tnot done: "]

    for scale in list(sbj_data.keys()):
        for num in list(sbj_data[scale].keys()):
            if sbj_data[scale][num]["status"] == "done":
                done.append(scale + num)
            else:
                not_done.append(scale + num)

    print(str_together(done, "\t"))
    print(str_together(not_done, "\t"))

    # %% 080: Rewrite data files to exclude catch trials and bad subjects

    # First: Go through sbj_data and
    #  (1) determine which subjects failed the catch trials
    #  (2) record which columns correspond to catch trials

    exclude = {}
    for scale in list(sbj_data.keys()):
        exclude[scale] = {}
        for num in list(sbj_data[scale].keys()):
            exclude[scale][num] = {}
            # Store excluded subject IDs to skip them in later writing steps
            exclude[scale][num]["subjects"] = [
                n
                for n in sbj_data[scale][num]["subject"]["id"]
                if sbj_data[scale][num]["correct"][
                    sbj_data[scale][num]["subject"]["id"].index(n)
                ]
                < 8
            ]
            # Store QIDs for catch trials to exclude them in processed data
            exclude[scale][num]["QIDs"] = list(
                sbj_data[scale][num]["subject"]["catch"][
                    sbj_data[scale][num]["subject"]["id"][0]
                ].keys()
            )
    # For each survey:
    #  (1) Import survey data file
    #  (2) Get header row(s)
    #  (3) Get inds of catch trials (to exclude)
    #  (4) Write rows corresponding to good subjects to new data file in data_out path

    data_out = os.path.join(relpath, "processed_data")  # Output directory

    for scale in scales:
        for d in os.listdir(os.path.join(data_in, scale)):

            # Repeating some lines from earlier
            s = d.split("_")[2]
            num = s[-3:]
            s = s[0:-3]

            data = open(os.path.join(data_in, scale, d), "r").readlines()

            headers = data[0:1]  # Retain first two header rows
            cols = headers[0]
            cols = [c.replace("_1", "") for c in cols.split(",")]

            catch_inds = [
                cols.index(i) for i in cols if i in exclude[scale][num]["QIDs"]
            ]

            data = data[2:]
            with open(
                os.path.join(data_out, scale + "_" + num + ".csv"), "w"
            ) as outfile:
                for h in headers:
                    tmp = [
                        h.split(",")[t]
                        for t in range(0, len(h.split(",")))
                        if t not in catch_inds
                    ]
                    tmp[-1] = tmp[-1].replace("\n", "")
                    outfile.write(str_together(tmp, ","))
                    del tmp

                for row in data:
                    tmp = [
                        row.split(",")[t]
                        for t in range(0, len(row.split(",")))
                        if t not in catch_inds
                    ]
                    tmp[-1] = tmp[-1].replace("\n", "")
                    if len(exclude[scale][num]["subjects"]):
                        if tmp[-1] not in exclude[scale][num]["subjects"]:
                            outfile.write(str_together(tmp, ","))
                            del tmp
                    else:
                        outfile.write(str_together(tmp, ","))
                        del tmp
            outfile.close()

            data = open(os.path.join(data_in, scale, d), "r").readlines()

            headers = data[0:1]  # Retain first two header rows
            cols = headers[0]
            cols = [c.replace("_1", "") for c in cols.split(",")]

            catch_inds = [
                cols.index(i) for i in cols if i in exclude[scale][num]["QIDs"]
            ]

            data = data[2:]
            with open(
                os.path.join(data_out, scale + "_" + num + ".csv"), "w"
            ) as outfile:
                for h in headers:
                    tmp = [
                        h.split(",")[t]
                        for t in range(0, len(h.split(",")))
                        if t not in catch_inds
                    ]
                    tmp[-1] = tmp[-1].replace("\n", "")
                    outfile.write(str_together(tmp, ","))
                    del tmp

                for row in data:
                    tmp = [
                        row.split(",")[t]
                        for t in range(0, len(row.split(",")))
                        if t not in catch_inds
                    ]
                    tmp[-1] = tmp[-1].replace("\n", "")
                    if len(exclude[scale][num]["subjects"]):
                        if tmp[-1] not in exclude[scale][num]["subjects"]:
                            outfile.write(str_together(tmp, ","))
                            del tmp
                    else:
                        outfile.write(str_together(tmp, ","))
                        del tmp
            outfile.close()
