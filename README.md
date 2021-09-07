# meaning_map
 A python package to generate and analyse meaning maps from images of natural scenes

This package provides the code for the following:
* Creating scene patches from natural images
* Creating qualtrics survey consisting of these scene patches - Participants task is to rate how meaningful these patches are on a scale of [1-7]
* Uploading the generated surveys to qualtrics API (This requires a valid qualtrics API token in order to upload)
* Check and process the patch rating obtained surveys - This will consolidate all the ratings that correspond directly to the given image
* Build meaning maps based on the processed ratings
