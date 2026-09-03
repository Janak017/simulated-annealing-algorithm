import math
import random
import numpy as np
import matplotlib.pyplot as plt

# --- 1. PARAMETERS ---
NUM_CITIES = 20
INITIAL_TEMPERATURE = 1000
MIN_TEMPERATURE = 10**-3
COOLING_RATE = 0.995
ITERATIONS_PER_TEMP = 100
RANDOM_SEED = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# --- 2. CITY DATA ---
NEPAL_CITIES = {
    "Kathmandu":   (85.3240, 27.7172),
    "Pokhara":     (83.9856, 28.2096),
    "Lalitpur":    (85.3247, 27.6588),
    "Biratnagar":  (87.2718, 26.4525),
    "Bharatpur":   (84.4380, 27.6766),
    "Birgunj":     (84.8770, 27.0104),
    "Dharan":      (87.2846, 26.8065),
    "Butwal":      (83.4486, 27.7000),
    "Hetauda":     (85.0322, 27.4287),
    "Dhangadhi":   (80.5877, 28.6939),
    "Nepalgunj":   (81.6167, 28.0500),
    "Itahari":     (87.2780, 26.6650),
    "Janakpur":    (85.9266, 26.7288),
    "Bhaktapur":   (85.4298, 27.6710),
    "Damak":       (87.7000, 26.6644),
    "Tulsipur":    (82.2967, 28.1300),
    "Ghorahi":     (82.4833, 28.0333),
    "Bhairahawa":  (83.4519, 27.5041),
    "Gorkha":      (84.6333, 28.0000),
    "Ilam":        (87.9280, 26.9088),
}

def generate_cities():
    """Extract first NUM_CITIES names and (x, y) coordinates."""
    names = list(NEPAL_CITIES.keys())[:NUM_CITIES]
    coords = np.array([NEPAL_CITIES[name] for name in names])
    return names, coords

# --- 3. DISTANCE CALCULATIONS ---
def calculate_distance(city_a, city_b):
    """Euclidean distance between two 2D points."""
    return math.sqrt((city_a[0] - city_b[0]) ** 2 + (city_a[1] - city_b[1]) ** 2)

def calculate_route_distance(route, coords):
    """Total length of closed-loop route visiting all cities."""
    total = 0.0
    n = len(route)
    for i in range(n):
        city_a = coords[route[i]]
        city_b = coords[route[(i + 1) % n]]  # Wrap back to starting city
        total += calculate_distance(city_a, city_b)
    return total

# --- 4. ROUTE MANIPULATION ---
def generate_initial_route(num_cities):
    """Create a randomized city permutation."""
    route = list(range(num_cities))
    random.shuffle(route)
    return route

def generate_neighbor(route):
    """Swap two randomly selected cities to generate a candidate neighbor."""
    neighbor = route.copy()
    i, j = random.sample(range(len(route)), 2)
    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
    return neighbor

# --- 5. SIMULATED ANNEALING ALGORITHM ---
def simulated_annealing(coords, initial_temp, min_temp, cooling_rate, iterations_per_temp):
    num_cities = len(coords)

    # STEP 1: Initialize current solution with a random route
    current_route = generate_initial_route(num_cities)
    current_distance = calculate_route_distance(current_route, coords)

    # Save initial state for benchmarking
    initial_route = current_route.copy()
    initial_distance = current_distance

    # STEP 2: Track global best solution found across all iterations
    best_route = current_route.copy()
    best_distance = current_distance

    # STEP 3: Set initial system temperature
    temperature = initial_temp

    # Data collection containers for analysis/plotting
    history_best_distance = []
    history_temperature = []
    total_iterations = 0

    # STEP 4: Main Outer Loop - Run until system cools down below minimum threshold
    while temperature > min_temp:

        # STEP 5: Equilibrium Loop - Perform multiple trials at current temperature
        for _ in range(iterations_per_temp):
            total_iterations += 1

            # STEP 6: Generate a candidate solution by mutating the current state
            neighbor_route = generate_neighbor(current_route)
            neighbor_distance = calculate_route_distance(neighbor_route, coords)

            # STEP 7: Calculate change in cost/energy (Delta = New_Cost - Current_Cost)
            delta = neighbor_distance - current_distance

            # STEP 8: Decision Rule - Accept or Reject candidate solution
            if delta < 0:
                # STEP 8a: Always accept shorter routes (greedy step)
                current_route = neighbor_route
                current_distance = neighbor_distance
            else:
                # STEP 8b: Accept worse routes probabilistically based on Metropolis Criterion: P = exp(-delta / T)
                probability = math.exp(-delta / temperature)
                if random.random() < probability:
                    current_route = neighbor_route
                    current_distance = neighbor_distance

            # STEP 9: Update global best if the newly accepted route outperforms overall best
            if current_distance < best_distance:
                best_route = current_route.copy()
                best_distance = current_distance

            # Log metrics for plotting
            history_best_distance.append(best_distance)
            history_temperature.append(temperature)

        # STEP 10: Cooling Schedule - Reduce temperature exponentially
        temperature *= cooling_rate

    # STEP 11: Return final optimization results and history
    return {
        "initial_route": initial_route,
        "initial_distance": initial_distance,
        "best_route": best_route,
        "best_distance": best_distance,
        "history_best_distance": history_best_distance,
        "history_temperature": history_temperature,
        "total_iterations": total_iterations,
        "final_temperature": temperature,
    }

