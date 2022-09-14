import numpy as np
import pandas as pd
import os
from natsort import natsorted
import re
from pathlib import Path
from DataProcessor.tools.shape_analysis import CrystalShape as cs
from DataProcessor.data.calc_data import Calculate as calc


class GUICommands:

    def __init__(self):
        self.method = 0

    def read_folder(self):
        pass
