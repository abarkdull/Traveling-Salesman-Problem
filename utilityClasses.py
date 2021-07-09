import csv


# class used for storing distance info between locations
class DistanceDictionary:

    def __init__(self):

        self.myDict = {}
        self.locationArray = []

        # read data from csv file
        with open("DistanceTable.csv") as csvFile:
            readcsv = csv.reader(csvFile, delimiter=',')

            for row in readcsv:

                # assign first row to location array to use as a reference
                if row[0] == "":
                    self.locationArray = row
                else:
                    # current hub = current location on list
                    currentHub = row[0]
                    currentHubDict = {}

                    # for each distance in current row
                    for i in range(len(row)):

                        # Ignore first row
                        if len(row[i]) > 8:
                            continue

                        # key = current column header (location)
                        # value = current distance
                        else:
                            currentHubDict[self.locationArray[i]] = float(row[i])
                    self.myDict[currentHub] = currentHubDict


# class used for structuring packages
class Package:

    # list of all packages, used in load trucks method
    allPackages = []

    def __init__(self, packageId, address, city, state, zipcode, deliveryDeadline, mass, specialNotes):
        self.packageId = packageId
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.deliveryDeadline = deliveryDeadline
        self.mass = mass
        self.specialNotes = specialNotes
        self.deliveredTime = None
        self.leftHubTime = None
        self.truck = 0

    # returns list of all deliveries with a deadline
    def getDeadlineDeliveries():
        res = []
        for package in Package.allPackages:
            if package.deliveryDeadline != 'EOD':
                res.append(package)

        return res


# class used for storing packages in a hash table
class PackageHashTable:

    def __init__(self):
        self.packageHashTable = []
        for x in range(10):
            self.packageHashTable.append([])
        self.populateTable()

    # populates hash table from csv file
    def populateTable(self):
        with open('WGUPS_Package_File.csv') as csvFile:
            readcsv = csv.reader(csvFile, delimiter=',')\

            # for each row in csv
            for row in readcsv:

                # skip first row
                if len(row[0]) > 2:
                    continue

                # create package, insert package into hash table, and add to Package.allPackages list
                else:
                    package = Package(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                    Package.allPackages.append(package)
                    self.insert(package)

    # inserts package into hash table
    def insert(self, package):

        # hash the package id and get remainder of hash / the length of the hash table
        bucket = hash(package.packageId) % len(self.packageHashTable)

        # list inside bucket
        bucketList = self.packageHashTable[bucket]

        # append package to end of bucket list
        bucketList.append(package)

    # returns package object of packageId
    def lookup(self, packageId):
        bucket = hash(packageId) % len(self.packageHashTable)
        bucketList = self.packageHashTable[bucket]

        # for each package in the bucket list
        for package in bucketList:

            # if matching package is found, return the package
            if package.packageId == packageId:
                return package

        return None
