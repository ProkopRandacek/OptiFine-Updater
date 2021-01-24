import http.client, re

ofweb = "optifine.net"  # Optifine website to send the requests to
page = ""
pre = True  # Set this to False if you dont want prerelease versions
verbose = False  # Verbose logging


def vp(text):
    """ Verbose logging. """
    if verbose:
        print(text)


def downloadPage(domain, page):
    vp(f"downloading {domain}{page}")
    conn = http.client.HTTPSConnection(domain, 443)
    conn.putrequest("GET", page)
    conn.endheaders()
    vp("done")
    return str(conn.getresponse().read()).replace("\\r\\n", "\n").replace("\\'", "'")


def cutAllBefore(what, text):
    return text[text.find(what) + len(what) :]


def cutAllAfter(what, text):
    return text[: text.find(what)]


def downloadVersionList():
    """ Downloads OF download page for other functions to use """
    global page
    vp("downloading OF download page")
    page = downloadPage(ofweb, "/downloads")  # Download the html page
    vp("cutting page")
    page = cutAllBefore("</script>", page)  # remove header
    page = cutAllAfter("<span style=\\'font-size:small\\'>", page)  # remove footer
    page = re.sub(r"\n\s+", "\n", page)  # remove indents
    page = re.sub(r"<!--(.+?)*-->", "", page)  # remove comments
    page = re.sub(r"\n+", "\n", page)  # remove empty lines
    vp("done")


def getAvailableVersions():
    """ Reads the downloaded download page and exports list of available mc versions """
    global page
    vp("Checking downloaded page")
    if len(page) == 0:
        vp("downloaded page check failed")
        raise Exception("Version list is empty")
    vp("downloaded page check succeeded")
    vp("searching for OF versions")
    raw = re.findall(r"Minecraft 1\.\d+\.\d+", page)
    v = []
    for r in raw:  # Remove "Minecraft "
        # v.append(tuple(map(int, r[10:].split("."))))
        v.append(r[10:])
    vp("done")
    return v


def getOFVs4MCV(mcv):
    """ Reads the downloaded download page and exports list of available OFVs for given MCv """
    global page
    vp("Checking downloaded page")
    if len(page) == 0:
        vp("downloaded page check failed")
        raise Exception("Version list is empty")
    vp("downloaded page check succeeded")
    pagec = page
    mcvString = ".".join(map(str, mcv))
    pagec = cutAllBefore(f"Minecraft {mcvString}</h2>\n", pagec)
    pagec = cutAllAfter("Minecraft", pagec)
    raw = re.findall(r"<td.+</td>", pagec)  # all cells containg all OFVs info
    OFVs = dict()
    activeOFV = ""  # the cells are all ordered in an array and we need to split different OFVs into different dics
    vp("parsing the page into a dictionary")
    for i in range(len(raw)):
        key, value = raw[i][11 : len(raw[i]) - 5].split("'>", 1)
        key = key[3:]
        if key in ["Download", "Mirror", "Changelog"]:
            continue
        if key == "File":
            activeOFV = value[14:]
            OFVs[value[14:]] = dict()
            continue
        if key == "Forge":
            value = tuple(
                map(int, value.replace("Forge", "").split("."))
            )  # "Forge 34.1.42" > (34, 1, 42)
        OFVs[activeOFV][key] = value
    vp("done")
    return OFVs


def getOFFileLink(mcv, ofv):
    """ Returns download link for given OFV and MCV """
    vp("downloading download button page")
    mcvString = ".".join(map(str, mcv))
    dpage = downloadPage(
        "optifine.net",
        f"/adloadx?f={'preview_' if 'pre' in ofv else ''}OptiFine_{mcvString}_HD_U_{ofv.replace(' ', '_')}.jar",  # The page with the download button
    )
    vp("searing for the direct download link")
    dpage = cutAllBefore("downloadx?f=", dpage)
    dpage = cutAllAfter("'", dpage)
    filelink = "/" + dpage
    vp("done")
    return filelink


def getChangelog(mcv, ofv):
    """ Returns changelog for given version """
    vp("downloading changelog page")
    mcvString = ".".join(map(str, mcv))
    changelog = str(
        downloadPage(
            "optifine.net",
            f"/changelog?f={'preview_' if 'pre' in ofv else ''}OptiFine_{mcvString}_HD_U_{ofv.replace(' ', '_')}.jar",  # The page with the download button
        )
    )[2:]
    changelog = cutAllAfter("\n\n", changelog)
    vp("done")
    return changelog


def getLatestMCV():
    """ Returns the latest mc version """
    vp("downloading the wiki page")
    vpage = downloadPage("minecraft.gamepedia.com", "/Java_Edition")
    vpage = cutAllBefore('<p><b>Release:</b> <a href="/Java_Edition_', vpage)
    vpage = cutAllAfter('"', vpage)
    vp("done")
    return tuple(map(int, vpage.split(".")))


def getLatestOFV():
    """ Returns the latest OF version """
    OFVs = getOFVs4MCV(getLatestMCV())
    vp("searching for latest optifine")
    OFVs = sorted(list(OFVs.keys()))[::-1]  # sorted OFVs from newest to oldest
    for OFV in OFVs:
        if not pre:  # if prerelease versions are not allowed
            if "pre" in OFV:  # and if the newest available version is a prerelease
                continue  # skip it
        vp("found it")
        return OFV  # else use it


def init():
    """ Call this before using the API """
    vp("initiaization")
    downloadVersionList()
    vp("initalized")
