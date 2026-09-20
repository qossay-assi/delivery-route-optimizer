import random
import streamlit as st
import matplotlib.pyplot as plt
from optimizer import *

st.set_page_config(page_title="Package Delivery Optimizer", layout="wide")

st.title("AI Optimizer for Local Package Delivery")


seed = st.number_input("Random seed", min_value=0, value=42)
random.seed(seed)
algo = st.radio(
    "Choose Optimization Algorithm", ["Simulated Annealing", "Genetic Algorithm"]
)

n_vehicles = st.slider("Number of Delivery Vehicles", 1, 10, 3)

capacity = st.number_input("Vehicle Capacity (kg)", min_value=1, value=50)

n_packages = st.slider("Number of Packages", 1, 20, 6)


if algo == "Simulated Annealing":

    cooling_rate = st.slider("Cooling Rate", 0.90, 0.99, 0.95)

if algo == "Genetic Algorithm":

    mutation_rate = st.slider("Mutation Rate", 0.01, 0.1, 0.05)

    population_size = st.slider("Population Size", 50, 100, 50)


packages = []

st.subheader("Package Details")

for i in range(n_packages):

    x = st.number_input(f"Package {i+1} - X Coordinate", 0.0, 100.0, float(i + 1) * 2)

    y = st.number_input(f"Package {i+1} - Y Coordinate", 0.0, 100.0, float(i + 1) * 3)

    weight = st.number_input(f"Package {i+1} - Weight (kg)", 0.1, 50.0, 5.0)

    priority = st.slider(f"Package {i+1} - Priority (1=High, 5=Low)", 1, 5, 3)

    packages.append(Package(i, x, y, weight, priority))


vehicles = [Vehicle(i, capacity) for i in range(n_vehicles)]


if st.button("Run Optimization"):

    try:
        if algo == "Simulated Annealing":
            result = simulated_annealing(packages, vehicles, cooling=cooling_rate)
        else:
            result = genetic_algorithm(
                packages,
                vehicles,
                population_size=population_size,
                mutation_rate=mutation_rate,
            )

    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    st.success(f"Total Traveled Distance: {round(evaluate_solution(result), 2)} km")

    fig, ax = plt.subplots()

    colors = ["blue", "orange", "green", "red", "purple", "brown"]

    for v in result:

        route = [(0, 0)] + [p.location for p in v.route] + [(0, 0)]

        xs, ys = zip(*route)

        ax.plot(
            xs,
            ys,
            marker="o",
            label=f"Vehicle {v.id} ({round(total_distance(v),1)} km)",
            color=colors[v.id % len(colors)],
        )

        for idx, p in enumerate(v.route):

            ax.text(
                p.location[0],
                p.location[1] + 0.5,
                f"{p.id}",
                fontsize=9,
                color=colors[v.id % len(colors)],
            )

    ax.set_title("Vehicle Delivery Routes")

    ax.set_xlabel("X (km)")

    ax.set_ylabel("Y (km)")

    ax.legend()

    st.pyplot(fig)

    st.subheader("Assignment Summary")

    for v in result:

        st.markdown(
            f"**Vehicle {v.id}** - Total Distance: {round(total_distance(v),1)} km - Total Weight: {v.total_weight} kg"
        )

        data = [
            {
                "Package ID": p.id,
                "Destination": p.location,
                "Weight": p.weight,
                "Priority": p.priority,
            }
            for p in v.route
        ]

        st.table(data)
