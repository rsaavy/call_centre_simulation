import simpy
import random
import statistics
import math
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# streamlit run your_script.py

customerArrivalTime = 0  # one customer every x mins
serviceTime = [None]*5   # avg. service time of each type of agent
target = 0 # waittime target
servingTarget = 0 # % served target 

wait_times = []

closing_time = 0 # duration of the simulation

customer_ID = 0
targetMetWaitingTimes = []

my_bar = None

AREgenerated = 0
ARFgenerated = 0
BREgenerated = 0

AREserved = 0
ARFserved = 0
BREserved = 0

customers = []

class Customer(object):
    def __init__(self,customer_ID,department,english):
        self.ID = customer_ID
        self.department = department
        self.english = english

class Call_Centre(object):
    def __init__(self,env,agent_numbers):
        # agent_numbers is a list containing the number of agents of each type 
        self.env = env
        self.agentsARE = simpy.Resource(env, agent_numbers[0])
        self.agentsARF = simpy.Resource(env, agent_numbers[1])
        self.agentsBRE = simpy.Resource(env, agent_numbers[2])
        self.agentsBRF = simpy.Resource(env, agent_numbers[3])
        self.agentsCRE = simpy.Resource(env, agent_numbers[4])

    def handle_customer(self, customer, serviceTime):
        yield self.env.timeout(serviceTime)

def place_call(env, customer, call_centre):
        # Customer places call with call centre
        arrival_time = env.now
        global AREserved
        global ARFserved
        global BREserved

        # if-else assigns caller to particular department and English/French - needs to be modified if additional services are added 
        if customer.department == 'A':
            if customer.english: 
                with call_centre.agentsARE.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer,serviceTime[0]))
                    AREserved += 1
                    wait_times.append((env.now - arrival_time) - serviceTime[0])
            else:
                with call_centre.agentsARF.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer,serviceTime[1]))
                    ARFserved += 1
                    wait_times.append((env.now - arrival_time) - serviceTime[1])
        elif customer.department == 'B':
            if customer.english: 
                with call_centre.agentsBRE.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer,serviceTime[2]))
                    BREserved += 1
                    wait_times.append((env.now - arrival_time) - serviceTime[2])
            else:
                with call_centre.agentsBRF.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer,serviceTime[3]))
                    wait_times.append((env.now - arrival_time) - serviceTime[3])
        elif customer.department == 'C':
            if customer.english: 
                with call_centre.agentsCRE.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer,serviceTime[4]))
                    wait_times.append((env.now - arrival_time) - serviceTime[4])
        
        # Customer ends call with call centrer

def run_call_centre(env,agent_numbers):
    call_centre = Call_Centre(env,agent_numbers)
    global customer_ID
    global customers

    # customers already calling when call-centre opens    
    english = False 
    for customer_ID in range(3):
        langGen =  random.random()
        deptGen = random.randint(0,2400)
        if deptGen <= 637:
            dept = "A"
            if langGen <= 0.77:
                english = True
        elif deptGen <= 1241:
            dept = "B"
            if langGen <= 0.77:
                english = True
        elif deptGen <= 2400:
            dept = "C"
            english = True

    customer = Customer(customer_ID, dept ,english)
       
    env.process(place_call(env, customer, call_centre))  

    global AREgenerated
    global ARFgenerated
    global BREgenerated   

    while not wait_times  or (wait_times[-1] < (closing_time - env.now)) :

        yield env.timeout(customerArrivalTime)  # Wait a bit before generating a new person

        # assigns caller to different services randomly (values chosen arbitrarily)
        customer_ID += 1
        
        english = False 
        langGen =  random.random()
        deptGen = random.randint(0,2000)
        if deptGen <= 837:
            dept = "A"
            if langGen <= 0.77:
                english = True
        elif deptGen <= 1241:
            dept = "B"
            if langGen <= 0.77:
                english = True
        elif deptGen <= 2000:
            dept = "C"
            english = True

        customer = Customer(customer_ID, dept ,english)

        env.process(place_call(env, customer, call_centre))

def get_average_wait_time_mins(wait_times):
    average_wait = statistics.mean(wait_times)
    return average_wait

def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)

    # Pretty print the results
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds) 
        
def get_user_input():
    agent_numbers[0] = input("Input # of ARE working: ")
    agent_numbers[1] = input("Input # of ARF working: ")
    agent_numbers[2] = input("Input # of BRE working: ")
    params = [agent_numbers[0], agent_numbers[1], agent_numbers[2]]
    if all(str(i).isdigit() for i in params):  # Check input is valid
        params = [int(x) for x in params]
    else:
        print(
             "Could not parse input. The simulation will use default values:",
            "\n1 ARE, 1 ARF, 1 BRE.",
        ) 
        params = [1, 1, 1]
    return params

