import sys
import os,glob
import numpy as np
import pandas as pd
import calendar
from scipy import stats
import time

def load_boxscores(inputpath):
    x = pd.read_csv(inputpath, sep="|")
    return x;

if __name__ == "__main__":
    #Init Variables
    boxscoredata_path=sys.argv[1]

    #Load Combined Box Scores