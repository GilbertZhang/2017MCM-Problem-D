"""
Bank renege example

Covers:

- Resources: Resource
- Condition events

Scenario:
  A counter with a random service time and customers who renege. Based on the
  program bank08.py from TheBank tutorial of SimPy 2. (KGM)

"""
import random
import simpy
import copy
import pandas
import numpy
import scipy.stats as sci

# RANDOM_SEED = 50
NUM_OF_LAYERS = 3
RANDOM_SEED = 45

MIN_PATIENCE = 10000000  # Min. customer patience
MAX_PATIENCE = 30000000 # Max. customer patience
# TIME_IN_ZONE_A_reg = 1.0/0.079818  # service rate A
TIME_IN_ZONE_A_reg = 12.52857
TIME_IN_ZONE_B_reg = [32.305588, 2.172682]  # service rate B
TIME_IN_ZONE_C_reg = [11.6359, 7.54]  # service rate C
# TIME_IN_ZONE_A_pre = 1.0/0.079818  # service rate A
TIME_IN_ZONE_A_pre = 10.188888
TIME_IN_ZONE_B_pre = [32.305588, 2.172682]  # service rate B
TIME_IN_ZONE_C_pre = [11.6359, 7.54]  # service rate c
NUM_OF_SCANNING_MACHINE = 3
NUM_OF_SCANNING_MACHINE_PRE = 1


def NoInSystem(R):
    """ Total number of customers in the resource R"""
    return len(R.queue) + len(R.users)

def equal_ele(list1):
    for i in range(len(list1)-1):
        if list1[i] != list1[i+1]:
            return False
    return True

