#!/usr/bin/python
import optifineAPI as of
import argparse
from argparse import Namespace

# https://stackoverflow.com/questions/47131263/python-3-6-print-dictionary-data-in-readable-tree-structure
def formatData(t, s):
    """ Pretty dict print """
    if not isinstance(t, dict) and not isinstance(t, list):
        print("  " * s + str(t))
    else:
        for key in t:
            print("  " * s + str(key))
            if not isinstance(t, list):
                formatData(t[key], s + 1)


def handleLastMC(args: Namespace) -> None:
    print(".".join(map(str, of.getLatestMCV())))


def handleLastOF(args: Namespace) -> None:
    print(of.getLatestOFV())


def handleChangelog(args: Namespace) -> None:
    print(of.getChangelog(tuple(args.mcv.split(".")), args.ofv))


def handleOFFileLink(args: Namespace) -> None:
    print(of.getOFWeb() + of.getOFFileLink(tuple(args.mcv.split(".")), args.ofv))


def handleOFVs(args: Namespace) -> None:
    formatData(of.getOFVs4MCV(tuple(args.mcv.split("."))), 0)


def handleAvailableVersions(args: Namespace) -> None:
    print("\n".join(of.getAvailableVersions()))


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--noprev", help="ignore the previews", action="store_true")
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

of.noprev = not args.noprev
if args.domain != None:
    of.domain = args.domain

operations: dict = {
    "lastmc": handleLastMC,
    "lastof": handleLastOF,
    "changelog": handleChangelog,
    "filelink": handleOFFileLink,
    "ofvs": handleOFVs,
    "availvers": handleAvailableVersions,
}

if __name__ == "__main__":
    if args.operationName == None:
        parser.print_help()
    else:
        of.init()
        operations[args.operationName](args)
