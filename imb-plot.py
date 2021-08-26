
"imb-plot: making graphs from IMB-MPI1 output"

import os
import sys
import pandas as pd
import math
import matplotlib.pyplot as plt

bench_dict = {}

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

def ping( bench, np ):
    clm = 0
    try:
        np_dict = bench_dict[bench]
        try:
            ( clm, df_lat, df_bdw ) = np_dict[np]
        except:
            df_lat = pd.DataFrame( [], dtype=float )
            df_bdw = pd.DataFrame( [], dtype=float )
    except:
        df_lat = pd.DataFrame( [], dtype=float )
        df_bdw = pd.DataFrame( [], dtype=float )
        clm = 0
        bench_dict.setdefault( bench, { 2: ( clm, df_lat, df_bdw ) } )
        np_dict = bench_dict[bench]

    while True:
        while True:
            tokens = my_readline( f )
            if tokens == [] or tokens is None:
                break
            try:
                if int(tokens[0]) == 0:
                    continue
                df_lat.at[ int(tokens[0]), clm ] = float(tokens[2])
                df_bdw.at[ int(tokens[0]), clm ] = float(tokens[3])
            except:
                break
        clm += 1
        rv = get_benchmark( f )
        if rv is None:
            break
        ( b, p ) = rv
        if b != bench or p != np:
            break

    np_dict[np] = ( clm, df_lat, df_bdw )
    return rv

def ping_aft( f, bench, np_dict ):
    ( clm, df_lat, df_bdw ) = np_dict[2]

    df_lat.to_csv( fbase+bench+'-latency.csv',   sep=',' )
    df_bdw.to_csv( fbase+bench+'-bandwidth.csv', sep=',' )

    df_lat_mean = df_lat.mean( axis='columns' )
    df_bdw_mean = df_bdw.mean( axis='columns' )

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

    ax0.plot( df_lat_mean, label='Latency',   color='Red'  )
    ax1.plot( df_bdw_mean, label='Bandwidth', color='Blue' )
    ( h0, l0 ) = ax0.get_legend_handles_labels()
    ( h1, l1 ) = ax1.get_legend_handles_labels()
    ax1.legend( h0+h1, l0+l1, loc='upper left' )
    plt.title( bench )
    plt.savefig( fbase+bench+'.pdf' )
    plt.close( 'all' )


def exchange( bench, np ):
    clm = 0
    try:
        np_dict = bench_dict[bench]
        try:
            ( clm, df_lat, df_bdw ) = np_dict[np]
        except:
            df_lat = pd.DataFrame( [], dtype=float )
            df_bdw = pd.DataFrame( [], dtype=float )
    except:
        df_lat = pd.DataFrame( [], dtype=float )
        df_bdw = pd.DataFrame( [], dtype=float )
        clm = 0
        np_dict = { np: ( clm, df_lat, df_bdw ) }
        bench_dict.setdefault( bench, np_dict )
        
    while True:
        while True:
            tokens = my_readline( f )
            if tokens == [] or tokens is None:
                break;
            try:
                df_lat.at[ int(tokens[0]), clm ] = float(tokens[4])
                df_bdw.at[ int(tokens[0]), clm ] = float(tokens[5])
            except:
                break
        clm += 1
        rv = get_benchmark( f )
        if rv is None:
            break
        ( b, p ) = rv
        if b != bench or p != np:
            break

    np_dict[np] = ( clm, df_lat, df_bdw )
    return rv

def exchange_aft( f, bench, np_dict ):
    df_lat_mean = pd.DataFrame( [], dtype=float )
    df_bdw_mean = pd.DataFrame( [], dtype=float )
    for np in sorted( np_dict.keys() ):
        ( clm, df_lat, df_bdw ) = np_dict[np]
        df_lat.to_csv( fbase+bench+'-latency-'+str(np)+'.csv',
                       sep=',' )
        df_bdw.to_csv( fbase+bench+'-bandwidth-'+str(np)+'.csv',
                       sep=',' )
        df_lat_mean[np] = df_lat.mean( axis='columns' )
        df_bdw_mean[np] = df_bdw.mean( axis='columns' )

    ax = df_lat_mean.plot( title=bench+' (latency)',
                           loglog=True, grid=True, legend='reverse' )
    ax.set_xlabel( 'Length (bytes)' )
    ax.set_ylabel( 'Latency (usec)' )
    plt.savefig( fbase+bench+'-latency.pdf' )
    plt.close( 'all' )

    ax = df_bdw_mean.plot( title=bench+' (bandwidth)',
                           loglog=True, grid=True )
    ax.set_xlabel( 'Message Size [Bytes]' )
    ax.set_ylabel( 'Bandwidth (Mbytes/sec)' )
    plt.savefig( fbase+bench+'-bandwidth.pdf' )
    plt.close( 'all' )