class customer_ob:
    def __init__(self, id):
        self.id = id
        self.pre_check = bool(int(random.random() + 0.45))  # True for pre checking, False for regular checking
        self.choice = 0

    def customer(self, env, name, counter1, counter2, counter3,
                 time_in_zone_A, time_in_zone_B,time_in_zone_C,
                 queueing_time, service_time, time_stamp, queue_length, choice_machine):
        """Customer arrives, is served and leaves."""
        arrive = env.now
        time_stamp[0][self.id] = arrive
        queue_length[0][self.id] = len(counter1.queue)

        # queue_length[1][self.id] = len(counter2[0].queue)
        # queue_length[2][self.id] = len(counter2[1].queue)
        # queue_length[3][self.id] = len(counter2[2].queue)
        #
        # queue_length[4][self.id] = len(counter3[0].queue)
        # queue_length[5][self.id] = len(counter3[1].queue)
        # queue_length[6][self.id] = len(counter3[2].queue)

        print('%7.4f %s: Arrival' % (arrive, name))
        finished1 = 0
        finished2 = 0
        # time3 = max(random.expovariate(1.0/time_in_zone_C[0]),
        #             random.expovariate(1.0 / time_in_zone_C[1]) + random.expovariate(1.0 / time_in_zone_C[1]) )
        if self.pre_check:
            time3 = random.expovariate(1.0/time_in_zone_C[1])
        else:
            time3 = random.expovariate(1.0/time_in_zone_C[0])


        with counter1.request() as req:
            patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
            # Wait for the counter or abort at the end of our tether
            results = yield req | env.timeout(patience)




            wait = env.now - arrive
            queueing_time[0][self.id] = wait


            if req in results:
                # We got to the counter
                print('%7.4f %s: Queueing time @ ZoneA %6.3f' % (env.now, name, wait))

                # normal distribution
                tib = random.expovariate(1.0 / time_in_zone_A)
                # tib = sci.truncnorm.rvs(time_in_zone_A[0],time_in_zone_A[1], loc=10.2,scale=2.98)
                service_time[0][self.id] = tib
                yield env.process(self.check_queue_queue(counter2,30))

                queue_length[1][self.id] = len(counter2[0].queue)
                queue_length[2][self.id] = len(counter2[1].queue)
                queue_length[3][self.id] = len(counter2[2].queue)

                yield env.timeout(tib)
                finished1 = env.now
                time_stamp[1][self.id] = finished1
                print('%7.4f %s: Finishing time @ ZoneA' % (env.now, name))
            else:
                # We reneged
                print('%7.4f %s: RENEGED after %6.3f' % (env.now, name, wait))

        #choice of scanning machine
        if self.pre_check:
            self.choice = 0
        else:
            Qlength = [NoInSystem(counter2[i]) for i in range(NUM_OF_SCANNING_MACHINE)]
            if equal_ele(Qlength):
                self.choice = int(random.random()*3)
            for i in range(NUM_OF_SCANNING_MACHINE):
                if Qlength[i] == 0 or Qlength[i] == min(Qlength):
                    self.choice = i  # the chosen queue number
                    break
        #
        # queue_length[1][self.id] = len(counter2[0].queue)
        # queue_length[2][self.id] = len(counter2[1].queue)
        # queue_length[3][self.id] = len(counter2[2].queue)


        with counter2[self.choice].request() as req:
            patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
            # Wait for the counter or abort at the end of our tether
            results = yield req | env.timeout(patience)


            wait = env.now - finished1
            queueing_time[1][self.id] = wait

            if req in results:
                # We got to the counter
                print('%7.4f %s: Queueing time @ ZoneB %6.3f' % (env.now, name, wait))

                if self.pre_check:
                    tib = 0.3 * max(time_in_zone_B[0] * numpy.random.weibull(time_in_zone_B[1],1) - time3,0)
                else:
                    tib = max(time_in_zone_B[0] * numpy.random.weibull(time_in_zone_B[1],1) - time3,0)

                service_time[1][self.id] = tib

                yield env.process(self.check_queue_queue(counter3,8))
                yield env.timeout(tib)
                finished2 = env.now
                time_stamp[2][self.id] = finished2
                print('%7.4f %s: Finishing time @ ZoneB' % (env.now, name))
            else:
                # We reneged
                print('%7.4f %s: RENEGED after %6.3f' % (env.now, name, wait))

        queue_length[4][self.id] = len(counter3[0].queue)
        queue_length[5][self.id] = len(counter3[1].queue)
        queue_length[6][self.id] = len(counter3[2].queue)
        # print len(counter3[self.choice].queue)


        with counter3[self.choice].request() as req:
            # yield env.process(self.check_queue_queue(counter3[self.choice]))
            patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
            # Wait for the counter or abort at the end of our tether
            # yield waituntil(env,check_queue_length(counter3[self.choice]))
            results = yield req | env.timeout(patience)

            wait = env.now - finished2
            queueing_time[2][self.id] = wait

            if req in results:
                # We got to the counter
                print('%7.4f %s: Queueing time @ ZoneC %6.3f' % (env.now, name, wait))

                tib = time3
                service_time[2][self.id] = tib
                yield env.timeout(tib)
                time_stamp[3][self.id] = env.now
                print('%7.4f %s: Finishing time @ ZoneC' % (env.now, name))

            else:
                # We reneged
                print('%7.4f %s: RENEGED after %6.3f' % (env.now, name, wait))

        choice_machine[self.id] = self.choice

    def check_queue_queue(self, R, i, duration=1):
        # yield env.timeout(duration)
        while len(R[0].queue) > i or len(R[1].queue) > i or len(R[2].queue) > i:
            yield env.timeout(duration)


def check_queue_length():
    return bool(int(random.random() + 0.5))

def waituntil(env, check_queue_length, delay=1):
    while not check_queue_length():
        yield env.timeout(delay)

