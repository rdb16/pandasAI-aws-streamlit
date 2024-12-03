

import pandas as pd
from pandasai import PandasAI

# Charger un dataset
data = {
    "âge": [23, 45, 31, 35, 45, 25, 34, 44, 26, 29],
}
df = pd.DataFrame(data)

# Initialiser PandasAI
pandas_ai = PandasAI()

# Demander un histogramme de l'âge
pandas_ai.plot(df, chart_type='hist', column='âge')
