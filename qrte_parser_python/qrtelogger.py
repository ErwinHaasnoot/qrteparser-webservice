from inspect import getframeinfo, stack
import sys

class QRTEParserLogger():
    LEVEL_SPAM = -1
    LEVEL_VERBOSE = 0
    LEVEL_SILENT = 1
    LEVEL_WARNING = 2
    LEVEL_ERROR = 3
    LEVEL_EXCEPTION = 4
    
    DEFAULT_LEVEL = 0
    LISTENING_THRESHOLD = 0

    OUT = sys.stdout

    def __init__(self, formatstr, vals = (), level = None, stack_level = 0):
        caller = getframeinfo(stack()[1+stack_level][0])
        level = level or self.DEFAULT_LEVEL
        if level >= self.LISTENING_THRESHOLD:
            msg = formatstr % vals
            self.OUT.write("[%s:%d] %s" % (caller.filename, caller.lineno, msg))
            self.OUT.flush()
            
    @classmethod
    def exception(cls,formatstr, vals = ()):
        cls(formatstr="[EXCEPTION][!!!!] " + formatstr, vals = vals,level = cls.LEVEL_EXCEPTION, stack_level = 1)
            
    @classmethod
    def error(cls,formatstr, vals = ()):
        cls(formatstr="[ERROR] " + formatstr, vals = vals,level=cls.LEVEL_ERROR, stack_level = 1)
    
    @classmethod
    def warning(cls,formatstr, vals = ()):
        cls(formatstr="[WARNING] " + formatstr, vals = vals,level = cls.LEVEL_WARNING, stack_level = 1)
    
    @classmethod
    def silent(cls,formatstr, vals = ()):
        cls(formatstr=formatstr, vals = vals, level=cls.LEVEL_SILENT, stack_level = 1)
        
    @classmethod
    def spam(cls, formatstr, vals = ()):
        cls(formatstr=formatstr, vals = vals, level=cls.LEVEL_SPAM, stack_level = 1)
        
            

log = QRTEParserLogger        
 