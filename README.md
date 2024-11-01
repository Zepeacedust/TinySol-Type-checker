# TinySol-Type-checker
This is a type checker for a slightly modified TinySol, as described in [insert paper]

It consists of a handwritten LL(1) parser, and a type checker, if a program successfully type checks it will the be run.

It will verify both the standard properties that the program is not type-safe, and a novel security-type that ensures that it is free from reentrancy and is non-interferent.


## Requirements
The type-checker is written in python, and should run on at least python3.12.

It requires no packages not included in a standard python installation.


## Usage
Standard invocation is 

```
python main.py [FILENAME]
```

## language
The language has a few minor changes from the one described in the paper, they are documented in Desin\_Changes.txt
