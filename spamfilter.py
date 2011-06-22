#! /usr/bin/env python

"""Detect and remove spam using the filters specified in check_spam."""

import logging

SPAM_KEYWORDS = ('lottery', 'promotion', 'loan')


def check_spam(name, subject):
    """This function checks the name and subject fields for spam patterns.
    
    A string 'reason' is also returned which indicates the reason the field was
    labelled as spam. This is used to identify false positives (if any).
    """

    reason = ''
    spam_detected = False
    logging_msg = 'Spam detected: %s' 
    name_field = name
    subject_field = subject

    fields = {name_field: 'Name', subject_field: 'Subject'}
    
    for field, value in fields.iteritems():
        # An empty name is spam.
        if not field:
            spam_detected = True
            reason = "%s is an empty field" % fields[field]
            logging.warning(logging_msg % reason)

        # If the name starts with a =.
        if field.startswith('='):
            spam_detected = True
            reason = "%s starts with '='" % fields[field]
            logging.warning(logging_msg % reason)

        # If the name is in capital letters only.
        if field.isupper():
            spam_detected = True
            reason = '%s is in upper case' % fields[field]
            logging.warning(logging_msg % reason)

        # If the name is all digits.
        if field.isdigit():
            spam_detected = True
            reason = '%s is all digits' % fields[field]
            logging.warning(logging_msg % reason)

        for ignore_name in SPAM_KEYWORDS:
            if ignore_name in field:
                spam_detected = True
                reason = 'Ignored keyword in %s: %s' % (fields[field], ignore_name)
                logging.warning(logging_msg % reason)

    return name, subject, reason, spam_detected
