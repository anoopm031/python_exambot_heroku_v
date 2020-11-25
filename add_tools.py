def iscommand(text):
    if text.startswith('/'): return True
    else: return False

def isundo(text):
    if text=='/undo': return True
    else: return False

def iscancel(text):
    if text=='/cancel': return True
    else: return False

def isdone(text):
    if text=='/done': return True
    else: return False

def isstart(text):
    if text=='/start': return True
    else: return False

def ishelp(text):
    if text=='/help': return True
    else: return False


def isskip(text):
    if text=='/skip': return True
    else: return False



