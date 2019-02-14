"""OMKAR DHOMANE
   115009233
"""
import numpy as np
import math
from time import sleep
np.random.seed(0)


Pt=42 # Transmitted Power of Pilot Channel (Max)
total_time = 0  # A counter keeping track of the total time of simulation
time_step = 1   # Increment in time is one sec
RSL_pilot_min = -107    # Mobile Rx Threshold
sinr_req=6
num_users = 1000    # Total number of users at any given point of time
total_channels= 57
channels_in_use = 0
#channels_unused = 57 
#channels_in_use = total_channels - channels_unused

call_rate = 6.0/3600    # Number of calls made in one second
prob_call = call_rate * time_step

active_callers_info = []    # List which will hold the details of active calls during the simulation
callers_list = []    # List which will have the user number having active calls


#Shadowing value calculations
shadow_values_fixed = np.random.lognormal(0,2,4e6)
shadow_list=shadow_values_fixed.tolist()

# Since the log normally generated Shadow values can have large spikes/peaks we need to limit the shadowing values to a certain value
for v in range(len(shadow_list)):
    if shadow_list[v] > 12:
        shadow_list[v] = 12  #Limit the shadowing values to maximum of 12 dB
     

# Since the outer square is divided into 10m x 10m small squares, we find the center location of each smaller square
# The centers of smaller squares will lie from -9995m to +9995m in 10 meters increments on both axes
l1=[]
l2=[]
for i in range(-9995,10000,10):
    l1.append(i)
for i in range(2000):
    l2.append(l1)

center_x = np.array(l2)      # A matrix containing X-Coordinates of the center points of each 10m x 10m square
center_y = center_x.transpose() # A matrix containing Y-Coordinates of the center points of each 10m x 10m square

location_list=[]
for m in range(2000):
    for n in range(2000):
        location_list.append(tuple([center_x[m][n],center_y[m][n]]))
        
# Creates a dictionary with USER LOCATION as key and its corresponding FIXED SHADOW VALUES as values        
shadow_dictionary = dict(zip(location_list, shadow_list)) 

l=[]
for i in range(-9995,10000,10):
    l.append(i)
array_loc = np.array(l) # Array containing all possible X or Y cordinates of centers of the Squares

# Lookup the specified user location in the shadow dictionary for matching it with the closest x and y coordinates
def shadow_lookup(user_loc):
    x_co = user_loc[0]
    y_co = user_loc[1]
    
    idx = (np.abs(array_loc - x_co)).argmin()
    x_center = array_loc[idx]
    
    idy = (np.abs(array_loc - y_co)).argmin()
    y_center = array_loc[idy]
    
    loc=(x_center,y_center)
    return shadow_dictionary[loc] # Fixed shadow value corresponding to that location
    
    

# List of variables which will hold the system parameters
call_attempts_not_ret = 0 # Number of call attempts not counting retries
call_attempts_with_ret = 0 # Number of call attempts including retries
dropped_calls=0            # Number of dropped calls
blocked_calls_sigstrength=0 # Number of blocked calls due to signal strength
blocked_calls_channelcap=0 # Number of blocked calls due to channel capacity
successful_calls=0  # Number of successfully completed calls
#calls_in_progress = len(callers_list)
current_cell_rad = 0 # Current cell radius

#All Functions

#Location
def distance():                               
    d = np.random.uniform(0,10000)      # Uniformly varying randomly generated instataneous user distance from BTS
    return d

def angle():
    ang = np.random.uniform(0,360)
    ang = np.deg2rad(ang)               # Uniformly varying randomly generated instataneous angle of user from BTS
    return ang

def coordinates(theta, r):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return [x, y]                       # Converting the distance and angle to Cartesian coordinates

#Signal
def EIRP(Pt):
    #Maximum Tx_power = 42
    lc_loss = 2.1                       # Line and Connector Loss
    Antenna_Gain = 12.1                 # Antenna Gain
    eirp = Pt + Antenna_Gain - lc_loss  # EIRP
    return eirp

