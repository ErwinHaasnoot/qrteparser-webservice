from qrtelogger import QRTEParserLogger,log
from qrtemarkupnode import QRTEMarkUpNode

"""
    Main file for the QRTE Python Parser.
    
"""
        
class QRTEParser:
    
    headers = []
    
    @classmethod
    def parse(parser,file):
        
        # TODO: Wrap in try/except block
        parser = QRTEParser(file)
        parser._parse()
        
    
    def __init__(self, file):
        self.file = file
        self.headers = []
        
        
    def _parse(self):
        
        node = QRTEMarkUpNode.create(self.file)
        node.writeData(self.file, postfix = '_out')
        
        
        
if __name__ == "__main__":
    QRTEParserLogger.LISTENING_THRESHOLD = 1
    QRTEParser.parse('static/in/QRTE_Masked_Priming.csv')