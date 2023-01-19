# Load Profile Analysis Tool (LPAT) both in part and in its 
# totality is available under Creative Commons 
# Attribution-NonCommercial 4.0 International Licence, 
# see https://creativecommons.org/licenses/by-nc/4.0/legalcode 
# for more information. 

#For more information about this tool, please see the publication
#'Sizing of hybrid energy storage through analysis of load profile
#characteristics: A household case study',
#DOI: 10.1016/j.est.2022.104768

from ProfileData import PowerProfileDataAnalysis
from ReadWriteFiles import *
from Graphs import *
from scipy.signal import butter,filtfilt
import os, shutil
import math

# Settings
SampleFrequency = 1/900    # sample rate, Hz
SetCutoffFreqs = [1/86400,1/1800] # desired cutoff frequencies, each represents a timescale upper limit. 1 1dy/1hr/1 minute. slowest possible rate based on Nyquist Frequency (2x sample rate)
SetProfileNames = ['PGrid','PBat','PFW'] # set names of subprofiles. Should be 1 more than number of SetCutoffFreqs (one for rest profile)   
FilePathResults = 'Results/' #set folder name for results
FileNameDemandInput = 'Demo_Imbalance_1year_15min.csv'#Set .csv input file name. .csv must be single column, comma seperated
SplitProfiles = True # Set if input load profile needs to be split. This saves time in case of reanalysis with same submprofiles. If false, suprofiles should be available in results folder
CreateGraphs = True
StorageProfiles =[2,3] # Choose sub-profiles to be subtracted from original profile (can be considered storage devices), to give remaining imbalance profile. Original_Profile =0, sub-profile 1=1 etc
RampRateSetting = 1 # Set number of samples per ramp/rate. Ex, if the sample frequency is in seconds, and samples is set to 3600, then value is in power/hour

# splits the given profile into 2 subprofiles, based on desired lowpass filter cut-off frequency    
def split_power_profile(Cutoff, InputPowerProfile):
    FilterOrder = 2 # sin wave can be approx represented as quadratic
    print('Splitting Profile: Cutoff '+ str(1/Cutoff) +' seconds')
    NonFilteredProfile = []
    # Filter the energy profile 
    b, a = butter(FilterOrder, Cutoff, btype='low', analog=False)
    FilteredProfile = filtfilt(b, a, InputPowerProfile)
    NonFilteredProfile = InputPowerProfile - FilteredProfile # Remove filtered profile from original profile
    print ('Done Splitting: Cutoff '+ str(1/Cutoff) +' seconds')
    return FilteredProfile, NonFilteredProfile    

#writes profile to file  
def profile_writing (ProfileObject):    
    NewDir = ProfileObject.Dir + str(ProfileObject.Name)+'/' #name for directory to put analysis files in, based on name of profile   
    PowerProfileFileName = NewDir + ProfileObject.Name +".csv" # combines with directory name to make file name for Power Profile
    write_profile(PowerProfileFileName, ProfileObject.InputProfile) #write power profile to file
    if (ProfileObject.Name!='Original_Profile'):
        print ('Profile Written:'+ProfileObject.Name)
    if (CreateGraphs==True):
        make_single_graph(ProfileObject.InputProfile,ProfileObject.Name,NewDir,'Samples','Power')

