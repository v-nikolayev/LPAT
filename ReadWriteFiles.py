#read Energy Profile in CSV file
def read_power_profile (FileNameInput):
    import csv
    with open (FileNameInput, mode='r', encoding="utf-8-sig") as ReadInputFile:
#        print('Reading Input:', FileNameInput)	
        CSVreader = csv.reader(ReadInputFile,delimiter=',')

        ListOfLists = list(CSVreader)
        StrListOfRows = []
        FloatListOfRows = []
        EndOfLists = len(ListOfLists)#choose where to stop converting from CSV into list of floats. Default to entire list
        BeginOfLists = 0
        #EndOfLists = 100000
            
        # Merge all lists into single list.
        for i in range (BeginOfLists,EndOfLists):
            StrListOfRows.extend(ListOfLists[i]) #= StrListOfRows + ListOfLists[i]
#            if i%500000==0 or i==EndOfLists-1:
#                print('Reading Line: ' + str(i)) 
        #convert strings into floats
        for i in range(0, len(StrListOfRows)): 
            FloatListOfRows.append(float(StrListOfRows[i]))
 #   print('Done Reading:', FileNameInput)
    return FloatListOfRows  

#write an energy profile to an external file    
def write_profile (FileName, Profile):
    file1 = open(FileName, "w")
    for j in range (0,len(Profile)):
        file1.write(str(Profile[j]))	
        file1.write('\n')
    file1.close()

#write general information about profile, such as min/max    
def write_general_data(FileName, ProfileObject):
    
    file1 = open (FileName,"w")
    file1.write('Sample Frequency,'+str(ProfileObject.SampleFrequency))
    file1.write("\n")
    # file1.write('Total Energy,'+str(sum(ProfileObject.EnergyProfile)))
    # file1.write("\n")
    file1.write('Minimum Power,'+str(ProfileObject.MinPower))
    file1.write("\n")
    file1.write('Maximum Power,'+str(ProfileObject.MaxPower))
    file1.write("\n")
    file1.write('Minimum Ramp Rate,'+str(ProfileObject.MinRamp))
    file1.write("\n")
    file1.write('Maximum Ramp Rate,'+str(ProfileObject.MaxRamp))
    file1.write("\n")
 
    if ProfileObject.StorageSize in locals():
        file1.write('Storage Capacity,'+str(ProfileObject.StorageSize))
    file1.close()
  
#Write storage capacities per (sub) profile to .csv  
def write_capacities(Rootdir,ProfileObjectList):

    file1 = open(Rootdir+'Storage Capacities.csv', "w")
    
    for i in range (len(ProfileObjectList)):
        file1.write (str(ProfileObjectList[i].Name) + ','+str(ProfileObjectList[i].StorageSize))
        file1.write("\n")
    file1.close()    
 
# Create directories for results 
def create_dirs(RootDir,SetProfileNames):
    import os
    
    path1 = RootDir + 'Original_Profile'
    os.makedirs(path1)
    path2 = RootDir + 'Graphs'
    os.makedirs(path2)
    # path3 = RootDir + 'Single ESS'
    # os.makedirs(path3)    
    path4 = RootDir + 'PAfterStorage'
    os.makedirs(path4)
    
    for i in range (0,len(SetProfileNames)):
        path = RootDir + SetProfileNames[i]
        os.makedirs(path)
   

    

