
from inspect import getframeinfo, stack
class QRTEParserLogger:
    LEVEL_SPAM = -1
    LEVEL_VERBOSE = 0
    LEVEL_SILENT = 1
    LEVEL_WARNING = 2
    LEVEL_ERROR = 3
    
    DEFAULT_LEVEL = 0
    LISTENING_THRESHOLD = 0
    def __init__(self, msg, level = None, stack_level = 0):
        caller = getframeinfo(stack()[1+stack_level][0])
        level = level or self.DEFAULT_LEVEL
        if level >= self.LISTENING_THRESHOLD:
            print "[%s:%d] %s" % (caller.filename, caller.lineno, msg)
    
    @classmethod
    def warning(cls,msg):
        cls(msg="[WARNING] %s" % msg,level = cls.LEVEL_WARNING, stack_level = 1)
    
    @classmethod
    def silent(cls,msg):
        cls(msg=msg, level=cls.LEVEL_SILENT, stack_level = 1) 
        
    @classmethod
    def spam(cls, msg):
        cls(msg=msg, level=cls.LEVEL_SPAM, stack_level = 1)
        
            

log = QRTEParserLogger        
 