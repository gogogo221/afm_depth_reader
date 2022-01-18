# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 13:03:06 2022
@authors: Natalya Evans, Nathan Chan
This script is designed to extract the pin, depth, and time from auto-fire module files from Seabird systems, then concatenate that data into a single csv file
"""

# %% 1. Load relevant libraries
#This chunk gets all the pre-requisites out of the way for you
#Note that this code will overwrite the output file, so if there is already a file with output_name in the folder, it will be replaced
#This is the name of the file that this code outputs. The default is output_name='out.csv'
output_name='out.csv'
import os, fnmatch, csv, re
#%% 2. Create a list of btl files to iterate through
#This chunk identifies all the btl files in a folder then fills their names into a list, listOfFiles
listOfFiles = os.listdir('.') 
pattern = "*.afm" #filters what files get added into the listOfAFM list
listOfAFM = []
#gets a list of file names
for name in listOfFiles: #iterate through all files
    if fnmatch.fnmatch(name, pattern):
            name = name.lower()
            listOfAFM.append(name)

#%% 3. iterates through each file and scans for pin numbers; when it finds a pin number, it takes the next 5 lines of hex numbers and calculates depth
#saves the station, cast, pin, time, and depth into a list of dictionaries that will be exported into a csv
listOfAFM.sort(key=lambda f: int(re.sub('\D', '', f))) #sorts files based on numbers
total_data = [] #list to hold the data
for filename in listOfAFM:
    with open(filename) as file:
        for line in file:
            if line[0].isnumeric(): #check to see if file line holds important data
                listOfHex = []
                for i in range(5): #loop through the 5 hex and converts each to depth value
                    HexString = file.readline()
                    HexString = HexString.strip()
                    if "E+" in HexString:
                        HexString = HexString[ :HexString.find("E")]
                        HexString = HexString.replace(".", "")
                    else:
                        HexString = HexString[1:4]
                    HexString = "0x" + HexString
                    HexInt = int(HexString, 16)
                    HexInt -= 100
                    listOfHex.append(HexInt)
                line = line.split()
                dataDict = {} #dictionary to hold important information from each line
                #dataDict["File"] = filename[:filename.find(".")-len(filename)] (if uncommented out, need to add "File" to fieldnames)
                #adds values for each field into that field
                dataDict["Station"] = filename.split()[-1][0:filename.find(".")-len(filename)]                
                dataDict["Cast"] = filename.split()[1]
                dataDict["Pin"] = line[0]
                dataDict["Time"] = [s for s in line if ":" in s][0]
                dataDict["Depth"] = int(round(sum(listOfHex)/len(listOfHex), 0)) #averages the 5 trials and rounds to whole number
                total_data.append(dataDict)
                

#%% 4. outputs to a csv with "Station", "Cast",  "Pin", "Time", "Depth" as its field names
with open(output_name, "w") as outputFile:
    fieldnames = ["Station", "Cast",  "Pin", "Time", "Depth" ]
    writer = csv.DictWriter(outputFile, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()
    for row in total_data:
        writer.writerow(row)