def testBRE(agent_numbers, prev_agent_numbers, BREMins, max_agent_numbers):
    global targetMetWaitingTimes
    
    while agent_numbers[2] < max_agent_numbers[2]:

        prevBREMins = BREMins 
        
        random.seed(42)
        prev_agent_numbers[2] = agent_numbers[2]
        agent_numbers[2] *= 2  
        # Run the simulation

        wait_times.clear()

        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)

        # View the results
        BREMins = get_average_wait_time_mins(wait_times)
   
        if BREMins <= target:
          print(
              
              f"\nThe average wait time is {BREMins} minutes with {agent_numbers[0]} ARE, {agent_numbers[1]} ARF, and {agent_numbers[2]} BRE.",
          )
          targetMetWaitingTimes.append(agent_numbers)
          
        # while loop exited = first number of BRE with < 10mins wait time has been found or 10mins can't be reached

        # find lowest number of BRE with < 10mins wait time

        if BREMins <= target:
            targetMet = True
        else:
            targetMet = False

    return BREMins, targetMet

def testARF(agent_numbers, prev_agent_numbers, ARFMins, max_agent_numbers):

    while agent_numbers[1] < max_agent_numbers[1]:

        prevARFMins = ARFMins
        prev_agent_numbers[1] = agent_numbers[1]
        agent_numbers[1] *= 2

        BREMins = 999
        prevBREMins = 1000

        agent_numbers[2] = 0.5

        ARFMins, targetMet = testBRE(agent_numbers,prev_agent_numbers, BREMins, max_agent_numbers)
        
    return BREMins, targetMet

        

def testARE(agent_numbers, prev_agent_numbers, AREMins, max_agent_numbers):

    print(agent_numbers[0],max_agent_numbers[0])
    while agent_numbers[0] < max_agent_numbers[0]:


            prevAREMins = AREMins
            prev_agent_numbers[0] = agent_numbers[0]
            agent_numbers[0] *= 2

            ARFMins = 999
            prevARFMins = 1000

            agent_numbers[1] = 0.5

            AREMins, targetMet = testARF(agent_numbers,prev_agent_numbers, AREMins, max_agent_numbers)

    return AREMins, targetMet

def testBRF(agent_numbers, prev_agent_numbers, AREMins, max_agent_numbers):

    while agent_numbers[0] < max_agent_numbers[0]:

            prevAREMins = AREMins
            prev_agent_numbers[0] = agent_numbers[0]
            agent_numbers[0] *= 2

            ARFMins = 999
            prevARFMins = 1000

            agent_numbers[1] = 0.5

            BRFMins, targetMet = testARF(agent_numbers,prev_agent_numbers, BRFMins, max_agent_numbers)

    return BRFMins, targetMet

