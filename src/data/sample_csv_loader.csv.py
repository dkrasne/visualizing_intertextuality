import sys

import pandas as pd

csv = pd.read_csv("sample_csv.csv")

csv.to_csv(sys.stdout)