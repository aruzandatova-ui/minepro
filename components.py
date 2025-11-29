"""
Core game logic for Minesweeper.

This module contains pure domain logic without any pygame or pixel-level
concerns. It defines:
- CellState: the state of a single cell
- Cell: a cell positioned by (col,row) with an attached CellState
- Board: grid management, mine placement, adjacency computation, reveal/flag

The Board exposes imperative methods that the presentation layer (run.py)
can call in response to user inputs, and does not know anything about
rendering, timing, or input devices.
"""

import random
from typing import List, Tuple

class CellState:
    """Mutable state of a single cell.

    Attributes:
        is_mine: Whether this cell contains a mine.
        is_revealed: Whether the cell has been revealed to the player.
        is_flagged: Whether the player flagged this cell as a mine.
        adjacent: Number of adjacent mines in the 8 neighboring cells.
    """

    def __init__(self, is_mine: bool = False, is_revealed: bool = False, is_flagged: bool = False, adjacent: int = 0):
        self.is_mine = is_mine
        self.is_revealed = is_revealed
        self.is_flagged = is_flagged
        self.adjacent = adjacent


class Cell:
    """Logical cell positioned on the board by column and row."""

    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self.state = CellState()


class Board:
    """Minesweeper board state and rules.

    Responsibilities:
    - Generate and place mines with first-click safety
    - Compute adjacency counts for every cell
    - Reveal cells (iterative flood fill when adjacent == 0)
    - Toggle flags, check win/lose conditions
    """

    def __init__(self, cols: int, rows: int, mines: int):
        self.cols = cols
        self.rows = rows
        self.num_mines = mines
        self.cells: List[Cell] = [Cell(c, r) for r in range(rows) for c in range(cols)]
        self._mines_placed = False
        self.revealed_count = 0
        self.game_over = False
        self.win = False

    def index(self, col: int, row: int) -> int:
        """Return the flat list index for (col,row)."""
        return row * self.cols + col

    def is_inbounds(self, col: int, row: int) -> bool:
        # TODO: Return True if (col,row) is inside the board bounds.
        return 0 <= col < self.cols and 0 <= row < self.rows
    

    def neighbors(self, col: int, row: int):
      deltas = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0),           (1, 0),
        (-1, 1), (0, 1), (1, 1)]

      result = []

      for dc, dr in deltas:
        nc,nr = col + dc, row+dr
    

        if self.is_inbounds(nc, nr):
            result.append((nc, nr))

      return result
    

        # TODO: Return list of valid neighboring coordinates around (col,row).
        # deltas = [
        #     (-1, -1), (0, -1), (1, -1),
        #     (-1, 0),            (1, 0),
        #     (-1, 1),  (0, 1),  (1, 1),
        # ]
        # result = []
        
        # return result
    

    def place_mines(self, safe_col: int, safe_row: int) -> None:
        import random
        total_cells = self.cols * self.rows
        safe_zone = {(safe_col, safe_row)} | set(self.neighbors(safe_col, safe_row))
        available_cells = total_cells - len(safe_zone)
    
    
        if self.num_mines > available_cells:
          self.num_mines = available_cells
    
        if self.num_mines <= 0:
          self._mines_placed = True
          return
        
        all_positions = [(c,r)for r in range(self.rows) for c in range(self.cols)]
        forbidden = {(safe_col, safe_row)} | set(self.neighbors(safe_col, safe_row))
        pool = [p for p in all_positions if p not in forbidden]
        random.shuffle(pool)
        mine_positions = pool[:self.num_mines]

        for col, row in mine_positions:
         index = self.index(col, row)
         self.cells[index].state.is_mine = True
     
        for r in range(self.rows):
            for c in range(self.cols):
             idx = self.index(c, r)
             cell = self.cells[idx]
            
             if cell.state.is_mine:
                continue
            
            count = 0
            for nc, nr in self.neighbors(c, r):
                nidx = self.index(nc, nr)
                if self.cells[nidx].state.is_mine:
                    count += 1
                cell.state.adjacent = count

        self._mines_placed = True
        

        # TODO: Place mines randomly, guaranteeing the first click and its neighbors are safe. And Compute adjacency counts
        # all_positions = [(c, r) for r in range(self.rows) for c in range(self.cols)]
        # forbidden = {(safe_col, safe_row)} | set(self.neighbors(safe_col, safe_row))
        # pool = [p for p in all_positions if p not in forbidden]
        # random.shuffle(pool)
        
        # Compute adjacency counts
        # for r in range(self.rows):
        #     for c in range(self.cols):

        # self._mines_placed = True

    def reveal(self, col: int, row: int) -> None:
    
    # Check if coordinates are within bounds
      if not self.is_inbounds(col, row):
        return
    
    # Don't allow moves after game is over
      if self.game_over or self.win:
        return
    
    # First click - place mines
      if not self._mines_placed:
         self.place_mines(col, row)
    
      index = self.index(col, row)
      cell = self.cells[index]
    
    # Don't reveal flagged or already revealed cells
      if cell.state.is_flagged or cell.state.is_revealed:
        return
    
    # Reveal this cell
      cell.state.is_revealed = True
      self.revealed_count += 1
    
    # Game over if it's a mine
      if cell.state.is_mine:
        self.game_over = True
        self._reveal_all_mines()
        return
    
    # If it's an empty cell (adjacent == 0), flood fill to neighbors
      if cell.state.adjacent == 0:
         stack = [(col, row)]
         visited = set()
        
         while stack:
            c, r = stack.pop()
            current_index = self.index(c, r)
            current_cell = self.cells[current_index]
            
            # Skip if already visited
            if (c, r) in visited:
                continue
            visited.add((c, r))
            
            # Reveal all neighbors regardless of adjacent count
            for nc, nr in self.neighbors(c, r):
                neighbor_index = self.index(nc, nr)
                neighbor_cell = self.cells[neighbor_index]
                
                # Skip if flagged, already revealed, or visited
                if (neighbor_cell.state.is_flagged or 
                    neighbor_cell.state.is_revealed or 
                    (nc, nr) in visited):
                    continue
                
                # Reveal the neighbor
                neighbor_cell.state.is_revealed = True
                self.revealed_count += 1
                
                # If neighbor is also empty, add to stack for further expansion
                if neighbor_cell.state.adjacent == 0:
                    stack.append((nc, nr))
    
    # Check win condition
      self._check_win()
      

    

        # TODO: Reveal a cell; if zero-adjacent, iteratively flood to neighbors.
        # if not self.is_inbounds(col, row):
        #     return
        # if not self._mines_placed:
        #     self.place_mines(col, row)

        
        # self._check_win()
    

    def toggle_flag(self, col: int, row: int) -> None:
        if self.game_over or self.win:
          return
        
        if not self.is_inbounds(col, row):
          return
        
        index = self.index(col, row)
        cell = self.cells[index]

        if cell.state.is_revealed:
           return
    
        cell.state.is_flagged = not cell.state.is_flagged
        # TODO: Toggle a flag on a non-revealed cell.
        # if not self.is_inbounds(col, row):
        #     return
        


    def flagged_count(self) -> int:
        count =0
        for cell in self.cells:
            if cell.state.is_flagged:
                count+=1
        return count
        # TODO: Return current number of flagged cells.
        

    def _reveal_all_mines(self) -> None:
        """Reveal all mines; called on game over."""
        for cell in self.cells:
            if cell.state.is_mine:
                cell.state.is_revealed = True

    def _check_win(self) -> None:
        """Set win=True when all non-mine cells have been revealed."""
        total_cells = self.cols * self.rows
        if self.revealed_count == total_cells - self.num_mines and not self.game_over:
            self.win = True
            for cell in self.cells:
                if not cell.state.is_revealed and not cell.state.is_mine:
                    cell.state.is_revealed = True