def simulate(customerArrivalTime,serviceTime,target,servingTarget):
    # Setup
    global my_bar

    # Setup
    random.seed(42)

    targetMetWaitingTimes = []

    agent_numbers = [1,1,0.5,1,1]
    prev_agent_numbers = [1,1,1,1,1]
    max_agent_numbers = [None]*5

    AREMins = 999
    ARFMins = 999
    BREMins = 999
    BRFMins = 999
    CREMins = 999

    prevAREMins = 1000
    prevAREecs = 0

    prevARFMins = 1000
    prevARFecs = 0

    prevBREMins = 1000
    prevBREecs = 0

    prevBRFMins = 1000
    prevCREMins = 1000

    output = ["agent_numbers[0]", "agent_numbers[1]", "agent_numbers[2]", "mins", "secs"]

    optimalNums = []

    # Step 1.a)i): find max number of BRE that improve efficiency of system

    my_bar.progress(0)

    while BREMins > target:
        
                prevBREMins = BREMins 
            
                random.seed(42)
                prev_agent_numbers[2] = agent_numbers[2]
                agent_numbers[2] *= 2  
                # Run the simulation

                wait_times.clear()

                env = simpy.Environment()
                env.process(run_call_centre(env, agent_numbers))
                env.run(until=closing_time)

                # View the results
                BREMins = get_average_wait_time_mins(wait_times)

                if BREMins <= target:
                  print(
                      
                      f"\nThe average wait time is {BREMins} minutes with {agent_numbers[0]} ARE, {agent_numbers[1]} ARF, and {agent_numbers[2]} BRE.",
                  )
                  targetMetWaitingTimes.append(agent_numbers)

          

                # find lowest number of BRE with < 10mins wait time

                if BREMins <= target:
                    targetMet = True
                else:
                    targetMet = False

    upper_bound = agent_numbers[2]
    lower_bound = agent_numbers[2] / 2 

    # Step 1.b)i): find optimal number of BRE

    my_bar.progress(3)

    if not targetMet:
        max_agent_numbers[2] = agent_numbers[2]/2

    agent_numbers[0], agent_numbers[1] = 1,1

    while targetMet and lower_bound < upper_bound and agent_numbers[2] != prev_agent_numbers[2]:
        
                prev_agent_numbers[2] = agent_numbers[2]
                agent_numbers[2] = (lower_bound + upper_bound)//2

                prevBREMins = BREMins 
                
                random.seed(42) 
                # Run the simulation

                wait_times.clear()

                env = simpy.Environment()
                env.process(run_call_centre(env, agent_numbers))
                env.run(until=closing_time)

                # View the results
                BREMins = get_average_wait_time_mins(wait_times) 

                if BREMins <= target:
                  targetMetWaitingTimes.append(agent_numbers)

                # find lowest number of BRE with < 10mins wait time

                if BREMins <= target:
                    prevLessThanTargetTime = True
                else:
                    prevLessThanTargetTime = False

                if prevLessThanTargetTime:
                    upper_bound = agent_numbers[2]
                else:
                    lower_bound = agent_numbers[2]

    if targetMet:
        max_agent_numbers[2] = agent_numbers[2]
    
    optimalNums.insert(0,max_agent_numbers[2])
   
    # Step 1.a)ii): find max number of ARF that improve efficiency of system

    my_bar.progress(5)

    agent_numbers = [1,0.5,0.5,1,1]
    prev_agent_numbers = [1,1,1,1,1]

    while ARFMins < prevARFMins:

        prevARFMins = ARFMins
        prev_agent_numbers[1] = agent_numbers[1]
        agent_numbers[1] *= 2

        BREMins = 999
        prevBREMins = 1000

        agent_numbers[2] = 0.5

        BREMins, targetMet = testBRE(agent_numbers,prev_agent_numbers,BREMins, max_agent_numbers)

      
        ARFMins = BREMins

    upper_bound = agent_numbers[1]
    lower_bound = agent_numbers[1] / 2 
    
    # Step 1.b)ii): find optimal number of ARF

    my_bar.progress(8)

    agent_numbers[0] = 1

    if not targetMet:
        max_agent_numbers[1] = agent_numbers[1]/2

    while targetMet and lower_bound < upper_bound and agent_numbers[1] != prev_agent_numbers[1]:

    
            prev_agent_numbers[1] = agent_numbers[1]
            agent_numbers[1] = (lower_bound + upper_bound)//2

            prevBREMins = BREMins 
            

            BREMins = 999
            prevBREMins = 1000

            agent_numbers[2] = 0.5

            BREMins, targetMet = testBRE(agent_numbers,prev_agent_numbers, BREMins, max_agent_numbers)

            if targetMet:
                upper_bound = agent_numbers[1]
            else:
                lower_bound = agent_numbers[1]    
                    
    
    if targetMet:
        max_agent_numbers[1] = agent_numbers[1]

    optimalNums.insert(0,max_agent_numbers[1])

    
    #STEP 1.a)iii): find max number of ARE that improve efficiency of system

    my_bar.progress(10)

    agent_numbers = [0.5,0.5,0.5,1,1]
    prev_agent_numbers = [1,1,1,1,1]


    while AREMins < prevAREMins:

        prevAREMins = AREMins
        prev_agent_numbers[0] = agent_numbers[0]
        agent_numbers[0] *= 2

        ARFMins = 999
        prevARFMins = 1000

        agent_numbers[1] = 0.5

        ARFMins, targetMet = testARF(agent_numbers,prev_agent_numbers,ARFMins, max_agent_numbers)
    
        
    AREMins = ARFMins

    prev_agent_numbers[0] /= 2
    agent_numbers[0] /= 2
    
    lower_bound = math.ceil(prev_agent_numbers[0])
    upper_bound = math.ceil(agent_numbers[0])

    #STEP 1.b)iii): find optimal number of ARE that improve efficiency of system
  
    my_bar.progress(13)
    
    if not targetMet:
        max_agent_numbers[0] = agent_numbers[0]/2

    while lower_bound < upper_bound and agent_numbers[0] != prev_agent_numbers[0]:

        prev_agent_numbers[0] = agent_numbers[0]
        agent_numbers[0] = (lower_bound + upper_bound)//2
        
        ARFMins = 999
        prevARFMins = 1000

        agent_numbers[1] = 0.5
        prev_agent_numbers[1] = 1

        ARFMins, targetMet = testARF(agent_numbers,prev_agent_numbers,ARFMins, max_agent_numbers)         

        AREMins = ARFMins

        if targetMet:
            upper_bound = agent_numbers[0]
        else:
            lower_bound = agent_numbers[0]

    if targetMet:
        max_agent_numbers[0] = math.ceil(agent_numbers[0])
        
    optimalNums.insert(0,agent_numbers[0])


    #STEP 1.a)iv): find max number of BRF that improve efficiency of system
    my_bar.progress(15)

    agent_numbers = [0.5,0.5,0.5,0.5,1]
    prev_agent_numbers = [1,1,1,1,1]


    while BRFMins < prevBRFMins:

        prevBRFMins = BRFMins
        prev_agent_numbers[3] = agent_numbers[3]
        agent_numbers[3] *= 2

        AREMins = 999
        prevAREMins = 1000

        agent_numbers[0] = 0.5

        AREMins, targetMet = testARE(agent_numbers,prev_agent_numbers,AREMins, max_agent_numbers)           
    
        
    BRFMins = AREMins


    prev_agent_numbers[3] /= 2
    agent_numbers[3] /= 2
    
    lower_bound = math.ceil(prev_agent_numbers[3])
    upper_bound = math.ceil(agent_numbers[3])

    #STEP 1.b)iv): find optimal number of BRF
 
    my_bar.progress(18)

    if not targetMet:
        max_agent_numbers[3] = agent_numbers[3]/2

    while lower_bound < upper_bound and agent_numbers[0] != prev_agent_numbers[0]:


        prev_agent_numbers[3] = agent_numbers[3]
        agent_numbers[3] = (lower_bound + upper_bound)//2
        
        BRFMins = 999
        prevBRFMins = 1000

        agent_numbers[3] = 0.5
        prev_agent_numbers[3] = 1

        AREMins, targetMet = testARE(agent_numbers,prev_agent_numbers,AREMins, max_agent_numbers)          

        BRFMins = AREMins

        if targetMet:
            upper_bound = agent_numbers[3]
        else:
            lower_bound = agent_numbers[3]

    if targetMet:
        max_agent_numbers[3] = math.ceil(agent_numbers[3])
    
    optimalNums.append(agent_numbers[3])

    
    #STEP 1.a)v): find max number of CRE

    my_bar.progress(20)

    agent_numbers = [0.5,0.5,0.5,0.5,0.5]
    prev_agent_numbers = [1,1,1,1,1]


    while CREMins < prevCREMins:

        prevCREMins = CREMins
        prev_agent_numbers[4] = agent_numbers[4]
        agent_numbers[4] *= 2

        BRFMins = 999
        prevBRFMins = 1000

        agent_numbers[3] = 0.5

        BRFMins, targetMet = testARE(agent_numbers,prev_agent_numbers,BRFMins, max_agent_numbers)           
    
        
    CREMins = BRFMins


    prev_agent_numbers[4] /= 2
    agent_numbers[4] /= 2
    
    lower_bound = math.ceil(prev_agent_numbers[4])
    upper_bound = math.ceil(agent_numbers[4])

    #STEP 1.b)v): find optimal number of CRE


    my_bar.progress(23)

    if not targetMet:
        max_agent_numbers[4] = agent_numbers[4]/2

    while lower_bound < upper_bound and agent_numbers[4] != prev_agent_numbers[4]:

        prev_agent_numbers[4] = agent_numbers[4]
        agent_numbers[4] = (lower_bound + upper_bound)//2
        
        BRFMins = 999
        prevBRFMins = 1000

        agent_numbers[3] = 0.5
        prev_agent_numbers[3] = 1

        BRFMins, targetMet = testBRF(agent_numbers,prev_agent_numbers, BRFMins, max_agent_numbers)         

        CREMins = BRFMins

        if targetMet:
            upper_bound = agent_numbers[4]
        else:
            lower_bound = agent_numbers[4]

    if targetMet:
        max_agent_numbers[4] = math.ceil(agent_numbers[4])
    
    optimalNums.append(agent_numbers[4])


    #Step 2: determine percentage served and wait-time using the combination determined in step 1

    my_bar.progress(25)
    
    totalEmployees = []
    for i in range(len(targetMetWaitingTimes)):
        totalNum = 0
        for j in range(len(targetMetWaitingTimes[i])):
            totalNum += targetMetWaitingTimes[i][j]

        totalEmployees.append(totalNum)

    bestComboTotal = min(totalEmployees)
    bestComboTotalIndex = totalEmployees.index(bestComboTotal)
    bestCombo = targetMetWaitingTimes[bestComboTotalIndex]

    agent_numbers = bestCombo

    wait_times.clear()

    random.seed(42)
    env = simpy.Environment()
    env.process(run_call_centre(env, agent_numbers))
    env.run(until=closing_time)
    waitTime = get_average_wait_time_mins(wait_times)

    percentCustomersServed = len(wait_times)/customer_ID

    
    prevWaitTime = 0

    # Step 3: Increase agents of other type to reduce number of rejected customers, while maintaining wait-time within target
    my_bar.progress(50)

    bestComboSorted = sorted(bestCombo)
    bestComboSorted = bestComboSorted[:-1]
    while len(bestComboSorted) > 0:
    
        nextLargest = bestComboSorted[-1]
        nextLargestIndex = bestCombo.index(nextLargest)
        agent_numbers,percentCustomersServed,waitTime = increaseNextLargest(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime,prevWaitTime,nextLargestIndex)
        prevWaitTime = 0
        bestComboSorted = bestComboSorted[:-1]

    for i in range(len(agent_numbers)):	
        agent_numbers[i] += 1	
        random.seed(42)	
        wait_times.clear()		
        env = simpy.Environment()	
        env.process(run_call_centre(env, agent_numbers))	
        env.run(until=closing_time)	
        waitTime = get_average_wait_time_mins(wait_times)	
        percentCustomersServed = len(wait_times)/customer_ID	

    while (waitTime > target or percentCustomersServed < servingTarget):
        for i in range(len(agent_numbers)):
            agent_numbers[i] += 1

        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID
 

    # Step 4.a): Determine how much each type of agent could be reduced 

    my_bar.progress(75)
    agent_numbers0,_,_ = decreaseNextLargest(agent_numbers.copy(),prev_agent_numbers,percentCustomersServed,waitTime,prevWaitTime,0)
    agent_numbers1,_,_ = decreaseNextLargest(agent_numbers.copy(),prev_agent_numbers,percentCustomersServed,waitTime,prevWaitTime,1)
    agent_numbers2,_,_ = decreaseNextLargest(agent_numbers.copy(),prev_agent_numbers,percentCustomersServed,waitTime,prevWaitTime,2)
    agent_numbers3,_,_ = decreaseNextLargest(agent_numbers.copy(),prev_agent_numbers,percentCustomersServed,waitTime,prevWaitTime,3)
    agent_numbers4,_,_ = decreaseNextLargest(agent_numbers.copy(),prev_agent_numbers,percentCustomersServed,waitTime,prevWaitTime,4)

    improvements = [agent_numbers[0]-agent_numbers0[0],agent_numbers[1]-agent_numbers1[1],agent_numbers[2]-agent_numbers2[2],agent_numbers[3]-agent_numbers3[3],agent_numbers[4]-agent_numbers4[4]]

    # Step 4.b): Decrease each type of agent as much as possible 

    my_bar.progress(88)
    improvementsSorted = sorted(improvements)
    while len(improvementsSorted) > 0:
        nextLargest = improvementsSorted[-1]
        nextLargestIndex = improvements.index(nextLargest)
        improvements[nextLargestIndex] = None
        agent_numbers,percentCustomersServed,waitTime = decreaseNextLargest(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime,prevWaitTime,nextLargestIndex)
        agent_numbers[nextLargestIndex] += 1
        prevWaitTime = 0
        improvementsSorted = improvementsSorted[:-1]

    for i in range(len(agent_numbers)):
        agent_numbers,percentCustomersServed,waitTime = decreaseNextLargest(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime,prevWaitTime,i)

    for i in range(len(agent_numbers)):
        if waitTime < target and percentCustomersServed > servingTarget:
            break
        
        agent_numbers[i] += 1
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID           

    my_bar.progress(100)
    return len(wait_times),percentCustomersServed,waitTime,agent_numbers  

