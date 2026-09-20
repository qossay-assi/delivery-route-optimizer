# Delivery Route Optimizer

Explore capacitated vehicle routing with simulated annealing and a genetic algorithm. Enter packages, vehicle capacities and priorities, then compare routes on a 2D map.

## Run
Python 3.12 was used for validation.
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
Use the seed field to reproduce a run. Both algorithms minimize Euclidean round-trip distance. Within each vehicle, lower numeric priority is delivered first; this is not a time-window or global-priority optimizer.

## Contents
- `optimizer.py`: package/vehicle models, feasibility checks, neighborhood search and order crossover.
- `app.py`: Streamlit controls, route visualization and assignment summary.
- `test_optimizer.py`: regression tests for capacity, package conservation, one-vehicle input and infeasible packing.

## Recovery and fixes
Adapted from the AI course delivery project and compared with its archived and command-line variants. Fixed silent package loss, stale vehicle loads after swaps, single-vehicle failures and final-generation selection. Added capacity-safe relocation, same-priority route swaps, true order crossover, validation and repeatable seeds. Extracted the algorithm from the UI for testing.

The initial packer is greedy, not a complete feasibility solver. A packing failure means the heuristic could not construct a complete assignment; it does not prove the instance is mathematically infeasible. Neither search guarantees a global optimum. Original report claims about CSV import and empty-vehicle penalties were not present in the recovered code and are not advertised here.

## Validation
```bash
python -m unittest -v
```
Four regression tests passed, including 10 seeds for both algorithms. Streamlit AppTest also ran the SA and GA buttons without exceptions.

## Attribution
Original report credits Qusai Assi. This portfolio edition includes later recovery and correctness work; it is not presented as the unchanged university submission.

## License
MIT for this repository's project code; dependencies retain their own licenses. See `LICENSE`.
