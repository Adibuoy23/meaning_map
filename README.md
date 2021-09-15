# meaning_map
 A python package to generate and analyse meaning maps from images of natural scenes
 
# Installation
* On Windows / Mac / Ubuntu:
  - Download anaconda / miniconda
  - If you are using windows:
    * Open the Anaconda / miniconda shell from the search bar
    * Download and install git from [https://gitforwindows.org](https://gitforwindows.org)
  - On ubuntu / MacOS:
    * MacOs / Ubuntu should most likely have git installed. If not, you could download from [https://git-scm.com/downloads](https://git-scm.com/downloads)
    * Open the terminal
  - create a new environment by running `conda create -n <env_name> python=3.9` in the shell
  - activate the environment by running `activate <env_name>` in the shell
  - Download jupyter notebook by running `conda install jupyter` in the shell
  - clone the github repository using `git clone https://github.com/Adibuoy23/meaning_map/`
  - Navigate to the downloaded github repository through terminal `cd <path_to_repo>`
  - launch jupyter notebook by running `jupyter notebook` command in the shell from the navigated repo directory
  - Open the `live_notebooks/meaning_map.ipynb` notebook within live_notebooks folder and follow the instructions there

# Built in features
This package provides the code for the following:
* Creating scene patches from natural images
* Creating qualtrics survey consisting of these scene patches - Participants task is to rate how meaningful these patches are on a scale of [1-7]
* Uploading the generated surveys to qualtrics API (This requires a valid qualtrics API token in order to upload)
* Check and process the patch rating obtained surveys - This will consolidate all the ratings that correspond directly to the given image
* Build meaning maps based on the processed ratings

# To Do
* Automate the survey extraction from Qualtrics