#Path Loss using COST231 Model
def path_loss(dist):
    h_bts = 50  # in meters
    fc = 1900   # in MHz
    pathloss = 46.3 + 33.9*math.log10(fc) - 13.82*math.log10(h_bts) + (44.9 - 6.55*math.log10(h_bts))*math.log10(dist*0.001)
    return pathloss

#Fading
def fading():
    x=np.random.normal(0,1)      #Real part in Rayleigh distribution 
    y=np.random.normal(0,1)      #Imaginary part in Rayleigh distribution
    z=x+y*(1j)                   #Combining Both real and imaginary part
    fd=np.abs(z)                 #Magnitude of the distribution
    fade = 20*math.log10(fd)
    return fade

#SINR
def sinr(rsl_value,active_users):
    pg = 20                 # Processing Gain
    noise_level = -110      # Noise Level
    signal_level = rsl_value + pg
    
    if active_users==1:
        int_level = 0     # Interference is 0 when only one active user present
    else:
        int_level = rsl_value + 10*math.log10(active_users-1) # Interference due to other active users
    
    signal_linear = 10**(signal_level/10)
    int_linear = 10**(int_level/10)
    noise_linear=10**(noise_level/10)
    sinr_linear= signal_linear/(int_linear + noise_linear)
    sinr=10*math.log10(sinr_linear)
    return sinr        #SINR value

"""
**************************
SIMULATOR PROGRAM STARTS
**************************
"""
print(" ")
print('********************************************************')
print('SIMULATOR FOR A SINGLE CELL OF A MOBILE CELLULAR NETWORK')
print('********************************************************')
sleep(2)
print('Starting the Simulator........')
sleep(2)
print('Generating Reports for two minute intervals.... Please Wait!')
sleep(2)
print(" ")


simulator_ends = False     # End the simulation when the timer reaches the total simulation time
count_ac=0
while simulator_ends is False:
    total_time += time_step     # Increment the time counter in counts of 1 second
    caller_id = 0
    
#Admission Control ( Cd=20 and  Ci=15 )
    
    if channels_in_use > 20:    # Check each second if the channels-in-use (Cd) crosses 20
        while(Pt >= 30.5):      # Minimum power has to be atleast 30 dBm
            Pt = Pt - 0.5       # Reduces the Pilot EIRP by 0.5 dB
            count_ac +=1
        
    if channels_in_use < 15 and count_ac > 0: # Check each second if the channels-in-use after implementing Admission control doesn't go below 15
        while(Pt <= 41.5):      # Maximum power can be atmost 42 dB
            Pt = Pt + 0.5       # Increases the Pilot EIRP by 0.5 dB
            
        
    
    # Go through active caller List
    for u in active_callers_info:
        caller_id += 1
        
        u[3] -= 1   # Decrement total call duration left by 1 second
        if u[3] <= 0:   # Check if call duration of user is completed 
            #channels_unused += 1 # Free up the channel
            channels_in_use -= 1
            successful_calls += 1 # Mark this call as successful
            
            #Remove this caller and their call info from the list
            callers_list.remove(u[0]) 
            del active_callers_info[caller_id-1]
            continue
        
        # For users who still have an active call
        fixed_dist = u[1] # User is stationary while attempting the call too
        rsl_value = EIRP(Pt) - path_loss(fixed_dist) + fading() + shadow_lookup(u[2]) # RSL for the user
        sinr_user = sinr(rsl_value, len(callers_list)) # SINR for the user
        if (sinr_user < sinr_req):
            u[4]+=1              #Increment the sinr_count value in user info which shows whether it rechecks after one unsuccessful attempt
        else:
            u[4]=0
            
        if (u[4]>=3):           # check if no. of attempts of sinr checks is more than 3
             dropped_calls += 1 # Mark this call as dropped call
             #channels_unused += 1 # Free up a channel
             channels_in_use -=1
             
             #Remove this caller and their call info from the list
             callers_list.remove(u[0])
             del active_callers_info[caller_id-1]

            
