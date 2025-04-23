#!/usr/bin/python3

import os,sys
import re
import xmltodict
import json
import sqlite3

with open('fogbugz.cfg', 'r') as f:
    cfg = json.load(f)

conn = sqlite3.connect(cfg['dbFilename'])
conn.execute('PRAGMA foreign_keys=ON;')

def getStagedJSON(filename):
    pathname = os.path.join(cfg["stageDir"], filename)
    with open(pathname, 'r') as f:
        data = json.load(f)
    return data

apers_json = getStagedJSON('active-people.json')
ipers_json = getStagedJSON('inactive-people.json')
vpers_json = getStagedJSON('virtual-people.json')
pers_json = apers_json['person'] + ipers_json['person'] + vpers_json['person']
proj_json = getStagedJSON('project.json')
area_json = getStagedJSON('area.json')
kbc_json = getStagedJSON('kanbancol.json')
stat_json = getStagedJSON('status.json')
cat_json = getStagedJSON('category.json')
prio_json = getStagedJSON('priority.json')
mile_json = getStagedJSON('milestone.json')

pers_conf = {
     'PERSON_ID'               : ('ixPerson', int)
    ,'NAME'                    : ('sFullName', str)
    ,'EMAIL'                   : ('sEmail', str)
    ,'PHONE'                   : ('sPhone', str)
    ,'IS_ADMIN'                : ('fAdministrator', str)
    ,'IS_COMMUNITY'            : ('fCommunity', str)
    ,'IS_VIRTUAL'              : ('fVirtual', str)
    ,'IS_DELETED'              : ('fDeleted', str)
    ,'IS_NOTIFY'               : ('fNotify', str)
    ,'LOCALE'                  : ('sLocale', str)
    ,'LANGUAGE'                : ('sLanguage', str)
    ,'TIME_ZONE'               : ('sTimeZoneKey', str)
    ,'LDAP_ID'                 : ('sLDAPUid', str)
    ,'LAST_CHANGED_WHEN'       : ('dtLastActivity', str)
    ,'RECURSE_BUG_CHILDREN'    : ('fRecurseBugChildren', str)
    ,'PALLETE_EXPANDED'        : ('fPaletteExpanded', str)
#   ,'IN_PROGRESS_TICKET_ID'   : ('ixBugWorkingOn', int)     # see upd_pers_conf
    ,'EMAIL_SPOOF_FROM'        : ('sFrom', str)
}

proj_conf = {
     'PROJECT_ID'              : ('ixProject', int)
    ,'NAME'                    : ('sProject', str)
    ,'OWNER_ID'                : ('ixPersonOwner', int)
    ,'HAS_INBOX'               : ('fInbox', str)
    ,'WORK_FLOW'               : ('ixWorkflow', int)
    ,'IS_DELETED'              : ('fDeleted', str)
}

area_conf = {
     'AREA_ID'                 : ('ixArea', int)
    ,'NAME'                    : ('sProject', str)
    ,'PROJECT_ID'              : ('ixProject', int)
    ,'OWNER_ID'                : ('ixPersonOwner', int)
    ,'NTYPE'                   : ('nType', int)
    ,'CDOC'                    : ('cDoc', int)
}

kbc_conf = {
     'PLANNER_ID'              : ('ixPlanner', int)
    ,'COLUMN_ID'               : ('ixKanbanColumn', int)
    ,'NAME'                    : ('sKanbanColumn', str)
}

cat_conf = {
     'CATEGORY_ID'             : ('ixCategory', int)
    ,'NAME'                    : ('sCategory', str)
    ,'PLURAL_NAME'             : ('sPlural', str)
#   ,'DEFAULT_STATUS_ID'       : ('ixStatusDefault', int)     # see upd_cat_conf and upd_pers_conf,
    ,'IS_SCHEDULE_ITEM'        : ('fIsScheduleItem', str)
    ,'IS_DELETED'              : ('fDeleted', str)
    ,'SORT_ORDER'              : ('iOrder', int)
    ,'ICON_TYPE'               : ('nIconType', int)
    ,'ATTACHMENT_ICON'         : ('ixAttachmentIcon', int)
    ,'IS_DEFAULT_ACTIVE'       : ('ixStatusDefaultActive', str)
}

