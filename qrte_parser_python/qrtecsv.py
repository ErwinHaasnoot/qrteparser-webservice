import csv
        
def csvreader(file, compression=None):
    """
        Generator function that yields the lines from the csv file one by one as arrays
    """
    if compression is None:
        with open(file, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',',quotechar='"')
            for row in reader:
                yield row
                
def csvwriter(file, arr, compression=None):
    if compression is None:
        with open(file, 'a') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',quotechar='"')
            spamwriter.writerow(arr)

        