"""
This module defines the SegregationModel class.

The model reproduces the basic behaviour of the NetLogo Segregation model.
It creates two groups of agents on a toroidal grid, checks whether agents
are satisfied with their neighbours, and moves unhappy agents to empty cells.
"""

import math
import random

from agent import Agent
from grid import Grid

NETLOGO_RANDOM_WALK_DISTANCE = 10.0
"""
Maximum random movement distance used to approximate NetLogo's fd random-float 10.
"""


RELOCATION_ATTEMPT_FACTOR = 20
"""
Multiplier used to limit relocation search attempts and avoid infinite loops.
"""

class SegregationModel:
    """
    Run the basic grid-based segregation model.

    Attributes:
        width: The number of columns in the grid.
        height: The number of rows in the grid.
        density: The percentage of grid cells occupied by agents.
        similar_wanted: The minimum percentage of similar neighbours wanted.
        max_ticks: The maximum number of update steps to run.
        max_move_distance: Optional movement distance limit for the extension.
        random_generator: A local random generator used for reproducible runs.
        grid: The Grid object storing the spatial state of the model.
        agents: A list containing all agents in the model.
        tick: The current model step.
        results: A list of metric dictionaries recorded during the run.
    """

    def __init__(
        self,
        width: int,
        height: int,
        density: float,
        similar_wanted: float,
        max_ticks: int,
        seed: int | None = None,
        max_move_distance: int | None = None,
    ) -> None:
        """
        Create and initialise a segregation model.

        This method assumes that density and similar_wanted are percentages.
        Density must be less than 100 so that unhappy agents can move.
        """
        self._validate_parameters(width, height, density, similar_wanted, max_ticks)

        self.width = width
        self.height = height
        self.density = density
        self.similar_wanted = similar_wanted
        self.max_ticks = max_ticks
        self.max_move_distance = max_move_distance
        self.random_generator = random.Random(seed)

        self._validate_move_distance()

        self.grid = Grid(width, height)
        self.agents: list[Agent] = []
        self.tick = 0
        self.results: list[dict[str, int | float | bool]] = []

        self._setup_agents()

    def _validate_parameters(
        self,
        width: int,
        height: int,
        density: float,
        similar_wanted: float,
        max_ticks: int,
    ) -> None:
        """
        Validate the model parameters before the model is created.

        A ValueError is raised if a parameter would make the model invalid.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")

        if density <= 0 or density >= 100:
            raise ValueError("Density must be greater than 0 and less than 100.")

        if similar_wanted < 0 or similar_wanted > 100:
            raise ValueError("Similar wanted must be between 0 and 100.")

        if max_ticks <= 0:
            raise ValueError("Max ticks must be positive.")

    def _validate_move_distance(self) -> None:
        """
        Validate the optional movement distance limit.

        The basic model uses None, which means agents may move to any empty
        cell. The extended model uses a non-negative integer distance limit.
        """
        if self.max_move_distance is not None and self.max_move_distance < 0:
            raise ValueError("Maximum move distance must be non-negative.")

    def _setup_agents(self) -> None:
        """
        Place agents randomly on the grid according to the density value.

        The basic model uses two groups. Their population sizes are kept as
        equal as possible. If the total number of agents is odd, group 1 has
        one more agent than group 0.
        """
        total_cells = self.grid.count_cells()
        total_agents = round(total_cells * self.density / 100)

        group_zero_count = total_agents // 2
        group_one_count = total_agents - group_zero_count

        groups = [0 for _ in range(group_zero_count)]
        groups.extend(1 for _ in range(group_one_count))
        self.random_generator.shuffle(groups)

        positions = [
            (row, col)
            for row in range(self.height)
            for col in range(self.width)
        ]
        self.random_generator.shuffle(positions)

        # The first selected positions become occupied by agents.
        for agent_id, group in enumerate(groups):
            row, col = positions[agent_id]
            agent = Agent(agent_id=agent_id, group=group, row=row, col=col)
            self.grid.place_agent(agent, row, col)
            self.agents.append(agent)

    def _calculate_similarity_ratio(self, agent: Agent) -> float:
        """
        Calculate the ratio of similar occupied neighbours for one agent.

        Empty neighbouring cells are ignored. If an agent has no occupied
        neighbours, this method returns 1.0. This means the agent is treated
        as satisfied because there are no dissimilar neighbours nearby.
        """
        neighbours = self.grid.get_neighbors(agent.row, agent.col)

        if len(neighbours) == 0:
            return 1.0

        similar_count = 0

        for neighbour in neighbours:
            if neighbour.group == agent.group:
                similar_count += 1

        return similar_count / len(neighbours)

    def _is_agent_happy(self, agent: Agent) -> bool:
        """
        Check whether an agent is satisfied with its current neighbourhood.

        The agent is happy when the percentage of similar occupied neighbours
        is greater than or equal to the similar_wanted threshold.
        """
        similarity_percentage = self._calculate_similarity_ratio(agent) * 100
        return similarity_percentage >= self.similar_wanted

    def _update_happiness(self) -> None:
        """
        Update the happiness state of every agent in the model.

        This method must be called after agents are moved, because moving one
        agent can change the neighbourhood of other agents.
        """
        for agent in self.agents:
            agent.is_happy = self._is_agent_happy(agent)

    def _get_unhappy_agents(self) -> list[Agent]:
        """
        Return a list of all currently unhappy agents.

        This method assumes that _update_happiness has already been called
        for the current grid state.
        """
        return [agent for agent in self.agents if not agent.is_happy]

    def _find_netlogo_like_empty_cell(self, agent: Agent) -> tuple[int, int] | None:
        """
        Find an empty cell using a NetLogo-like random walk search.

        This method approximates NetLogo's find-new-spot rule. It repeatedly
        samples a random direction and a random distance up to 10 cells. If the
        target cell is occupied, the search continues from that target position.
        The method returns None if no empty cell is found within the attempt
        limit.
        """
        search_row = agent.row
        search_col = agent.col
        max_attempts = self.grid.count_cells() * RELOCATION_ATTEMPT_FACTOR

        for _ in range(max_attempts):
            angle = self.random_generator.random() * 2 * math.pi
            distance = (
                self.random_generator.random() * NETLOGO_RANDOM_WALK_DISTANCE
            )

            row_step = round(math.sin(angle) * distance)
            col_step = round(math.cos(angle) * distance)

            target_row, target_col = self.grid.wrap_position(
                search_row + row_step,
                search_col + col_step,
            )

            if self.grid.is_empty(target_row, target_col):
                return target_row, target_col

            search_row = target_row
            search_col = target_col

        return None

    def _find_limited_random_walk_empty_cell(
        self,
        agent: Agent,
        max_distance: int,
    ) -> tuple[int, int] | None:
        """
        Find an empty cell using a limited random walk search.

        This method is used by the extended model. It preserves the random
        direction and random distance mechanism, but the final target cell
        must remain within max_distance from the agent's original position.
        """
        original_row = agent.row
        original_col = agent.col
        search_side_length = 2 * max_distance + 1
        local_search_cells = search_side_length * search_side_length
        max_attempts = local_search_cells * RELOCATION_ATTEMPT_FACTOR

        for _ in range(max_attempts):
            angle = self.random_generator.random() * 2 * math.pi
            distance = self.random_generator.random() * max_distance

            row_step = round(math.sin(angle) * distance)
            col_step = round(math.cos(angle) * distance)

            if row_step == 0 and col_step == 0:
                continue

            target_row, target_col = self.grid.wrap_position(
                original_row + row_step,
                original_col + col_step,
            )

            if self.grid.is_empty(target_row, target_col):
                return target_row, target_col

        return None

    def _move_unhappy_agents(self, unhappy_agents: list[Agent]) -> int:
        """
        Move unhappy agents to available empty cells.

        In the basic model, agents use a NetLogo-like random walk search. In
        the extended model, agents may only move to empty cells within the
        configured maximum movement distance. The method returns the number
        of agents that were successfully moved during this tick.
        """
        moved_count = 0
        self.random_generator.shuffle(unhappy_agents)

        for agent in unhappy_agents:
            if self.max_move_distance is None:
                target_cell = self._find_netlogo_like_empty_cell(agent)
            else:
                target_cell = self._find_limited_random_walk_empty_cell(
                    agent=agent,
                    max_distance=self.max_move_distance,
                )

            if target_cell is None:
                continue

            new_row, new_col = target_cell
            self.grid.move_agent(agent, new_row, new_col)
            moved_count += 1

        return moved_count

    def _calculate_percent_similar(self) -> float:
        """
        Calculate the overall percentage of similar neighbour relationships.

        This metric is based only on occupied neighbouring cells. If there are
        no occupied neighbour relationships in the model, it returns 100.0.
        """
        total_similar_neighbours = 0
        total_occupied_neighbours = 0

        for agent in self.agents:
            neighbours = self.grid.get_neighbors(agent.row, agent.col)
            total_occupied_neighbours += len(neighbours)

            for neighbour in neighbours:
                if neighbour.group == agent.group:
                    total_similar_neighbours += 1

        if total_occupied_neighbours == 0:
            return 100.0

        return 100 * total_similar_neighbours / total_occupied_neighbours

    def _record_metrics(self, moves_this_tick: int) -> None:
        """
        Record the model metrics for the current tick.

        The recorded values are designed to be comparable with the numerical
        outputs of the original NetLogo Segregation model.
        """
        total_agents = len(self.agents)
        num_happy = sum(1 for agent in self.agents if agent.is_happy)
        num_unhappy = total_agents - num_happy

        result = {
            "tick": self.tick,
            "total_agents": total_agents,
            "num_happy": num_happy,
            "num_unhappy": num_unhappy,
            "percent_happy": 100 * num_happy / total_agents,
            "percent_unhappy": 100 * num_unhappy / total_agents,
            "percent_similar": self._calculate_percent_similar(),
            "moves_this_tick": moves_this_tick,
            "converged": num_unhappy == 0,
        }

        self.results.append(result)

    def step(self) -> int:
        """
        Run one update step of the model.

        The model first identifies unhappy agents, then moves them to random
        empty cells, and finally recalculates happiness after movement.
        """
        self._update_happiness()
        unhappy_agents = self._get_unhappy_agents()
        moves_this_tick = self._move_unhappy_agents(unhappy_agents)

        self.tick += 1

        self._update_happiness()
        self._record_metrics(moves_this_tick)

        return moves_this_tick

    def run(self) -> list[dict[str, int | float | bool]]:
        """
        Run the model until it converges or reaches the maximum tick limit.

        The initial state is recorded at tick 0 before any agents move.
        """
        self._update_happiness()
        self._record_metrics(moves_this_tick=0)

        while self.tick < self.max_ticks:
            latest_result = self.results[-1]

            if latest_result["converged"]:
                break

            self.step()

        return self.results