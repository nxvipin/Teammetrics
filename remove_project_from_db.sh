#!/bin/sh
#set -x
if [ $# != 1 ] ; then
	echo "Usage: $0 <list|url>"
	exit 1
fi

PRJCOUNT=`psql teammetrics --tuples-only --command "SELECT COUNT(*) FROM listarchives WHERE project='$1' ;"`
if [ $PRJCOUNT = 0 ] ; then
    # no such project found - check for a domain to remove
    DOMCOUNT=`psql teammetrics --tuples-only --command "SELECT COUNT(*) FROM listarchives WHERE domain='$1' ;"`
    if [ $DOMCOUNT = 0 ] ; then
        # no such project found - check for a commits to remove
	COMCOUNT=`psql teammetrics --tuples-only --command "SELECT COUNT(*) FROM commitstat WHERE project='$1' ;"`
	if [ $COMCOUNT = 0 ] ; then
	    if grep -q $1 /etc/teammetrics/commitinfo.conf /etc/teammetrics/listinfo.conf ; then
		echo "The project $1 was found in configuration files but we do not have data in the DB"
		exit 0
	    else
		echo "Unknown project $1."
	    fi
	else
    	    echo "There are $DOMCOUNT commits known for project $1.  Just fix this script if these should be deleted."
	    exit 0
	fi
    else
	psql teammetrics --tuples-only <<EOT
  BEGIN ;
  -- Delete all SPAM obtained from this domain
  DELETE FROM listspam WHERE project IN
      (SELECT project FROM listarchives WHERE domain='$1' GROUP BY project) ;
  DELETE FROM listarchives WHERE domain='$1';
  COMMIT;
EOT
	exit 0
    fi
else
    psql teammetrics --tuples-only --command "BEGIN; DELETE FROM listarchives WHERE project='$1' ; DELETE FROM listspam WHERE project='$1' ; COMMIT;"
    exit 0
fi