# --- 6. VISUALIZATION ---
def plot_route(ax, route, coords, names, title):
    """Plot route network connecting city locations."""
    ordered_coords = coords[route + [route[0]]]
    ax.plot(ordered_coords[:, 0], ordered_coords[:, 1], "b-o", linewidth=1.5, markersize=6)

    # Highlight origin
    start_city = coords[route[0]]
    ax.plot(start_city[0], start_city[1], "gs", markersize=12, label="Start/End City")

    # Annotate indices
    for idx, (x, y) in enumerate(coords):
        ax.annotate(str(idx), (x, y), textcoords="offset points", xytext=(5, 5), fontsize=9)

    ax.set_title(title)
    ax.set_xlabel("Longitude (x)")
    ax.set_ylabel("Latitude (y)")
    ax.legend(loc="best")
    ax.grid(True, linestyle="--", alpha=0.5)

def plot_all_results(names, coords, result, show=True):
    """Generates four separate popup figures for individual viewing."""

    # 1. Initial Random Route Window
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    plot_route(
        ax1,
        result["initial_route"],
        coords,
        names,
        f"1. Initial Random Route\nDistance = {result['initial_distance']:.2f}",
    )
    fig1.tight_layout()
    fig1.savefig("plot_1_initial_route.png", dpi=150)

    # 2. Best Route Window
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    plot_route(
        ax2,
        result["best_route"],
        coords,
        names,
        f"2. Best Route Found (Simulated Annealing)\nDistance = {result['best_distance']:.2f}",
    )
    fig2.tight_layout()
    fig2.savefig("plot_2_best_route.png", dpi=150)

    # 3. Best Distance vs Iteration Window
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    ax3.plot(result["history_best_distance"], color="darkorange")
    ax3.set_title("3. Best Distance vs Iteration")
    ax3.set_xlabel("Iteration")
    ax3.set_ylabel("Best Distance Found So Far")
    ax3.grid(True, linestyle="--", alpha=0.5)
    fig3.tight_layout()
    fig3.savefig("plot_3_best_distance_vs_iteration.png", dpi=150)

    # 4. Temperature vs Iteration Window
    fig4, ax4 = plt.subplots(figsize=(8, 6))
    ax4.plot(result["history_temperature"], color="crimson")
    ax4.set_title("4. Temperature vs Iteration")
    ax4.set_xlabel("Iteration")
    ax4.set_ylabel("Temperature")
    ax4.grid(True, linestyle="--", alpha=0.5)
    fig4.tight_layout()
    fig4.savefig("plot_4_temperature_vs_iteration.png", dpi=150)

    # Display all 4 figures simultaneously
    if show:
        plt.show()


# --- 7. TEMPERATURE-ACCEPTANCE DEMONSTRATION ---
def run_fixed_temperature_experiment(coords, temperature, iterations, seed=None):
    """
    Runs Simulated Annealing's inner loop at a CONSTANT temperature and logs the
    CURRENT (accepted) route distance at every iteration -- not the running best.
    This is what makes the worse-solution-acceptance behaviour visible: the running
    best can only ever go down, but the current distance can go up whenever a
    worse neighbor is accepted.
    """
    if seed is not None:
        random.seed(seed)

    num_cities = len(coords)
    route = generate_initial_route(num_cities)
    current_distance = calculate_route_distance(route, coords)

    history = [current_distance]  # iteration 0 = starting distance
    accepted_worse_count = 0

    for _ in range(iterations):
        neighbor_route = generate_neighbor(route)
        neighbor_distance = calculate_route_distance(neighbor_route, coords)
        delta = neighbor_distance - current_distance

        if delta < 0:
            # Always accept an improving move
            route = neighbor_route
            current_distance = neighbor_distance
        else:
            # Accept a worse move with probability P = e^(-delta / T)
            probability = math.exp(-delta / temperature)
            if random.random() < probability:
                route = neighbor_route
                current_distance = neighbor_distance
                accepted_worse_count += 1

        history.append(current_distance)

    return history, accepted_worse_count


