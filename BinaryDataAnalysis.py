# -*- coding: utf-8 -*-

import os

BANNER = \
"""
         _   _
        (q\_/p)
         /. .\         __
  ,__   =\_t_/=      .'o O'-.
     )   /   \      / O o_.-`|   _   _
    (   ((   ))    /O_.-'  O |  (q\_/p)
     \  /\) (/\    | o   o  o|   /. .\.-´´´´´ -.     ___,
      `-\  Y  /    |o   o O.-`  =\_t_/=     /  `\  (
         nn^nn     | O _.-'       )\ ))__ __\   |___)
                   '--`          (/-(/`  `nn---'                                                                        
"""


FOLDER_WITH_BFthinned_FILES = "./Datos/"


class BehaviourFile:
    """
    This class contains the information needed from the Bthinned and Fthinned files in order to do the analysis. The following constants can be modified as desired
    to process the data as you prefer
    """
    
    SECONDS_PREVIOUS_TO_ONEs_BURST = 10 # Seconds previously to a 1s burst in order to get the amount of 0s. Set to -1 to get all the 0s
    TIMESTAMP_STEP = 0.1 # Timestamp incrementation (in seconds). By default, data is collected each 0.1s    
    MAX_0s_TO_EXPORT = SECONDS_PREVIOUS_TO_ONEs_BURST / TIMESTAMP_STEP # Maximun number of 0s to export into the csv file    
    
    VALUES_CONSIDER_AS_ONES = ["1"] # If you want to consider also 0.5 as "1" just copy and replace the line with this> VALUES_CONSIDER_AS_ONES = ["1", "0.5"]
    
    START_ROW = 10 #Row from the Bthinned and Fthinned files where start getting the data (to avoid the first erroneous data)
    BINARY_DATA_COLUMN_FOR_B_THINNED_FILES = 9 #Column from Bthinned file which have the binary data
    TIMESTAMP_DATA_COLUMN_FOR_F_THINNED_FILES = 0 #Column from Fthinned which have the timestamp
    ACTIVITY_DATA_COLUMN_FOR_F_THINNED_FILES = 1 #Column from Fthinned which have the activity data
    
    
    
    """
    <Class constructor> It initializes the data needed for the analysis.
    
    <bFile> Bthinned file route
    <fFile> Fthinned file route
    
    <contentBFile> The content of the Bthinned file. It contains an array per row
    <contentFFile> The content of the Fthinned file. It contains an array per row
    
    <binaryData> Binary data from the Bthinned file. An array of 0, 1 or even 0.5 (by default consider as a 0)
    <timestamp> Timestamp of collected data. An array with the different timestamps
    <activityData> Activity data from Fthinned file. An array with the different values
    
    <unifyData> An array of dictionaries to combine the previously data collected from Bthinned and Fthinned files. It has the following data per position: 
        
                "position" : from 0 to len(contentBFile) or len(contentFFile) as both files has the same length
                "binaryData" : 0, 0.5 or 1
                "timestamp" : timestamps values
                "activity" : activity values
        
    <onesBursts> An array of arrays. Each of the arrays represents a burst of 1s continuous in time. Each position of the array contains a dictionary with the unifyData values.
    <zerosBurst> An array of arrays. Each of the arrays represents a burst of 0s continuous in time previous to a 1s burst. Each position of the array contains a dictionary with the unifyData values.
    
    """
    def __init__(self):    
        
        self.bFile, self.fFile = self.GetFilesFromPath()
        
        self.contentBFile = self.GetDataFromFile(self.bFile)
        self.contentFFile = self.GetDataFromFile(self.fFile)    
        
        self.binaryData = self.GetColumnData(self.BINARY_DATA_COLUMN_FOR_B_THINNED_FILES, self.contentBFile)
        self.timestamp = self.GetColumnData(self.TIMESTAMP_DATA_COLUMN_FOR_F_THINNED_FILES, self.contentFFile)
        self.activityData = self.GetColumnData(self.ACTIVITY_DATA_COLUMN_FOR_F_THINNED_FILES, self.contentFFile)
        
        self.unifyData = self.UnifyData()        
        self.onesBursts = self.FindOnesBursts()
        self.zerosBurst = self.AdjustZerosBurstsLength(self.FindZerosBurst())        
        
    
    """
    Method to get the route to the Fthinned and Bthinned files
    """
    def GetFilesFromPath(self):
        bfileName = ""
        fFileName = ""
        
        folderWithFiles = os.listdir(FOLDER_WITH_BFthinned_FILES)
        
        for file in folderWithFiles:
            
            fileName = file.split('.')[0]
                
            if fileName == 'B-thinned':
                bfileName = FOLDER_WITH_BFthinned_FILES + file
                    
            elif fileName == "F-thinned":
                fFileName = FOLDER_WITH_BFthinned_FILES + file

        return bfileName, fFileName        


    """
    Method to read the data from a file
    """
    def GetDataFromFile(self, file: str):
        dataset = []

        with open(file, "r") as openedFile: 
            lines = openedFile.readlines()
        

        for line in lines: 
            line = line.split("\n")[0]
            dataset.append(line.split("\t"))

        dataset = dataset[self.START_ROW::] #Get the data fom the START_ROW row in advance
        
        return dataset
        
    
    """
    Method to get all data in a specified column from a specified file
    """
    def GetColumnData(self, column: int, fileContent: str):
        data = []
        
        for row in fileContent: 
            data.append(row[column])
            
        return data

    
    """
    Method to create an array of dictionaries combining the data from the Bthinned and Fthinned files
    """
    def UnifyData(self):
        
        burstData = []
        
        for index, value in enumerate(self.binaryData):
            singleData = {}
            
            singleData["position"] = index
            singleData["binaryData"] = value
            singleData["timestamp"] = self.timestamp[index]
            singleData["activity"] = self.activityData[index]
            
            burstData.append(singleData)
                
        return burstData
  
    
    """
    Method to find and save the 1s bursts
    """
    def FindOnesBursts(self):
        
        allOnesBurst = []
        itemsToLookFor = []
        
        indexDeleted = 0   
        
        for originalData in self.unifyData: #Copy unifyData to itemsToLookFor
            itemsToLookFor.append(originalData)
        
        for index, data in enumerate(itemsToLookFor):
             
            oneBurst = []
            burstGoing = True
            
            while(burstGoing): # If we are in a 1s burst 
                
                data = itemsToLookFor[index]
                
                if data["binaryData"] in self.VALUES_CONSIDER_AS_ONES: #Found a value consider as 1
                    burstGoing = True # We are on a burst
                    
                    oneBurst.append(data)
                    itemsToLookFor.pop(index - indexDeleted)
                    
                    indexDeleted += 1 #Increment in 1 the index deleted
                    
                else: #The 1s burst has ended
                    burstGoing = False
                    index += 1 # Because we don't do a 
                    
                    if oneBurst: #Save the 1s burst if is not empty
                        allOnesBurst.append(oneBurst) 
    
        return allOnesBurst
        
            
    """
    Method to find and save the 0s burst
    """
    def FindZerosBurst(self):
        
        firstPosition = 0
        allZerosBurst = []
        
        for burst in self.onesBursts:            
            
            zerosBurst = []
            
            lastPosition = burst[0]["position"]  # Last position of 0s burst = first position of 1s burst
            zerosRange = list(range(firstPosition, lastPosition)) # Get the number of 0s the burst has >>> Number of 0s = number of positions between 1s bursts
            
            for index in zerosRange:    
                zerosBurst.append(self.unifyData[index] )
                        
            firstPosition = burst[-1]["position"] + 1 # Get the start of the next 0s burst >>> Position = last 1s burst value + 1
            
            allZerosBurst.append(zerosBurst) #Save the 0s burst
            
        return allZerosBurst
    
    
    """
    Method to adjust the length of the 0s burst to the specified in the SECONDS_PREVIOUS_TO_ONEs_BURST constant
    """
    def AdjustZerosBurstsLength(self, originalZeroBurst):
        adjustedBursts = originalZeroBurst 
        
        if self.SECONDS_PREVIOUS_TO_ONEs_BURST != -1: # If the constant is not -1, get the specified number of 0s
            adjustedBursts = []
            
            for burst in originalZeroBurst:
                adjustedBursts.append(burst[-int(self.MAX_0s_TO_EXPORT):]) # From the 0s burst get the latest MAX_0s_TO_EXPORT zeros
        
        return adjustedBursts
    
    
    """
    Method to create a string for export the data to a csv (values separated by ";")
    - It appends the 0s burst to the corresponding 1s burst. When the burst is completed, it adds a line break ("\n")
    - Each 0s + 1s burst are in one line and each value is separated by ;
    """
    def CraftStringFromZerosAndOnesBurst(self):
        completeBursts = ""
        
        for burstNumber, burstData in enumerate(self.onesBursts):
            
            for dataZeros in self.zerosBurst[burstNumber]:
                completeBursts += dataZeros["activity"] + ";"
            
            for dataOnes in burstData: 
                completeBursts += dataOnes["activity"] + ";"
                
            completeBursts += "\n"
        
        return completeBursts
    
    
    """
    Method to adjust the length of the strings with the 0s + 1s bursts so the 1s bursts start at the same point in the csv file. 
    - It adds the ";" character to create blank cells in the csv for the needed strings. 
    - The new strigns looks like: blank spaces (";" chars) + 0s burst + 1s burst. That way, the first position of the 1s burst is in the same column in the CSV file.
    """
    def AdjustStringToInitiateOnesBurstAtSameTime(self):
        
        fullString = self.CraftStringFromZerosAndOnesBurst() # Get 0s + 1s bursts strings
        formatedString = ""
        
        maxZerosLength = 0 
        lines = fullString.split() # Get each burst string separately
        
        for burstIndex, zerosBurst in enumerate(self.zerosBurst):
            
            if len(zerosBurst) > maxZerosLength:
                maxZerosLength = len(zerosBurst) #Get maximun number of 0 in a burst
            
            spacesToAdd = maxZerosLength - len(zerosBurst) # Number of ";" chars (blank cells in CSV) to add. Blank cells = maxZerosLength - number of 0s that the 0s burst has.
            
            formatedString += ";" * spacesToAdd + lines[burstIndex] + "\n"
            
        return formatedString
            
                    
    """
    Method to write all the data processed into strings as desire to the excel file. The way the strings work is described in the AdjustStringToInitiateOnesBurstAtSameTime mehtod. 
    """
    def ExportToCSV(self, fileName: str):
        
        formatedString = self.AdjustStringToInitiateOnesBurstAtSameTime()
            
        with open(fileName, "w") as file:
            for line in formatedString: 
                file.write(line)
            


if __name__ == "__main__": 
    
    print(BANNER)
    
    Data = BehaviourFile()
    Data.ExportToCSV("test.csv")
