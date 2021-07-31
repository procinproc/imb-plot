
"imb-plot: making graphs from IMB-MPI1 output"

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

def my_readline( f ):
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
        nc = len( tokens )
        if nc > 3:
            if tokens[1] == 'BAD' and tokens[2] == 'TERMINATION':
                print( 'BAD TERMINATION' )
                return None
            continue
        if nc != 3:
            continue
        if tokens[1] == 'Benchmarking':
            bench = tokens[2]
            if not bench in benchmarks:
                print( 'Unsupported benchmark: ', bench )
                continue
            break

    tokens = my_readline( f )
    if tokens is None:
        return None
    nprocs = int( tokens[3] )
    # skip '#-----'
    while( True ):
        tokens = my_readline( f )
        if tokens is None:
            return None
        if len( tokens ) == 1 and tokens[0][0] == '#' and tokens[0][1] == '-':
            while( True ) :
                tokens = my_readline( f )
                if tokens[0] == '#bytes' or tokens[0] == '#repetitions':
                    break;
            break
    return ( bench, nprocs )

def ping( f, bench, np ):
    df = pd.DataFrame( [], columns=['Latency','Bandwidth'] )
    while( True ):
        tokens = my_readline( f )
        if tokens == [] or tokens is None:
            break;
        try:
            df.loc[ int(tokens[0]) ] = [ float(tokens[2]), float(tokens[3]) ]
        except:
            break

    df.to_csv( fbase+bench+'.csv', sep=',' )

    plt.loglog()
    fig, ax0 = plt.subplots(1,1)
    ax0.set_xscale('log')
    ax0.set_yscale('log')
    ax0.grid()
    ax0.set_ylabel( 'Latency' )
    ax0.set_xlabel( 'Message Size [Bytes]' )
    ax1 = ax0.twinx()
    ax1.grid( axis='y', linestyle='dotted' )
    ax1.set_yscale('log')
    ax1.set_ylabel( 'Bandwidth' )

    ax0.plot( df['Latency'],   label='Latency',   color='Red'  )
    ax1.plot( df['Bandwidth'], label='Bandwidth', color='Blue' )
    ( h0, l0 ) = ax0.get_legend_handles_labels()
    ( h1, l1 ) = ax1.get_legend_handles_labels()
    ax1.legend( h0+h1, l0+l1, loc='upper left' )
    plt.title( bench )
    plt.savefig( fbase+bench+'.pdf' )
    plt.close( 'all' )

    return get_benchmark( f )

def exchange( f, bench, np ):
    df_lat = pd.DataFrame( [], columns=[ np ] )
    df_bdw = pd.DataFrame( [], columns=[ np ] )
    while( True ):
        while( True ):
            tokens = my_readline( f )
            if tokens == [] or tokens is None:
                break;
            try:
                df_lat.loc[ int(tokens[0]), np ] = float(tokens[4])
                df_bdw.loc[ int(tokens[0]), np ] = float(tokens[5])
            except:
                break
        rv = get_benchmark( f )
        if rv is None or rv[0] != bench:
            break
        np = rv[1]

    df_lat.to_csv( fbase+bench+'-latency.csv',   sep=',' )
    ax = df_lat.plot( title=bench+' (latency)',
                      loglog=True, grid=True, legend='reverse' )
    ax.set_xlabel( 'Length (bytes)' )
    ax.set_ylabel( 'Latency (usec)' )
    plt.savefig( fbase+bench+'-latency.pdf' )
    plt.close( 'all' )

    df_bdw.to_csv( fbase+bench+'-bandwidth.csv', sep=',' )
    ax = df_bdw.plot( title=bench+' (bandwidth)',
                      loglog=True, grid=True )
    ax.set_xlabel( 'Message Size [Bytes]' )
    ax.set_ylabel( 'Bandwidth (Mbytes/sec)' )
    plt.savefig( fbase+bench+'-bandwidth.pdf' )
    plt.close( 'all' )

    return rv

def collective( f, bench, np ):
    df = pd.DataFrame( [], columns=[ np ] )
    while( True ):
        while( True ):
            tokens = my_readline( f )
            if tokens == [] or tokens is None:
                break;
            try:
                df.loc[ int(tokens[0]), np ] = float(tokens[4])
            except:
                break
        rv = get_benchmark( f )
        if rv is None or rv[0] != bench:
            break
        np = rv[1]

    df.to_csv( fbase+bench+'.csv', sep=',' )

    ax = df.plot( title=bench,
                  loglog=True, grid=True, legend='reverse' )
    ax.set_xlabel( 'Message Size [Bytes]' )
    ax.set_ylabel( 'Latency (usec)' )
    plt.savefig( fbase+bench+'.pdf' )
    plt.close( 'all' )

    return rv

def barrier( f, bench, np ):
    df = pd.DataFrame( [], columns=[ 'Latency' ] )
    while( True ):
        while( True ):
            tokens = my_readline( f )
            if tokens == [] or tokens is None:
                break;
            try:
                df.loc[ np ] = float(tokens[3])
            except:
                break
        rv = get_benchmark( f )
        if rv is None or rv[0] != bench:
            break
        np = rv[1]

    df.to_csv( fbase+bench+'.csv', sep=',' )
    
    ax = df.plot( title=bench,
                  grid=True, marker='*', ylim=(0,None), legend=None )
    ax.set_xscale( 'log' )
    ax.set_xlabel( '# Procs' )
    ax.set_ylabel( 'Latency [usec]' )
    plt.savefig( fbase+bench+'.pdf' )
    plt.close( 'all' )

    return rv

benchmarks = {
    # MPI1
    'PingPong': 		ping,
    'PingPing': 		ping,
    'Sendrecv': 		exchange,
    'Exchange': 		exchange,
    'Allreduce': 		collective,
    'Reduce': 			collective,
    'Reduce_local':		collective,
    'Reduce_scatter': 		collective,
    'Reduce_scatter_block': 	collective,
    'Allgather':		collective,
    'Allgatherv':		collective,
    'Gather':			collective,
    'Gatherv':			collective,
    'Scatter':			collective,
    'Scatterv':			collective,
    'Alltoall':			collective,
    'Alltoallv':		collective,
    'Bcast':			collective,
    'Barrier':			barrier,
    # RMA
    'Put_all_local':		ping,
    'One_put_all':		ping,
    'All_put_all':		collective,
    'One_get_all':		ping,
    'All_get_all':		collective,
    'Exchange_put':		collective,
    'Exchange_get':		collective,
    'Accumulate':		ping
}

argc = len( sys.argv )
if argc == 0:
    print( 'No input file' )
    sys.exit( 1 )

for i in range( 1, argc ):
    imb_datfile = sys.argv[i]
    print( imb_datfile )
    fbase = os.path.splitext( os.path.basename( imb_datfile ) )[0] + '-'

    with open( imb_datfile, mode='r' ) as f:
        rv = get_benchmark( f )
        while rv != None:
            ( bench, nproc ) = rv
            print( '   ', bench )
            rv = benchmarks[bench]( f, bench, nproc )

sys.exit( 0 )
