#!/usr/bin/env python
from ConfigParser import SafeConfigParser
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime
import tempfile
import argparse
import json
import os

# Engines with various parameter setups
# (alias, runs, engine, env-vars)
engines = [
    ('numpy',        None,        None),
    ('simple',       'simple',    None),
    ('score',        'score', None),
    ('mcore',        'mcore', None),

    ('score_1',         'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"1"}),
    ('score_2',         'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"2"}),
    ('score_4',         'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"4"}),
    ('score_16',        'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"16"}),
    ('score_32',        'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"32"}),
    ('score_64',        'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"64"}),
    ('score_512',       'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"512"}),
    ('score_1024',      'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"1024"}),
    ('score_2048',      'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"2048"}),
    ('score_4096',      'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"4096"}),
    ('score_8192',      'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"8192"}),
    ('score_16384',     'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"16384"}),
    ('score_32768',     'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"32768"}),
    ('score_65536',     'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"65536"}),
    ('score_131072',    'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"131072"}),
    ('score_262144',    'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"262144"}),
    ('score_524288',    'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"524288"}),
    ('score_1048576',   'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"1048576"}),
    ('score_2097152',   'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"2097152"}),
    ('score_4194304',   'score',    {"CPHVB_VE_SCORE_BLOCKSIZE":"4194304"}),

    ('score_bins1',    'score',    {"CPHVB_VE_SCORE_BINMAX":"1"}),
    ('score_bins2',    'score',    {"CPHVB_VE_SCORE_BINMAX":"2"}),
    ('score_bins4',    'score',    {"CPHVB_VE_SCORE_BINMAX":"4"}),
    ('score_bins5 ',   'score',    {"CPHVB_VE_SCORE_BINMAX":"5"}),
    ('score_bins6',    'score',    {"CPHVB_VE_SCORE_BINMAX":"6"}),
    ('score_bins8',    'score',    {"CPHVB_VE_SCORE_BINMAX":"8"}),
    ('score_bins10',    'score',    {"CPHVB_VE_SCORE_BINMAX":"10"}),
    ('score_bins12',    'score',    {"CPHVB_VE_SCORE_BINMAX":"12"}),

] + \
[('score_bs%d_bm%d' % (2**i, j), 'score', {"CPHVB_VE_SCORE_BLOCKSIZE": str(2**i), "CPHVB_VE_SCORE_BINMAX": str(j)})  for j in xrange(1,20) for i in xrange(2,26)]

# Scripts and their arguments
# (alias, script, parameters)
scripts   = [
    ('Jacobi Fixed',                'jacobi_fixed.py',      '--size=7168*7168*4'),
    ('Monte Carlo PI - RIL',        'MonteCarlo.py',        '--size=10*1000000*10'),
    ('Shallow Water',               'swater.py',            '--size=2200*1'),
    ('kNN',                         'kNN.py',               '--size=10000*120'),
    ('Stencil - 1D 4way',           'stencil.simplest.py',  '--size=100000000*1'),
    ('Black Scholes',               'BlackSholes.py',       '--size=2000000*4'),

    ('Stencil - 2D',            'stencil.2d.py',      '--size=10240*1024*10'),
    ('Cache Synth',             'cache.py',        '--size=10485760*10*1'),
    ('Monte Carlo PI - 2byN',   'mc.2byN.py', '--size=10000000*20'),
    ('Monte Carlo PI - Nby2',   'mc.2byN.py', '--size=10000000*20'),
]
                                # DEFAULT BENCHMARK
default = {                     # Define a benchmark "suite" which runs:
    'scripts': [0,1,2,3,4,5],   # these scripts
    'engines': [0,1,2,3]        # using these engines
} 

waters = {
    'scripts':  [2],
    'engines':  [0, 1,2]
}

swaters = {
    'scripts':  [2],
    'engines':  [0,1]+[c for c, x in enumerate(engines) if 'score_b' in x[0]] 
}

cache_tiling = {
    'scripts': [0],
    'engines': [0,1]+[c for c, x in enumerate(engines) if 'score_bs' in x[0]]
}

test = {
    'scripts': [0],
    'engines': [0,1]
}

montecarlo = {
    'scripts': [1,9,10],
    'engines':  [0,1,2,3]
}

suites = {
    'default':      default,
    'cache_tiling': cache_tiling,
    'test':         test,
    'monte':        montecarlo,
    'waters':       waters,
    'swaters':      swaters,
}

def meta(src_dir, suite):

    p = Popen(              # Try grabbing the repos-revision
        ["git", "log", "--pretty=format:%H", "-n", "1"],
        stdin   = PIPE,
        stdout  = PIPE,
        cwd     = src_dir
    )
    rev, err = p.communicate()

    p = Popen(              # Try grabbing hw-info
        ["lshw", "-quiet", "-numeric"],
        stdin   = PIPE,
        stdout  = PIPE,
    )
    hw, err = p.communicate()

    p = Popen(              # Try grabbing hw-info
        ["hostname"],
        stdin   = PIPE,
        stdout  = PIPE,
    )
    hostname, err = p.communicate()

    p = Popen(              # Try grabbing python version
        ["python", "-V"],
        stdin   = PIPE,
        stdout  = PIPE,
        stderr  = PIPE
    )
    python_ver, err = p.communicate()
    python_ver  += err

    p = Popen(              # Try grabbing python version
        ["gcc", "-v"],
        stdin   = PIPE,
        stdout  = PIPE,
        stderr  = PIPE
    )
    gcc_ver, err = p.communicate()
    gcc_ver += err

    info = {
        'suite':    suite,
        'rev':      rev if rev else 'Unknown',
        'hostname': hostname if hostname else 'Unknown',
        'started':  str(datetime.now()),
        'ended':    None,
        'hw':       {
            'cpu':  open('/proc/cpuinfo','r').read(),
            'list': hw if hw else 'Unknown',
        },
        'sw':   {
            'os':       open('/proc/version','r').read(),
            'python':   python_ver if python_ver else 'Unknown',
            'gcc':      gcc_ver if gcc_ver else 'Unknown',
            'env':      os.environ.copy(),
        },
    }

    return info

def main(config, src_root, output, suite, runs=5):

    benchmark   = suites[suite]
    script_path = src_root +os.sep+ 'benchmark' +os.sep+ 'Python' +os.sep
    
    parser = SafeConfigParser()     # Parser to modify the cphvb configuration file.
    parser.read(config)             # Read current configuration

    results = {
        'meta': meta(src_root, suite),
        'runs': []
    }
    with tempfile.NamedTemporaryFile(delete=False, dir=output, prefix='benchmark-', suffix='.json') as fd:
        print "Running benchmark suite '%s'; results are written to: %s." % (suite, fd.name)
        for mark, script, arg in (scripts[snr] for snr in benchmark['scripts']):
            for alias, engine, env in (engines[enr] for enr in benchmark['engines']):

                cphvb = False
                if engine:                                  # Enable cphvb with the given engine.
                    cphvb = True
                    parser.set("node", "children", engine)  
                    parser.write(open(config, 'wb'))

                envs = None                                 # Populate environment variables
                if env:
                    envs = os.environ.copy()
                    envs.update(env)
                                                            # Setup process + arguments
                args        = ['taskset', '-c', '1', 'python', script, arg, '--cphvb=%s' % cphvb ]
                args_str    = ' '.join(args)
                print "{ %s - %s ( %s ),\n  %s" % ( mark, alias, engine, args_str )

                times = []
                for i in xrange(1, runs+1):

                    p = Popen(                              # Run the command
                        args,
                        stdin=PIPE,
                        stdout=PIPE,
                        env=envs,
                        cwd=script_path
                    )
                    out, err = p.communicate()              # Grab the output
                    elapsed = 0.0
                    if err:
                        print "ERR: Something went wrong %s" % err
                    else:
                        elapsed = float(out.split(' ')[-1] .rstrip())

                    print "  %d/%d, " % (i, runs), elapsed
                    
                    times.append( elapsed )

                print "}"
                                                            # Accumulate results
                results['runs'].append(( mark, alias, engine, env, args_str, times ))
                results['meta']['ended'] = str(datetime.now())

                fd.truncate(0)                              # Store the results in a file...
                fd.seek(0)
                fd.write(json.dumps(results, indent=4))
                fd.flush()
                os.fsync(fd)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Runs a benchmark suite and stores the results in a json-file.')
    parser.add_argument(
        'src',
        help='Path to the cphvb source-code.'
    )
    parser.add_argument(
        '--suite',
        default="default",
        choices=[x for x in suites],
        help="Name of the benchmark suite to run."
    )
    parser.add_argument(
        '--output',
        default="results",
        help='Where to store benchmark results.'
    )
    args = parser.parse_args()

    main(
        os.getenv('HOME')+os.sep+'.cphvb'+os.sep+'config.ini',
        args.src,
        args.output,
        args.suite,
        5
    )

