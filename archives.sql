#! /bin/sh

createdb teammetrics

psql teammetrics <<EOF

BEGIN;

CREATE TABLE listarchives (
    project             text,
    domain              text,
    name                text,
    email_addr          text,
    subject             text,
    archive_date        date,
    today_date          date,
    msg_raw_len         int,
    msg_no_blank_len    int,
    msg_no_quotes_len   int,
    msg_no_sig_len      int
);

CREATE TABLE gitstat (
    project             text,
    package             text,
    name                text,
    changes             int,
    lines_inserted      int,
    lines_deleted       int
);

CREATE TABLE listspam (
    project             text,
    name                text,
    email_addr          text,
    subject             text,
    reason              text
);

COMMIT;
EOF
