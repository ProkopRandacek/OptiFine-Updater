import http.client, re

ofweb = "optifine.net"  # Optifine website to send the requests to
page = ""
pre = True  # Set this to False if you don't want prerelease versions


def downloadPage(domain, page):
    conn = http.client.HTTPSConnection(domain, 443)
    conn.putrequest("GET", page)
    conn.endheaders()
    return str(conn.getresponse().read()).replace("\\r\\n", "\n").replace("\\'", "'")


def cutAllBefore(what, text):
    return text[text.find(what) + len(what) :]


def cutAllAfter(what, text):
    return text[: text.find(what)]


def downloadVersionList():
    """ Downloads OF download page for other functions to use """
    global page
    page = downloadPage(ofweb, "/downloads")  # Download the html page
    page = cutAllBefore("</script>", page)  # remove header
    page = cutAllAfter("<span style=\\'font-size:small\\'>", page)  # remove footer
    page = re.sub(r"((\n\s+)|(\n+))", "\n", page)  # remove indents and empty lines
    page = re.sub(r"<!--(.+?)*-->", "", page)  # remove comments


def getAvailableVersions():
    """ Reads the downloaded download page and exports list of available mc versions """
    global page
    if len(page) == 0:
        raise Exception("Version list is empty")
    v = re.findall(r"Minecraft 1\.\d+\.\d+", page)
    for i in range(len(v)):  # Remove "Minecraft " and convert to tuple
        v[i].append(tuple(map(int, v[i][10:].split("."))))
    return v


def getOFVs4MCV(mcv):
    """ Reads the downloaded download page and exports list of available OFVs for given MCv """
    global page
    if len(page) == 0:
        raise Exception("Version list is empty")
    pagec = page
    mcvString = ".".join(map(str, mcv))
    pagec = cutAllBefore(f"Minecraft {mcvString}</h2>\n", pagec)
    pagec = cutAllAfter("Minecraft", pagec)
    raw = re.findall(r"<td.+</td>", pagec)  # all cells containg all OFVs info
    OFVs = dict()
    activeOFV = ""  # the cells are all ordered in an array and we need to split different OFVs into different dics
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
    return OFVs


def getOFFileLink(mcv, ofv):
    """ Returns download link for given OFV and MCV """
    mcvString = ".".join(map(str, mcv))
    dpage = downloadPage(
        "optifine.net",
        f"/adloadx?f={'preview_' if 'pre' in ofv else ''}OptiFine_{mcvString}_HD_U_{ofv.replace(' ', '_')}.jar",  # The page with the download button
    )
    dpage = cutAllBefore("downloadx?f=", dpage)
    dpage = cutAllAfter("'", dpage)
    filelink = "/" + dpage
    return filelink


def getChangelog(mcv, ofv):
    """ Returns changelog for given version """
    mcvString = ".".join(map(str, mcv))
    changelog = str(
        downloadPage(
            "optifine.net",
            f"/changelog?f={'preview_' if 'pre' in ofv else ''}OptiFine_{mcvString}_HD_U_{ofv.replace(' ', '_')}.jar",
        )
    )[2:]
    changelog = cutAllAfter("\n\n", changelog)
    return changelog


def getLatestMCV():
    """ Returns the latest mc version """
    vpage = downloadPage("minecraft.gamepedia.com", "/Java_Edition")
    vpage = cutAllBefore('<p><b>Release:</b> <a href="/Java_Edition_', vpage)
    vpage = cutAllAfter('"', vpage)
    return tuple(map(int, vpage.split(".")))


def getLatestOFV():
    """ Returns the latest OF version """
    OFVs = getOFVs4MCV(getLatestMCV())
    OFVs = sorted(list(OFVs.keys()))[::-1]  # sorted OFVs from newest to oldest
    for OFV in OFVs:
        if not (not pre and "pre" in OFV):
            return OFV


def init():
    """ Call this before using the API """
    downloadVersionList()
