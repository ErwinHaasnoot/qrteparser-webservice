from qrte_parser_python import QRTEParser, QRTEParserLogger, log
import sys, os

def main(file = None, log_level = 0):
    log.silent('Initing parser on file: %s', file)
    if file is None:
        log.warning('Please run using the following: python parser.py path/to/file.name')
        exit()
        
    if not os.path.isfile(file):
        log.warning('File does not exist: %s', (file,))
        exit()
        
    if os.path.getsize(file) == 0:
        log.warning('Can\'t parse an empty file - %s',(file,))
        exit()
    QRTEParserLogger.LISTENING_THRESHOLD = 2
    QRTEParser.parse(file, outfile=file.split('.')[0]+'_out.csv ',exit_q_unique = False)

        

if __name__ == "__main__":
    main(*sys.argv[1:])