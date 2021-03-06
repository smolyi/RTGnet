# RTGnet


RTGnet is a Python based tool, so no real setup or compilation is required.
The RTGnet tool implements a graph-search algorithm which identifies the
k-best trees defined using a Regular Tree Grammar (RTG). The user must specify
the graph to be searched, the RTG query which defines the trees to be searched
and additional parameters (see below). The algorithm was published in a peer-
reviewed journal [https://www.liebertpub.com/doi/full/10.1089/cmb.2015.0168].
RTGnet is implemented in Python2.7, no setup or compilation is required.


Presequites
============

- Python 2 (>= 2.7) 
- numpy

Usage
============
usage: rtgnet.py [-h] [-t T] [-ss SS] graph nodes grammar k maxSize

positional arguments:
  graph       A graph file path. Format: node1<tab>node2<tab>weight.
  nodes       A node-labeling file path. Format: node<tab>label.
  grammar     A grammar file path. Format: node<tab>label.
  k           The number of trees in the output.
  maxSize     The upper bound on the number of nodes in the output trees.

optional arguments:
  -h, --help  show this help message and exit
  -t T        A lower bound on the score of the sought trees.
  -ss SS      Scoring scheme.1=sum of edge weights. 2=Average of edge
              weights.3=sum of grammar weights

Example
============
python rtgnet.py sample/graph.txt sample/labels.txt sample/grammar.txt 10 5


 Output
============
- dump.txt
- dump.pkl
