"""
Austin Barkdull
S02601711
"""
import datetime

from utilityClasses import PackageHashTable, DistanceDictionary, Package

from datetime import datetime, timedelta

# global variable to track total mileage
totalMileageStatic = 0

# main controller method
def main():

    PackageHashTable()

    # load truck and deliver package
    # returns list of packages, after day is complete
    deliveryResult = loadTrucksAndDeliver()

    # Time of day values to satisfy requirements G1 - G3
    earlyTime = datetime(2021, 5, 13, 8, 50, 00)
    midTime = datetime(2021, 5, 13, 10, 0, 00)
    lateTime = datetime(2021, 5, 13, 12, 5, 00)

    printOptions(earlyTime, midTime, lateTime)
    userInput = int(input("Select an option: "))
    while userInput != 6:

        if userInput == 1:
            getTimeStatus(deliveryResult, earlyTime)
        elif userInput == 2:
            getTimeStatus(deliveryResult, midTime)
        elif userInput == 3:
            getTimeStatus(deliveryResult, lateTime)
        elif userInput == 4:
            printDeliveryResult(deliveryResult)
        elif userInput == 5:
            print('Total mileage:', round(totalMileageStatic, 1))
        else:
            print('Invalid input')

        printOptions(earlyTime, midTime, lateTime)
        userInput = int(input("Select an option: "))


# print options menu
def printOptions(earlyTime, midTime, lateTime):
    print()
    print('---------------------------------------------------')
    print('1. Delivery status at', earlyTime.strftime("%H:%M %p"))
    print('2. Delivery status at', midTime.strftime("%H:%M %p"))
    print('3. Delivery status at', lateTime.strftime("%H:%M %p"))
    print('4. End of day delivery results')
    print('5. Total mileage')
    print('6. Exit')
    print('---------------------------------------------------')

    print()


# Greedy algorithm to order packages into trucks based on delivery deadline and nearest neighbor
# Time complexity: O(n^3), function contains 3 nested loops (while -> for -> for) hence a worst case of n^3
# Space complexity: O(n)
def loadTrucksAndDeliver():

    truck = []

    # Nested dictionary ( {key : {}} ) containing distances between each location for every location
    distanceTable = DistanceDictionary()
    distanceTable = distanceTable.myDict

    # start at WGU Hub
    currentHubNextLocations = distanceTable['Western Governors University\n4001 South 700 East \nSalt Lake City UT 84107']
    numFound = 0

    # while there are packages with deadlines still to be loaded
    while len(Package.getDeadlineDeliveries()) != 0:
        found = False

        # sort the locations in the current hub by distance (lowest -> highest)
        # example:
        # if wgu is the current hub, currentHubNextLocations = {wgu: 0, international peace garderns: 7.2, sugar hours park: 3.8...}
        # after running the next line, currentHubNextLocations = {wgu:0, cottonwood regional softball: 1.9, housing auth. of salt lake: 2.0...}
        currentHubNextLocations = {hub: distance for hub, distance in sorted(currentHubNextLocations.items(), key=lambda item: item[1])}

        # for each possible next location after the current hub
        for nextLocation in currentHubNextLocations:

            # Skip the location if same as current hub (i.e. at the same location)
            if currentHubNextLocations[nextLocation] == 0.0:
                continue

            # for each package with a deadline
            for package in Package.getDeadlineDeliveries():

                # if the package is to be delivered to the nextLocation,
                # load the package on the truck (at the end)
                # remove package from allPackages list to keep track of
                # packages still needing to be loaded
                if package.address in nextLocation:
                    numFound += 1
                    truck.append(package)
                    Package.allPackages.remove(package)
                    found = True

            # if a package was found for the next nearest location,
            # change currentHub to nextLocation and repeat
            if found:
                currentHubNextLocations = distanceTable[nextLocation]
                break

    # currentHub = location of last package on truck
    currentHubNextLocations = distanceTable[getHub(truck[-1].address, distanceTable)]

    # while packages are still left to be loaded on a truck
    while len(Package.allPackages) != 0:

        found = False

        # sort the locations in the current hub by distance (lowest -> highest)
        currentHubNextLocations = {hub: distance for hub, distance in
                                   sorted(currentHubNextLocations.items(), key=lambda item: item[1])}

        # for each possible next location after the current hub
        for nextLocation in currentHubNextLocations:
            if currentHubNextLocations[nextLocation] == 0.0:
                continue

            # for each remaining package
            for package in Package.allPackages:

                # if the package is to be delivered to the nextLocation,
                # load the package on the truck (at the end)
                # remove package from allPackages list to keep track of
                # packages still needing to be loaded
                if package.address in nextLocation:
                    numFound += 1
                    truck.append(package)
                    Package.allPackages.remove(package)
                    found = True

            # if a package was found for the next nearest location,
            # change currentHub to nextLocation and repeat loop
            if found:
                currentHubNextLocations = distanceTable[nextLocation]
                break

    # divide loaded packages among 3 trucks
    truck1 = truck[0:16]
    truck2 = truck[16:33]
    truck3 = truck[33:]

    # handle packages with special reuests and assign each package its corresponding truck
    handleSpecialRequest(truck, truck1, truck2, truck3)
    assignPackageToTruck(truck1 + truck2 + truck3)

    # return loaded trucks
    return makeDeliveries(truck1, truck2, truck3)


