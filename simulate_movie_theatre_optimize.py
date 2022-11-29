import simpy
import random
import statistics
import csv

from collections import deque

wait_times = []
# wait-time target
target = 10
closing_time = 90

class Theater(object):
    def __init__(self, env, num_cashiers, num_servers, num_ushers):
        # More to come!
        self.env = env
        self.cashier = simpy.Resource(env, num_cashiers)
        self.server = simpy.Resource(env, num_servers)
        self.usher = simpy.Resource(env, num_ushers)

    def purchase_ticket(self, moviegoer):
        yield self.env.timeout(random.randint(1, 3))

    def check_ticket(self, moviegoer):
        yield self.env.timeout(0.05)

    def sell_food(self, moviegoer):
        yield self.env.timeout(random.randint(1, 5))

def go_to_movies(env, moviegoer, theater):
        # Moviegoer arrives at the theater
        arrival_time = env.now

        with theater.cashier.request() as request:
            yield request
            yield env.process(theater.purchase_ticket(moviegoer))

        with theater.usher.request() as request:
            yield request
            yield env.process(theater.check_ticket(moviegoer))

        if random.choice([True, False]):
            with theater.server.request() as request:
                yield request
                yield env.process(theater.sell_food(moviegoer))

        # Moviegoer heads into the theater
        wait_times.append(env.now - arrival_time)


def run_theater(env, num_cashiers, num_servers, num_ushers):
    theater = Theater(env, num_cashiers, num_servers, num_ushers)
  
    for moviegoer in range(3):
        env.process(go_to_movies(env, moviegoer, theater))

    #while True:
    #while env.now < 60:
    while not wait_times  or (wait_times[-1] < (closing_time - env.now)) :
        yield env.timeout(0.20)  # Wait a bit before generating a new person

        moviegoer += 1
        env.process(go_to_movies(env, moviegoer, theater))

def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)

    # Pretty print the results
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds) 
        
