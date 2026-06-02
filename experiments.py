"""
This module runs batch experiments for the basic segregation model.

It executes the model across multiple parameter values and random seeds.
The output files can be used to compare model behaviour across runs.
Only Python standard library modules are used.
"""

import argparse
import csv

from model import SegregationModel

CSVValue = int | float | bool | str | None
CSVRow = dict[str, CSVValue]
"""
Shared type aliases for CSV rows used by the batch experiment output.
"""


DEFAULT_DENSITIES: tuple[float, ...] = (60.0, 70.0, 80.0, 90.0)
"""
Default density values used in the batch experiments.

Density is interpreted as the percentage of occupied grid cells.
"""


DEFAULT_SIMILAR_WANTED_VALUES: tuple[float, ...] = (20.0, 30.0, 40.0, 50.0)
"""
Default similarity threshold values used in the batch experiments.

Similar wanted is interpreted as the minimum percentage of similar neighbours.
"""

DEFAULT_MAX_MOVE_DISTANCES: tuple[int | None, ...] = (None, 1, 3, 5, 10)
"""
Default movement distance settings used in the batch experiments.

None represents the basic model, where unhappy agents may move to any empty
cell. Integer values represent the extended model with limited movement.
"""

DETAIL_FIELD_NAMES: tuple[str, ...] = (
    "run_id",
    "model_type",
    "max_move_distance",
    "seed",
    "width",
    "height",
    "density",
    "similar_wanted",
    "tick",
    "total_agents",
    "num_happy",
    "num_unhappy",
    "percent_happy",
    "percent_unhappy",
    "percent_similar",
    "moves_this_tick",
    "converged",
)
"""
Column names written to the detailed batch output file.

The detailed file records every tick from every model run.
"""


SUMMARY_FIELD_NAMES: tuple[str, ...] = (
    "run_id",
    "model_type",
    "max_move_distance",
    "seed",
    "width",
    "height",
    "density",
    "similar_wanted",
    "final_tick",
    "final_num_unhappy",
    "final_percent_unhappy",
    "final_percent_similar",
    "converged",
)
"""
Column names written to the summary batch output file.

The summary file records only the final state of each model run.
"""


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments for the batch experiment runner.

    Default values are provided so the experiment can be run without arguments.
    The default experiment is small enough to run quickly.
    """
    parser = argparse.ArgumentParser(
        description="Run batch experiments for the basic segregation model."
    )

    parser.add_argument(
        "--width",
        type=int,
        default=50,
        help="Grid width. Default is 50.",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=50,
        help="Grid height. Default is 50.",
    )
    parser.add_argument(
        "--max-ticks",
        type=int,
        default=500,
        help="Maximum number of ticks for each run. Default is 500.",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=5,
        help="Number of random seeds for each parameter setting. Default is 5.",
    )
    parser.add_argument(
        "--detail-output",
        type=str,
        default="batch_detail_output.csv",
        help="CSV file storing every tick from every run.",
    )
    parser.add_argument(
        "--summary-output",
        type=str,
        default="batch_summary_output.csv",
        help="CSV file storing the final state of every run.",
    )

    return parser.parse_args()


def build_seed_list(repetitions: int) -> list[int]:
    """
    Build the list of random seeds used in the batch experiments.

    This method assumes that repetitions is a positive integer.
    """
    if repetitions <= 0:
        raise ValueError("Repetitions must be positive.")

    return [seed for seed in range(1, repetitions + 1)]


def run_single_experiment(
    run_id: int,
    seed: int,
    width: int,
    height: int,
    density: float,
    similar_wanted: float,
    max_ticks: int,
    max_move_distance: int | None,
) -> tuple[list[CSVRow], CSVRow]:
    """
    Run one model configuration and return detailed and summary results.

    The detailed results contain every tick. The summary result contains only
    the final state of this run. A None movement distance represents the basic
    model, while an integer distance represents the extended model.
    """
    if max_move_distance is None:
        model_type = "basic"
    else:
        model_type = "limited_movement"

    model = SegregationModel(
        width=width,
        height=height,
        density=density,
        similar_wanted=similar_wanted,
        max_ticks=max_ticks,
        seed=seed,
        max_move_distance=max_move_distance,
    )

    results = model.run()
    detailed_rows: list[CSVRow] = []

    for result in results:
        detailed_row = {
            "run_id": run_id,
            "model_type": model_type,
            "max_move_distance": max_move_distance,
            "seed": seed,
            "width": width,
            "height": height,
            "density": density,
            "similar_wanted": similar_wanted,
        }
        detailed_row.update(result)
        detailed_rows.append(detailed_row)

    final_result = results[-1]
    summary_row = {
        "run_id": run_id,
        "model_type": model_type,
        "max_move_distance": max_move_distance,
        "seed": seed,
        "width": width,
        "height": height,
        "density": density,
        "similar_wanted": similar_wanted,
        "final_tick": final_result["tick"],
        "final_num_unhappy": final_result["num_unhappy"],
        "final_percent_unhappy": final_result["percent_unhappy"],
        "final_percent_similar": final_result["percent_similar"],
        "converged": final_result["converged"],
    }

    return detailed_rows, summary_row


def write_csv(
    rows: list[dict[str, int | float | bool]],
    field_names: tuple[str, ...],
    output_path: str,
) -> None:
    """
    Write rows to a CSV file using the provided field names.

    This method assumes that each row contains the required field names.
    """
    with open(output_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)


def run_batch_experiments(arguments: argparse.Namespace) -> None:
    """
    Run all batch experiment configurations and write the output files.

    The experiment varies movement distance, density, similar_wanted, and
    random seed. A None movement distance represents the basic model.
    """
    seeds = build_seed_list(arguments.repetitions)
    all_detailed_rows: list[CSVRow] = []
    all_summary_rows: list[CSVRow] = []

    run_id = 1

    for max_move_distance in DEFAULT_MAX_MOVE_DISTANCES:
        for density in DEFAULT_DENSITIES:
            for similar_wanted in DEFAULT_SIMILAR_WANTED_VALUES:
                for seed in seeds:
                    detailed_rows, summary_row = run_single_experiment(
                        run_id=run_id,
                        seed=seed,
                        width=arguments.width,
                        height=arguments.height,
                        density=density,
                        similar_wanted=similar_wanted,
                        max_ticks=arguments.max_ticks,
                        max_move_distance=max_move_distance,
                    )

                    all_detailed_rows.extend(detailed_rows)
                    all_summary_rows.append(summary_row)
                    run_id += 1

    write_csv(all_detailed_rows, DETAIL_FIELD_NAMES, arguments.detail_output)
    write_csv(all_summary_rows, SUMMARY_FIELD_NAMES, arguments.summary_output)

    print("Batch experiments completed.")
    print(f"Total runs: {len(all_summary_rows)}")
    print(f"Detailed output file: {arguments.detail_output}")
    print(f"Summary output file: {arguments.summary_output}")


def main() -> None:
    """
    Run the batch experiment script.

    Command line arguments are parsed first, then all experiment combinations
    are executed.
    """
    arguments = parse_arguments()
    run_batch_experiments(arguments)


if __name__ == "__main__":
    main()