# Assign package data value to track which package is on which truck
# Time complexity = O(n)
# Space complexity = O(1)
def assignPackageToTruck(truck):

    # for each package
    for i in range(len(truck)):
        # if truck 1, package.truck = 1
        if i < 16:
            truck[i].truck = 1
        # if truck 3, package.truck = 3
        elif i >= 33:
            truck[i].truck = 3
        # if truck 2, package.truck = 2
        else:
            truck[i].truck = 2


# (Non self-adjusting)
# deliver packages,
# track mileage, delivery times, hub departure times, and return list of all packages
# time complexity: O(n^2)
# space complexity: O(n)
def makeDeliveries(truck1, truck2, truck3):
    distanceTable = DistanceDictionary()
    distanceTable = distanceTable.myDict

    # Start time for truck 1 and 2 is 8:00 AM
    truck1Time = datetime(2021, 5, 13, 8, 00, 00)
    truck2Time = datetime(2021, 5, 13, 8, 00, 00)

    truck1Mileage = 0

    # Start at WGU
    currentHub = distanceTable['Western Governors University\n4001 South 700 East \nSalt Lake City UT 84107']

    # for each package in truck 1
    for package in truck1:

        # If package is delayed, set the hub departure time to 9:05 AM
        if 'Delayed' in package.specialNotes:
            package.leftHubTime = datetime(2021, 5, 13, 9, 5, 00)

        # If package is not delayed, set hub departure time to 8:00 AM
        else:
            package.leftHubTime = datetime(2021, 5, 13, 8, 00, 00)

        # (Non self-adjusting portion)
        # if package id is 25 (delayed on flight and has a deadline)
        # return to wgu to pick up packages (25 and 6)
        # continue delivering packages
        if package.packageId == '25':
            nextHub = 'Western Governors University\n4001 South 700 East \nSalt Lake City UT 84107'
            mileage = currentHub[nextHub]
            duration = (mileage / 18) * 60
            newTime = timedelta(minutes=duration)
            truck1Time = truck1Time + newTime
            package.deliveredTime = truck1Time
            truck1Mileage += mileage
            currentHub = distanceTable[nextHub]
            continue

        # set next hub to current packages address
        packageAddress = package.address
        nextHub = getHub(packageAddress, distanceTable)  # time complexity O(n)

        # miles to next location from current location
        mileage = currentHub[nextHub]

        # amount of time to drive to next location (18 mph)
        duration = (mileage / 18) * 60

        # add curation to truck 1's time
        newTime = timedelta(minutes=duration)
        truck1Time = truck1Time + newTime

        # set package delivery time and increment truck 1s total mileage
        package.deliveredTime = truck1Time
        truck1Mileage += mileage

        # assign current hub to the next location
        currentHub = distanceTable[nextHub]

    # Truck 1 driver returns to pick up truck 3
    truck1Mileage += currentHub['Western Governors University\n4001 South 700 East \nSalt Lake City UT 84107']

    # call method to deliver packages in trucks 2 and 3
    # unable to use this method for truck 1 as
    # truck 1 had special cases that needed to be manually handled.
    truck2Mileage = deliverTrucks(truck2, truck2Time)
    truck3Mileage = deliverTrucks(truck3, truck1Time)

    global totalMileageStatic
    totalMileageStatic = truck1Mileage + truck2Mileage + truck3Mileage

    # print results
    print('\nDeliveries complete...\n')

    # return all packages
    return truck1 + truck2 + truck3


# (Self-adjusting) could be used for any truck starting out at WGU
# deliver trucks
# see above for algo. explanation
# time complexity: O(n^2)
# space complexity: O(n)
def deliverTrucks(truck, truckTime):
    distanceTable = DistanceDictionary()
    distanceTable = distanceTable.myDict
    totalMileage = 0
    startTruckTime = truckTime
    currentHub = distanceTable['Western Governors University\n4001 South 700 East \nSalt Lake City UT 84107']
    for package in truck:
        package.leftHubTime = startTruckTime
        packageAddress = package.address
        nextHub = getHub(packageAddress, distanceTable)  # time complexity = O(n)
        mileage = currentHub[nextHub]
        duration = (mileage / 18) * 60
        newTime = timedelta(minutes=duration)
        truckTime = truckTime + newTime
        package.deliveredTime = truckTime
        totalMileage += mileage
        currentHub = distanceTable[nextHub]

    return totalMileage


