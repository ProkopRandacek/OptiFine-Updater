#!/usr/bin/python
from optifineAPI import (
    getLatestMCV,
    getLatestOFV,
    getChangelog,
    getOFFileLink,
    getOFVs4MCV,
    getAvailableVersions,
    setPrev,
    setVerbose,
    setOFWeb,
    getOFWeb,
    formatData,
    init,
)

import argparse
from argparse import Namespace


def handleLastMC(args: Namespace) -> None:
    print(".".join(map(str, getLatestMCV())))


def handleLastOF(args: Namespace) -> None:
    print(getLatestOFV())


def handleChangelog(args: Namespace) -> None:
    print(getChangelog(tuple(args.mcv.split(".")), args.ofv))


def handleOFFileLink(args: Namespace) -> None:
    print(getOFWeb() + getOFFileLink(tuple(args.mcv.split(".")), args.ofv))


def handleOFVs(args: Namespace) -> None:
    formatData(getOFVs4MCV(tuple(args.mcv.split("."))), 0)


def handleAvailableVersions(args: Namespace) -> None:
    print("\n".join(getAvailableVersions()))


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--noprev", help="ignore the previews", action="store_true")
parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
parser.add_argument("-d", "--domain", help="Set different optifine domain")

subparsers = parser.add_subparsers(help="subparser help", dest="operationName")

parserLastMC = subparsers.add_parser("lastmc", help="Outputs the last MC version.")

parserLastOF = subparsers.add_parser("lastof", help="Outputs the last OF version.")

parserChlog = subparsers.add_parser(
    "changelog",
    help="Outputs changelog for given OptiFine version.",
    epilog="example usage: ./optifineCLI.py changelog 1.16.4 G6",
)
parserChlog.add_argument("mcv", help="Minecraft version")
parserChlog.add_argument("ofv", help="Optifine version")

parserFileLink = subparsers.add_parser(
    "filelink",
    help="Outputs direct OptiFine download link",
    epilog="example usage: ./optifineCLI.py filelink 1.16.4 G6",
)
parserFileLink.add_argument("mcv", help="Minecraft version")
parserFileLink.add_argument("ofv", help="Optifine version")

parserOFVs = subparsers.add_parser(
    "ofvs",
    help="Returns all available OptiFine versions for given Minecraft version.",
    epilog="example usage: ./optifineCLI.py ofvs 1.16.4",
)
parserOFVs.add_argument("mcv", help="Minecraft version")

parserAV = subparsers.add_parser(
    "availvers",
    help="Returns all Minecraft versions that have any OptiFine version available.",
    epilog="example usage: ./optifineCLI.py availvers",
)

args = parser.parse_args()

setVerbose(args.verbose)
setPrev(not args.noprev)
if args.domain != None:
    setOFWeb(args.domain)

operations: dict = {
    "lastmc": handleLastMC,
    "lastof": handleLastOF,
    "changelog": handleChangelog,
    "filelink": handleOFFileLink,
    "ofvs": handleOFVs,
    "availvers": handleAvailableVersions,
}

if args.operationName == None:
    parser.print_help()
else:
    init()
    operations[args.operationName](args)