def increaseNextLargest(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime,prevWaitTime,i):
    prevCustServed = 0  
    while (percentCustomersServed <=  servingTarget and prevCustServed != percentCustomersServed) or (percentCustomersServed >=  servingTarget and waitTime > target):	

        prevWaitTime = waitTime
        prevCustServed = percentCustomersServed
        prev_agent_numbers[i] = agent_numbers[i]
        agent_numbers[i] *= 2
        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID
        
    # find optimal number of ARF that meets wait time target
    # agent_numbers[i] = prev_agent_numbers[i]

    upper_bound = prev_agent_numbers[i]
    lower_bound = prev_agent_numbers[i]//2

    agent_numbers[i] = upper_bound
    prev_agent_numbers[i] = lower_bound

    prevWaitTime = 0
    prevCustServed = 0

    maxPercentServed = percentCustomersServed

    while lower_bound < upper_bound and agent_numbers[i] != prev_agent_numbers[i]:
        
        prevWaitTime = waitTime
        prevCustServed = percentCustomersServed
        prev_agent_numbers[i] = agent_numbers[i]
        agent_numbers[i] = (lower_bound + upper_bound)//2

        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID
        
        if percentCustomersServed == maxPercentServed or (percentCustomersServed > servingTarget) :
            upper_bound = agent_numbers[i]
        else:
            lower_bound = agent_numbers[i]

    if percentCustomersServed < servingTarget:
        lower_bound = agent_numbers[i]
        upper_bound = agent_numbers[i]*2

   

    agent_numbers[i] = upper_bound
    prev_agent_numbers[i] = lower_bound

    while lower_bound < upper_bound and agent_numbers[i] != prev_agent_numbers[i]:

        
        prevWaitTime = waitTime
        prev_agent_numbers[i] = agent_numbers[i]
        agent_numbers[i] = (lower_bound + upper_bound)//2

        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID

        if percentCustomersServed == maxPercentServed or (percentCustomersServed > servingTarget) :
            upper_bound = agent_numbers[i]
        else:
            lower_bound = agent_numbers[i]

    

    percentCustomersServed = servingTarget

    prevWaitTime = 0

    return agent_numbers,percentCustomersServed,waitTime

