# START

I use this to read this markdown file:

    pandoc -s -t man README.md -o fogbugz.1
    groff -man -Tutf8 fogbugz.1|less -R

# SYNOPSIS

Use this project to extract (dump) data from a Fogbugz web site using its JSON and XML APIs and then load those staged data into some other RDBMS using SQL.

# DESCRIPTION

The process is not too complicated.

1. Edit configuration file, fogbugz.cfg
    - set the host value to the host of the Fogbugz web site from which you will extract data.
    - set the apiToken value to the api token value you get from your fogbugz administrative page
    - set the stageDir value to the output directory to store dumped files
    - set the casePerFetch value to the number of cases to fetch for every request to get case detail
    - set the caseCols value to the list of columns to get in the case detail requests
1. Execute dump.py
1. Create a database
1. Execute populate.py

The code in populate.py uses named bind variables for its queries and DML statements. So, as long as your database supports those features and python has a module for your database, you should be good to go.

Neither python script takes arguments. All options, which are few, are defined in the configuration file.

To create the schema, you execute create.sql. There are scripts for dropping tables and deleting rows.

To create the sqlite database, I do this:

    sqlite3 fogbugz.db
    sqlite> .read create.sql

The code uses ISO-8601 strings for dates since sqlite has no native date datatypes. The alternative is to store them as integers. In any case, you'd have to use a function to perform certain date operations. The advantage of storing dates as ISO-8601 strings is that if you query a date column without a function (out of laziness), then you see something you recognize.

# PREREQUISITES

You need a stable internet connection especially when dump.py starts downloading case details.

You need to install python3 and pip3.

As written, you'll install a few modules with pip3. You'll see those listed at the top of the python scripts among modules that are already installed. The requests and xmltodict modules are probably not part of the standard python installation.

You'll also need to install sqlite3 (e.g., brew install sqlite3) unless you edit populate.py to use some other database or if you've never installed sqlite3.

# REFERENCES

The supported API documention is at:

    https://api.manuscript.com/

I also found this to be helpful:

    https://fogbugz.unco.mcgware.com/help/topics/advanced/API.html

These documents will show you how the URLs are composed and how to select columns for cases that you want to download. If you add columns for downloading and you want them to be part of the schema loaded with populate.py, then you will need to edit the dicts related to those tables.

# LIMITATIONS and BUGS

Even though you can get kanban column details, there is no provision for downloading planner details. I have logged fogbugz case 60026168 to request changes to the API.

I have not seen any problems downloading 100 cases at a time but I have seen a HTTP 500 error when I accidentally tried downloading thousands of cases with one HTTP request.

There are a number of denormalizations in the data returned by various HTTP requests. When you read populate.py, you'll see places where a call is made to reinsertTable(). Those are attempts to insert rows into a referenced table with values that will be inserted into the referencing table (i.e., the following insertTable). Doing it this way allows populate.py to enable foreign key constraints.

    reinsertTableVerbose('PRIORITY'  , prio_missing_conf, [tkt], False)
    insertTableVerbose('TICKET'      , case_conf        , [tkt], False)

In this segment of the code, before a ticket (case) is inserted into the database, any missing PRIORITY rows are backfilled by the denormalized priority fields that are downloaded with a case.


If you inspect the JSON that is extracted for a case, you'll see these two key-value pairs:

      "ixPriority": 3,
      "sPriority": "Required"

If all priorities would be extracted with the listProrities command, then there would be no need to store sPriority on a case record. But there are some data that are not extractable in the obvious way. So, this "backpatching" method is necessary for some tables.
