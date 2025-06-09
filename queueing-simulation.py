import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import random

class MM1Queue:
    def __init__(self, arrival_rate, service_rate, simulation_time=10000):
      
        self.lembda = arrival_rate/60
        self.meu = service_rate/60
        self.rho = self.lembda / self.meu 

        self.current_time = 0
        self.next_arrival_time = self.generate_inter_arrival_time()
        self.next_departure_time = float('inf')
        
        
        self.ls = 0
        self.lq = 0
        self.customers_arrival_times = {}
        self.service_time = {}
        self.queue = deque()
        self.system_states={}
        self.system_state_counts = {}
        self.customers_served = 0
        self.total_system_time = 0
        self.total_queue_time = 0
        self.server_busy_time = 0
        self.busy = False
        self.simulation_time = simulation_time
        
        # Initialize missing variables
        self.area_under_curve_system = 0
        self.area_under_curve_queue = 0
        

    
    def generate_inter_arrival_time(self):
        y= np.random.exponential(1 / self.lembda)
        print(f"yyyyyyyyy+{y}")
        return y
    
    def generate_service_time(self):
        x= np.random.exponential(1 / self.lembda)
        print(f"xxxxxxxxx+{x}")
        return x

    
    def update_statistics(self, time_elapsed):
        
        self.area_under_curve_system += self.ls * time_elapsed
        self.area_under_curve_queue += self.lq * time_elapsed

        state = self.ls
        if state not in self.system_state_counts:
            self.system_state_counts[state] = 0
        self.system_state_counts[state] += time_elapsed
        
    
    def simulate(self):
       
        while self.current_time < self.simulation_time:  

            # Fix: Calculate time_elapsed correctly using min()
            time_elapsed = min(self.next_arrival_time, self.next_departure_time) - self.current_time
            if time_elapsed > 0:
                self.update_statistics(time_elapsed)
            
            if self.next_arrival_time < self.next_departure_time:  
                self.current_time = self.next_arrival_time

                # Fix: Use self.busy instead of undefined server_busy
                if not self.busy:
                    self.service_time = self.generate_service_time()
                    self.next_departure_time = self.current_time + self.service_time
                    self.busy = True  # Fix: Use self.busy
                    self.ls += 1
                   
                else:
                    self.queue.append(self.next_arrival_time)
                    self.ls += 1
                    self.lq += 1

                inter_arrival_time = self.generate_inter_arrival_time()
                self.next_arrival_time = self.current_time + inter_arrival_time
                
            else:
                # Fix: Use self.next_departure_time instead of undefined next_departure_time
                self.current_time = self.next_departure_time
                self.customers_served += 1
                self.ls -= 1
                
                if len(self.queue) > 0:

                    arrival_time = self.queue.popleft() 
                    self.lq -= 1
                    

                    queue_time = self.current_time - arrival_time  
                    
                    self.total_queue_time += queue_time
                    
                    service_time = self.generate_service_time()
                    # Fix: Use self.next_departure_time consistently
                    self.next_departure_time = self.current_time + service_time
                    
                    system_time = self.next_departure_time - arrival_time  
                    self.total_system_time += system_time

                else:
                    self.busy = False
                    self.next_departure_time = float('inf')  # Fix: Use self.next_departure_time
                     
        self.server_busy_time = self.simulation_time - sum(
            time for state, time in self.system_state_counts.items() if state == 0
        )
    
    def get_results(self):

        avg_customers_system = self.area_under_curve_system / self.simulation_time
        avg_customers_queue = self.area_under_curve_queue / self.simulation_time
        
        avg_system_time = self.total_system_time / self.customers_served if self.customers_served > 0 else 0
        avg_queue_time = self.total_queue_time / self.customers_served if self.customers_served > 0 else 0
        
        total_time = self.current_time  # Fix: Use simulation_time instead of current_time
        probabilities = {state: time/total_time for state, time in self.system_state_counts.items()}
        
        return {
            'customers_served': self.customers_served,
            'avg_customers_system': avg_customers_system,
            'avg_customers_queue': avg_customers_queue,
            'avg_system_time_min': avg_system_time,
            'avg_queue_time_min': avg_queue_time,
            'server_utilization': self.server_busy_time / self.simulation_time,
            'probabilities': probabilities
        }



