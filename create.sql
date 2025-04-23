create table PERSON (
    PERSON_ID              integer primary key,  -- ixPerson
    NAME                   text,                 -- sFullName
    EMAIL                  text,                 -- sEmail
    PHONE                  text,                 -- sPhone
    IS_ADMIN               text,                 -- fAdministrator
    IS_COMMUNITY           text,                 -- fCommunity
    IS_VIRTUAL             text,                 -- fVirtual
    IS_DELETED             text,                 -- fDeleted
    IS_NOTIFY              text,                 -- fNotify
    HOME_PAGE              text,                 -- sHomepage
    LOCALE                 text,                 -- sLocale
    LANGUAGE               text,                 -- sLanguage
    TIME_ZONE              text,                 -- sTimeZoneKey
    LDAP_ID                text,                 -- sLDAPUid
    LAST_CHANGED_WHEN      text,                 -- dtLastActivity
    RECURSE_BUG_CHILDREN   text,                 -- fRecurseBugChildren
    PALLETE_EXPANDED       text,                 -- fPaletteExpanded
    IN_PROGRESS_TICKET_ID  integer,              -- ixBugWorkingOn
    EMAIL_SPOOF_FROM       text,                 -- sFrom
    check (lower(IS_ADMIN)             in ('true','false')),
    check (lower(IS_COMMUNITY)         in ('true','false')),
    check (lower(IS_VIRTUAL)           in ('true','false')),
    check (lower(IS_DELETED)           in ('true','false')),
    check (lower(IS_NOTIFY)            in ('true','false')),
    check (lower(IS_NOTIFY)            in ('true','false')),
    check (lower(RECURSE_BUG_CHILDREN) in ('true','false')),
    check (lower(PALLETE_EXPANDED)     in ('true','false')),
    foreign key (IN_PROGRESS_TICKET_ID) references TICKET (TICKET_ID)
);

create table PROJECT (
    PROJECT_ID             integer primary key,  -- ixProject
    NAME                   text,                 -- sProject
    OWNER_ID               integer,              -- ixPersonOwner
    HAS_INBOX              text,                 -- fInbox
    WORK_FLOW              integer,              -- ixWorkflow
    IS_DELETED             text,                 -- fDeleted
    foreign key (OWNER_ID) references PERSON (PERSON_ID),
    check (lower(IS_DELETED)     in ('true','false')),
    check (lower(HAS_INBOX)      in ('true','false'))
);

create table PRIORITY (
    PRIORITY_ID            integer primary key,  -- ixPriority
    IS_DEFAULT             text,                 -- fDefault
    NAME                   text                  -- sPriority
);

create table MILESTONE (
    MILESTONE_ID           integer primary key,  -- ixFixFor
    NAME                   text,                 -- sFixFor
    IS_DELETED             text,                 -- fDeleted
    IS_REALLY_DELETED      text,                 -- fReallyDeleted
    DUE_WHEN               text,                 -- dt
    STARTED_WHEN           text,                 -- dtStart
    START_NOTE             text,                 -- sStartNote
    PROJECT_ID             integer,              -- ixProject
    DEPENDENCY             text,                 -- setixFixForDependency
    foreign key (PROJECT_ID) references PROJECT (PROJECT_ID),
    check (lower(IS_DELETED)           in ('true','false')),
    check (lower(IS_REALLY_DELETED)    in ('true','false'))
);

create table CATEGORY (
    CATEGORY_ID            integer primary key,  -- ixCategory
    NAME                   text,                 -- sCategory
    PLURAL_NAME            text,                 -- sPlural
    DEFAULT_STATUS_ID      integer,              -- ixStatusDefault
    IS_SCHEDULE_ITEM       text,                 -- fIsScheduleItem
    IS_DELETED             text,                 -- fDeleted
    SORT_ORDER             integer,              -- iOrder
    ICON_TYPE              integer,              -- nIconType
    ATTACHMENT_ICON        integer,              -- ixAttachmentIcon
    IS_DEFAULT_ACTIVE      integer,              -- ixStatusDefaultActive
    foreign key (DEFAULT_STATUS_ID) references STATUS (STATUS_ID),
    check (lower(IS_SCHEDULE_ITEM)     in ('true','false')),
    check (lower(IS_DELETED)           in ('true','false'))
);

create table STATUS (
    STATUS_ID              integer primary key,  -- ixStatus
    NAME                   text,                 -- sStatus
    CATEGORY_ID            integer,              -- ixCategory
    IS_WORK_DONE           integer,              -- fWorkDone
    IS_RESOLVED            integer,              -- fResolved
    IS_DUPLICATE           integer,              -- fDuplicate
    IS_DELETED             integer,              -- fDeleted
    IS_REACTIVATED         integer,              -- fReactivate
    SORT_ORDER             integer,              -- iOrder
    foreign key (CATEGORY_ID) references CATEGORY (CATEGORY_ID),
    check (lower(IS_WORK_DONE)     in ('true','false')),
    check (lower(IS_RESOLVED)      in ('true','false')),
    check (lower(IS_DUPLICATE)     in ('true','false')),
    check (lower(IS_DELETED)       in ('true','false')),
    check (lower(IS_REACTIVATED)   in ('true','false'))
);

create table KANBAN_COLUMN (
    PLANNER_ID             integer,              -- ixPlanner
    COLUMN_ID              integer,              -- ixKanbanColumn
    NAME                   text                  -- sKanbanColumn
);

