import pandas as pd
import plotly.express as pex
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from datetime import datetime
from matplotlib.pyplot import cm
import numpy as np
import os
from io import BytesIO
import logging
import textwrap
import json
import matplotlib.patches as mpatches

from flask import Flask, request, jsonify, current_app

###############################
#### What this does
####    - if user chooses, imports an ics calendar
####