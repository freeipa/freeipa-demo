import logging

def yes_no(question, unattended, default='y'):
    if unattended:
        reply = default
    else:
        reply = str(input('{} (y/n): '.format(question))).lower().strip()
    if reply[0] == 'y':
        return True
    return False

def configure_logger(debug):
    logger = logging.getLogger('demo1.freeipa.org')
    logger.setLevel(logging.WARNING)
    if debug:
        logger.setLevel(logging.DEBUG)
        level = logging.DEBUG
    else:
        level = logging.WARNING

    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