def collective( bench, np ):
    clm = 0
    try:
        np_dict = bench_dict[bench]
        try:
            ( clm, df_lat, df_bdw ) = np_dict[np]
        except:
            df = pd.DataFrame( [], dtype=float )
            np_dict.setdefault( np, ( clm, df ) )
    except:
        df = pd.DataFrame( [], dtype=float )
        np_dict = { np: ( clm, df) }
        bench_dict.setdefault( bench, np_dict )

    while True:
        while True:
            tokens = my_readline( f )
            if tokens == [] or tokens is None:
                break;
            try:
                df.at[ int(tokens[0]), clm ] = float(tokens[4])
            except:
                break
        clm += 1
        rv = get_benchmark( f )
        if rv is None:
            break
        ( b, p ) = rv
        if b != bench or p != np:
            break

    np_dict[np] = ( clm, df )
    return rv

def coll_aft( f, bench, np_dict ):
    df_mean = pd.DataFrame( [], dtype=float )
    for np in sorted( np_dict.keys() ):
        ( clm, df ) = np_dict[np]
        df.to_csv( fbase+bench+'-'+str(np)+'.csv', sep=',' )
        df_mean[np] = df.mean( axis='columns' )

    ax = df_mean.plot( title=bench,
                       loglog=True, grid=True, legend='reverse' )
    ax.set_xlabel( 'Message Size [Bytes]' )
    ax.set_ylabel( 'Latency (usec)' )
    plt.savefig( fbase+bench+'.pdf' )
    plt.close( 'all' )

def barrier( bench, np ):
    clm = 0
    try:
        ( clm, df ) = bench_dict[bench]
    except:
        df = pd.DataFrame( [], dtype=float )
        bench_dict.setdefault( bench, ( clm, df ) )

    while True:
        while True:
            tokens = my_readline( f )
            if tokens == [] or tokens is None:
                break;
            try:
                df.at[ np, clm ] = float(tokens[3])
            except:
                break
        clm += 1
        rv = get_benchmark( f )
        if rv is None:
            break
        ( b, p ) = rv
        if b != bench or p != np:
            break

    bench_dict[bench] = ( clm, df )
    return rv

def barrier_aft( f, bench, bar ):
    ( clm, df ) = bar
    df.to_csv( fbase+bench+'.csv', sep=',' )
    df_mean = df.mean( axis='columns' )

    print( df_mean )
    ax = df_mean.plot( title=bench, grid=True, marker='*',
                       ylim=(0,None), legend=None )
    ax.set_xscale( 'log' )
    ax.set_xlabel( '# Procs' )
    ax.set_ylabel( 'Latency [usec]' )
    plt.savefig( fbase+bench+'.pdf' )
    plt.close( 'all' )


benchmarks = {
    # MPI1
    'PingPong': 		( ping,		ping_aft ),
    'PingPing': 		( ping,		ping_aft ),
    'Sendrecv': 		( exchange,	exchange_aft ),
    'Exchange': 		( exchange,	exchange_aft ),
    'Allreduce': 		( collective,	coll_aft ),
    'Reduce': 			( collective,	coll_aft ),
    'Reduce_local':		( collective,	coll_aft ),
    'Reduce_scatter': 		( collective,	coll_aft ),
    'Reduce_scatter_block': 	( collective,	coll_aft ),
    'Allgather':		( collective,	coll_aft ),
    'Allgatherv':		( collective,	coll_aft ),
    'Gather':			( collective,	coll_aft ),
    'Gatherv':			( collective,	coll_aft ),
    'Scatter':			( collective,	coll_aft ),
    'Scatterv':			( collective,	coll_aft ),
    'Alltoall':			( collective,	coll_aft ),
    'Alltoallv':		( collective,	coll_aft ),
    'Bcast':			( collective,	coll_aft ),
    'Barrier':			( barrier,	barrier_aft ),
    # RMA
    'Put_all_local':		( ping,		ping_aft ),
    'One_put_all':		( ping,		ping_aft ),
    'All_put_all':		( collective,	coll_aft ),
    'One_get_all':		( ping,		ping_aft ),
    'All_get_all':		( collective,	coll_aft ),
    'Exchange_put':		( collective,	coll_aft ),
    'Exchange_get':		( collective,	coll_aft ),
    'Accumulate':		( ping,		ping_aft )
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
            print( '   Parsing:', bench, '[', nproc, ']' )
            ( func0, func1 ) = benchmarks[bench]
            rv = func0( bench, nproc )

for key in bench_dict.keys():
    ( func0, func1 ) = benchmarks[key]
    print( '   Drawing:', key )
    func1( f, key, bench_dict[key] )

sys.exit( 0 )
