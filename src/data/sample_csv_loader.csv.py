import sys

import pandas as pd

csv = pd.read_csv("C:/workspace/viz_intxt/sample_csv.csv")

csv.to_csv(sys.stdout)