#!/usr/bin/python3

import os,sys
import xmltodict
import json
import requests
import pathlib
import shutil

with open('fogbugz.cfg', 'r') as f:
    cfg = json.load(f)

urlPref   = 'https://{}/api.asp?token={}&cmd='.format(cfg['host'], cfg['apiToken'])
apers_url = urlPref + 'listPeople'
ipers_url = urlPref + 'listPeople&fIncludeDeleted=1'
vpers_url = urlPref + 'listPeople&fIncludeVirtual=1'
area_url  = urlPref + 'listAreas'
proj_url  = urlPref + 'listProjects'
kbc_url   = urlPref + 'listKanbanColumns'
cat_url   = urlPref + 'listCategories'
prio_url  = urlPref + 'listPriorities'
stat_url  = urlPref + 'listStatuses'
mile_url  = urlPref + 'listFixFors'
case_url  = urlPref + 'listCases'

def fetchDictVerbose(fetchURL, jsonArgs, dictPath, description, verbose):
    if verbose:
        print('Fetching ' + description)
    resp = requests.post(url=fetchURL, json=jsonArgs)
    contentType = resp.headers.get("Content-Type", "")
    if ('json' in contentType):
        d = json.loads(resp.text)
    elif ('xml' in contentType):
        d = xmltodict.parse(resp.text)
    else:
        raise Exception("unknown content type" + contentType)
    for key in dictPath.split('.'):
        d = d[key]
    return d;

def fetchDict(fetchURL, jsonArgs, dictPath, description):
    return fetchDictVerbose(fetchURL, jsonArgs, dictPath, description, True)

def stageDictVerbose(filename, data, description, verbose):
    pathname = os.path.join(cfg["stageDir"], filename)
    dir = os.path.dirname(pathname)
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)
    if verbose:
        print('Writing {} to {}'.format(description, pathname));
    handle = open(pathname, "w")
    json.dump(data, handle)
    handle.close()

def stageDict(filename, data, description):
    stageDictVerbose(filename, data, description, True)


def downloadURL(filename, fetchURL, jsonArgs, description, dictPath):
    d = fetchDict(fetchURL, jsonArgs, dictPath, description)
    stageDict(filename, d, description)

downloadURL('active-people.json'  , apers_url, None, 'active people'     , 'response.people')
downloadURL('inactive-people.json', ipers_url, None, 'inactive people'   , 'response.people')
downloadURL('virtual-people.json' , vpers_url, None, 'virtual people'    , 'response.people')
downloadURL('project.json'        , proj_url , None, 'undeleted projects', 'response.projects')
downloadURL('area.json'           , area_url , None, 'areas'             , 'response.areas')
downloadURL('kanbancol.json'      , kbc_url  , None, 'kanban columns'    , 'response.kanbancolumns')
downloadURL('status.json'         , stat_url , None, 'statuses'          , 'response.statuses')
downloadURL('category.json'       , cat_url  , None, 'categories'        , 'response.categories')
downloadURL('priority.json'       , prio_url , None, 'priorities'        , 'response.priorities')
downloadURL('milestone.json'      , mile_url , None, 'milestones'        , 'response.fixfors')

caseDict = fetchDict(case_url, None, 'response.cases.case', 'ticket numbers')
sortedCases = sorted(caseDict, key=lambda x: int(x['@ixBug']))
stageDict('ticketnum.json', sortedCases, 'ticket numbers')

# Every attachment will be stored in cfg["stageDir"]/attachments/<eventId>/<n>-<originalfilename>
# with <eventId> being the event identifier from the event that is a child of the case and
# with <n> being an ordering integer starting with 1 and with <originalfilename> being as close
# to the original filename as possible. The complete original filename will, of course, still
# be an attribute of the event.
def downloadTicketAttachment(case, event, attachment, attachmentIndex):
    evId = event['ixBugEvent']
    filename = attachment['sFileName']
    frag = attachment['sURL'].replace("&amp;", "&")
    url = "https://%s/%s&token=%s" % (cfg['host'], frag, cfg['apiToken'])
    resp = requests.get(url, stream=True)
    if resp.status_code != 200:
        raise Exception("Failed to download attachment %s" % url)

    # Make the filename as friendly as possible. We have to replace some characters and
    # add some others to avoid name collisions.
    suffix = ".unsafe"
    if filename.endswith(suffix):
        filename = filename[:-len(suffix)]
    filename = filename.replace("/", "-")
    filename = '{}-{}'.format(attachmentIndex, filename)
    pathname = os.path.join(cfg["stageDir"], "attachments", str(evId), filename)
    dir = os.path.dirname(pathname)
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)
    with open(pathname, "wb") as f:
        resp.raw.decode_content = True
        shutil.copyfileobj(resp.raw, f)

ticketsDownloaded = 0
ticketCountFloat = float(len(sortedCases))

def printPct():
    pct = float(ticketsDownloaded) * 100.0 / ticketCountFloat
    print(f"{pct:.1f}%", end='\r')

def downloadTicketRange(cases, firstCaseNum, lastCaseNum):
    global ticketsDownloaded
    caseParams = dict(
        token = cfg['apiToken'],
        cmd   = 'search',
        q     = "case:%s..%s" % (firstCaseNum, lastCaseNum),
        cols  = cfg["caseCols"]
    )
    url = 'https://%s/f/api/0/jsonapi' % cfg['host']
    d = fetchDictVerbose(url, caseParams, 'data.cases', 'cases {} to {}'.format(firstCaseNum, lastCaseNum), False)
    for case in d:
        filename = 'cases/{}.json'.format(case["ixBug"])
        stageDictVerbose(filename, case, None, False)
        for event in case['events']:
            attachments = event['rgAttachments']
            evtAttInd = 1
            for attachment in event['rgAttachments']:
                downloadTicketAttachment(case, event, attachment, evtAttInd)
                evtAttInd += 1
        ticketsDownloaded += 1;
        printPct()

def makeTicketRange(list, i, n):
    range = {}
    j = i + n - 1
    if j >= len(list):
        j = len(list) - 1
    return { 'first' : list[i]['@ixBug'], 'last' : list[j]['@ixBug'] }

n = int(cfg["casePerFetch"])
ticketRanges = [makeTicketRange(sortedCases, i, n) for i in range(0, len(sortedCases), n)]

print('Fetching ticket detail')
printPct()
for i in range(len(ticketRanges)):
    range = ticketRanges[i]
    downloadTicketRange(sortedCases, range['first'], range['last'])

print("")
print("Done")

sys.exit(0)
