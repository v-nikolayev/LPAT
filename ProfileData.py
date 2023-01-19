#Profile class definition, with properties inlcuding name, frequency, the profile itself, flexibility values and storage profile
class PowerProfileDataAnalysis:
    def __init__(self,Name,InputProfile,SampleFrequency,Dir,MinRamp=None,MaxRamp=None,MinPower=None,MaxPower=None,StorageProfile=None,StorageSize=None):
        self.InputProfile = InputProfile
        self.Name = Name 
        self.SampleFrequency = SampleFrequency
        self.Dir = Dir
        self.MaxPower = max(self.InputProfile)
        self.MinPower = min(self.InputProfile)   
        
    #Adds the min and max ramp rates to the profile object, based on a given number of samples
    def get_ramp_rates (self,RampRateSize):
        RampRateProfile = []
        for i in range (RampRateSize,len(self.InputProfile)):
            CurrentValue= self.InputProfile[i]
            PreviousValue= self.InputProfile[i-RampRateSize] 
            RampRateValue= (CurrentValue-PreviousValue)/((1/self.SampleFrequency)*RampRateSize)
            RampRateProfile.insert(i,RampRateValue)
        self.MaxRamp = max(RampRateProfile)
        self.MinRamp = min(RampRateProfile)
                              
    #Adds the min and max powers to the profile object
    def min_max_power (self):
        self.MaxPower = max(self.InputProfile)
        self.MinPower = min(self.InputProfile)
                
    





   
   

        
        
        
    
            