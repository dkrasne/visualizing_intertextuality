import sys

import pandas as pd
import os

scriptdir = os.path.dirname(os.path.abspath(__file__))

csv = pd.read_csv(f"{scriptdir}/sample_csv.csv")
print(csv.head())

csv.to_csv(sys.stdout)