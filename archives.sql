#! /bin/sh

createdb liststat

psql liststat <<EOF

BEGIN;

CREATE TABLE listarchive (
    project         text,
    netloc          text,
    name            text,
    email_addr      text,
    subject         text,
    archive_date    date,
    today_date      date,
    msg_blank_len   int,
    msg_quotes_len  int,
    msg_raw_len     int
);

COMMIT;
EOF
