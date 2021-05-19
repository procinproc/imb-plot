# Purpose

This Python program is to create graphs from the output
of [IMB](https://github.com/intel/mpi-benchmarks).

# Usage

	$ python3 imb-plot.py <IMB-OUTPUT-FILENAME> [ <COMMENT> ]

The IMB output file may contain a single benchmark result or mutiple
benchmark results. This program will produce a graph in PDF of each
benchmark. The title of each graph consists of benchmark name
(PingPong, Alltoall, Barrier, ...) and optional comment.

Additionally, CSV file corresponding to each PDF graph will allso be
created so that users can create neat graphs easily.

# Limitation

Currently only IMB-MPI1 output can be handled.

# Author

Atsushi Hori  
NII, Japan  
