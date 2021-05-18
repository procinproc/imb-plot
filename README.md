# Purpose

This Python program is to create graphs from the output
of [IMB](https://github.com/intel/mpi-benchmarks).

# Usage

	$ python3 imb-plot.py <IMB-OUTPUT-FILENAME>

The IMB output file may contain a single benchmark result or mutiple
benchmark results. This program will produce a graph in PDF of each
benchmark.

Additionally, CVS file corresponding to each PDF graph will allso be
created so that users can create neat graphs easily.

# Limitation

Currently only IMB-MPI1 output can handle.

# Author

Atsushi Hori
NII, Japan