stat_conf = {
     'STATUS_ID'               : ('ixStatus', int)
    ,'NAME'                    : ('sStatus', str)
    ,'CATEGORY_ID'             : ('ixCategory', int)
    ,'IS_WORK_DONE'            : ('fWorkDone', str)
    ,'IS_RESOLVED'             : ('fResolved', str)
    ,'IS_DUPLICATE'            : ('fDuplicate', str)
    ,'IS_DELETED'              : ('fDeleted', str)
    ,'IS_REACTIVATED'          : ('fReactivate', str)
    ,'SORT_ORDER'              : ('iOrder', int)
}

prio_conf = {
     'PRIORITY_ID'             : ('ixPriority', int)
    ,'NAME'                    : ('sPriority', str)
    ,'IS_DEFAULT'              : ('fDefault', str)
}

mile_conf = {
     'MILESTONE_ID'            : ('ixFixFor', int)
    ,'NAME'                    : ('sFixFor', str)
    ,'IS_DELETED'              : ('fDeleted', str)
    ,'IS_REALLY_DELETED'       : ('fReallyDeleted', str)
    ,'DUE_WHEN'                : ('dt', str)
    ,'STARTED_WHEN'            : ('dtStart', str)
    ,'START_NOTE'              : ('sStartNote', str)
    ,'PROJECT_ID'              : ('ixProject', int)
    ,'DEPENDENCY'              : ('setixFixForDependency', str)
}

def ltOneToNone (id):
    return id if int(id) >= 1 else None

case_conf = {
     'TICKET_ID'               : ('ixBug', int)
#   ,'PARENT_ID'               : ('ixBugParent', int)        # see upd_tkt_conf
    ,'IS_OPEN'                 : ('fOpen', str)
    ,'TITLE'                   : ('sTitle', str)
    ,'ORIGINAL_TITLE'          : ('sOriginalTitle', str)
    ,'LATEST_SUMMARY'          : ('sLatestTextSummary', str)
    ,'PROJECT_ID'              : ('ixProject', int)
    ,'AREA_ID'                 : ('ixArea', int)
    ,'STATUS_ID'               : ('ixStatus', int)
    ,'PRIORITY_ID'             : ('ixPriority', int)
    ,'MILESTONE_ID'            : ('ixFixFor', int)
    ,'OPENED_BY'               : ('ixPersonOpenedBy', int)
    ,'RESOLVED_BY'             : (lambda row: ltOneToNone(row['ixPersonResolvedBy']), int)
    ,'CLOSED_BY'               : (lambda row: ltOneToNone(row['ixPersonClosedBy']), int)
    ,'ASSIGNED_TO'             : ('ixPersonAssignedTo', int)
    ,'CATEGORY_ID'             : ('ixCategory', int)
    ,'CREATED_WHEN'            : ('dtOpened', str)
    ,'RESOLVED_WHEN'           : ('dtResolved', str)
    ,'CLOSED_WHEN'             : ('dtClosed', str)
    ,'UPDATED_WHEN'            : ('dtLastUpdated', str)
    ,'VIEWED_WHEN'             : ('dtLastView', str)
    ,'DUE_WHEN'                : ('dtDue', str)
    ,'RELEASE_NOTES'           : ('sReleaseNotes', str)
    ,'KANBAN_COLUMN_ID'        : ('ixKanbanColumn', int)
    ,'TICKET'                  : ('sTicket', str)
    ,'VERSION'                 : ('sVersion', str)
    ,'VERSION'                 : ('sVersion', str)
    ,'STORY_POINTS'            : ('dblStoryPts', float)
    ,'TAGS'                    : ('tags', str)
}

