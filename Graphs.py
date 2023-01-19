def make_storage_profile_graph(ProfileObjectList,Name,Xaxis,Yaxis,ProfileListToInclude):
    import matplotlib.pyplot as plt
        
    NumberOfLists = len(ProfileListToInclude)
    figure1,axs = plt.subplots(NumberOfLists, sharex = 'row') 
    
    for i in range (len(ProfileListToInclude)):
        axs[i].plot (ProfileObjectList[ProfileListToInclude[i]].StorageProfile)
        axs[i].set_title('Profile: '+ProfileObjectList[ProfileListToInclude[i]].Name, fontsize=12)
        if i==NumberOfLists-1: 
            axs[i].set_xlabel(Xaxis,fontsize=12)          
        axs[i].set_ylabel(Yaxis,fontsize=12)
    #figure2.tight_layout() 
    plt.savefig(Name)      
    plt.show()
    plt.clf()

def make_duration_curve_graph(ProfileObjectList,Name,Xaxis,Yaxis):
    import matplotlib.pyplot as plt
    
    NumberOfLists = len(ProfileObjectList)

    for i in range (NumberOfLists): 
        plt.plot (ProfileObjectList[i].InputProfile,label=ProfileObjectList[i].Name)
        plt.title('Load Duration Curves')
        plt.xlabel(Xaxis,fontsize=12)        
        plt.ylabel(Yaxis,fontsize=12)
    plt.legend()
    plt.savefig(Name)  
    plt.show()
    plt.clf()

def make_single_graph(InputProfile,Name,Dir,Xaxis,Yaxis):
    import matplotlib.pyplot as plt
    
    plt.plot (InputProfile)
    plt.xlabel(Xaxis,fontsize=12)        
    plt.ylabel(Yaxis,fontsize=12)
    plt.title(Name) 

    plt.savefig(str(Dir)+'/'+str(Name)+'.png') 
    plt.show()
    plt.clf()
    
def after_storage_graph(ImprovedProfile,ProfileObjectList,Name):
    import matplotlib.pyplot as plt

    plt.plot (ProfileObjectList[0].InputProfile,label='Original Profile')
    plt.plot (ImprovedProfile, label='Improved Profile')
    plt.title(Name)
    plt.xlabel('Samples',fontsize=12)        
    plt.ylabel('Power',fontsize=12)
    plt.legend()
    plt.savefig('results/Graphs/'+Name,dpi=1000)
    plt.show()
    plt.clf()
