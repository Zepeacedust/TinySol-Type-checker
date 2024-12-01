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
The language has a few minor changes from the one described in the paper, they are documented in Design\_Changes.txt.


### Comments
Single line comments are started with # at any point in the line, after which the lexer will ignore the rest of the line.

### Context free grammar
```
S -> INTERFACE_DEC CONTRACT_DEC TRANSACTION

INTERFACE_DEC -> ID { 
	FIELD_DEC
	METHOD_DEC 
} INTERFACE_DEC

INTERFACE_DEC -> epsilon

FIELD_DEC -> field ID: type ; FIELD_DEC

FIELD_DEC -> epsilon

METHOD_DEC -> method ID: ([TYPE[, TYPE]*]): SEC; METHOD_DEC
		| epsilon

CONTRACT_DEC -> ID TYPE {
	FIELD_DEF
	METHOD_DEF
} CONTRACT_DEC

CONTRACT_DEC -> epsilon

METHOD_DEF -> ID (PARAMETER_DEC) { STATEMENTS } METHOD_DEF
		| epsilon

FIELD_DEF -> field ID := CONSTANT; FIELD_DEF 
		| epsilon

TRANSACTION -> ID -> ID.ID(~ID); TRANSACTION
		| epsilon

STATEMENTS -> STMT; STATEMENTS
		| epsilon

STMT -> skip
		| throw
		| var ID: TYPE := EXPRESSION
		| if (EXPRESSION) {STATEMENTS} else {STATEMENTS}
		| while (EXPRESSION) {STATEMENTS}
		| call ID.ID([EXPRESSION[, EXPRESSION]*])
		| set L_VAL := EXPRESSION
		| print EXPRESSION
		| dcall ID.ID(EXPRESSION[, EXPESSION]*)
		| unsafe STMT

EXPRESSION -> ID
		| ID.ID
		| EXPRESSION * EXPRESSION
		| EXPRESSION // EXPRESSION
		| EXPRESSION + EXPRESSION
		| EXPRESSION == EXPRESSION
		| EXPRESSION < EXPRESSION
		| EXPRESSION > EXPRESSION
		| EXPRESSION <= EXPRESSION
		| EXPRESSION >= EXPRESSION
		| EXPRESSION || EXPRESSION
		| EXPRESSION && EXPRESSION
		| (EXPRESSION)
		| -EXPRESSION
		| CONSTANT

CONSTANT -> number | T | F

TYPE -> (id, SEC)

SEC -> min | max | number
```

## Security levels
In this implementation 
The Security levels form a total order, where for every number n, min < n < max. 
Numbers follow a standard total order of the integers where the highest number have the maximum security.



## Examples
The programs folder contains a few example files. 

## Errors

