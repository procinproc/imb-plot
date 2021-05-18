
"imb-plot: making graphs from IMB-MPI1 output"

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

if len( sys.argv ) == 0:
    print( 'No input file' )
    sys.exit( 1 )

imb_outfile = sys.argv[1]

def my_readline( file ):
    byte_str = f.readline()
    if len( byte_str ) == 0:
        return None
    try:
        if byte_str[0] in 'abc':
            ch_str = byte_str   # python2
        else:
            ch_str = byte_str
    except:                     # python3
        ch_str = byte_str.decode()
    if len( ch_str ) > 0:
        ch_str = ch_str[0:-1]   # remove newline
    tokens = ch_str.split()
    return tokens

def get_benchmark( f ):
    while( True ):
        tokens = my_readline( f )
        if tokens is None:
            return None
        if len( tokens ) != 3:
            continue
        if tokens[1] == 'Benchmarking':
            return tokens[2]

def get_nprocs( f ):
    tokens = my_readline( f )
    if tokens is None:
        return None
    nprocs = int( tokens[3] )
    while( True ):
        tokens = my_readline( f )
        if len( tokens ) == 1 and tokens[0][0] == '#' and tokens[0][1] == '-':
            my_readline( f )    # skip header
            break
    return nprocs

def ping( f, bench, np ):
    print( bench )
    df = pd.DataFrame( [], columns=['Latency','Bandwidth'] )
    while( True ):
        tokens = my_readline( f )
        if tokens == [] or tokens is None:
            break;
        df.loc[ int(tokens[0]) ] = [ float(tokens[2]), float(tokens[3]) ]

    df.to_csv( bench+'.csv', sep=',' )

    plt.loglog()
    fig, ax0 = plt.subplots(1,1)
    ax0.set_xscale('log')
    ax0.set_yscale('log')
    ax0.grid()
    ax1 = ax0.twinx()
    ax1.grid( axis='y', linestyle='dotted' )
    ax1.set_yscale('log')
    ax0.plot( df['Latency'],   label='Latency',   color='Red'  )
    ax1.plot( df['Bandwidth'], label='Bandwidth', color='Blue' )
    h0, l0 = ax0.get_legend_handles_labels()
    h1, l1 = ax1.get_legend_handles_labels()
    ax1.legend( h0+h1, l0+l1, loc='lower right' )
    plt.title( bench )
    plt.savefig( bench+'.pdf' )
    plt.close('all')

    nb = get_benchmark( f )
    np = get_nprocs( f )
    return ( nb, np )

def exchange( f, bench, np ):
    print( bench )
    df_lat = pd.DataFrame( [], columns=[ np ] )
    df_bdw = pd.DataFrame( [], columns=[ np ] )
    while( True ):
        while( True ):
            tokens = my_readline( f )
            if tokens == [] or tokens is None:
                break;
            df_lat.loc[ int(tokens[0]), np ] = float(tokens[4])
            df_bdw.loc[ int(tokens[0]), np ] = float(tokens[5])
        nb = get_benchmark( f )
        np = get_nprocs( f )
        if nb != bench:
            break

    df_lat.to_csv( bench+'-latency.csv',   sep=',' )
    df_bdw.to_csv( bench+'-bandwidth.csv', sep=',' )

    ax = df_lat.plot( title=bench+' (latency)',
                      loglog=True, grid=True, legend='reverse' )
    ax.set_xlabel( 'Length (bytes)' )
    ax.set_ylabel( 'Latency (usec)' )
    plt.savefig( bench+'-latency.pdf' )
    plt.close('all')
    ax = df_bdw.plot( title=bench+' (bandwidth)',
                      loglog=True, grid=True, legend='reverse' )
    ax.set_xlabel( 'Length (bytes)' )
    ax.set_ylabel( 'Bandwidth (Mbytes/sec)' )
    plt.savefig( bench+'-bandwidth.pdf' )
    plt.close('all')

    return ( nb, np )

def collective( f, bench, np ):
    print( bench )
    df = pd.DataFrame( [], columns=[ np ] )
    while( True ):
        while( True ):
            tokens = my_readline( f )
            if tokens == [] or tokens is None:
                break;
            df.loc[ int(tokens[0]), np ] = float(tokens[4])
        nb = get_benchmark( f )
        np = get_nprocs( f )
        if nb != bench:
            break

    df.to_csv( bench+'.csv', sep=',' )

    ax = df.plot( title=bench,
                  loglog=True, grid=True, legend='reverse' )
    ax.set_xlabel( 'Length (bytes)' )
    ax.set_ylabel( 'Latency (usec)' )
    plt.savefig( bench+'.pdf' )
    plt.close('all')

    return ( nb, np )

def barrier( f, bench, np ):
    print( bench )
    df = pd.DataFrame( [], columns=[ 'Latency' ] )
    while( True ):
        tokens = my_readline( f )
        if tokens == [] or tokens is None:
            break;
        df.loc[ np ] = float(tokens[3])
        nb = get_benchmark( f )
        np = get_nprocs( f )
        if nb != bench:
            break

    df.to_csv( bench+'.csv', sep=',' )
    
    ax = df.plot( title=bench,
                  grid=True, marker='*', ylim=(0,None), legend=None )
    ax.set_xscale( 'log' )
    ax.set_xlabel( '# procs' )
    ax.set_ylabel( 'Latency (usec)' )
    plt.savefig( bench+'.pdf' )
    plt.close('all')

    return ( nb, np )

benchmarks = { 'PingPong': 		ping,
               'PingPing': 		ping,
               'Sendrecv': 		exchange,
               'Exchange': 		exchange,
               'Allreduce': 		collective,
               'Reduce': 		collective,
               'Reduce_local':		collective,
               'Reduce_scatter': 	collective,
               'Reduce_scatter_block': 	collective,
               'Allgather':		collective,
               'Allgatherv':		collective,
               'Gather':		collective,
               'Gatherv':		collective,
               'Scatter':		collective,
               'Scatterv':		collective,
               'Alltoall':		collective,
               'Alltoallv':		collective,
               'Bcast':			collective,
               'Barrier':		barrier }

with open( imb_outfile, mode='r' ) as f:
    bench = get_benchmark( f )
    nproc = get_nprocs( f )
    while bench != None:
        if not bench in benchmarks:
            print( 'Unknown benchmark: ', bench )
            bench = get_benchmark( f )
            nproc = get_nprocs( f )
        else:
            ( bench, nproc ) = benchmarks[bench]( f, bench, nproc )

sys.exit( 0 )
