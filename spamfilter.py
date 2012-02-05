#! /usr/bin/env python

"""Detect and remove spam using the filters specified in check_spam.

The following field patterns are treated as spam where 'field' indicates either
a 'Name' or a 'Subject' field:

    - matches the keywords specified by SPAM_KEYWORDS.
"""

SPAM_KEYWORDS = (
                'loan', 
                'lottery', 
                'Mail Delivery Subsystem',
                'Pls check this new site',
                'promotion', 
                'Tim.com.br',
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
        # Ignore the spam keywords specified.
        for ignore_name in SPAM_KEYWORDS:
            if ignore_name.lower() in field.lower():
                spam_detected = True
                reason = "Keyword '%s' in '%s'" % (ignore_name, fields[field])

    return name, subject, reason, spam_detected
