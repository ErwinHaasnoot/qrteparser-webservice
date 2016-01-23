from .qrtemarkupnode import QRTEMarkUpNode

"""
    Main file for the QRTE Python Parser.
    
"""


class QRTEParser():
    headers = []

    @classmethod
    def parse(parser, file, outfile=None, exit_q_unique=True, entrance='CLI', version='2'):
        # TODO: Wrap in try/except block
        parser = QRTEParser(file, outfile, exit_q_unique)
        parser._parse(version=version, entrance=entrance)

    def __init__(self, file, outfile, exit_q_unique):
        self.file = file
        self.outfile = outfile or file + '_out'
        self.headers = []
        self.exit_q_unique = exit_q_unique

    def _parse(self, version, entrance):
        node = QRTEMarkUpNode.create(self.file, self.exit_q_unique)
        # Add version information
        node.data['Parser[Version]'] = version
        node.data['Parser[Type'] = entrance
        node.write_data(self.file, self.outfile)


if __name__ == "__main__":
    print('Cannot run directly')
    exit()
