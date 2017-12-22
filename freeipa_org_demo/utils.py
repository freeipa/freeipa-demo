def yes_no(question, unattended, default='y'):
    if unattended:
        reply = default
    else:
        reply = str(input('{} (y/n): '.format(question))).lower().strip()
    if reply[0] == 'y':
        return True
    return False