# For all other users who do not have an active call yet....
    for i in range(num_users): # iterate over all users
        prob = np.random.uniform(0, 1) #generate a random instant probability to determine whether a acll attempt is made by this user
        if i+1 in callers_list:  # Since active users are already taken care of....
            continue
        
        user_distance = distance() # Distance of this user from BTS (in meters)
        user_theta = angle()       # Angle of this user from BTS (in meters)
        user_location = coordinates(user_theta,user_distance) # x and y coordinates of the user
        
        if prob < prob_call: # Check if this user will attempt a call or not
            call_attempts_not_ret +=1 # Record the attempted calls not including retries
            count_rsl=0               # Counter to store no. of RSL check attempts
            while (count_rsl< 3):     # Check if the total attempt count does not exceed 3 conscecutive attempts
                call_attempts_with_ret += 1  # Record the attempted calls not including retries
                RSL_user = EIRP(Pt) - path_loss(user_distance) + fading() + shadow_lookup(user_location)
                if RSL_user > RSL_pilot_min:  # Check if minimum RSL criteria matches
                    if channels_in_use < 57:   # Check if channel capacity criteria matches
                        channels_in_use += 1  # Occupy a channel
                        # Add this user to caller list along with their info
                        callers_list.append(i+1) 
                        sinr_count=0 # no. of sinr attempts count (which will be used later on during the call)
                        active_callers_info.append([i+1, user_distance, user_location, np.random.exponential(60),sinr_count])
                        break
                    else:
                        blocked_calls_channelcap += 1 # Mark this as blocked due to inadequate channel capacity
                        break
                else:
                    count_rsl += 1 #Increment the reattempt counter for RSL checks
            
            if (count_rsl >= 3) : # If more than 3 attempts
                blocked_calls_sigstrength += 1 # Mark this as blocked due to insufficient signal strength
                
                
              
    if total_time % 120 is 0:
        print('--------------------------TWO MINUTE REPORT----------------------------')
        print('Number of call attempts not counting retries         :'+str(call_attempts_not_ret))
        print('Number of call attempts including retries            :'+str(call_attempts_with_ret))
        print('Number of dropped calls                              :'+str(dropped_calls))
        print('Number of blocked calls due to signal strength       :'+str(blocked_calls_sigstrength))
        print('Number of blocked calls due to channel capacity      :'+str(blocked_calls_channelcap))
        print('Number of successfully completed calls               :'+str(successful_calls))
        print('Number of calls in progress at any given time        :'+str(len(callers_list)))
        print('Number of failed calls (blocks + drops)              :'+str(dropped_calls + blocked_calls_sigstrength + blocked_calls_channelcap))
        dist_list=[]
        for d in active_callers_info:
            dist_list.append(d[1])
        rad = max(dist_list)
        print('Current Cell Radius                                  :'+'%.2f'%round(rad,2) + ' meters')
        print('\n')
        
    if total_time == 3600*2:
        simulator_ends = True
print('******************************************************************')        
print('--------------------------FINAL REPORT----------------------------')
print('******************************************************************')

print('Number of call attempts not counting retries         :'+str(call_attempts_not_ret))
print('Number of call attempts including retries            :'+str(call_attempts_with_ret))
print('Number of dropped calls                              :'+str(dropped_calls))
print('Number of blocked calls due to signal strength       :'+str(blocked_calls_sigstrength))
print('Number of blocked calls due to channel capacity      :'+str(blocked_calls_channelcap))
print('Number of successfully completed calls               :'+str(successful_calls))
print('Number of calls in progress at any given time        :'+str(len(callers_list)))
print('Number of failed calls (blocks + drops)              :'+str(dropped_calls + blocked_calls_sigstrength + blocked_calls_channelcap))
dist_list=[]
for d in active_callers_info:
    dist_list.append(d[1])
rad = max(dist_list)
print('Current Cell Radius                                  :'+'%.2f'%round(rad,2) + ' meters')
print('\n')        