event_conf = {
     'EVENT_ID'                : ('ixBugEvent', int)
    ,'TICKET_ID'               : ('ixBug', int)
    ,'EVENT_TYPE'              : ('evt', int)
    ,'VERB'                    : ('sVerb', str)
    ,'DESCRIPTION'             : ('evtDescription', str)
    ,'HAPPENED_WHEN'           : ('dt', str)
    ,'CREATED_BY'              : (lambda row: ltOneToNone(row['ixPerson']), int)
    ,'ASSIGNED_TO'             : (lambda row: ltOneToNone(row['ixPersonAssignedTo']), int)
    ,'CHANGES'                 : ('sChanges', str)
    ,'FORMAT'                  : ('sFormat', str)
    ,'IS_EMAIL'                : ('fEmail', str)
    ,'IS_HTML'                 : ('fHTML', str)
    ,'HTML_CONTENT'            : ('sHtml', str)
}

evt_comment_conf = {
     'EVENT_ID'                : ('ixBugEvent', int)
    ,'TICKET_ID'               : ('ixBug', int)
    ,'PART_INDEX'              : ('COMMENT_IND', int)
    ,'PART'                    : ('COMMENT', str)
}

att_conf = {
     'EVENT_ID'                : ('ixBugEvent', int)
    ,'TICKET_ID'               : ('ixBug', int)
    ,'ORDER_IND'               : ('ORDER', int)
    ,'FILE_NAME'               : ('FILENAME', str)
    ,'FILE_PATH'               : ('FILEPATH', str)
}

# This dict is for iterating over milestones to determine if a milestone
# refers to a project that was not inserted earlier (due to a deficiency
# in the listProjects command. Since a milestone contains a project id and
# a project name, we can insert from the milestone:
#     (project_id, name, is_deleted) values (ixProject, sProject, 'true')
# for every milestone that refers to a non-existing project. There is no
# way to tell listProjects to return deleted projects. They let you return
# other things that are deleted but not projects. Insert eyeroll emoji.
proj_missing_conf = {
      'keyCols' : {
          'PROJECT_ID'              : ('ixProject', int)
     }
     ,'insCols' : {
          'PROJECT_ID'              : ('ixProject', int)
         ,'NAME'                    : ('sProject', str)
         ,'IS_DELETED'              : (lambda row: "true", str)
     }
}

area_missing_conf = {
      'keyCols' : {
          'AREA_ID'                 : ('ixArea', int)
     }
     ,'insCols' : {
          'AREA_ID'                 : ('ixArea', int)
         ,'NAME'                    : ('sArea', str)
     }
}

mile_missing_conf = {
      'keyCols' : {
          'MILESTONE_ID'            : ('ixFixFor', int)
     }
     ,'insCols' : {
          'MILESTONE_ID'            : ('ixFixFor', int)
         ,'NAME'                    : ('sFixFor', str)
         ,'IS_DELETED'              : (lambda row: "true", str)
     }
}

pers_missing_conf = {
      'keyCols' : {
          'PERSON_ID'               : ('ixPersonAssignedTo', int)
     }
     ,'insCols' : {
          'PERSON_ID'               : ('ixPersonAssignedTo', int)
         ,'NAME'                    : ('sPersonAssignedTo', str)
     }
}

prio_missing_conf = {
      'keyCols' : {
          'PRIORITY_ID'             : ('ixPriority', int)
     }
     ,'insCols' : {
          'PRIORITY_ID'             : ('ixPriority', int)
         ,'NAME'                    : ('sPriority', str)
     }
}

# Update CATEGORY set DEFAULT_STATUS_ID = ixStatusDefault.
upd_cat_conf = {
      'keyCols' : {
          'CATEGORY_ID'             : ('ixCategory', int)
    }
    , 'updCols' : {
          'DEFAULT_STATUS_ID'       : ('ixStatusDefault', int)
    }
}