# function for the create a of one or more subprofiles. Will only work if SplitProfiles is True. Remainder of profile written into sepearte file.     
def create_subprofiles():
    ProfileObjectList=[]
    print('--------------------------------')
    if SplitProfiles == True: 

        ProfileName = 'Original_Profile'# set profile name for original (input) file
        RemainingProfile = read_power_profile(FileNameDemandInput)#Read input profile
        OriginalProfile = PowerProfileDataAnalysis (ProfileName,RemainingProfile,'none',FilePathResults) #Analyse Original_Profile
        ProfileObjectList.append(OriginalProfile) 
        profile_writing (OriginalProfile)     
        
        #Loop to split up the power profiles, 1 profile for each cutoff given + 1 for rest profile
        for i in range (0,len(SetCutoffFreqs)):  
            #Check if cutoff is withing nyquist (0.5*SampleFrequency)
            if SetCutoffFreqs[i]<=(SampleFrequency*0.5): 
                Cutoff = SetCutoffFreqs[i]
                InputProfile, NonFilteredProfile = split_power_profile (Cutoff,RemainingProfile)
                ProfileName = SetProfileNames[i]
                ProfileObject = PowerProfileDataAnalysis (ProfileName,InputProfile,SampleFrequency,FilePathResults)     
                ProfileObjectList.append(ProfileObject)
                profile_writing (ProfileObject)
                RemainingProfile = NonFilteredProfile

            #write the remainder of profile (highest frequency behaviour) into a file after all filtering is done    
            if i==len(SetCutoffFreqs)-1:
                ProfileName = SetProfileNames[len(SetProfileNames)-1]
                ProfileObject = PowerProfileDataAnalysis (ProfileName,RemainingProfile,SampleFrequency,FilePathResults)  
                ProfileObjectList.append(ProfileObject)                    
                profile_writing (ProfileObject)
                
        print (str(len(ProfileObjectList)-1)+' Sub-profiles Created') 
        del(ProfileObjectList)
    else:
        print('No Sub-Profiles Created')
    print('--------------------------------')

#read profiles   
def read_profiles(SetProfileNames):
    from os import path
    
    #Read profiles in, get list of profiles
    ProfileObjectList=[]
    OriginalProfileFilePath = FilePathResults+'Original_Profile/Original_Profile.csv'
    if path.exists(OriginalProfileFilePath):
        ProfileName = 'Original_Profile'
        ProfileObject = PowerProfileDataAnalysis (ProfileName,read_power_profile(OriginalProfileFilePath),SampleFrequency,FilePathResults)  
        ProfileObjectList.append(ProfileObject)
        
        for i in range (0,len(SetProfileNames)):

            ProfileObjectPath = FilePathResults + SetProfileNames[i]+'/'+SetProfileNames[i]+'.csv'
#            print(ProfileObjectPath)
            if path.exists(ProfileObjectPath):

                ProfileName = SetProfileNames[i]
                ProfileObject = PowerProfileDataAnalysis (ProfileName,read_power_profile(ProfileObjectPath),SampleFrequency,FilePathResults)  
                ProfileObjectList.append(ProfileObject)              
        return ProfileObjectList

#analyse input power profile
def profile_analysis(ProfileObjectList):

    for i in range (0,len(ProfileObjectList)):  
        print('Analysing: ' + ProfileObjectList[i].Name)
        
        ProfileObjectList[i].get_ramp_rates(RampRateSetting) #Calculate the min/max ramp rates
        ProfileObjectList[i].min_max_power()   
        write_general_data(ProfileObjectList[i].Dir+ProfileObjectList[i].Name+ '/' + 'General Data.csv',ProfileObjectList[i])
        
        print('Done Analysing: ' + ProfileObjectList[i].Name)
 
#Calculates the storage profile based on an input load profile
def get_storage_info (ProfileObjectList,SampleFrequency):

    for i in range (len(ProfileObjectList)):     

        TimeUnitEnergy = (1/SampleFrequency)* (1/3600)#Establish unit of time for time-energy conversion
        CalculatedStorageProfile = []
        NewEnergyValue = ProfileObjectList[i].InputProfile[0]*TimeUnitEnergy  # Derive 1st value of battery, based on starting charge
        CalculatedStorageProfile.append(-NewEnergyValue)
    
        #from the 2nd value, create the storage profile. 1-1 link with input profile
        for j in range (1,len(ProfileObjectList[i].InputProfile)):
            NewEnergyValue =(CalculatedStorageProfile[j-1])-(ProfileObjectList[i].InputProfile[j]*TimeUnitEnergy)
            CalculatedStorageProfile.append(NewEnergyValue)
        ProfileObjectList[i].StorageProfile = CalculatedStorageProfile
        ProfileObjectList[i].StorageSize = max(CalculatedStorageProfile)-min(CalculatedStorageProfile)

