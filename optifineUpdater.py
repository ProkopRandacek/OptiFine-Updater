import http.client, subprocess, os, platform, sys
from pathlib import Path


def downloadPage(domain, page):
    conn = http.client.HTTPSConnection(domain, 443)
    conn.putrequest("GET", page)
    conn.endheaders()
    return str(conn.getresponse().read())


def downloadProgress(url, file_name):
    conn = http.client.HTTPSConnection("optifine.net", 443)
    conn.putrequest("GET", url)
    conn.endheaders()
    r = conn.getresponse()
    f = open(file_name, "wb")
    file_size = int(r.getheader("Content-Length"))
    file_size_dl = 0
    block_sz = 8192
    while True:
        buff = r.read(block_sz)
        if not buff:
            break
        file_size_dl += len(buff)
        f.write(buff)
        status = int(file_size_dl * 50 / file_size)
        status = f"[{'#' * status}{' ' * (50 - status)}] {status * 2}%"
        print(status, end="\r")
    f.close()
    print("                                                         ", end="\r")


def getFilelink(mcv, ofv):
    downloadpage = downloadPage(
        "optifine.net",
        f"/adloadx?f={'preview_' if 'pre' in ofv else ''}OptiFine_{mcv}_HD_U_{ofv.replace(' ', '_')}.jar",
    )
    pos1 = downloadpage.find("downloadx?f=")
    pos2 = downloadpage[pos1:].find("'") + pos1
    filelink = "/" + downloadpage[pos1 : pos2 - 1]
    return filelink


def update(ofv):
    print(f"Updating from {mcVersion} {ofVersion} to {mcVersion} {ofv}")
    print(f"Downloading OptiFine HD U {ofv}")
    downloadProgress(getFilelink(mcVersion, ofv), "optifine")
    print("Running OptiFine installer")
    if oflog:
        subprocess.run(["java", "-cp", "optifine", "optifine.Installer"])
    else:
        ofo = str(
            subprocess.check_output(["java", "-cp", "optifine", "optifine.Installer"])
        )
        if "Cannot find Minecraft" in ofo:
            print(
                f"Cannot find Minecraft {mcVersion}. You must download and start Minecraft {mcVersion} once in the official launcher."
            )
            exit(1)
    print("OptiFine updated")
    os.remove("optifine")


def getLatestMcV():
    versionPage = downloadPage("minecraft.gamepedia.com", "/Java_Edition")
    pos1 = versionPage.find('<p><b>Release:</b> <a href="/Java_Edition_') + 42
    pos2 = versionPage[pos1:].find('"') + pos1
    return versionPage[pos1:pos2]


def getMcFolder():
    path = None
    if platform.system() == "Linux":
        if os.path.isdir(str(Path.home()) + "/.minecraft/"):
            path = str(Path.home()) + "/.minecraft/launcher_profiles.json"
        else:
            raise FileNotFoundError(str(Path.home()) + "/.minecraft/ folder not found!")
    elif platform.system() == "Windows":
        if os.path.isdir(str(os.getenv("APPDATA")) + "/.minecraft/"):
            path = str(os.getenv("APPDATA")) + "/.minecraft/launcher_profiles.json"
        else:
            raise FileNotFoundError(
                str(os.getenv("APPDATA")) + "/.minecraft/ folder not found!"
            )
    return path


def getInstalledOfV():
    path = getMcFolder()
    prof = open(path).read().replace(" ", "")
    prof = prof[prof.find('"OptiFine":{') :]
    prof = prof[prof.find('"lastVersionId":"') + 18 :]
    ofv = prof[prof.find("HD_U_") + 5 : prof.find('"')].replace("_", " ")
    return ofv


preview = True
oflog = False

if "help" in sys.argv:
    print(
        """Usage:
help  - print this menu
nopre - dont use preview versions of OptiFine
oflog - print OptiFine installator log"""
    )
    exit(0)
if "nopre" in sys.argv:
    preview = False
if "oflog" in sys.argv:
    oflog = True


mcVersion = getLatestMcV()
ofVersion = getInstalledOfV()

downloads = downloadPage("optifine.net", "/downloads")
latestVersions = {}

pos1 = None
while pos1 != -1:
    pos1 = downloads.find("OptiFine 1.")
    pos2 = downloads[pos1:].find("<") + pos1
    v = downloads[pos1 + 9 : pos2].replace("HD U ", "")
    downloads = downloads[pos2:]
    if not preview and "pre" in v:
        continue
    v = v.split(" ")
    if not (v[0] in latestVersions.keys()):
        latestVersions[v[0]] = " ".join(v[1:])
if mcVersion in latestVersions:
    if latestVersions[mcVersion] > ofVersion:
        update(latestVersions[mcVersion])
        exit()
print(f"Already using latest OptiFine version ({ofVersion} for {mcVersion})")
