"""
This module defines the Grid class for the segregation model.

The grid stores agents in a two dimensional toroidal space. A toroidal
space means that the top edge connects to the bottom edge, and the left
edge connects to the right edge.
"""

from agent import Agent


NEIGHBOR_OFFSETS: tuple[tuple[int, int], ...] = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)
"""
Relative positions used to find the eight surrounding neighbour cells.

The basic segregation model uses the Moore neighbourhood, which contains
the eight cells around an agent.
"""


class Grid:
    """
    Store and manage agents in a toroidal two dimensional grid.

    Attributes:
        width: The number of columns in the grid.
        height: The number of rows in the grid.
        cells: A two dimensional list storing Agent objects or None.
    """

    def __init__(self, width: int, height: int) -> None:
        """
        Create an empty grid with the given width and height.

        This method assumes that width and height must both be positive.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Grid width and height must be positive.")

        self.width = width
        self.height = height
        self.cells: list[list[Agent | None]] = [
            [None for _ in range(width)] for _ in range(height)
        ]

    def wrap_position(self, row: int, col: int) -> tuple[int, int]:
        """
        Convert a position into its wrapped position inside the grid.

        This method implements the toroidal boundary assumption used by
        the basic segregation model.
        """
        wrapped_row = row % self.height
        wrapped_col = col % self.width
        return wrapped_row, wrapped_col

    def get_agent(self, row: int, col: int) -> Agent | None:
        """
        Return the agent at the given position.

        The input position is wrapped before reading from the grid.
        """
        wrapped_row, wrapped_col = self.wrap_position(row, col)
        return self.cells[wrapped_row][wrapped_col]

    def is_empty(self, row: int, col: int) -> bool:
        """
        Check whether the given grid position is empty.

        The input position is wrapped before the cell is checked.
        """
        wrapped_row, wrapped_col = self.wrap_position(row, col)
        return self.cells[wrapped_row][wrapped_col] is None

    def place_agent(self, agent: Agent, row: int, col: int) -> None:
        """
        Place an agent at the given grid position.

        This method assumes that each grid cell can contain at most one
        agent. A ValueError is raised if the target cell is occupied.
        """
        wrapped_row, wrapped_col = self.wrap_position(row, col)

        if not self.is_empty(wrapped_row, wrapped_col):
            raise ValueError("Cannot place an agent in an occupied cell.")

        self.cells[wrapped_row][wrapped_col] = agent
        agent.move_to(wrapped_row, wrapped_col)

    def move_agent(self, agent: Agent, new_row: int, new_col: int) -> None:
        """
        Move an existing agent to a new empty grid position.

        This method assumes that the agent is currently stored at its own
        row and column position in the grid.
        """
        old_row, old_col = agent.get_position()
        wrapped_new_row, wrapped_new_col = self.wrap_position(new_row, new_col)

        if self.cells[old_row][old_col] is not agent:
            raise ValueError("The agent is not stored at its recorded position.")

        if not self.is_empty(wrapped_new_row, wrapped_new_col):
            raise ValueError("Cannot move an agent to an occupied cell.")

        self.cells[old_row][old_col] = None
        self.cells[wrapped_new_row][wrapped_new_col] = agent
        agent.move_to(wrapped_new_row, wrapped_new_col)

    def get_neighbors(self, row: int, col: int) -> list[Agent]:
        """
        Return all occupied neighbouring cells around a position.

        Empty neighbouring cells are ignored. The returned list contains
        only Agent objects.
        """
        neighbors: list[Agent] = []

        for row_offset, col_offset in NEIGHBOR_OFFSETS:
            neighbor_row = row + row_offset
            neighbor_col = col + col_offset
            neighbor = self.get_agent(neighbor_row, neighbor_col)

            if neighbor is not None:
                neighbors.append(neighbor)

        return neighbors

    def get_empty_cells(self) -> list[tuple[int, int]]:
        """
        Return the positions of all empty cells in the grid.

        Each returned position is represented as a tuple in the form
        (row, col).
        """
        empty_cells: list[tuple[int, int]] = []

        for row in range(self.height):
            for col in range(self.width):
                if self.cells[row][col] is None:
                    empty_cells.append((row, col))

        return empty_cells


    def count_cells(self) -> int:
        """
        Return the total number of cells in the grid.

        This value is equal to width multiplied by height.
        """
        return self.width * self.height