# Creates a new profile after subtracting one or more other profiles
def get_remainder_profile (ProfileObjectList,StorageProfiles,SampleFrequency):
    
    NewImbalanceProfile = ProfileObjectList[0].InputProfile
    TimeUnitEnergy = (1/SampleFrequency)* (1/3600)#Establish unit of time for time-energy conversion

    for i in range (0,len(StorageProfiles)):
        StorageProfileNumber = StorageProfiles[i]
        TempProfile1 = NewImbalanceProfile
        TempProfile2 = ProfileObjectList[StorageProfileNumber].InputProfile          
        NewProfile = []
        for (TempProfile1,TempProfile2) in zip(TempProfile1,TempProfile2):
            NewProfile.append(TempProfile1-TempProfile2)
        NewImbalanceProfile = NewProfile
    
    return NewImbalanceProfile
                  
def main(FileResults,FileInput):

    global FileNameDemandInput, FilePathResults

    FileNameDemandInput = FileInput
    FilePathResults = FileResults

    #folder creation
    if SplitProfiles == True:
        #deletes all current files in the directory where new results will be put
        try:
            shutil.rmtree(FilePathResults)
        except:
            pass
        create_dirs(FilePathResults,SetProfileNames)
#        print("Directories Created")
    else:
        print("No Directories Created")    
    
    #create sub-profiles (if necessary), and read into program relevant data
    create_subprofiles()     
    ProfileObjectList = read_profiles(SetProfileNames)
    
    NewImbalanceProfile = get_remainder_profile(ProfileObjectList,StorageProfiles,SampleFrequency)
    NewImbalancProfileName = 'PAfterStorage'# set profile name for original (input) file
    ImpProfile = PowerProfileDataAnalysis (NewImbalancProfileName,NewImbalanceProfile,SampleFrequency,FilePathResults) #Analyse Original_Profile
    ProfileObjectList.append(ImpProfile) 
    profile_writing (ImpProfile)  

    # create storage information and analyse/write profiles and analysis
    get_storage_info(ProfileObjectList,SampleFrequency) 
    write_capacities(FilePathResults,ProfileObjectList)
    profile_analysis(ProfileObjectList)

    # Print power, capacity and ramping values to screen for each profile
    print('--------------------------------')
    for i in range (len(ProfileObjectList)):
        print(ProfileObjectList[i].Name)        
        print('Min Ramp Rate: '+ str(ProfileObjectList[i].MinRamp)) 
        print('Max Ramp Rate: '+ str(ProfileObjectList[i].MaxRamp)) 
        print('Min Power: '+ str(ProfileObjectList[i].MinPower)) 
        print('Max Power: '+ str(ProfileObjectList[i].MaxPower)) 
        print('Storage Size '+ str(ProfileObjectList[i].StorageSize)) 
        print('\r')
    print('--------------------------------')


    #Create graphs for sub-profiles storage profiles, improved profile (after removing storage sub-profiles) and improved load duration curve
    if (CreateGraphs==True): 
        after_storage_graph(NewImbalanceProfile,ProfileObjectList,'NewEnergyBalance.png') 
        make_storage_profile_graph(ProfileObjectList,'results\Graphs\Storage_Profiles.png','Samples','Energy',StorageProfiles)
        for i in range (len(ProfileObjectList)):
            ProfileObjectList[i].InputProfile.sort(reverse=True) #Sort values in profile by size, for load duration curve
        NewImbalanceProfile.sort(reverse=True) 
        make_duration_curve_graph(ProfileObjectList,'results\Graphs\Load Duration Curve.png','Samples','Power')
        after_storage_graph(NewImbalanceProfile,ProfileObjectList,'NewEnergyBalance Load Duration Curve.png')    

    print("This is the end")


main(FilePathResults,FileNameDemandInput) #Use this line to run a single simulation based on settings.