def decreaseAll(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime,prevWaitTime,i):

    # Step 6.0 decrease number of BRF while still meeting wait time and serving target
    lower_bound = 0
    upper_bound = agent_numbers[i]

    prev_agent_numbers[i] = 0

    while lower_bound < upper_bound and agent_numbers[i] != prev_agent_numbers[i]:


        prev_agent_numbers[i] = agent_numbers[i]
        agent_numbers[i] = (lower_bound + upper_bound)//2

        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID

        if percentCustomersServed > servingTarget and waitTime < target:
            upper_bound = agent_numbers[i]
        else:
            lower_bound = agent_numbers[i]

    if percentCustomersServed < servingTarget or waitTime < target:
        agent_numbers[i] = upper_bound

    return agent_numbers,percentCustomersServed,waitTime

def decreaseNextLargest(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime,prevWaitTime,i):

    # Step 6.0 decrease number of BRF while still meeting wait time and serving target
    lower_bound = 0
    upper_bound = agent_numbers[i]

    prev_agent_numbers[i] = 0

    while agent_numbers[i] > 0 and lower_bound < upper_bound and agent_numbers[i] != prev_agent_numbers[i]:
        

        prev_agent_numbers[i] = agent_numbers[i]
        agent_numbers[i] = (lower_bound + upper_bound)//2
        if agent_numbers[i] <= 0:
            break

        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID

        if percentCustomersServed > servingTarget and waitTime < target:
            upper_bound = agent_numbers[i]
        else:
            lower_bound = agent_numbers[i]

    if percentCustomersServed < servingTarget or waitTime < target:
        agent_numbers[i] = upper_bound

    return agent_numbers,percentCustomersServed,waitTime



