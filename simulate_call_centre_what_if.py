import simpy
import random
import statistics


wait_times = []
customerArrivalTime = 0.003965607 # time between customers
serviceTime = 16.425
numAgents = 1369
closing_time = 90

customer_ID = 0


global AREgenerated
AREgenerated = 0
global ARFgenerated 
ARFgenerated = 0
global BREgenerated 
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
    def __init__(self,env,num_agentsARE,num_agentsARF,num_agentsBRE):
        # More to come!
        self.env = env
        self.agentsARE = simpy.Resource(env, num_agentsARE)
        self.agentsARF = simpy.Resource(env, num_agentsARF)
        self.agentsBRE = simpy.Resource(env, num_agentsBRE)

    def handle_customer(self, customer):
        yield self.env.timeout(serviceTime)

    def handle_customerARE(self, customer):
        yield self.env.timeout(serviceTime)

    def handle_customerARF(self, customer):
        yield self.env.timeout(serviceTime)

    def handle_customerBRE(self, customer):
        yield self.env.timeout(serviceTime)

def place_call(env, customer, call_centre):
        # Customer places call with call centre
        arrival_time = env.now

        global AREserved
        global ARFserved
        global BREserved

        if customer.department == 'A':
            if customer.english: 
                with call_centre.agentsARE.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customerARE(customer))
                    AREserved += 1
            else:
                with call_centre.agentsARF.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customerARF(customer))
                    ARFserved += 1
        elif customer.department == 'B':
            if customer.english: 
                with call_centre.agentsBRE.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customerBRE(customer))
                    BREserved += 1
            else:
                with call_centre.agentsBRF.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer))
        elif customer.department == 'C':
            if customer.english: 
                with call_centre.agentsCRE.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer))
            else:
                with call_centre.agentsCRF.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer))
        elif customer.department == 'D':
            if customer.english: 
                with call_centre.agentsDRE.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer))
            else:
                with call_centre.agentsDRF.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer))
        elif customer.department == 'E':
            if customer.english: 
                with call_centre.agentsERE.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer))
            else:
                with call_centre.agentsERF.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer))
        elif customer.department == 'F':
            if customer.english: 
                with call_centre.agentsFRF.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer))
            else:
                with call_centre.agentsFRF.request() as request:
                    yield request
                    yield env.process(call_centre.handle_customer(customer))
        
        

        # Customer ends call with call centrer
        wait_times.append(env.now - arrival_time)


def run_call_centre(env, num_agentsARE, num_agentsARF, num_agentsBRE):
    call_centre = Call_Centre(env,num_agentsARE, num_agentsARF, num_agentsBRE)

    global AREgenerated
    global ARFgenerated
    global BREgenerated
    global customer_ID
    global customers


    # customers already calling when call_centre opens  
    for customer_ID in range(3):
        langGen =  random.random()
        if langGen <= 0.77:
            english = True
            deptGen = random.randint(0,1241)
            if deptGen <= 637:
                dept = "A"
                customers.append("ARE")
            elif deptGen <= 1241:
                dept = "B"
                customers.append("BRE")
        else:
            english = False
            deptGen = random.randint(0,506)
            if deptGen <= 174:
                dept = "A"
                customers.append("ARF")
            elif deptGen <= 506:
                dept = "A"
                customers.append("ARF")


        customer = Customer(customer_ID, dept ,english)

        
        env.process(place_call(env, customer, call_centre))  


    while not wait_times  or (wait_times[-1] < (closing_time - env.now)) :
        yield env.timeout(customerArrivalTime)  # Wait a bit before generating a new person

        customer_ID += 1
        
        langGen =  random.random()
        if langGen <= 0.77:
            english = True
            deptGen = random.randint(0,1241)
            if deptGen <= 637:
                dept = "A"
                customers.append("ARE")
                AREgenerated += 1
            elif deptGen <= 1241:
                dept = "B"
                customers.append("BRE")
                BREgenerated += 1
            
        else:
            english = False
            deptGen = random.randint(0,506)
            if deptGen <= 174:
                dept = "A"
                customers.append("ARF")
                ARFgenerated += 1
            elif deptGen <= 506:
                dept = "A"
                customers.append("ARF")
                ARFgenerated += 1
            

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
    num_cashiers = input("Input # of ARE working: ")
    num_servers = input("Input # of ARF working: ")
    num_ushers = input("Input # of BRE working: ")
    params = [num_cashiers, num_servers, num_ushers]
    if all(str(i).isdigit() for i in params):  # Check input is valid
        params = [int(x) for x in params]
    else:
        print(
             "Could not parse input. The simulation will use default values:",
            "\n1 cashier, 1 server, 1 usher.",
        ) 
        params = [1, 1, 1]
    return params

def simulate():
    
    random.seed(42)

    num_agentsARE, num_agentsARF, num_agentsBRE = get_user_input()

    num_agents = numAgents

    # Run the simulation
    env = simpy.Environment()
    env.process(run_call_centre(env, num_agentsARE, num_agentsARF, num_agentsBRE))

    # runs until environment time reaches until value given
    env.run(until=closing_time)

    print(wait_times)
    print("Number served: " + str(len(wait_times)))
    print(max(wait_times))
    
    mins = get_average_wait_time_mins(wait_times) - serviceTime

    
    print(
      "Running simulation...",
      f"\nThe average wait time is {mins} minutes",
    )


    percentCustomersServed = len(wait_times)/customer_ID
    print("Percent Served =" + str(percentCustomersServed))    

    
def main():
    simulate()

if __name__ == '__main__':
    main()
