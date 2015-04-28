import csv
from bufferedzipfile import EnhZipFile
import gzip
import os
import zipfile
import StringIO
import time
from qrteexception import QRTEParserException

def csvreader(file):
    """
        Generator function that yields the lines from the csv file one by one as arrays
    """
    tokens = file.split('.')
    open_cmd = 'rU'

    if tokens[-1] != 'csv':
        compression = tokens[-1]
    else:
        compression = None

    if compression is None:
        with open(file, open_cmd + 'b') as csvfile:
            reader = csv.reader(csvfile, delimiter=',',quotechar='"')
            for row in reader:
                yield row

    elif compression == 'zip':
        zf = None
        try:
            with EnhZipFile(file) as zf:
                files = zf.namelist()
                if len(files) == 0:
                    raise QRTEParserException(code=QRTEParserException.ERR_ZIP_CONTAINS_NO_FILES,subject=None,ZipFile=file)

                if len(files) > 1:
                    raise QRTEParserException(code=QRTEParserException.ERR_ZIP_CONTAINS_TWO_OR_MORE_FILES,subject=None,ZipFile=file)
                with zf.open(files[0],open_cmd) as csvfile:
                    reader = csv.reader(csvfile, delimiter=',',quotechar='"')
                    for row in reader:
                        yield row
        except Exception as e:
            print e
            raise QRTEParserException(code=QRTEParserException.ERR_ZIP_INVALID,subject=None,ZipFile=file)

class csvwriter():

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
        cls.filehandler = open(file,'w')
        cls.writer = csv.writer(cls.filehandler, delimiter=',',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

    @classmethod
    def write(cls,arr):
        cls.writer.writerow(arr)

    @classmethod
    def close(cls):
        cls.filehandler.close()
        #cls.zip.close()
        