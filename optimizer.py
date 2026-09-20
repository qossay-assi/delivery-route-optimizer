import random

import math

import copy

# ------------------- Data Models -------------------


class Package:

    def __init__(self, id, x, y, weight, priority):

        self.id = id

        self.location = (x, y)

        self.weight = weight

        self.priority = priority


class Vehicle:

    def __init__(self, id, capacity):

        self.id = id

        self.capacity = capacity

        self.route = []

        self.total_weight = 0

    def can_add(self, package):

        return self.total_weight + package.weight <= self.capacity

    def add_package(self, package):

        self.route.append(package)

        self.total_weight += package.weight

    def reset(self):

        self.route = []

        self.total_weight = 0


# ------------------- Utility Functions -------------------


def euclidean(p1, p2):

    return round(math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2), 2)


def total_distance(vehicle, origin=(0, 0)):

    route = [origin] + [p.location for p in vehicle.route] + [origin]

    return sum(euclidean(route[i], route[i + 1]) for i in range(len(route) - 1))


def evaluate_solution(vehicles):

    return sum(total_distance(v) for v in vehicles)


# ------------------- Algorithms -------------------


def initial_solution(packages, vehicles):
    validate_input(packages, vehicles)
    for v in vehicles:
        v.reset()
    for package in sorted(packages, key=lambda p: -p.weight):
        fits = [v for v in vehicles if v.can_add(package)]
        if not fits:
            raise ValueError(
                "Greedy packing could not place every package; adjust the fleet or weights."
            )
        min(fits, key=lambda v: v.capacity - v.total_weight).add_package(package)
    for v in vehicles:
        v.route.sort(key=lambda p: p.priority)
    return vehicles


def neighbor(vehicles):
    # Move, swap, or reorder while preserving package multiplicity and capacity.
    occupied = [v for v in vehicles if v.route]
    if not occupied:
        return vehicles
    source = random.choice(occupied)
    target = random.choice(vehicles)
    if source is target:
        if len(source.route) > 1:
            i, j = random.sample(range(len(source.route)), 2)
            if source.route[i].priority == source.route[j].priority:
                source.route[i], source.route[j] = source.route[j], source.route[i]
    elif random.random() < 0.5 or not target.route:
        package = random.choice(source.route)
        if target.can_add(package):
            source.route.remove(package)
            source.total_weight -= package.weight
            target.add_package(package)
    else:
        i, j = random.randrange(len(source.route)), random.randrange(len(target.route))
        first, second = source.route[i], target.route[j]
        if (
            source.total_weight - first.weight + second.weight <= source.capacity
            and target.total_weight - second.weight + first.weight <= target.capacity
        ):
            source.route[i], target.route[j] = second, first
            source.total_weight += second.weight - first.weight
            target.total_weight += first.weight - second.weight
    for v in vehicles:
        v.route.sort(key=lambda p: p.priority)
    return vehicles


def accept(new, current, T):

    e_new = evaluate_solution(new)

    e_curr = evaluate_solution(current)

    if e_new < e_curr:

        return True

    return math.exp((e_curr - e_new) / T) > random.random()


def simulated_annealing(
    packages, vehicles, T_init=1000, cooling=0.95, T_min=1, iterations=100
):

    if not (0 < cooling < 1 and T_init > T_min > 0 and iterations > 0):
        raise ValueError("Invalid annealing parameters")
    current = initial_solution(packages, copy.deepcopy(vehicles))

    best = copy.deepcopy(current)

    T = T_init

    while T > T_min:

        for _ in range(iterations):

            new = neighbor(copy.deepcopy(current))

            if accept(new, current, T):

                current = new

                if evaluate_solution(current) < evaluate_solution(best):

                    best = copy.deepcopy(current)

        T *= cooling

    return best


def random_assignment(packages, vehicles_template):
    validate_input(packages, vehicles_template)
    vehicles = copy.deepcopy(vehicles_template)
    for v in vehicles:
        v.reset()
    order = list(packages)
    random.shuffle(order)
    for package in order:
        fits = [v for v in vehicles if v.can_add(package)]
        if not fits:
            raise ValueError("Random packing did not place every package")
        random.choice(fits).add_package(package)
    for v in vehicles:
        v.route.sort(key=lambda p: p.priority)
    return vehicles


def crossover(p1, p2):
    # Order crossover: inherit a prefix from the first parent, then unseen IDs
    # from the second. Failed greedy packing falls back to a feasible parent.
    first = [p for v in p1 for p in v.route]
    second = [p for v in p2 for p in v.route]
    cut = random.randrange(len(first) + 1)
    order = first[:cut]
    seen = {p.id for p in order}
    order += [p for p in second if p.id not in seen]
    child = copy.deepcopy(p2)
    for v in child:
        v.reset()
    for package in order:
        fits = [v for v in child if v.can_add(package)]
        if not fits:
            return copy.deepcopy(p1)
        random.choice(fits).add_package(copy.deepcopy(package))
    for v in child:
        v.route.sort(key=lambda p: p.priority)
    return child


def mutate(vehicles):

    return neighbor(vehicles)


def genetic_algorithm(
    packages, vehicles_template, population_size=50, mutation_rate=0.05, generations=200
):

    if population_size < 2 or generations < 0 or not 0 <= mutation_rate <= 1:
        raise ValueError("Invalid genetic search parameters")
    baseline = initial_solution(packages, copy.deepcopy(vehicles_template))
    population = []
    for _ in range(population_size):
        try:
            population.append(random_assignment(packages, vehicles_template))
        except ValueError:
            population.append(copy.deepcopy(baseline))

    for _ in range(generations):

        population.sort(key=lambda sol: evaluate_solution(sol))

        next_gen = population[:2]

        while len(next_gen) < population_size:

            p1, p2 = random.sample(population[:10], 2)

            child = crossover(p1, p2)

            if random.random() < mutation_rate:

                child = mutate(child)

            next_gen.append(child)

        population = next_gen

    return min(population, key=evaluate_solution)


def validate_input(packages, vehicles):
    if not vehicles:
        raise ValueError("At least one vehicle is required")
    if len({p.id for p in packages}) != len(packages):
        raise ValueError("Package IDs must be unique")
    if any(not math.isfinite(v.capacity) or v.capacity <= 0 for v in vehicles):
        raise ValueError("Capacities must be positive and finite")
    if any(
        not math.isfinite(p.weight)
        or p.weight <= 0
        or not all(math.isfinite(x) for x in p.location)
        for p in packages
    ):
        raise ValueError("Package weights and coordinates must be valid")
    if any(p.weight > max(v.capacity for v in vehicles) for p in packages):
        raise ValueError("A package exceeds every vehicle capacity")
