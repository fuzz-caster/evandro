import numpy as np
import math
import pandas as pd

def f_low(x, _mid, _min): return 1.0 * (_mid - x) / (_mid - _min)

def f_mid_1(x, _mid, _min): return 1.0 * (x - _min) / (_mid - _min)
def f_mid_2(x, _max, _mid): return 1.0 * (_max - x) / (_max - _mid)

def f_high(x, _max, _mid): return 1.0 * (x - _mid) / (_max - _mid)

def inv_f_high(y, _max, _mid): return y * (_max - _mid) + _mid

def inv_f_low(y, mid, min): return y * (mid - min) + min

def inv_f_mid(y, max, mid, min):
    mid_1 = y * (mid - min) + min
    mid_2 = max - (y * (max - mid))
    return (mid_1 + mid_2) / 2.0

def membership(x, _max, _mid, _min):
    # Low
    low = None
    mid = None
    high = None

    if (x <= _min):
        low = 1
    elif (_min < x < _mid):
        low = f_low(x, _mid, _min)
    else:
        low = 0

    if x <= _min or x >= _max:
        mid = 0
    elif _min < x <= _mid:
        mid = f_mid_1(x, _mid, _min)
    elif _mid < x < _max:
        mid = f_mid_2(x, _max, _mid)
    else:
        raise Exception(f"Can't find matching condition for x={x}, max={_max}, mid={_mid}, min={_min}")

    if x >= _max:
        high = 1
    elif _mid < x < _max:
        high = f_high(x, _max, _mid)
    else:
        high = 0

    return [
        low,
        mid,
        high
    ]

def vector_membership(X, _max, _mid, _min):
    f = lambda x: membership(x, _max, _mid, _min)
    return np.vectorize(f)(X)

def almost_zero(x):
    return abs(x - 0) < 0.01

def filter_rule(rule, membership):
    *components, target = rule
    results = []
    for idx, comp in enumerate(components):
        mem = membership[idx][comp]
        if (almost_zero(mem)):
            return None
        results.append(mem)
    return results

def predict(x, Xs, rules):
    '''
    :param x: list of inputs.
    :param Xs: previous data (numpy array).
    :rules Xs: List of rules.
    :return:
    '''

    maxes = Xs.max(axis=0)
    mins = Xs.min(axis=0)
    mids = (mins + maxes) / 2.0

    print("maxes")
    print(maxes)
    print()
    print("mins")
    print(mins)
    print()

    N_DIM = 3

    memberships = []
    for i in range(N_DIM):
        _max = maxes[i]
        _mid = mids[i]
        _min = mins[i]
        mem_i = membership(x[i], _max, _mid, _min)
        memberships.append(mem_i)

    results = []
    for idx, rule in enumerate(rules):
        rule_result = filter_rule(rule, memberships)
        if (rule_result is None):
            continue
        min_in_rule = min(rule_result)
        results.append(( idx, rule_result, rule, min_in_rule ))

    if len(results) == 0:
        print(results)
        raise Exception("Can't find at least one matching rule")

    _filter_zero = [ result for result in results if 0 not in result ]
    if len(_filter_zero) != 0:
        results = _filter_zero

    max_rule = max(results, key=lambda r: r[3])
    y = max_rule[3]
    target_level = max_rule[2][-1]

    target_max = maxes[3]
    target_min = mins[3]
    target_mid = (target_min + target_max) / 2.0

    defuzz = None
    if target_level == 2:
        defuzz = inv_f_high(y, target_max, target_mid)
    if target_level == 1:
        defuzz = inv_f_mid(y, target_max, target_mid, target_min)
    if target_level == 0:
        defuzz = inv_f_low(y, target_mid, target_min)

    if defuzz is None:
        raise Exception("Something wrong")

    clf_result = {
        "label": target_level,
        "defuzz": defuzz
    }

    return clf_result