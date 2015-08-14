#!/usr/bin/env python
import argparse
import pprint
import json
import press

from result_parser import from_file, from_str, avg
from result_parser import standard_deviation as std

def stack_label(stack):
    """Returns a descriptive label of the stack"""
    ret = ""
    for component in stack[1:]:
        ret += "%s/"%component[0]
    return ret[:-1] #We remove the last "/" before returning

def raw(results):
    pprint.pprint(results)

def parsed(results):
    pprint.pprint(from_str(results))

def times(results):
    for script, bridge, manager, engine, res in from_str(results):
        print "%s [%s]:" % (script, stack_label(res['stack'])),
        if 'elapsed' not in res or len(res['elapsed']) < 1:
            print "N/A"
        else:
            print res["elapsed"],"%f (%f) %d"%(avg(res["elapsed"]), std(res["elapsed"]), len(res['elapsed']))

def csv(results):
    i = 1
    for script, bridge, manager, engine, res in from_str(results):
        print "%d, %s, %s, %s, %s, %f, %f"%(i, script, bridge, manager,
		engine, avg(res["elapsed"]), std(res["elapsed"]))
        i += 1

def troels(results):
    results = json.loads(results)['runs']
    i = 0
    for run in results:
        i += 1
        script = run['script_alias']
        total_time = filter(None,run['elapsed'])
        timings = run['timings']
        if i == 1:
            tk = timings.keys()
            print "#, Script, Total time, Total time dev., %s"%(", ".join(map(lambda (a,b):a+b,zip(tk,map(lambda s: " ,"+s+" dev.",tk)))))
        print ("%d, %s, %f, %f, "+(", ".join(map(lambda s: "%f, %f",tk))))%((i,script,avg(total_time),std(total_time))+sum(map(lambda k: (avg(timings[k]),std(timings[k])),tk),()))


def datadiff(results, baseline):
    import numpy as np
    results = json.loads(results)['runs']
    #Sort results into sets of scripts
    script_sets = {}
    for run in results:
        if run['script_alias'] not in script_sets:
            script_sets[run['script_alias']] = []
        script_sets[run['script_alias']].append(run)

    if len(script_sets) == 0:
        print "No valid results!"

    for s in script_sets.values():
        #Lets find the baseline
        base = None
        for run in s:
            if run['bridge_alias'] == baseline and len(run['data_output']) == 1:
                base = press.decode_data(run['data_output'][0])
                base = np.loads(base)
                break
        if base is None:
            print "Baseline not found for %s!"%s[0]['script_alias']
            continue
        for run in s:
            if run['bridge_alias'] == baseline:
                continue
            print "%s/%s/%s, "%(run['script_alias'], run['bridge_alias'], run['engine_alias']),

            if not run['save_data_output'] or len(run['data_output']) != 1:
                print "N/A"
                continue
            if np.isscalar(base) or base.ndim == 0:
                continue
            data = press.decode_data(run['data_output'][0])
            data = np.loads(data)
            diff = np.zeros_like(data)
            nz = base != 0
            diff[nz] = np.absolute(base[nz] - data[nz]) / np.absolute(base[nz])
            print "%s (std: %s, max: %s)"%(diff.mean(), np.std(diff), np.max(diff))

def fusepricer(results):
    out = ""
    for script, bridge, manager, engine, res in from_str(results):
        s = "%s ["%script
        for label, name, env in res['stack']:
            s += "%s/"%label
        out += "%s]"%s[:-1]
        if 'fuseprice' not in res:
            out += "N/A"
        else:
            out += " %s"%str(res['fuseprice'])
        out += "\n"
    out = out.split("\n")
    out.sort()
    print "\n".join(out)

def main():
    printers = {'raw':raw, 'times':times, 'parsed': parsed, 'csv': csv, \
                'troels': troels, 'datadiff': datadiff, 'pricer':fusepricer}

    parser = argparse.ArgumentParser()
    parser.add_argument("results", help="JSON file containing results")
    parser.add_argument(
        "-p", "--printer",
        choices=[p for p in printers],
        default='times',
        help="How to print results."
    )
    parser.add_argument(
        "--baseline",
        help="Set a baseline run."
    )
    args = parser.parse_args()

    printer = printers[args.printer]
    if args.baseline:
        printer(open(args.results).read(), args.baseline)
    else:
        printer(open(args.results).read())