# (Self-adjusting) could be used for any list of packages
# get status of packages at given time of day
# time complexity: O(n)
# space complexity: O(n)
def getTimeStatus(packages, currentTime):
    # sort packages by package id
    packages = sorted(packages, key=lambda x: int(x.packageId))

    print('\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print('++                  ALL PACKAGES AS OF', currentTime.strftime("%H:%M %p"), '                 ++')
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

    # for each package
    for package in packages:

        # if package has already been delivered
        if package.deliveredTime < currentTime:
            print(package.packageId, '|', package.address, '|', 'Deadline:', package.deliveryDeadline, '|',
                  'Delivered:', package.deliveredTime.strftime("%H:%M %p"))

        # if package is sill at hub
        elif package.leftHubTime > currentTime:
            print(package.packageId, '|', package.address, '|', 'Deadline:', package.deliveryDeadline, '|',
                  'At hub')

        # package is en route
        else:
            print(package.packageId, '|', package.address, '|', 'Deadline:', package.deliveryDeadline, '|',
                  'En Route - Truck', package.truck)


# Helper method used for debugging
def printTrucks(truck1, truck2, truck3):
    truck = []
    for package in truck1:
        print(package.packageId, end=' , ')
        truck.append(int(package.packageId))
    print()
    for package in truck2:
        print(package.packageId, end=' , ')
        truck.append(int(package.packageId))

    print()
    for package in truck3:
        print(package.packageId, end=' , ')
        truck.append(int(package.packageId))

    print()
    print(truck)


# prints results of all deliveries at EOD
# time complexity: O(n)
# space complexity: O(n)
def printDeliveryResult(truck):
    # Sort packages in truck by package
    truck = sorted(truck, key=lambda x: int(x.packageId), reverse=False)

    print('\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print('++                  ALL PACKAGES AS OF COB                       ++')
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

    total = 0

    # for each package
    for package in truck:
        total += 1

        # print package details and delivery time
        print(package.packageId, '|', package.address, '|', package.city, '|', package.state, '|', package.zipcode, '|',
              'Mass (kg):', package.mass, '|', 'Deadline:', package.deliveryDeadline, '|', 'Delivered:',
              package.deliveredTime.strftime("%H:%M %p"))

    # print total # of packages delivered
    print('Total packages delivered:', total)


# (Non self-adjusting)
# handles special requests for each package
# in future implementations, developers will need to
# tweak this portion of the code to adhere to their
# specific task
# Time complexity: O(n^2)
# space complexity: O(n)
def handleSpecialRequest(truck, truck1, truck2, truck3):
    # for each package
    for package in truck:

        # if package has wrong address (i.e. package 9)
        if 'Wrong address' in package.specialNotes:

            # assign packages address to correct address
            ind = truck.index(package)
            package.address = '410 S State St'

        # if package con only be on truck 2
        elif 'Can only be on truck 2' in package.specialNotes:

            packageIndex = truck.index(package)

            # if package is not on truck 2
            if packageIndex < 16 or packageIndex > 32:

                # for each package on truck 2
                for i in range(len(truck2)):

                    # if package on truck 2 has no special notes, switch that
                    # package with current package and add package on truck 2
                    # to end of truck 3
                    if len(truck2[i].specialNotes) == 0:
                        truck3.append(truck2[i])
                        temp = package
                        truck3.remove(package)
                        truck2[i] = temp
                        break

        # if package is delayed
        elif 'Delayed' in package.specialNotes:

            packageIndex = truck.index(package)

            # if package does not have a deadline
            if package.deliveryDeadline == 'EOD':

                # if package is on truck 2, remove from truck 2 and add to truck 3
                if packageIndex < 33 and packageIndex > 16:
                    truck2.remove(package)
                    truck3.append(package)

                # if package is on truck 1, remove from truck 1 and add to truck 3
                elif packageIndex < 16:
                    truck1.remove(package)
                    truck3.append(package)

            # if package has a deadline, move package to end of truck 1
            else:
                truck1.remove(package)
                truck1.append(package)

        # if package 19, insert package at 3rd from last position on truck1
        # remove package 27 from truck 1 and add to end of truck 2
        elif package.packageId == '19':

            packHashTable = PackageHashTable()
            truck1.insert(-2, package)
            truck2.remove(package)
            truck2.append(packHashTable.lookup(packageId='27'))
            for pack in truck1:
                if pack.packageId == '27':
                    truck1.remove(pack)


# returns the hub key of a given package's address
# necessary as package address' only contain part of
# the location key (ex. package 8s address = 300 state st.,
# however, the location key is "Council Hall 300 State St")
# time complexity: O(n)
# space complexity: O(1)
def getHub(address, distanceDict):
    for item in distanceDict.keys():
        if address in item:
            return item
    return None


main()