# def theoretical_calculations(lam, mu):

#     # TODO: Calculate utilization factor ρ = λ/μ
#     # TODO: Calculate Ls = ρ/(1-ρ)
#     # TODO: Calculate Lq = ρ²/(1-ρ)
#     # TODO: Calculate Ws = 1/(μ-λ)
#     # TODO: Calculate Wq = λ/(μ(μ-λ))
#     # TODO: Calculate probabilities Pn = (1-ρ)ρⁿ
#     # TODO: Return all results in dictionary
#     pass

# def run_part1_theoretical():
#     """
#     Part 1: Manual theoretical calculations
#     λ = 4 customers/hour, μ = 12 customers/hour
#     """
#     # TODO: Call theoretical_calculations function
#     # TODO: Print all required results formatted nicely
#     # TODO: Convert times to hours and minutes
#     pass

# Fix: Remove self parameter from standalone function
def run_part2_simulation():
    print("M/M/1 Queue Simulation Analysis")
    print("=" * 50)

    lembda = 5  
    mu = 10  
    
    np.random.seed(42)  
    queue_sim = MM1Queue(lembda, mu, simulation_time=100)
    queue_sim.simulate()
    sim_results = queue_sim.get_results()
    
    if sim_results:
        print(f"Customers served: {sim_results['customers_served']}")
        print(f"Average customers in system: {sim_results['avg_customers_system']:.4f}")
        print(f"Average customers in queue: {sim_results['avg_customers_queue']:.4f}")
        print(f"Average time in system: {sim_results['avg_system_time_min']:.2f} minutes")
        print(f"Average time in queue: {sim_results['avg_queue_time_min']:.2f} minutes")
        print(f"Server utilization: {sim_results['server_utilization']:.4f}")
        print("State probabilities:")
        for state in sorted(sim_results['probabilities'].keys())[:4]:
            print(f"   P{state} = {sim_results['probabilities'].get(state, 0):.4f}")



# def run_part3_comparison(theoretical_results, simulation_results):
#     """
#     Part 3: Compare theoretical and simulation results
    
#     Args:
#         theoretical_results: results from theoretical calculations
#         simulation_results: results from simulation
#     """
#     # TODO: Create comparison table
#     # TODO: Calculate percentage differences
#     # TODO: Print formatted table
#     pass

def run_bonus_analysis():
    """
    Bonus: Analysis for different utilization factors
    """
    # TODO: Define scenarios with different ρ values
    # TODO: Run simulations for each scenario
    # TODO: Collect Wq values
    # TODO: Create plot comparing theoretical vs simulated Wq
    # TODO: Add smooth theoretical curve
    pass

def demonstrate_arrival_process():
    """
    Optional: Demonstrate how arrivals are generated
    """
    # TODO: Show example of inter-arrival time generation
    # TODO: Verify that mean matches 1/λ
    pass

if __name__ == "__main__":
    print("M/M/1 Queue Analysis")
    print("=" * 50)
    
    # # TODO: Run Part 1
    # print("\nPart 1: Theoretical Calculations")
    # theoretical_results = run_part1_theoretical()
    
    # TODO: Run Part 2  
    print("\nPart 2: Simulation Results")
    simulation_results = run_part2_simulation()
    
    # # TODO: Run Part 3
    # print("\nPart 3: Comparison")
    # run_part3_comparison(theoretical_results, simulation_results)
    
    # TODO: Run Bonus
    print("\nBonus: Different Utilization Factors")
    run_bonus_analysis()