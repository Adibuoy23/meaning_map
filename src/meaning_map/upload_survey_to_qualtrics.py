# -*- coding: utf-8 -*-

"""

import_qualtrics_surveys- Uses Qualtrics API to automate the import and activation of the meaning map patch rating surveys.



@author: Taylor R. Hayes

		 Modified by Gwen Rehrig
		 Modified by Zoe Loh for NYU_Depth2 Dataset

"""


# %% 010: Import modules and define relative folder path


# Set your project ID and your API token here

# This can be found in your Qualtrics account settings->Qualtrics IDs edited by AT)
from natsort import natsorted, ns
from datetime import timedelta
from datetime import datetime
import requests  # lib needs to be downloaded
import re
import os
import tkinter
from tkinter import filedialog, messagebox, simpledialog

apiToken = "nUZl2yNaafGgtPZCKI8YCU4joNJPlanHWULcks78"


########
########
# os.chdir(r"\\henderson.cmb.ucdavis.edu\Share\main\tools\NYU_Depth2\data\surveys\set2")


# %% 020: Define various API functions


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


def get_text(prompt):
    root = tkinter.Tk()
    root.withdraw()  # use to hide tkinter window
    text = ()  # Create an empty tuple for the url
    text_len = any(map(len, text))  # Initialize the url_len to 0
    while not text_len:
        text = simpledialog.askstring("Input", prompt, parent=root)
        try:
            text_len = any(map(len, text))
        except TypeError:
            text_len = 1
    return text


###################
# Import Survey API
###################


def import_survey(survey, survey_file, name, apiToken):
    # Setting user parameters
    dataCenter = "co1"  # UC Davis ID
    # Defining inputs
    baseUrl = "https://ucdavis.co1.qualtrics.com/API/v3/surveys".format(dataCenter)
    headers = {
        "x-api-token": apiToken,
    }
    files = {
        "file": (
            survey,
            open(survey_file, "r"),
            "application/vnd.qualtrics.survey.txt",
        )
    }
    data = {"name": name}
    # Make response and print output
    response = requests.post(baseUrl, files=files, data=data, headers=headers)
    return response


###############
# Update Survey
###############


def update_survey(surveyId, name, apiToken):
    # Setting user Parameters
    dataCenter = "co1"
    baseUrl = "https://{0}.qualtrics.com/API/v3/surveys/{1}".format(
        dataCenter, surveyId
    )
    headers = {
        "content-type": "application/json",
        "x-api-token": apiToken,
    }
    data = {
        "name": name,
        "isActive": True,
        "expiration": {
            "startDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "endDate": (datetime.now() + timedelta(days=90)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        },
    }
    response = requests.put(baseUrl, json=data, headers=headers)


################
# Get Survey API
################


def get_survey(surveyId, apiToken):
    # Setting user Parameters
    dataCenter = "co1"
    baseUrl = "https://{0}.qualtrics.com/API/v3/surveys/{1}".format(
        dataCenter, surveyId
    )
    headers = {
        "x-api-token": apiToken,
    }
    response = requests.get(baseUrl, headers=headers)
    # print(response.text)
    return response


###################
# Delete Survey API
###################


def delete_survey(surveyId, apiToken):

    # Setting user Parameters
    dataCenter = "co1"
    baseUrl = "https://{0}.qualtrics.com/API/v3/surveys/{1}".format(
        dataCenter, surveyId
    )
    headers = {
        "x-api-token": apiToken,
    }
    response = requests.delete(baseUrl, headers=headers)


def upload_survey_to_qualtrics():
    # Preallocate array to store surveyIds for later operations
    all_ids = []
    print("Enter the project name \n")
    project_ID = get_text(
        "Enter the project name:"
    )  # This will be the name stem for each survey
    print("Enter the qualtrics API token \n")
    apiToken = get_text("Enter the qualtrics api token: ")
    # %% 030: Import and generate all fine patch jobs in Qualtrics
    # -- Get fine survey files
    # -- (AT EDITS) set the directory to:
    # "\\henderson.cmb.ucdavis.edu\Share\main\tools\NYU_Depth2\data\surveys\set2"
    # os.chdir(r"\\henderson.cmb.ucdavis.edu\Share\main\tools\NYU_Depth2\data\surveys\set2")
    print("Select the qualtrics folder \n")
    relpath = search_for_file_path("Select the qualtrics folder")
    fine_path = os.path.join(relpath, "survey_jobs", "fine")
    fine_files = os.listdir(fine_path)
    fine_files = [f for f in fine_files if "survey" in f]
    fine_files = natsorted(fine_files, alg=ns.IGNORECASE)

    # -- For each file
    for x in fine_files:
        # -- Create survey
        survey_file = os.path.join(fine_path, x)
        survey_number = re.findall("\d+", x)
        name = (
            survey_number[0].rjust(3, "0")
        )  # Qualtrics name sort

        # -- Call API to import survey
        response = import_survey(x, survey_file, name, apiToken)

        # -- Extract survey id from response.text
        response_list = re.findall('"([^"]*)"', response.text)
        surveyId = response_list[2]
        all_ids.append(surveyId)

        # -- Activate survey
        update_survey(surveyId, name, apiToken)

    # %% 040: Import and generate all coarse patch jobs in Qualtrics

    # -- Get coarse survey files
    coarse_path = os.path.join(relpath, "survey_jobs", "coarse")
    coarse_files = os.listdir(coarse_path)
    coarse_files = [f for f in coarse_files if "survey" in f]
    coarse_files = natsorted(coarse_files, alg=ns.IGNORECASE)

    # -- For each file
    for x in coarse_files:
        # -- Create survey
        survey_file = os.path.join(coarse_path, x)
        survey_number = re.findall("\d+", x)
        name = (
            survey_number[0].rjust(3, "0")
        )  # Qualtrics name sort
        # -- Call API to import survey
        response = import_survey(x, survey_file, name, apiToken)
        # -- Extract survey id from response.text
        response_list = re.findall('"([^"]*)"', response.text)
        surveyId = response_list[2]
        all_ids.append(surveyId)

        # -- Activate survey
        update_survey(surveyId, name, apiToken)

        # END OF IMPORT_QUALTRICS_SURVEYS

    # %% 050: Write surveyIds to file

    with open(os.path.join(relpath, "survey_jobs", "survey_ids.txt"), "w") as outfile:
        for id_str in all_ids:
            outfile.write(id_str + "\n")
    outfile.close()

    existing_surveys = open(
        os.path.join(relpath, "survey_jobs", "survey_ids.txt"), "r"
    ).readlines()

    existing_surveys = [d.replace("\n", "") for d in existing_surveys]

    # %% 060: Retrieve surveys uploaded to Qualtrics in .qsf to get actual QIDs

    get_survey_path = os.path.join(relpath, "survey_jobs", "from_qualtrics")
    if not os.path.isdir(get_survey_path):
        os.mkdir(get_survey_path)
    for f in existing_surveys:
        tmp = get_survey(f, apiToken)
        tmp = tmp.text
        name = tmp.split('"name":"')[1].split('"')[0] + ".txt"
        f = open(os.path.join(get_survey_path, name), "w")
        f.write(tmp)
        f.close()

    # %% 070: Delete surveys -- Only run this if you need to delete all surveys generated in steps 030 and 040

    # task = 'interact' # Set to the task surveys do be deleted
    to_delete = existing_surveys
    for survey in to_delete:
        delete_survey(survey, apiToken)
