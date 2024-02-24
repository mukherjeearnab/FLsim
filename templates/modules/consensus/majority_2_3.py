'''
Majority 2/3 Consensus
Selects the parameter (hash) which is similar to more than 2/3rd of all the parameters (hash)
'''
from collections import Counter


def consensus(params: list, extra_datas: list) -> str:
    '''
    Majority 2/3 Consensus
    '''

    p_count = dict(Counter(params))

    print("Param Count", p_count)

    c_dict = dict()
    for k, v in p_count.items():
        c_dict[v] = k

    next_param = c_dict[max(c_dict.keys())]

    return next_param, extra_datas[0]