def get_user_input():
    num_cashiers = input("Input # of cashiers working: ")
    num_servers = input("Input # of servers working: ")
    num_ushers = input("Input # of ushers working: ")
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
    # Setup
    random.seed(42)
    #num_cashiers, num_servers, num_ushers = get_user_input()


    #num_cashiers, num_servers, num_ushers = [9,9,9]
    # Run the simulation
    #env = simpy.Environment()
    #env.process(run_theater(env, num_cashiers, num_servers, num_ushers))
    #env.run(until=90)

    # View the results
    #mins, secs = get_average_wait_time(wait_times)
    '''if mins <= 10:
      print(
          "Running simulation...",
          f"\nThe average wait time is {mins} minutes and {secs} seconds with {num_cashiers} cashiers, {num_servers} servers, and {num_ushers} ushers.",
      )  '''



    ''' for i in range(10,1,-1):
      for j in range(10,1,-1):
            for k in range(10,1,-1):
              num_cashiers, num_servers, num_ushers = [i,j,k]
              # Run the simulation
              env = simpy.Environment()
              env.process(run_theater(env, num_cashiers, num_servers, num_ushers))
              env.run(until=90)

                  # View the results
                  mins, secs = get_average_wait_time(wait_times)
                  if mins == 10:
                      print(
                          
                          f"\nThe average wait time is {mins} minutes and {secs} seconds with {num_cashiers} cashiers, {num_servers} servers, and {num_ushers} ushers.",
                      )
    '''

    #Step 1: Find first combo with wait time < target 

    # Initializing a queue
    q = deque()
      
    # Adding elements to a queue
    q.append([1,1,1])
      
    print("Initial queue")
    print(q)

    dequeuedElem = [0]
    mins = 999

    while mins > target:
        # Removing elements from a queue
        print("\nElements dequeued from the queue")
        dequeuedElem = list(q.popleft())
        origDequeuedElem = list(dequeuedElem)
        print(dequeuedElem)

        for i in range(len(dequeuedElem)):
             dequeuedElem[i] *= 2
             q.append(dequeuedElem)
             dequeuedElem = list(origDequeuedElem)

        wait_times.clear()
        env = simpy.Environment()
        env.process(run_theater(env, origDequeuedElem[0], origDequeuedElem[1], origDequeuedElem[2]))
        env.run(until=closing_time)

        # View the results
        mins, secs = get_average_wait_time(wait_times)
        print(mins)
    
        #print("\nQueue after appending new elements")
        #print(q)

    print(origDequeuedElem)

    #Step 2: Find optimal combo with wait time < target 

    prev_num_cashiers = origDequeuedElem[0] / 2
    num_cashiers = origDequeuedElem[0]
    
    lower_bound = origDequeuedElem[0] / 2
    upper_bound = origDequeuedElem[0]

    print("LB: " + str(lower_bound ))
    print("UB: " + str(upper_bound ))

    #num_cashiers, num_servers, num_ushers = [0.5,0.5,0.5]
    #prev_num_cashiers, prev_num_servers, prev_num_ushers = [1,1,1]

    # find optimal number of cashiers

    tenMinWaitingTimes = []

    while lower_bound < upper_bound and num_cashiers != prev_num_cashiers:


        print("LB: " + str(lower_bound ))
        print("UB: " + str(upper_bound ))
        

        #print("BBB")
        prev_num_cashiers = num_cashiers
        num_cashiers = (lower_bound + upper_bound)//2
        
        serverMins = 999
        prevServerMins = 1000

        num_servers = 0.5
        prev_num_servers = 1

        while num_servers < origDequeuedElem[1] :

            #print("AAA")

            prevServerMins = serverMins
            prev_num_servers = num_servers
            num_servers *= 2

            usherMins = 999
            prevUsherMins = 1000

            num_ushers = 0.5

            #print(usherMins)
            #print(prevUsherMins)
            #print(usherMins > 10 and usherMins < prevUsherMins)

            num_ushers = 0.5
            prev_num_ushers = 1
            
            while num_ushers < origDequeuedElem[2]:
                    #while mins < prevUsherMins:

                    prevUsherMins = usherMins 
                    #prevUsherSecs = secs
                    
                    #print(num_cashiers, num_servers, num_ushers)
                    random.seed(42)
                    prev_num_ushers = num_ushers
                    num_ushers *= 2  
                    # Run the simulation

                    #num_cashiers, num_servers, num_ushers = 10, 13, 7
                    wait_times.clear()

                    print(num_cashiers, num_servers, num_ushers)
                    env = simpy.Environment()
                    env.process(run_theater(env, num_cashiers, num_servers, num_ushers))
                    env.run(until=90)

                    # View the results
                    print("Bef " + str(usherMins))
                    usherMins, secs = get_average_wait_time(wait_times)
                    print("Aft " + str(usherMins))

                    if prevUsherMins <= usherMins and prevUsherSecs == secs:
                      break

                    output = [num_cashiers, num_servers, num_ushers, usherMins, secs]

                    with open('output.csv','a') as f:
                      # create the csv writer
                      writer = csv.writer(f)

                      # write a row to the csv file
                      writer.writerow(output)

                    print("usherMins " + str(usherMins))

                    if usherMins <= target:
                      print(
                          
                          f"\nThe average wait time is {usherMins} minutes and {secs} seconds with {num_cashiers} cashiers, {num_servers} servers, and {num_ushers} ushers.",
                      )
                      tenMinWaitingTimes.append([num_cashiers, num_servers, num_ushers])

                    #print(num_cashiers, num_servers, num_ushers)
                    
                    #prevUsherMins = mins
                    #prevUsherSecs = secs            

                    # while loop exited = first number of ushers with < 10mins wait time has been found or 10mins can't be reached

                    # find lowest number of ushers with < 10mins wait time

                    if usherMins <= target:
                        prevLessThanTenMins = True
                    else:
                        prevLessThanTenMins = False

                    #lower_bound = prev_num_ushers
                    #upper_bound = num_ushers

                    #print(usherMins)
                    #print(prevUsherMins)
                    #print(usherMins > 10 and usherMins < prevUsherMins)

            serverMins = usherMins
            print("serverMins: " + str(serverMins))
            #print("PrevServerMins: " + str(prevServerMins))

        cashierMins = usherMins

        if prevLessThanTenMins:
            upper_bound = num_cashiers
        else:
            lower_bound = num_cashiers

    print(tenMinWaitingTimes)
    #tenMinWaitingTimes contains all optimal combinations 

    #find combination with least number of employees 
    totalEmployees = []
    for i in range(len(tenMinWaitingTimes)):
        totalNum = 0
        for j in range(len(tenMinWaitingTimes[i])):
            totalNum += tenMinWaitingTimes[i][j]

        totalEmployees.append(totalNum)

    bestComboTotal = min(totalEmployees)
    bestComboTotalIndex = totalEmployees.index(bestComboTotal)
    bestCombo = tenMinWaitingTimes[bestComboTotalIndex]
    
    print(bestCombo)

        
    
    '''
    tenMinWaitingTimes = []
    num_cashiers, num_servers, num_ushers = [1,1,1]

    mins = 999

    prevUsherMins = 0
    prevUsherSecs = 0

    prevServerMins = 0
    prevServerSecs = 0

    prevCashierMins = 0
    prevCashierSecs = 0

    output = ["num_cashiers", "num_servers", "num_ushers", "mins", "secs"]

    with open('output.csv','a') as f:
                      # create the csv writer
                      writer = csv.writer(f)

                      # write a row to the csv file
                      writer.writerow(output)

    while mins > 10 and num_cashiers < 25:
            random.seed(42)
            num_cashiers += 1
            wait_times.clear()

            env = simpy.Environment()
            env.process(run_theater(env, num_cashiers, num_servers, num_ushers))
            env.run(until=90)

            # View the results
            mins, secs = get_average_wait_time(wait_times)

            with open('output.csv','a') as f:
                      # create the csv writer
                      writer = csv.writer(f)

                      # write a row to the csv file
                      writer.writerow(output)
            
            if prevCashierMins <= mins and prevCashierSecs == secs:
                break

            print(
                      
                    f"\nThe average wait time is {mins} minutes and {secs} seconds with {num_cashiers} cashiers, {num_servers} servers, and {num_ushers} ushers.",
            )
            
            if mins <= 10:
                print(
                      
                    f"\nThe average wait time is {mins} minutes and {secs} seconds with {num_cashiers} cashiers, {num_servers} servers, and {num_ushers} ushers.",
                )
                tenMinWaitingTimes.append([num_cashiers, num_servers, num_ushers])
                break

            prevCashierMins = mins
            prevCashierSecs = secs
          
            while mins > 10 and num_servers < 25:
                random.seed(42)
                num_servers += 1
                wait_times.clear()
                
                env = simpy.Environment()
                env.process(run_theater(env, num_cashiers, num_servers, num_ushers))
                env.run(until=90)

                # View the results
                mins, secs = get_average_wait_time(wait_times)

                with open('output.csv','a') as f:
                      # create the csv writer
                      writer = csv.writer(f)

                      # write a row to the csv file
                      writer.writerow(output)
                
                if prevServerMins <= mins and prevServerSecs == secs:
                      break
                
                if mins <= 10:
                    print(
                          
                        f"\nThe average wait time is {mins} minutes and {secs} seconds with {num_cashiers} cashiers, {num_servers} servers, and {num_ushers} ushers.",
                    )
                    tenMinWaitingTimes.append([num_cashiers, num_servers, num_ushers])
                    break

                prevServerMins = mins
                prevServerSecs = secs
                
                while mins > 10 and num_ushers < 25 :
                  random.seed(42)
                  num_ushers += 1  
                  # Run the simulation

                  #num_cashiers, num_servers, num_ushers = 10, 13, 7
                  wait_times.clear()
                  
                  print(num_cashiers, num_servers, num_ushers)
                  env = simpy.Environment()
                  env.process(run_theater(env, num_cashiers, num_servers, num_ushers))
                  env.run(until=90)

                  # View the results
                  mins, secs = get_average_wait_time(wait_times)

                  if prevUsherMins <= mins and prevUsherSecs == secs:
                      break

                  output = [num_cashiers, num_servers, num_ushers, mins, secs]
                   
                  with open('output.csv','a') as f:
                      # create the csv writer
                      writer = csv.writer(f)

                      # write a row to the csv file
                      writer.writerow(output)

                  #print(mins)
                  
                  if mins <= 10:
                      print(
                          
                          f"\nThe average wait time is {mins} minutes and {secs} seconds with {num_cashiers} cashiers, {num_servers} servers, and {num_ushers} ushers.",
                      )
                      tenMinWaitingTimes.append([num_cashiers, num_servers, num_ushers])

                  prevUsherMins = mins
                  prevUsherSecs = secs

                
                num_ushers = 1
                mins = 999

            num_servers = 1
            mins = 999

    print(tenMinWaitingTimes)
    #tenMinWaitingTimes contains all optimal combinations 

    #find combination with least number of employees 
    totalEmployees = []
    for i in range(len(tenMinWaitingTimes)):
        totalNum = 0
        for j in range(len(tenMinWaitingTimes[i])):
            totalNum += tenMinWaitingTimes[i][j]

        totalEmployees.append(totalNum)

    bestComboTotal = min(totalEmployees)
    bestComboTotalIndex = totalEmployees.index(bestComboTotal)
    bestCombo = tenMinWaitingTimes[bestComboTotalIndex]
    
    print(bestCombo)
    '''

    '''num_cashiers, num_servers, num_ushers = [1,1,1]

    mins = 999

    count = 0
    while mins > 10:
        if count%3 == 0:
            num_cashiers += 1
        elif count%3 == 1:
            num_servers += 1
        elif count%3 == 2:
            num_ushers += 1

        # Run the simulation
        env = simpy.Environment()
        env.process(run_theater(env, num_cashiers, num_servers, num_ushers))
        env.run(until=90)
        mins, secs = get_average_wait_time(wait_times)
        count += 1

    print(f"\nThe average wait time is {mins} minutes and {secs} seconds with {num_cashiers} cashiers, {num_servers} servers, and {num_ushers} ushers")
    '''
def main():
    simulate()

if __name__ == '__main__':
    main()
