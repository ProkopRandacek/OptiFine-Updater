#!/usr/bin/python
from optifineAPI import *

init()

MCV = getLatestMCV()  # (1, 10, 2) style
print("Latest Minecraft version available:", MCV)
OFV = getLatestOFV()  # "G6 pre3" or "G5" style
print("\nLatest OptiFine Version available:", OFV)
print("\nDownload link:", ofweb + getOFFileLink(MCV, OFV))

print("\nChangelog for the latest Optifine release:")
print(getChangelog(MCV, OFV))

print("\nInfo about all available OptiFine version for Minecraft version 1.16.3")
formatData(getOFVs4MCV((1, 16, 3)), 0)  # returns a dict
