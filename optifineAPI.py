import http.client, re

ofweb = "optifine.net"  # Optifine website to send the requests to
page = ""  # internal
pre = False  # set this to False if you dont want prerelease versions


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
    page = re.sub(r"\n\s+", "\n", page)  # remove indents
    page = re.sub(r"<!--(.+?)*-->", "", page)  # remove comments
    page = re.sub(r"\n+", "\n", page)  # remove empty lines


def getAvailableVersions():
    """ Reads the downloaded download page and exports list of available mc versions """
    global page
    if len(page) == 0:
        raise Exception("Version list is empty")
    raw = re.findall(r"Minecraft 1\.\d+\.\d+", page)
    v = []
    for r in raw:  # Remove "Minecraft "
        # v.append(tuple(map(int, r[10:].split("."))))
        v.append(r[10:])
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
    """ Returns changelog for given verion """
    mcvString = ".".join(map(str, mcv))
    changelog = str(
        downloadPage(
            "optifine.net",
            f"/changelog?f={'preview_' if 'pre' in ofv else ''}OptiFine_{mcvString}_HD_U_{ofv.replace(' ', '_')}.jar",  # The page with the download button
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
        if not pre:  # if prerelease versions are not allowed
            if "pre" in OFV:  # and if the newest available version is a prerelease
                continue  # skip it
        return OFV  # else use it


downloadVersionList()

# ====== EXAMPLE USAGE ======
if __name__ == "__main__":
    MCV = getLatestMCV()  # (1, 10, 2) style
    print("Latest Minecraft version available:", MCV)
    OFV = getLatestOFV()  # "G6 pre3" or "G5" style
    print("\nLatest OptiFine Version available:", OFV)
    print("\nDownload link:", ofweb + getOFFileLink(MCV, OFV))

    print("\nChangelog for the latest Optifine release:")
    print(getChangelog(MCV, OFV))

    print("\nInfo about all available OptiFine version for Minecraft version 1.16.3")
    formatData(getOFVs4MCV((1, 16, 3)), 0)  # returns a dict
