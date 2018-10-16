import sys

gridStringFormat = """\
 %s %s %s | %s %s %s | %s %s %s 
 %s %s %s | %s %s %s | %s %s %s 
 %s %s %s | %s %s %s | %s %s %s 
-------+-------+-------
 %s %s %s | %s %s %s | %s %s %s 
 %s %s %s | %s %s %s | %s %s %s 
 %s %s %s | %s %s %s | %s %s %s 
-------+-------+-------
 %s %s %s | %s %s %s | %s %s %s 
 %s %s %s | %s %s %s | %s %s %s 
 %s %s %s | %s %s %s | %s %s %s \
"""

showLog = False
def logStep(message):
  """Called with an informative message whenever progress is made."""
  
  if showLog:
    sys.stderr.write("%s\n" % message)

class SudokuError(Exception):
  """Base class for all exceptions in this module."""

class UnsolvableError(SudokuError):
  """Raised when the script is unable to solve a puzzle."""

class ValueError(ValueError, SudokuError):
  """Raised when an invalid value is passed to this module."""

class Cell(object):
  """A cell in a Sudoku grid."""
  
  def __init__(self, value, name):
    self.possibilities = set(range(1, 10))
    self.value = value
    self.name  = name
  
  def __setValue(self, value):
    if value:
      self.possibilities &= {value}
    
    self.__value = value
  
  def discardPossibility(self, possibility):
    """Removes a possibility from the cell if it has it.
    Returns True if it is removed, False if it is not."""
    
    try:
      self.possibilities.remove(possibility)
      
      if len(self.possibilities) == 1:
        self.value, = self.possibilities
        logStep("%s can only contain a %i." % (str(self).capitalize(), self.value))
      
      return True
    except KeyError:
      return False
  
  value = property(lambda self: self.__value, __setValue)
  
  def __str__(self):
    return self.name

class Group(list):
  """A group of Sudoku cells with disinct values. And a name."""
  
  def __init__(self, cells, name):
    super().__init__(cells)
    self.name = name
  
  def discardPossibility(self, possibility):
    """Removes a possibility from each cell that has it.
    Returns True if it was removed from any, False if it was not."""
    
    result = False
    
    for cell in self:
      result = cell.discardPossibility(possibility) or result
    
    return result
  
  def __str__(self):
    return self.name

def regionName(number):
  if number < 3:
    vertical = "top"
  elif number < 6:
    vertical = "middle"
  else:
    vertical = "bottom"
  
  if number % 3 == 0:
    return("the %s-left nontet" % vertical)
  elif number % 3 == 1:
    if vertical == "middle":
      return("the middle nontet")
    else:
      return("the %s-middle nontet" % vertical)
  else:
    return("the %s-right nontet" % vertical)

class Grid(object):
  """A Sudoku grid."""
  
  def __init__(self, values):
    if len(values) != (9 * 9):
      raise ValueError("Grid requires exactly 81 values for initialization.")
    
    self.cells = [Cell(values[n], name="cell (%i, %i)" %
                    (n % 9 + 1, n // 9 + 1)) for n in range(9 * 9)]
    
    self.groups = [None for n in range(3 * 9)]
    
    for row in range(9):
      self.groups[row] = Group(
        (self.cells[row * 9 + i] for i in range(9)),
        "row %i" % (row + 1)
      )
    
    for column in range(9):
      self.groups[9 + column] = Group(
        (self.cells[column + 9 * i] for i in range(9)),
        "column %i" % (row + 1)
      )
    
    for region in range(9):
      offset = (region // 3) * 3 * 9 + (region % 3) * 3
      
      self.groups[18 + region] = Group(
        (self.cells[offset + (i % 3) + 9 * (i // 3)] for i in range(9)),
        regionName(region)
      )
  
  def __str__(self):
    return gridStringFormat % tuple(cell.value or "_" for cell in self.cells)
  
  def solve(self):
    progress = True
    
    while progress:
      progress = False
      
      # Eliminate possibilities and identify cells with only one possible value.
      for group in self.groups:
        for cell in group:
          if cell.value:
            progress = group.discardPossibility(cell.value) or progress
      
      # Groups with only one possible cell with a value
      for group in self.groups:
        possibilities = set(range(1, 10))
        
        for cell in group:
          if cell.value:
            possibilities.remove(cell.value)
        
        for possibility in possibilities:
          possibleCells = [cell for cell in group if possibility in cell.possibilities]
          
          if len(possibleCells) == 1:
            possibleCells[0].value = possibility
            logStep("%s is the only cell in %s that can contain a %s." % (str(possibleCells[0]).capitalize(), group, possibleCells[0].value))
            progress = True
            continue
    
    # If any cells aren't solved, we failed.
    if any(cell.value is None for cell in self.cells):
      raise UnsolvableError("Unable to make further progress.")
    
    if not self.isValid():
      raise ValueError("The solution has duplicate values.")
  
  def isValid(self):
    """Checks for any duplicate values in groups, True if none are found."""
    
    for group in self.groups:
      found = set()
      
      for cell in group:
        if cell.value:
          if cell.value in found:
            return False
          else:
            found.add(cell.value)
    
    return True