def plot_temperature_comparison(history_high, history_low, temp_high, temp_low,
                                 accepted_high, accepted_low, iterations):
    """Side-by-side plots of current distance vs iteration at a high vs low temperature."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    axes[0].plot(history_high, color="crimson", marker="o", markersize=3, linewidth=1)
    axes[0].set_title(f"T = {temp_high}  (High Temperature)\nWorse moves accepted: {accepted_high}/{iterations}")
    axes[0].set_xlabel("Iteration")
    axes[0].set_ylabel("Current Route Distance")
    axes[0].grid(True, linestyle="--", alpha=0.5)

    axes[1].plot(history_low, color="steelblue", marker="o", markersize=3, linewidth=1)
    axes[1].set_title(f"T = {temp_low}  (Low Temperature)\nWorse moves accepted: {accepted_low}/{iterations}")
    axes[1].set_xlabel("Iteration")
    axes[1].set_ylabel("Current Route Distance")
    axes[1].grid(True, linestyle="--", alpha=0.5)

    fig.suptitle("Effect of Temperature on Acceptance of Worse Solutions\n"
                  "(same starting route, 100 iterations, current distance per iteration)")
    fig.tight_layout()
    fig.savefig("plot_5_temperature_acceptance_comparison.png", dpi=150)
    return fig


def demonstrate_temperature_effect(coords, iterations=100, seed=RANDOM_SEED, show=True):
    """Runs the fixed-temperature experiment at T=1000 and T=0.001 and plots both."""
    high_temp = 1000
    low_temp = 0.001

    history_high, accepted_high = run_fixed_temperature_experiment(
        coords, high_temp, iterations, seed=seed
    )
    history_low, accepted_low = run_fixed_temperature_experiment(
        coords, low_temp, iterations, seed=seed
    )

    print("-" * 60)
    print(f"Fixed-temperature demonstration ({iterations} iterations, same start route)")
    print(f"  T = {high_temp:<8} -> worse moves accepted: {accepted_high}/{iterations}")
    print(f"  T = {low_temp:<8} -> worse moves accepted: {accepted_low}/{iterations}")
    print("-" * 60)

    plot_temperature_comparison(
        history_high, history_low, high_temp, low_temp, accepted_high, accepted_low, iterations
    )
    if show:
        plt.show()

    return history_high, history_low


# --- 8. MAIN PROGRAM ---
def main():
    names, coords = generate_cities()

    result = simulated_annealing(
        coords=coords,
        initial_temp=INITIAL_TEMPERATURE,
        min_temp=MIN_TEMPERATURE,
        cooling_rate=COOLING_RATE,
        iterations_per_temp=ITERATIONS_PER_TEMP,
    )

    initial_route_names = [names[i] for i in result["initial_route"]]
    best_route_names = [names[i] for i in result["best_route"]]

    print("=" * 60)
    print("SIMULATED ANNEALING - TSP ON 20 CITIES OF NEPAL")
    print("=" * 60)
    print(f"Number of cities         : {NUM_CITIES}")
    print(f"Initial temperature      : {INITIAL_TEMPERATURE}")
    print(f"Minimum temperature      : {MIN_TEMPERATURE}")
    print(f"Cooling rate             : {COOLING_RATE}")
    print(f"Iterations per temp step : {ITERATIONS_PER_TEMP}")
    print(f"Total iterations run     : {result['total_iterations']}")
    print(f"Final temperature        : {result['final_temperature']:.6f}")
    print("-" * 60)
    print("Initial route (city indices):", result["initial_route"])
    print("Initial route (city names)  :", initial_route_names)
    print(f"Initial distance            : {result['initial_distance']:.2f}")
    print("-" * 60)
    print("Best route (city indices):", result["best_route"])
    print("Best route (city names)  :", best_route_names)
    print(f"Best distance            : {result['best_distance']:.2f}")
    print("-" * 60)
    improvement = (1 - result["best_distance"] / result["initial_distance"]) * 100
    print(f"Improvement over initial route: {improvement:.2f}%")
    print("=" * 60)

    plot_all_results(names, coords, result)

    # Demonstrate how temperature controls acceptance of worse solutions
    demonstrate_temperature_effect(coords, iterations=100, seed=RANDOM_SEED)

if __name__ == "__main__":
    main()
    