create table AREA (
    AREA_ID                integer primary key,  -- ixArea
    NAME                   text,                 -- sArea
    PROJECT_ID             integer,              -- ixProject
    OWNER_ID               integer,              -- ixPersonOwner
    NTYPE                  integer,              -- nType
    CDOC                   integer,              -- cDoc
    foreign key (OWNER_ID)   references PERSON  (PERSON_ID),
    foreign key (PROJECT_ID) references PROJECT (PROJECT_ID)
);

create table TICKET (
    TICKET_ID              integer primary key,  -- ixBug
    PARENT_ID              integer,              -- ixBugParent
    IS_OPEN                boolean,              -- fOpen
    TITLE                  text,                 -- sTitle
    ORIGINAL_TITLE         text,                 -- sOriginalTitle
    LATEST_SUMMARY         text,                 -- sLatestTextSummary
    PROJECT_ID             integer,              -- ixProject
    AREA_ID                integer,              -- ixArea
    STATUS_ID              integer,              -- ixStatus
    PRIORITY_ID            integer,              -- ixPriority
    MILESTONE_ID           integer,              -- ixFixFor
    OPENED_BY              integer,              -- ixPersonOpenedBy
    RESOLVED_BY            integer,              -- ixPersonResolvedBy
    CLOSED_BY              integer,              -- ixPersonClosedBy
    ASSIGNED_TO            integer,              -- ixPersonAssignedTo
    CATEGORY_ID            integer,              -- ixCategory
    CREATED_WHEN           text,                 -- dtOpened
    RESOLVED_WHEN          text,                 -- dtResolved
    CLOSED_WHEN            text,                 -- dtClosed
    UPDATED_WHEN           text,                 -- dtLastUpdated
    VIEWED_WHEN            text,                 -- dtLastView
    RELEASE_NOTES          text,                 -- sReleaseNotes
    KANBAN_COLUMN_ID       integer,              -- ixKanbanColumn
    TICKET                 text,                 -- sTicket
    VERSION                text,                 -- sVersion
    STORY_POINTS           real,                 -- dblStoryPts
    DUE_WHEN               text,                 -- dtDue
    TAGS                   text,                 -- tags (also comma-separated or separate table if you prefer)
    foreign key (MILESTONE_ID)  references MILESTONE (MILESTONE_ID),
    foreign key (PARENT_ID)     references TICKET    (TICKET_ID),
    foreign key (PROJECT_ID)    references PROJECT   (PROJECT_ID),
    foreign key (MILESTONE_ID)  references MILESTONE (MILESTONE_ID),
    foreign key (AREA_ID)       references AREA      (AREA_ID),
    foreign key (CATEGORY_ID)   references CATEGORY  (CATEGORY_ID),
    foreign key (STATUS_ID)     references STATUS    (STATUS_ID),
    foreign key (PRIORITY_ID)   references PRIORITY  (PRIORITY_ID),
    foreign key (OPENED_BY)     references PERSON    (PERSON_ID),
    foreign key (RESOLVED_BY)   references PERSON    (PERSON_ID),
    foreign key (CLOSED_BY)     references PERSON    (PERSON_ID),
    foreign key (ASSIGNED_TO)   references PERSON    (PERSON_ID)
);

create table RELATED_TICKET (
    TICKET_ID         integer,
    RELATED_TICKET_ID integer,
    primary key (TICKET_ID, RELATED_TICKET_ID),
    foreign key (TICKET_ID)         references TICKET (TICKET_ID),
    foreign key (RELATED_TICKET_ID) references TICKET (TICKET_ID)
);

create table EVENT (
    EVENT_ID          integer primary key,        -- ixBugEvent
    TICKET_ID         integer,                    -- ixBug
    EVENT_TYPE        integer,                    -- evt
    VERB              text,                       -- sVerb
    DESCRIPTION       text,                       -- evtDescription
    HAPPENED_WHEN     text,                       -- dt
    CREATED_BY        integer,                    -- ixPerson
    ASSIGNED_TO       integer,                    -- ixPersonAssignedTo
    CHANGES           text,                       -- sChanges
    FORMAT            text,                       -- sFormat
    IS_EMAIL          boolean,                    -- fEmail
    IS_HTML           boolean,                    -- fHTML
    IS_EXTERNAL       boolean,                    -- fExternal
    PERSON_NAME       text,                       -- sPerson
    HTML_CONTENT      text,                       -- sHtml
    foreign key (TICKET_ID)   references TICKET (TICKET_ID),
    foreign key (CREATED_BY)  references PERSON (PERSON_ID),
    foreign key (ASSIGNED_TO) references PERSON (PERSON_ID),
    check (lower(IS_EMAIL)           in ('true','false')),
    check (lower(IS_HTML)            in ('true','false')),
    check (lower(IS_EXTERNAL)        in ('true','false'))
);

create table EVENT_COMMENT (
    TICKET_ID   integer,
    EVENT_ID    integer,
    PART_INDEX  integer,                       -- index of the part
    PART        text,                          -- part of the overall comment
    foreign key (TICKET_ID) references TICKET (TICKET_ID)
    foreign key (EVENT_ID)  references EVENT  (EVENT_ID),
    unique (TICKET_ID, EVENT_id, PART_INDEX)
);

create table ATTACHMENT (
    TICKET_ID   integer,
    EVENT_ID    integer,
    ORDER_IND   integer,
    FILE_NAME   text,
    FILE_PATH   text,
    foreign key (TICKET_ID) references TICKET (TICKET_ID),
    foreign key (EVENT_ID)  references EVENT  (EVENT_ID)
);
