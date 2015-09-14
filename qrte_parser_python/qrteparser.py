from __future__ import print_function
from builtins import object
from .qrtelogger import QRTEParserLogger,log
from .qrtemarkupnode import QRTEMarkUpNode

"""
    Main file for the QRTE Python Parser.
    
"""
        
class QRTEParser(object):
    
    headers = []
    
    @classmethod
    def parse(parser,file, outfile = None, exit_q_unique = True):
        
        # TODO: Wrap in try/except block
        parser = QRTEParser(file,outfile,exit_q_unique)
        parser._parse()
        
    
    def __init__(self, file, outfile, exit_q_unique):
        self.file = file
        self.outfile = outfile  or file + '_out'
        self.headers = []
        self.exit_q_unique = exit_q_unique

    def _parse(self):

        node = QRTEMarkUpNode.create(self.file, self.exit_q_unique)
        node.write_data(self.file, self.outfile)
        
        
        
if __name__ == "__main__":
    print('Cannot run directly')
    exit()