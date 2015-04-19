import csv
        
def csvreader(file):
        """
            Generator function that returns the lines from the csv file one by one
        """
        with open(file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',',quotechar='"')
            for row in spamreader:
                yield row
                
def csvwriter(file, arr):
    with open(file, 'a') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',quotechar='"')
        spamwriter.writerow(arr)
        