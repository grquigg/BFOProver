# PyProver #

## An algorithm for fact-checking and inference using Basic Formal Ontology (BFO) ##

This is a program designed to act as an interface for working with queries in Basic Formal Ontology (BFO). It is a Python adaptation of Werner Cuester's code, who originally wrote the code in Prolog. 

The repository itself is in it a bit of disarray currently, but ideally it should look more presentable sometime soon once the code actually becomes more readable. 

## Usage

### Inference 

The inference algorithm can be run using the command 

```python prover.py --start [start_file] --rulefile [rule_file] --debug [Boolean]```

The algorithm takes in a start_file as a "seed" to generate more facts from and recursively finds patterns in the list of generated facts and finds corresponding rules in the rulebase to generate new rules using First Order (FO) Logic.

The algorithm runs on a node based discovery algorithm similarly to the Rete algorithm. 

## File formatting

### Initial facts
The start file should look something like this:\
<code>
%-----database
t([instance-of,me,object,t]).\
t([inheres-in,my-smartness,me]).\
t([instance-of,my-smartness,quality,t]).\
t([realizes,my-thinking,my-thinking-disposition]).\
t([instance-of,my-thinking,process,t]).
</code>

## Future directions

The convient thing about designing the inference algorithm around a graph-like structure is that it will become very easy to develop a UI interface to determine how different facts were derived. 