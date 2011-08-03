#! /usr/bin/env python

"""Detect and remove spam using the filters specified in check_spam.

The following field patterns are treated as spam where 'field' indicates either
a 'Name' or a 'Subject' field:

    - empty,
    - starting with an equal-to sign,
    - all in upper case,
    - all digits,
    - matches the keywords specified by SPAM_KEYWORDS.
"""

import logging

SPAM_KEYWORDS = (
                'lottery', 
                'promotion', 
                'loan', 
                'Mail Delivery Subsystem'
                )


def check_spam(name, subject):
    """This function checks the field and subject fields for spam patterns.
    
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
        # An empty field is spam.
        if not field:
            spam_detected = True
            reason = "%s is an empty field" % fields[field]
            logging.warning(logging_msg % reason)

        # If the field starts with a =.
        if field.startswith('='):
            spam_detected = True
            reason = "%s starts with '='" % fields[field]
            logging.warning(logging_msg % reason)

        # If the field is in capital letters only.
        if field.isupper():
            spam_detected = True
            reason = '%s is in upper case' % fields[field]
            logging.warning(logging_msg % reason)

        # If the field is all digits.
        if field.isdigit():
            spam_detected = True
            reason = '%s is all digits' % fields[field]
            logging.warning(logging_msg % reason)

        # Ignore the spam keywords specified.
        for ignore_name in SPAM_KEYWORDS:
            if ignore_name in field:
                spam_detected = True
                reason = 'Ignored keyword in %s: %s' % (fields[field], ignore_name)
                logging.warning(logging_msg % reason)

    return name, subject, reason, spam_detected