def increaseARF(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime):

    while percentCustomersServed <=  servingTarget and prevWaitTime != waitTime:

        prevWaitTime = waitTime        
        prev_agent_numbers[1] = agent_numbers[1]
        agent_numbers[1] *= 2
        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID
 
        
    # find optimal number of ARF that meets wait time target
    agent_numbers[1] = prev_agent_numbers[1]

    lower_bound = prev_agent_numbers[1]
    upper_bound = agent_numbers[1]

    prevWaitTime = 0

    while lower_bound < upper_bound and agent_numbers[1] != prev_agent_numbers[1]:


        prev_agent_numbers[1] = agent_numbers[1]
        agent_numbers[1] = (lower_bound + upper_bound)//2

        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID
 

        if percentCustomersServed > servingTarget:
            upper_bound = agent_numbers[1]
        else:
            lower_bound = agent_numbers[1]

        if percentCustomersServed < servingTarget:
            agent_numbers[1] = upper_bound

        percentCustomersServed = servingTarget

        prevWaitTime = 0


    
    # Step 5.5 increase number of ARE to meet percentage served target
def increaseARE(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime):

    while percentCustomersServed <=  servingTarget and prevWaitTime != waitTime:

        prevWaitTime = waitTime        
        prev_agent_numbers[0] = agent_numbers[0]
        agent_numbers[0] *= 2
        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID

    lower_bound = prev_agent_numbers[0]
    upper_bound = agent_numbers[0]


    # Step 5.7 find optimal number of ARE to meet serving target
    
    while lower_bound < upper_bound and agent_numbers[0] != prev_agent_numbers[0]:

        prev_agent_numbers[0] = agent_numbers[0]
        agent_numbers[0] = (lower_bound + upper_bound)//2

        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID

        if percentCustomersServed > servingTarget:
            upper_bound = agent_numbers[0]
        else:
            lower_bound = agent_numbers[0]

    if percentCustomersServed < servingTarget:
        agent_numbers[0] = upper_bound

    percentCustomersServed = servingTarget

    prevWaitTime = 0
    # Step 5.8 increase number of BRF to meet percentage served target
    
