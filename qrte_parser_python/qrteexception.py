class QRTEParserException(Exception):
    
    ERR_UNKNOWN = -1
    ERR_NONE = 0
    
    ERR_MSG = {
        ERR_UNKNOWN: 'ER_UKNOWN',
        ERR_NONE: 'ERR_NONE',
    }
    
    
    def __init__(self, code = -1, message = '', verbose_message = ''):
        super(QRTEParserException,self).__init__(QRTEParserException.ERR_MSG[code])
        self.code = code
        self.verbose_message = verbose_message