class SecurityCheck:
    def __init__(self,new_customers,time_in_zone_A_reg, time_in_zone_B_reg, time_in_zone_C_reg,
                 time_in_zone_A_pre, time_in_zone_B_pre, time_in_zone_C_pre):
        self.queueing_time = [[0] * new_customers, [0] * new_customers, [0] * new_customers]
        self.service_time = [[0] * new_customers, [0] * new_customers, [0] * new_customers]
        self.time_stamp = [[0] * new_customers, [0] * new_customers, [0] * new_customers, [0] * new_customers]
        self.queue_length = [[0] * new_customers, [0] * new_customers, [0] * new_customers,
                             [0] * new_customers, [0] * new_customers,
                             [0] * new_customers, [0] * new_customers]
        self.pre_check = [0] * new_customers
        self.choice_machine = [0] * new_customers
        self.time_interval = [0] * new_customers
        self.time_in_zoneA_pre = time_in_zone_A_pre
        self.time_in_zoneB_pre = time_in_zone_B_pre
        self.time_in_zoneC_pre = time_in_zone_C_pre
        self.time_in_zoneA_reg = time_in_zone_A_reg
        self.time_in_zoneB_reg = time_in_zone_B_reg
        self.time_in_zoneC_reg = time_in_zone_C_reg

    def source(self,env, number, interval,
               counter1_pre, counter2_pre, counter3_pre,
               counter1_reg, counter2_reg, counter3_reg):
        """Source generates customers randomly"""
        for i in range(number):
            customeri = customer_ob(i)
            self.pre_check[i] = customeri.pre_check
            # pre-check and normal check
            if customeri.pre_check:
                c = customeri.customer(env, 'Customer%02d' % i, counter1_pre, counter2_pre, counter3_pre,
                                       self.time_in_zoneA_pre, self.time_in_zoneB_pre, self.time_in_zoneC_pre,
                                       self.queueing_time, self.service_time, self.time_stamp, self.queue_length, self.choice_machine)
            else:
                c = customeri.customer(env, 'Customer%02d' % i, counter1_reg, counter2_reg, counter3_reg,
                                       self.time_in_zoneA_reg, self.time_in_zoneB_reg, self.time_in_zoneC_reg,
                                       self.queueing_time, self.service_time, self.time_stamp, self.queue_length, self.choice_machine)
            env.process(c)
            t = random.expovariate(1.0 / interval)
            self.time_interval[i] = t
            yield env.timeout(t)


# Setup and start the simulation
print('Bank renege')
random.seed(RANDOM_SEED)
numpy.random.seed(RANDOM_SEED)
env = simpy.Environment()



# Start processes and run
counter1_reg = simpy.Resource(env, capacity=5)

counter2_reg = [simpy.Resource(env, capacity=1), simpy.Resource(env, capacity=1), simpy.Resource(env, capacity=1)]
counter3_reg = [simpy.Resource(env, capacity=1), simpy.Resource(env, capacity=1), simpy.Resource(env, capacity=1)]
counter1_pre = simpy.Resource(env, capacity=2)
counter2_pre = [simpy.Resource(env, capacity=1), simpy.Resource(env, capacity=1), simpy.Resource(env, capacity=1)]
counter3_pre = [simpy.Resource(env, capacity=1), simpy.Resource(env, capacity=1), simpy.Resource(env, capacity=1)]

NEW_CUSTOMERS = 1000  # Total number of customers
INTERVAL_CUSTOMERS = 3600.0/1327.0#1.0/0.3687  # Generate new customers roughly every x seconds

regular = SecurityCheck(NEW_CUSTOMERS,
                        TIME_IN_ZONE_A_reg,TIME_IN_ZONE_B_reg,TIME_IN_ZONE_C_reg,
                        TIME_IN_ZONE_A_pre,TIME_IN_ZONE_B_pre,TIME_IN_ZONE_C_pre)
env.process(regular.source(env, NEW_CUSTOMERS, INTERVAL_CUSTOMERS,
                           counter1_pre, counter2_pre, counter3_pre,
                           counter1_reg, counter2_reg, counter3_reg))
env.run()

# Export to csv file
waiting_time = [0] * NEW_CUSTOMERS
for i in range(len(regular.time_stamp[0])):
    waiting_time[i] = regular.time_stamp[3][i] - regular.time_stamp[0][i]
dataframe1 = pandas.DataFrame(numpy.array(regular.time_stamp + [waiting_time] + regular.queueing_time + regular.service_time + regular.queue_length + [regular.choice_machine] + [regular.pre_check]).T,
                              columns=['arrivalA','arrivalB','arrivalC','leaveC','waiting time','QtimeA','QtimeB','QtimeC','serviceTA','serviceTB','serviceTC','Qlen_A','QlenB0','QlenB1','QlenB2','QlenC0','QlenC1','QlenC2','choice','precheck'])
dataframe1.to_csv("question3_original.csv")