def increaseBRF(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime):

    while percentCustomersServed <=  servingTarget and prevWaitTime != waitTime:

        prevWaitTime = waitTime        
        prev_agent_numbers[3] = agent_numbers[3]
        agent_numbers[3] *= 2
        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID

    lower_bound = prev_agent_numbers[3]
    upper_bound = agent_numbers[3]

    # Step 5.9 find optimal number of BRF to meet serving target
    
    while lower_bound < upper_bound and agent_numbers[3] != prev_agent_numbers[3]:

        prev_agent_numbers[3] = agent_numbers[3]
        agent_numbers[3] = (lower_bound + upper_bound)//2

        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID

        if percentCustomersServed > servingTarget:
            upper_bound = agent_numbers[3]
        else:
            lower_bound = agent_numbers[3]

    if percentCustomersServed < servingTarget:
        agent_numbers[3] = upper_bound

    percentCustomersServed = servingTarget
    
    prevWaitTime = 0
    # Step 5.92 increase number of CRE to meet percentage served target

def increaseCRE(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime):

    while percentCustomersServed <=  servingTarget and prevWaitTime != waitTime:

        prevWaitTime = waitTime        
        prev_agent_numbers[4] = agent_numbers[4]
        agent_numbers[4] *= 2
        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID
 

    lower_bound = prev_agent_numbers[4]
    upper_bound = agent_numbers[4]

    # Step 5.94 find optimal number of CRE to meet serving target
    
    while lower_bound < upper_bound and agent_numbers[4] != prev_agent_numbers[4]:



        prev_agent_numbers[4] = agent_numbers[4]
        agent_numbers[4] = (lower_bound + upper_bound)//2

        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID

        if percentCustomersServed > servingTarget:
            upper_bound = agent_numbers[4]
        else:
            lower_bound = agent_numbers[4]

    if percentCustomersServed < servingTarget:
        agent_numbers[4] = upper_bound

    percentCustomersServed = servingTarget

def decreaseBRF(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime):

    # Step 6.0 decrease number of BRF while still meeting wait time and serving target
    lower_bound = 0
    upper_bound = agent_numbers[3]

    prev_agent_numbers[3] = 0

    while lower_bound < upper_bound and agent_numbers[3] != prev_agent_numbers[3]:


        prev_agent_numbers[3] = agent_numbers[3]
        agent_numbers[3] = (lower_bound + upper_bound)//2

        random.seed(42)
        wait_times.clear()
    
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID
 

        if percentCustomersServed > servingTarget and waitTime < target:
            upper_bound = agent_numbers[3]
        else:
            lower_bound = agent_numbers[3]

    if percentCustomersServed < servingTarget or waitTime < target:
        agent_numbers[3] = upper_bound

def decreaseARF(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime):

        
    # Step 6.1 decrease number of ARF while still meeting wait time and serving target
    lower_bound = 0
    upper_bound = agent_numbers[1]

    prev_agent_numbers[1] = 0

    while lower_bound < upper_bound and agent_numbers[1] != prev_agent_numbers[1]:

        prev_agent_numbers[1] = agent_numbers[1]
        agent_numbers[1] = (lower_bound + upper_bound)//2

        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID

        if percentCustomersServed > servingTarget and waitTime < target:
            upper_bound = agent_numbers[1]
        else:
            lower_bound = agent_numbers[1]

    if percentCustomersServed < servingTarget or waitTime < target:
        agent_numbers[1] = upper_bound

def decreaseARE(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime):


    # Step 6.2 decrease number of ARE while still meeting wait time and serving target

    lower_bound = 0
    upper_bound = agent_numbers[0]

    prev_agent_numbers[0] = 0

    while lower_bound < upper_bound and agent_numbers[0] != prev_agent_numbers[0]:
        
        prev_agent_numbers[0] = agent_numbers[0]
        agent_numbers[0] = (lower_bound + upper_bound)//2

        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID

        if percentCustomersServed > servingTarget and waitTime < target:
            upper_bound = agent_numbers[0]
        else:
            lower_bound = agent_numbers[0]

    if percentCustomersServed < servingTarget or waitTime < target:
        agent_numbers[0] = upper_bound

