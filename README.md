# NetLogo Segregation Model in Python

## Project Overview

This project implements a Python version of the NetLogo Segregation model and an extended version with limited movement distance.

The basic model reproduces the main logic of the original NetLogo Segregation model, where two types of agents live in a grid-based neighbourhood. Each agent evaluates whether it is satisfied with its surrounding neighbours. If an agent is unhappy, it moves to a new empty location.

The extended model adds a movement distance limitation. This extension explores how restricted relocation opportunities may affect convergence speed and the final segregation level.

## Python Version

The code was developed and tested with Python 3.14.4.

## External Dependencies

This project does not require any third-party libraries.

It only uses Python standard library modules. The code can be run directly from the command line and does not require an IDE or any build tools.

## Project Files

### agent.py

Defines the `Agent` class used to represent residents in the model.

### grid.py

Defines the `Grid` class used to store agents, empty cells, neighbours, wrapped positions, and agent movement.

### model.py

Defines the `SegregationModel` class. It contains the setup process, happiness checking, relocation rules, metric recording, and stopping condition.

### main.py

Runs one model configuration and writes tick-by-tick output to a CSV file.

### experiments.py

Runs batch experiments across multiple parameter values and random seeds.

## Build and Run Instructions

No build step is required for this project.

Before running the model, open a command line window and move to the folder that contains the source code files.

Example command on Windows:

```bash
cd /d "C:\Users\YourName\Desktop\netlogo-segregation-python"
```

To check that Python 3.14 is available, run:

```bash
py -3.14 --version
```

To check that the source files can be compiled by Python 3.14, run:

```bash
py -3.14 -m py_compile agent.py grid.py model.py main.py experiments.py
```

If no error message is shown, the code is ready to run.

## Basic Model

To run the basic model:

```bash
py -3.14 main.py --output base_output.csv
```

The basic model uses a NetLogo-like relocation rule. When an agent is unhappy, it searches for an empty cell by repeatedly choosing a random direction and a random movement distance up to 10 cells. This approximates NetLogo's `find new spot` procedure.

## Extended Model

To run the extended model with limited movement distance:

```bash
py -3.14 main.py --max-move-distance 3 --output limited_distance_output.csv
```

In this example, unhappy agents use a limited random walk relocation rule. They still choose random directions and random distances, but the final target cell must be within distance 3 from the agent's original position.

A smaller movement distance means agents have fewer possible relocation options. Some runs may not converge within the maximum tick limit when the movement distance is very small.

## Batch Experiments

To run a small batch experiment:

```bash
py -3.14 experiments.py --repetitions 1 --max-ticks 100
```

To run the full experiment setting used in the report:

```bash
py -3.14 experiments.py --repetitions 5 --max-ticks 500
```

This creates two CSV files:

`batch_summary_output.csv`

`batch_detail_output.csv`

`batch_summary_output.csv` contains the final result of each run.

`batch_detail_output.csv` contains every tick from every run.

The batch experiment tests the following movement settings:

`None, 1, 3, 5, 10`

`None` represents the basic model with unrestricted NetLogo-like relocation.

`1, 3, 5, 10` represent the extended model with different maximum movement distances.

## Output Metrics

### tick

The current model step.

### total_agents

The total number of agents in the model.

### num_happy

The number of happy agents.

### num_unhappy

The number of unhappy agents.

### percent_happy

The percentage of happy agents.

### percent_unhappy

The percentage of unhappy agents.

### percent_similar

The overall percentage of similar occupied neighbours. This metric is used to measure the final segregation level.

### moves_this_tick

The number of agents moved during the current tick.

### converged

Whether the model has reached a state with no unhappy agents.

## Extension Parameter

### max_move_distance

If this value is not provided, the model runs as the basic model.

If this value is an integer, the model runs as the extended model. Unhappy agents use limited random walk relocation, and their final target cell must be within the specified maximum movement distance from their original position.

## Example Commands

Run the basic model:

```bash
py -3.14 main.py --output base_output.csv
```

Run the extended model with movement distance 3:

```bash
py -3.14 main.py --max-move-distance 3 --output limited_distance_3.csv
```

Run a harder case with high density and high similarity threshold:

```bash
py -3.14 main.py --density 90 --similar-wanted 50 --output harder_case.csv
```

Run batch experiments for testing:

```bash
py -3.14 experiments.py --repetitions 1 --max-ticks 100
```

Run batch experiments for the report:

```bash
py -3.14 experiments.py --repetitions 5 --max-ticks 500
```

## Notes

If an output CSV file already exists, running the same command again will overwrite it.

The CSV files are generated outputs. They can be deleted and regenerated by running the corresponding commands again.

For non-converged runs, `final_tick` usually equals the maximum tick limit. In that case, `percent_similar` represents the segregation level at the stopping limit rather than at convergence.

## Skills Demonstrated

This project demonstrates the following skills:

Python programming

Object-oriented programming

Agent-based modelling

Model reproduction

Simulation experiment design

CSV data output

Command-line execution

## Author

Ruoyu Zhang