# Update CATEGORY set DEFAULT_STATUS_ID = ixStatusDefault.
upd_pers_conf = {
      'keyCols' : {
          'PERSON_ID'               : ('ixPerson', int)
    }
    , 'updCols' : {
          'IN_PROGRESS_TICKET_ID'   : (lambda row: ltOneToNone(row['ixBugWorkingOn']), int)
    }
}

# Update TICKET set PARENT_ID = ixBugParent.
upd_tkt_conf = {
      'keyCols' : {
          'TICKET_ID'               : ('ixBug', int)
    }
    , 'updCols' : {
          'PARENT_ID'               : ('ixBugParent', int)
    }
}

def makeRow(obj, config):
    row = {}
    for col, (path, fn) in config.items():
        try:
            if isinstance(path, str):
                value = obj
                for part in path.split('.'):
                    value = value[part]
                row[col] = fn(value) if fn else value
            elif callable(path):
                row[col] = path(obj)
            else:
                raise ValueError(f"Invalid path type for column {col}: {type(path)}")
        except Exception:
            row[col] = None
    return row

def insertTableVerbose(tabName, config, data, verbose):
    if verbose:
        print("Insert " + tabName);
    rows = [makeRow(item, config) for item in data]
    cols = ', '.join(list(config.keys()))
    binds = ', '.join([':'+i for i in config.keys()])
    stm = 'INSERT INTO {} ({}) values ({})'.format(tabName, cols, binds)
    cur = conn.cursor()
    cur.executemany(stm, rows)
    cur.close()
    conn.commit()

def insertTable(tabName, config, data):
    insertTableVerbose(tabName, config, data, True)

def anyNull(config, row):
    for col in config.keys():
        if row[col] is None:
            return True;
    return False;

def reinsertTableVerbose(tabName, config, json, verbose):
    if verbose:
        print("Reinsert " + tabName);
    rows = [makeRow(item, config['insCols']) for item in json]

    icols = ', '.join(list(config['insCols'].keys()))
    ibinds = ', '.join([':'+i for i in config['insCols'].keys()])
    istm = 'insert into {} ({}) values ({})'.format(tabName, icols, ibinds)

    where = ' and '.join(f"{key} = :{key}" for key in config['keyCols'])
    qstm = 'select 1 from {} where {}'.format(tabName, where)
    qcur = conn.cursor()
    icur = conn.cursor()
    for irow in rows:
        if anyNull(config['keyCols'], irow):
            continue
        qcur.execute(qstm, irow)
        qrow = qcur.fetchone()
        if qrow is None:
            icur.execute(istm, irow)
    conn.commit()
    qcur.close()
    icur.close()

def reinsertTable(tabName, config, json):
    reinsertTableVerbose(tabName, config, json, True)

def updateTableVerbose(tabName, config, json, verbose):
    if verbose:
        print("Update " + tabName);
    flatRowConf = {
         **config['keyCols']
        ,**config['updCols']
    }
    rows = [makeRow(item, flatRowConf) for item in json]

    setClause = ', '.join(f"{key} = :{key}" for key in config['updCols'])
    whereClause = ' and '.join(f"{key} = :{key}" for key in config['keyCols'])
    ustm = 'update {} set {} where {}'.format(tabName, setClause, whereClause)

    ucur = conn.cursor()
    for irow in rows:
        if anyNull(config['keyCols'], irow):
            continue
        ucur.execute(ustm, irow)
    conn.commit()
    ucur.close()

def updateTable(tabName, config, json):
    updateTableVerbose(tabName, config, json, True)

def makeCommentRow(event, i):
    row = {
        'ixBugEvent' : event['ixBugEvent'],
        'ixBug' : event['ixBug']
    }
    if i is None:
        row['COMMENT'] = event['s']
        row['COMMENT_IND'] = 1
    else:
        row['COMMENT'] = event['s'][i]
        row['COMMENT_IND'] = i + 1
    return row

