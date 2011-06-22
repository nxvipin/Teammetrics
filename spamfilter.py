#! /usr/bin/env python

"""Detect and remove spam using the filters specified in check_spam."""

import logging

SPAM_KEYWORDS = ('lottery', 'promotion', 'loan', 'Mr', 'Mrs', 'Dr', '.com', '.net')


def check_spam(name, subject):
    """This function checks the name and subject fields for spam patterns.
    
    A string 'reason' is also returned which indicates the reason the field was
    labelled as spam. This is used to identify false positives (if any).
    """

    reason = ''
    logging_msg = 'Spam detected: %s' 
    return_items = name, subject, reason

    fields = {name: 'Name', subject: 'Subject'}
    
    for field, name in fields.iteritems():
        # If the name starts with a =.
        if field.startswith('='):
            reason = "%s starts with '='" % fields[field]
            logging.info(logging_msg % reason)

        # If the name is in capital letters only.
        elif field.isupper():
            reason = '%s is in upper case' % fields[field]
            logging.info(logging_msg % reason)

        elif field.isdigit():
            reason = '%s is all digits' % fields[field]
            logging.info(logging_msg % reason)

        for ignore_name in SPAM_KEYWORDS:
            if ignore_name in field:
                reason = 'Ignored keyword in %s: %s' % (fields[field], ignore_name)
                logging.info(logging_msg % reason)

    return name, subject, reason
