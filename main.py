import csv
import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl


class Boat:
    def __init__(self,path, csvpath, ThresholdHours):
        self.name = csvpath
        self.tasks = []
        self.trips = []
        self.startHarbour = None
        self.endHarbour = None
        #Handle tasks
        with open((path + csvpath), "r") as self.csv_file:
            next(self.csv_file)  # Skip the first line so we don't get the headers
            self.reader = csv.reader(self.csv_file, delimiter=',')
            for row in self.reader:
                self.tasks.append(Task(row[2], row[3], row[4], row[5], row[6], row[1]))
        self.tasks.sort(key=lambda x: x.startTime)  # Sort the list after StartTime.
        threshold = datetime.timedelta(hours=ThresholdHours)  # if less than 2 hours between tasks count it as the same Trip
        #Handle trips
        i = 0
        while i < (int(len(self.tasks) - 1)):
            self.startTime = self.tasks[i].startTime
            self.endTime = self.tasks[i].endTime
            if self.startHarbour is None:
                self.startHarbour = self.tasks[i].startHarbour
            if self.endHarbour is None:
                self.endHarbour = self.tasks[i].endHarbour
            self.distance = float(self.tasks[i].distance)
            self.routes = [self.tasks[i]]
            while threshold > (self.tasks[i + 1].startTime - self.tasks[i].endTime):
                i += 1
                self.distance += float(self.tasks[i].distance)
                self.routes.append(self.tasks[i])
                self.endTime = self.tasks[i].endTime
                self.endHarbour = self.tasks[i].endHarbour
                if (i+1) == len(self.tasks):
                    break
            i += 1
            self.trips.append(
                Trip(
                    self.startTime, self.endTime, self.distance, self.startHarbour, self.endHarbour, self.routes
                )
            )


class Task:
    def __init__(self, var1, var2, var3, var4, var5, var6):
        self.startHarbour = var1
        self.endHarbour = var2
        self.startTime = datetime.datetime.strptime(var3, '%Y-%m-%d %H:%M:%S')
        self.endTime = datetime.datetime.strptime(var4, '%Y-%m-%d %H:%M:%S')
        self.distance = var5
        self.routeId = var6
    def print(self):
        print("StartHarbour: " + self.startHarbour)
        print("endHarbour: " + self.endHarbour)
        print("startTime: " + str(self.startTime))
        print("endTime: " + str(self.endTime))
        print("distance: " + self.distance)
        print("routeID: " + self.routeId)


class Trip:
    def __init__(self, startTime, endTime, distance, startHarbour, endHarbour, routes):
        self.startTime = startTime
        self.endTime = endTime
        self.distance = distance
        self.startHarbour = startHarbour
        self.endHarbour = endHarbour
        self.routes = routes
        self.tripTime = endTime-startTime

    def correctTripTime(self):
        if not (self.tripTime == (self.routes[-1].endTime - self.routes[0].startTime)):
            print("Corrected time from: " + self.tripTime)
            print("New time: " + (self.routes[-1].endTime - self.routes[0].startTime))
            self.tripTime = (self.routes[-1].endTime - self.routes[0].startTime)

def plotHistogram(boats):
        #Split up trips in length
        x = []
        for b in boats:
            for trip in b.trips:
                x.append(trip.distance)
        #Plot graph
        plt.hist(x, bins=len(x), color='orange',density=True, histtype=u'step', cumulative=True)
        plt.yticks(np.arange(0,1, 0.05))
        plt.xlabel("Sjömil")
        plt.ylabel("Andel av uppdrag")
        plt.axvline(x=55, color='r')
        plt.savefig("histogram.png")
        plt.show()

def plotHeatmap(boats):
    x=[]
    y=[]
    for b in boats:
        for trip in b.trips:
            x.append(trip.tripTime.seconds / (60 * 60))
            y.append(trip.distance)
    plt.hexbin(x, y, norm=mpl.colors.LogNorm(), cmap=mpl.cm.inferno)
    plt.xlabel("Timmar:")
    plt.ylabel("Distanser:")
    plt.savefig("Heatmap.png")
    plt.show()

def __main__():
    path = "/Users/jakob/Documents/SSRS/"
    csvs = []
    maxDistance = 55
    for file in os.listdir(path):
        if file.endswith(".csv"):
            csvs.append(file)
    boats = []

    for c in csvs:
        boats.append(Boat(path, c, 2))
    boatsWithinTreshold = []
    for b in boats:
        tripCount = 0
        for t in b.trips:
            if t.distance < maxDistance:
                tripCount += 1
        withinTreshold = float(tripCount) / float(len(b.trips))
        if withinTreshold > 0.95:
            boatsWithinTreshold.append(b)

    #Used if you want to export a list of boats within threshold
    boatsWithinTreshold.sort(key=lambda x: len(x.trips), reverse=True)

    plotHistogram(boats)
    plotHeatmap(boats)


if __name__ == '__main__':
    __main__()