def makeAttachmentRows(event):
    evtDir = os.path.join("attachments", str(event['ixBugEvent']))
    stageEvtDir = os.path.join(cfg["stageDir"], evtDir)
    if not os.path.isdir(stageEvtDir):
        return [];
    rows = []
    for file in os.listdir(stageEvtDir):
        match = re.match(r'^(\d+)-(.*)', file)
        if match:
            orderId = match.group(1)
            origName = match.group(2)
            row = {
                'ixBugEvent' : event['ixBugEvent'],
                'ixBug' : event['ixBug'],
                'ORDER' : orderId,
                'FILENAME' : origName,
                'FILEPATH' : os.path.join(evtDir, file)
            }
            rows.append(row)
        else:
            print("Warning: file '{}' is not of the expected format %d-%s".format(file))
    return rows

def loadEvents(tkt):
    reinsertTableVerbose('PERSON'    , pers_missing_conf, [tkt], False)
    insertTableVerbose('EVENT'       , event_conf       , tkt['events'], False)
    evrows = []
    attrows = []
    for event in tkt['events']:
        comment = event['s']
        if (type(comment) == list):
            evrows += [makeCommentRow(event, i) for i in range(len(comment))]
        else:
            evrows += [makeCommentRow(event, None)]
        attrows += makeAttachmentRows(event)
  
    insertTableVerbose('EVENT_COMMENT', evt_comment_conf, evrows, False)
    insertTableVerbose('ATTACHMENT', att_conf, attrows, False)

def loadTicket(dir, filename):
    pathname = os.path.join('cases', filename)
    tkt = getStagedJSON(pathname)

    # The fogbugz tables are denormalized and these denormalizations allow
    # us to insert into parent tables where a foreign key value isn't found.
    reinsertTableVerbose('AREA'      , area_missing_conf, [tkt], False)
    reinsertTableVerbose('PROJECT'   , proj_missing_conf, [tkt], False)
    reinsertTableVerbose('MILESTONE' , mile_missing_conf, [tkt], False)
    reinsertTableVerbose('PERSON'    , pers_missing_conf, [tkt], False)
    reinsertTableVerbose('PRIORITY'  , prio_missing_conf, [tkt], False)
    insertTableVerbose('TICKET'      , case_conf        , [tkt], False)
    loadEvents(tkt)
    return tkt

def loadTickets():
    print("Insert TICKET...")
    rows = []
    caseDir = os.path.join(cfg["stageDir"], "cases")
    for file in os.listdir(caseDir):
        if (file.endswith(".json")):
            rows.append(loadTicket(caseDir, file))
        else:
            print('WARNING: {} is not a known ticket file'.format(file))
    return rows

def updateTicketParents(tkts):
    print("Update TICKET...")
    for tkt in tkts:
        if tkt['ixBugParent'] > 0:
            updateTableVerbose('TICKET', upd_tkt_conf, tkt, False)

insertTable('PERSON'       , pers_conf        , pers_json)
insertTable('PROJECT'      , proj_conf        , proj_json['project'])
insertTable('AREA'         , area_conf        , area_json['area'])
insertTable('PRIORITY'     , prio_conf        , prio_json['priority'])
insertTable('KANBAN_COLUMN', kbc_conf         , kbc_json['kanbancolumn'])
insertTable('CATEGORY'     , cat_conf         , cat_json['category'])
insertTable('STATUS'       , stat_conf        , stat_json['status'])
updateTable('CATEGORY'     , upd_cat_conf     , cat_json['category'])
reinsertTable('PROJECT'    , proj_missing_conf, mile_json['fixfor'])
insertTable('MILESTONE'    , mile_conf        , mile_json['fixfor'])

tkts = loadTickets()
updateTicketParents(tkts)

updateTable('PERSON', upd_pers_conf, pers_json)

conn.close()
sys.exit(0)
