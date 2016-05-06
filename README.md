# nonogram-solver

This is my attempt at a nonogram solver written in Python. I was compelled to do so from Nintendo's Pokemon Picross. I hope to eventually have it solve the mega puzzles.

Check out this code if you like. I'm quite pleased with the iteration I use to fill each row. I'm hoping to get it trimmed down to the absolute minimal time.

Usage: python3 nonogram.py puzzle_file

I haven't yet uploaded templates, but here's an example.

The puzzle file containing this:

    2 2
    1 1
    1
    2 1
    3
    -
    2 1
    1 2
    1 1
    1 1
    2 1
will solve and pretty print this:

    +-----+
    |**.**| *2 .1 *2
    |*...*| *1 .3 *1
    |..*..| .2 *1 .2
    |**..*| *2 .2 *1
    |.***.| .1 *3 .1
    +-----+
    Solved

By default * represents a filled square, . represents an empty square, and N represents an undetermined square. It will print an unsolved grid if the rules conflict.

There is a known issue that if the row and column rules conflict in such a way that the columns are solved and the grid filled but some rows are incorrect, or vice versa, it will still consider it solved. I must code in a check for this and fail the puzzle.