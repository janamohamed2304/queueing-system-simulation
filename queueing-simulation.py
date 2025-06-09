import numpy as np
from collections import deque
import matplotlib.pyplot as plt

def theoretical_mm1(lam, mu):
    rho = lam / mu
    if rho >= 1:
        return None
    return {
        'rho': rho,
        'Ls': rho / (1 - rho),
        'Lq': rho**2 / (1 - rho),
        'Ws_mins': 60 / (mu - lam),
        'Wq_mins': (lam / (mu * (mu - lam))) * 60,
        'P': lambda n: (1 - rho) * rho**n
    }

class MM1Sim:
    def __init__(self, lam, mu, sim_minutes=20000):
        self.lam = lam / 60  # Convert to per minute
        self.mu = mu / 60
        self.T = sim_minutes

    def run(self):
        t = 0
        queue = deque()
        busy = False
        next_dep = np.inf
        served = 0
        total_wait_time = 0  # Total waiting time in queue
        total_system_time = 0  # Total time in system
        ns = 0
        nts = {}
        arrivals = []  # Store arrival times

        next_arr = np.random.exponential(1 / self.lam)

        while t < self.T:
            nxt = min(next_arr, next_dep)
            # Track time-weighted number in system and queue
            nts[ns] = nts.get(ns, 0) + (nxt - t)
            t = nxt

            if next_arr < next_dep:  # Arrival event
                arrivals.append(t)
                ns += 1
                if not busy:
                    busy = True
                    next_dep = t + np.random.exponential(1 / self.mu)
                else:
                    queue.append(t)
                next_arr = t + np.random.exponential(1 / self.lam)
            else:  # Departure event
                # Customer leaves - calculate their times
                if arrivals:
                    arrival_time = arrivals.pop(0)
                    total_system_time += (t - arrival_time)
                
                if queue:
                    # Customer was waiting in queue
                    queue_arrival = queue.popleft()
                    total_wait_time += (t - queue_arrival)
                    next_dep = t + np.random.exponential(1 / self.mu)
                else:
                    busy = False
                    next_dep = np.inf
                served += 1
                ns -= 1

        util = (self.T - nts.get(0, 0)) / self.T
        
        # Calculate averages
        Ls_sim = sum(n * time for n, time in nts.items()) / self.T
        Lq_sim = sum(max(0, n-1) * time for n, time in nts.items()) / self.T if busy else sum(n * time for n, time in nts.items()) / self.T
        
        return {
            'served': served,
            'Ls_sim': Ls_sim,
            'Lq_sim': Lq_sim,
            'Ws_sim': (total_system_time / served) if served else 0,
            'Wq_sim': (total_wait_time / served) if served else 0,
            'util_sim': util,
            'nts': {n: time/self.T for n, time in nts.items()}
        }

if __name__ == "__main__":
    scenarios = [(4, 12), (6, 12), (10.8, 12)]
    np.random.seed(42)

    rhos, Wqs_sim, Wqs_theor = [], [], []

    for lam, mu in scenarios:
        theor = theoretical_mm1(lam, mu)
        sim = MM1Sim(lam, mu).run()

        print(f"\nScenario: lam={lam}, mu={mu}")
        print("Metric      Theoretical    Simulation")
        print(f"rho         {theor['rho']:.4f}        {sim['util_sim']:.4f}")
        print(f"Ls          {theor['Ls']:.4f}        {sim['Ls_sim']:.4f}")
        print(f"Lq          {theor['Lq']:.4f}        {sim['Lq_sim']:.4f}")
        print(f"Ws (min)    {theor['Ws_mins']:.4f}      {sim['Ws_sim']:.4f}")
        print(f"Wq (min)    {theor['Wq_mins']:.4f}      {sim['Wq_sim']:.4f}")

        # Print probabilities P0, P1, P2, P3
        for n in range(4):
            p_theor = theor['P'](n)
            p_sim = sim['nts'].get(n, 0)
            print(f"P{n}         Theor: {p_theor:.4f}, Sim: {p_sim:.4f}")

        # Print time proportions
        print("\nProportion of time with n customers:")
        for n in sorted(sim['nts']):
            print(f"n = {n}: {sim['nts'][n]:.4f}")

        rhos.append(theor['rho'])
        Wqs_sim.append(sim['Wq_sim'])
        Wqs_theor.append(theor['Wq_mins'])

    # Plot Wq vs rho - Fixed to show both lines on same plot
    plt.figure(figsize=(10, 6))
    plt.plot(rhos, Wqs_theor, label='Theoretical Wq', marker='o', linewidth=2)
    plt.plot(rhos, Wqs_sim, label='Simulated Wq', marker='x', linewidth=2)
    plt.xlabel('Utilization (ρ)')
    plt.ylabel('Avg Waiting Time in Queue (minutes)')
    plt.title('Wq vs Utilization')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()