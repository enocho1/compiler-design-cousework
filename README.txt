This runs on the python 3.7+
to run my program, you have to import the following (making sure they are all installed and up to date):
import time
import os
import sys
from networkx import *
import matplotlib.pyplot as plt
import networkx as nx

I've stored some example files if you want to give them a look.

The program is run in the commandline by calling: python cdcw.py {filename}, where {filename} is the name of the input file which should be in the same directory.

It will collect all the data in the input and genarate a grammar which will be stored in a n appropriately named grammar file in the same directory.

The program will then attempt to parse the formula and generate a syntax tree. if successful it will save an image of the graph and show it. to get better detail looking at the graph in the shown display with a large screen will reduce node overlapping and will make the directional edges clearer. i used some opensource code from github to try and space it out and make it look more like a graph, but some inputs result in very messy graphs. the graphs are saved as appropriately named png files in the same directory.

i have left a log file, but even if absent, after every request, the logfile will record the date, the name of the input and whether it was able to form a syntax tree from the given formula. this will be created and saved in an appropriate file.

thanks and have a great easter.