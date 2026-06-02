"""
This module provides the command line entry point for the segregation model.

It runs the basic segregation model and writes numerical output to a CSV file.
Only Python standard library modules are used.
"""

import argparse
import csv

from model import SegregationModel


OUTPUT_FIELD_NAMES: tuple[str, ...] = (
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
Column names written to the CSV output file.

These fields are selected to make the Python model output comparable with
the numerical outputs of the original Segregation model.
"""


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments for a single model run.

    Default values are provided so the program can be run without arguments.
    All parameters are passed to SegregationModel for validation.
    """
    parser = argparse.ArgumentParser(
        description="Run the basic segregation model and save results to CSV."
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
        "--density",
        type=float,
        default=80.0,
        help="Percentage of occupied cells. Default is 80.",
    )
    parser.add_argument(
        "--similar-wanted",
        type=float,
        default=30.0,
        help="Minimum percentage of similar neighbours wanted. Default is 30.",
    )
    parser.add_argument(
        "--max-ticks",
        type=int,
        default=500,
        help="Maximum number of ticks to run. Default is 500.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1,
        help="Random seed used for reproducible results. Default is 1.",
    )
    parser.add_argument(
        "--max-move-distance",
        type=int,
        default=None,
        help=(
            "Maximum movement distance for unhappy agents. "
            "Default is None, which allows movement to any empty cell."
        ),
    )
    parser.add_argument(
        "--output",
        type=str,
        default="segregation_output.csv",
        help="Path of the CSV output file.",
    )

    return parser.parse_args()


def write_results_to_csv(
    results: list[dict[str, int | float | bool]],
    output_path: str,
) -> None:
    """
    Write model results to a CSV file.

    This method assumes that each result dictionary contains all fields listed
    in OUTPUT_FIELD_NAMES.
    """
    with open(output_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_FIELD_NAMES)
        writer.writeheader()

        for result in results:
            writer.writerow(result)


def print_summary(
    results: list[dict[str, int | float | bool]],
    output_path: str,
    max_move_distance: int | None,
) -> None:
    """
    Print a short summary of the completed model run.

    The summary helps users quickly check whether the model ran successfully
    and whether it reached a stable state.
    """
    final_result = results[-1]

    print("Model run completed.")

    if max_move_distance is None:
        print("Model type: basic model")
    else:
        print(f"Model type: limited movement model, distance {max_move_distance}")

    print(f"Output file: {output_path}")
    print(f"Final tick: {final_result['tick']}")
    print(f"Converged: {final_result['converged']}")
    print(f"Final unhappy agents: {final_result['num_unhappy']}")
    print(f"Final percent unhappy: {final_result['percent_unhappy']:.2f}")
    print(f"Final percent similar: {final_result['percent_similar']:.2f}")


def main() -> None:
    """
    Run the segregation model using command line arguments.

    The function creates the model, runs it, saves the results, and prints a
    concise summary to the console.
    """
    arguments = parse_arguments()

    model = SegregationModel(
        width=arguments.width,
        height=arguments.height,
        density=arguments.density,
        similar_wanted=arguments.similar_wanted,
        max_ticks=arguments.max_ticks,
        seed=arguments.seed,
        max_move_distance=arguments.max_move_distance,
    )

    results = model.run()
    write_results_to_csv(results, arguments.output)
    print_summary(results, arguments.output, arguments.max_move_distance)


if __name__ == "__main__":
    main()