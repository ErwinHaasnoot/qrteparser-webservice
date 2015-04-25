import csv
import gzip

def csvreader(file):
    """
        Generator function that yields the lines from the csv file one by one as arrays
    """
    tokens = file.split('.')
    open_cmd = 'rbU'

    if tokens[-1] != 'csv' >= 2:
        compression = tokens[-1]
    else:
        compression = None

    if compression is None:
        print 'fuck yeaaah'
        with open(file, open_cmd) as csvfile:
            reader = csv.reader(csvfile, delimiter=',',quotechar='"')
            for row in reader:
                yield row

    elif compression == 'zip':
        with gzip.open(file, open_cmd) as csvfile:
            reader = csv.reader(csvfile, delimiter=',',quotechar='"')
            for row in reader:
                yield row

class csvwriter():
    """

    """
    writer = None
    writehandler = None
    @classmethod
    def open(cls,file):
        """

        :param file:
        :return:
        """
        cls.writehandler = gzip.open(file,'wb')
        cls.writer = csv.writer(cls.writehandler, delimiter=',',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

    @classmethod
    def write(cls,arr):
        """

        :param arr:
        :return:
        """
        cls.writer.writerow(arr)

    @classmethod
    def close(cls):
        """

        :return:
        """
        cls.writehandler.close()

        