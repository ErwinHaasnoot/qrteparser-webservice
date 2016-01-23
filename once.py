__author__ = 'erwin'
import csv
from collections import OrderedDict

with open('static/in/UploadedSoundFiles_Test_3.csv') as f:
    reader = csv.reader(f)
    header = next(reader)
    # print header
    next(reader)
    lines = next(reader)
    print OrderedDict(zip(header, lines))
