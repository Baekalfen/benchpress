from benchpress.default import *
from bp_cpu_shared import *

scripts = [
    ('Heat Equation',   'heat_equation',    '--size=14000*14000*10'),
]

numpy = {
    'scripts': scripts,
    'launchers': [python_numpy],
    'bohrium': bh_stack_none,
    "use_slurm_default": True,
}

sequential = {
    'scripts': scripts,
    'launchers': [c99_seq, cpp11_seq, c99_seq_ts, cpp11_seq_ts],
    'bohrium': bh_stack_none,
    "use_slurm_default": True,
}

multicore = {
    'scripts': scripts,
    'launchers': [c99_omp, cpp11_omp],
    'bohrium': stack_omp_t32,
    "use_slurm_default": True,
}

bohrium = {
    'scripts': scripts,
    'launchers': [python_bohrium, cpp11_bxx],
    'bohrium': bh_stack_cpu_t32,
    "use_slurm_default": True,
}

suites = [
    cseq,
    omp,
    bohrium,
    np
]