def decreaseBRE(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime):

    # Step 6.3 decrease number of BRE while still meeting wait time and serving target

    lower_bound = 0
    upper_bound = agent_numbers[2]

    prev_agent_numbers[2] = 0

    while lower_bound < upper_bound and agent_numbers[2] != prev_agent_numbers[2]:
        
        prev_agent_numbers[2] = agent_numbers[2]
        agent_numbers[2] = (lower_bound + upper_bound)//2

        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID

        if percentCustomersServed > servingTarget and waitTime < target:
            upper_bound = agent_numbers[2]
        else:
            lower_bound = agent_numbers[2]

    if percentCustomersServed < servingTarget or waitTime < target:
        agent_numbers[2] = upper_bound

def decreaseCRE(agent_numbers,prev_agent_numbers,percentCustomersServed,waitTime):
  
    # Step 6.4 decrease number of CRE while still meeting wait time and serving target

    lower_bound = 0
    upper_bound = agent_numbers[4]

    prev_agent_numbers[4] = 0

    while lower_bound < upper_bound and agent_numbers[4] != prev_agent_numbers[4]:


        
        prev_agent_numbers[4] = agent_numbers[4]
        agent_numbers[4] = (lower_bound + upper_bound)//2

        random.seed(42)
        wait_times.clear()
        env = simpy.Environment()
        env.process(run_call_centre(env, agent_numbers))
        env.run(until=closing_time)
        waitTime = get_average_wait_time_mins(wait_times)

        percentCustomersServed = len(wait_times)/customer_ID
 

        if percentCustomersServed > servingTarget and waitTime < target:
            upper_bound = agent_numbers[4]
        else:
            lower_bound = agent_numbers[4]

    if percentCustomersServed < servingTarget or waitTime < target:
        agent_numbers[4] = upper_bound


    mins = get_average_wait_time_mins(wait_times)

# You can access the value at any point with:
    
def main():
    global customerArrivalTime
    global serviceTime
    global target
    global servingTarget
    global my_bar
    global closing_time
    
    st.text_input("Customer Arrival Interval (one customer every x mins)", key="arrivalRate")

    st.write("Enter Average Service Time of each Agent Type (in mins): ")

    col1, col2, col3, col4, col5  = st.columns(5)

    with col1:
        st.text_input("AE - Service A English:", key="AE")

    with col2:
        st.text_input("AF - Service A French:", key="AF")

    with col3:
        st.text_input("BE - Service B English:", key="BE")

    with col4:
        st.text_input("BF - Service B French:", key="BF")

    with col5:
        st.text_input("Service C Bilingual:", key="C")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.text_input("Wait Time Target (in mins)", key="waitTarget")

    with col2:
         st.text_input("Percentage Served Target", key="servingTarget")        

    with col3:
         st.text_input("Running Time (in mins)", key="runningTime")

    if st.button('run'):
        st.write("RUNNING")
        customerArrivalTime = (float)(st.session_state.arrivalRate)
        serviceTime = [(float)(st.session_state.AE),(float)(st.session_state.AF),(float)(st.session_state.BE),(float)(st.session_state.BF),(float)(st.session_state.C)]
        target = (float)(st.session_state.waitTarget)
        servingTarget = (float)(st.session_state.servingTarget)
        closing_time = (float)(st.session_state.runningTime)

        my_bar = st.progress(0)

        numServed,percentCustomersServed,waitTime,agent_numbers = simulate(customerArrivalTime,serviceTime,target,servingTarget)

        agent_numbers[2] = math.floor(agent_numbers[2])

        d = {"Total Customers Served: ": [str(numServed)],"Percentage of Customers Served: ": [str(percentCustomersServed)],"Average Wait Time ": [str(waitTime)+ " mins"] }
        df = pd.DataFrame(data=d)
        st.table(df)

        d = {"Type of Agent": ["AE agents","AF agents","BE agents","BF agents","C agents"],"# Needed": [str(agent_numbers[0]),str(agent_numbers[1]),str(agent_numbers[2]),str(agent_numbers[3]),str(agent_numbers[4])] }
        df = pd.DataFrame(data=d)
        st.table(df)

        data = {'AE agents':agent_numbers[0],'AF agents':agent_numbers[1],'BE agents':agent_numbers[2],'BF agents':agent_numbers[3],'C agents':agent_numbers[4]}
        AgentTypes = list(data.keys())
        values = list(data.values())

        fig = plt.figure(figsize = (10, 5))

        plt.bar(AgentTypes, values)
        plt.xlabel("Type of Agent")
        plt.ylabel("Number of Agents")
        plt.title("Optimal Distribution of Agents")
        st.pyplot(fig)
        
if __name__ == '__main__':
    main()
