from collections import namedtuple
import altair as alt
import math
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objs as go

import datetime
import mango
import requests

# from driftpy.constants.markets import MARKETS
assets = ['SOL', 'BTC', 'ETH']

res = requests.get('https://api.dydx.exchange/v3/markets').json()
st.write(res)

st.write(pd.DataFrame(res['markets']))