from __future__ import print_function
from .unicode_csv_writer import UnicodeWriter, UnicodeReader
import csv
from .bufferedzipfile import EnhZipFile
import gzip
from .qrteexception import QRTEParserException

def csvreader(file):
    """
    Generator function that yield a given qualtrics datafile line by line.
    Can currently handle normal CSV and ZIP.
    :param file: filename of input file
    :return:
    """
    tokens = file.split('.')
    open_cmd = 'rU'

    if tokens[-1] != 'csv':
        compression = tokens[-1]
    else:
        compression = None

    if compression is None:
        with open(file, open_cmd) as csvfile:
            reader = UnicodeReader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                yield row


    elif compression == 'zip':
        # Buffered, line by line read of zip file
        zf = None
        try:
            with EnhZipFile(file) as zf:
                files = zf.namelist()
                if len(files) == 0:
                    raise QRTEParserException(code=QRTEParserException.ERR_ZIP_CONTAINS_NO_FILES,subject=None,ZipFile=file)

                if len(files) > 1:
                    raise QRTEParserException(code=QRTEParserException.ERR_ZIP_CONTAINS_TWO_OR_MORE_FILES,subject=None,ZipFile=file)
                with zf.open(files[0],open_cmd) as csvfile:
                    reader = UnicodeReader(csvfile, delimiter=',', quotechar='"')
                    for row in reader:
                        yield row
        except Exception as e:
            print(e)
            raise QRTEParserException(code=QRTEParserException.ERR_ZIP_INVALID,subject=None,ZipFile=file)

class csvwriter(object):

    MAXIMUM_FILE_SIZE = 524288000
    zip = None
    zipinfo = None
    writer = None
    filehandler = None
    @classmethod
    def open(cls,file):
        #cls.zip = EnhZipFile(file + '.zip',compression=zipfile.ZIP_DEFLATED,mode='w')

        #cls.zipinfo = zipfile.ZipInfo(os.path.basename(file),time.localtime()[:6])

        # cls.filehandler = cls.zip.start_entry(cls.zipinfo)
        cls.filehandler = gzip.open(file+'.gz','wt')
        # cls.filehandler = open(file,'wb')
        cls.writer = UnicodeWriter(cls.filehandler, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

    @classmethod
    def write(cls,arr):
        cls.writer.writerow(arr)

    @classmethod
    def close(cls):
        cls.filehandler.close()
        #cls.zip.close()
        