"""
This module defines the Agent class for the segregation model.

An Agent represents one resident in the grid-based model. Each agent has
a group, a grid position, and a happiness state.
"""

from dataclasses import dataclass


@dataclass
class Agent:
    """
    Represent one resident in the segregation model.

    Attributes:
        agent_id: A unique integer identifier for the agent.
        group: The agent group. The basic model uses 0 and 1.
        row: The current row position of the agent on the grid.
        col: The current column position of the agent on the grid.
        is_happy: Whether the agent is satisfied with its neighbourhood.
    """

    agent_id: int
    group: int
    row: int
    col: int
    is_happy: bool = True

    def move_to(self, row: int, col: int) -> None:
        """
        Update the stored position of the agent.

        This method assumes that the grid has already checked whether the
        target cell is valid and empty.
        """
        self.row = row
        self.col = col

    def get_position(self) -> tuple[int, int]:
        """
        Return the current position of the agent.

        The returned tuple follows the order (row, col).
        """
        return self.row, self.col