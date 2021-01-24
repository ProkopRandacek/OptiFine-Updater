#!/usr/bin/python
import optifineAPI as of
from optifineCLI import formatData

of.init()

MCV = of.getLatestMCV()  # (1, 10, 2) style
print("Latest Minecraft version available:", MCV)
OFV = of.getLatestOFV()  # "G6 pre3" or "G5" style
print("\nLatest OptiFine Version available:", OFV)
print("\nDownload link:", of.ofweb + of.getOFFileLink(MCV, OFV))

print("\nChangelog for the latest Optifine release:")
print(of.getChangelog(MCV, OFV))

print("\nInfo about all available OptiFine version for Minecraft version 1.16.3")
formatData(of.getOFVs4MCV((1, 16, 3)), 0)  # returns a dict
