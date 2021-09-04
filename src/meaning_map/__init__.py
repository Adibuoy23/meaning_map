from __future__ import print_function, division, absolute_import

__version__ = "0.1.0"
__bibtex__ = """
@article{henderson2017meaning,
  title={Meaning-based guidance of attention in scenes as revealed by meaning maps},
  author={Henderson, John M and Hayes, Taylor R},
  journal={Nature Human Behaviour},
  volume={1},
  number={10},
  pages={743--747},
  year={2017},
  publisher={Nature Publishing Group}
}
"""  # NOQA

# from . import train_data
# from . import pregrids
# from . import filters

# print('Starting Meaning maps... )

from .build_meaning_map import *
from .check_catch_patch_ratings import *
from .create_qualtrics_surveys import *
from .create_scene_patches import *
from .HeatMap import *
from .patch_cut import *
from .patch_stitch import *
from .process_patch_ratings import *
from .upload_survey_to_qualtrics import *
