"""
Created on Apr 17, 2014

@author: Jens Luebben

Module for filtering atom data. The module interprets
cmd line input to select atoms based on their attributes.
"""


def set_filter(config):
    """
    Function to define which atom pairs are used for the
    calculation of Uiso.

    The filter a list of lists. Every list is one
    filter critereon consisting of an attribute, a value
    a truth criteron and a function.
    For every list the value of the specified attribute is
    compared to the value specified. Only if the comparison of
    both values is equal to the specified truth criterion,
    the Uiso value is calculated.
    If a function is specified, the attribute is passed to
    the function and the return value is compared to
    the truth criterion.
    The latter three parameters default to 'True', True', None
    if not specified.

    To define the filter the commandline argument 'filter=' is
    used.
    Example:
    '... filter=filter=[invariom_name:O2c,invariom_code:42:True,None]
    will generate:
    [['invariom_name', 'O2c',True,None],
    ['invariom_code', 42 , True, len]]
    This filter defines that only those atoms with the invariom
    name 'O2c' and an invariom code with a length of 42 are considered
    for Uiso calculations.

    A second filter is defined for neighbor atoms. It follows the
    same syntax except its commanline keyword is 'partnerfilter'
    and is applied to all atoms returned by crystgeom.get_framework\
    _neighbors().
    """
    try:
        # =======================================================================
        # isofilter=[arg.partition('=')[-1] for arg in argv if 'atomfilter=' in arg][0][1:-1].split(',')
        #=======================================================================
        isofilter = config.arg('atomfilter')
        isofilter = [f.split('=') for f in isofilter]

        for f in isofilter:
            if len(f) < 2:
                f.append('True')
            if len(f) < 3:
                f.append('True')
            if len(f) < 4:
                f.append('None')
    except:
        isofilter = [['element', 'H', 'True', 'None']]
        isofilter = [['element', 'XXX', 'False', 'None']]
    try:
        # =======================================================================
        # isopartnerfilter=[arg.partition('=')[-1] for arg in argv if 'partnerfilter=' in arg][0][1:-1].split(',')
        #=======================================================================
        # isopartnerfilter = config.arg('partnerfilter')[1:-1].split(',')
        isopartnerfilter = config.arg('partnerfilter')
        isopartnerfilter = [f.split('=') for f in isopartnerfilter]
        # isopartnerfilter = [f.split(':') for f in isopartnerfilter]
        for f in isopartnerfilter:
            if len(f) < 2:
                f.append('True')
            if len(f) < 3:
                f.append('True')
            if len(f) < 4:
                f.append('None')
    except:
        isopartnerfilter = [['None', 'None', 'None', 'None']]
    return isofilter, isopartnerfilter
    isofilterlist = []
    isopartnerfilterlist = []
    for i in xrange(len(isofilter) / 2):
        isofilterlist.append(tuple(isofilter[2 * i:2 * i + 2]))
    for i in xrange(len(isopartnerfilter) / 2):
        isopartnerfilterlist.append(tuple(isopartnerfilter[2 * i:2 * i + 2]))

    return [isofilterlist, isopartnerfilterlist]


def apply_filter(atom, isofilters):
    """
    Evaluates the filter expression. Returns True
    if the the filter value is equal to the
    corresponding attribute for all filters.
    """
    if 'None' in isofilters[0][0]:
        return True

    functionfilters = [isofilter for isofilter in isofilters if not isofilter[-1] == 'None']
    functionfilters = ['{}(atom.{}){}={}'.format(f[3], f[0], f[2], f[1]).replace('True', '=').replace('False', '!') for
                       f in functionfilters]
    if all(getattr(atom, isofilter[0]) == isofilter[1] for isofilter in isofilters if
           isofilter[2] == 'True' and isofilter[-1] == 'None'):
        if all(getattr(atom, isofilter[0]) != isofilter[1] for isofilter in isofilters if
               isofilter[2] == 'False' and isofilter[-1] == 'None'):
            for functionfilter in functionfilters:
                if not eval(functionfilter):
                    return False
            return True
    else:
        return False


def filter_atom_pair(config, atom1, atom2):
    """
    Tests atom1 against 'atomfilter' and atom2 against 'partnerfilter'.
    Returns 'True' if both tests return 'True'.
    """
    atomfilter, partnerfilter = set_filter(config)
    if apply_filter(atom1, atomfilter) and apply_filter(atom2, partnerfilter):
        return True


def filter_atom(config,atom):
    atomfilter, _ = set_filter(config)
    if apply_filter(atom,atomfilter):
        return True