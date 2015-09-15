"""
Created on Nov 1, 2013

@author: jens

Module containing functionality related to the creation of
APD-database files.
"""
from os import walk, listdir

import numpy as np

from lauescript.invstring2 import get_invariom_names, get_invariom_names_simple
from lauescript.cryst import crystgeom as cg


def daba_generator(data, frequency_cutoff):
    """
    Generates a database.txt file that contains all neccesary data to
    use the APD-Tools without any other files. (Besides the experimental
    data files.)
    """
    errorlog = open('error.log', 'w')
    pathlist = []
    namedict = {}
    invlist = []
    print '\nRunning database generator!\n'
    filepointer = open('DABA.txt')
    nameswitch = False
    for line in filepointer.readlines():
        if 'Path' in line:
            newpath = line.split(' ')[-1][:-1]
            newpath = newpath.replace('[', '\[')
            newpath = newpath.replace(']', '\]')
            newpath = newpath.replace(',', '.')
            pathlist.append(newpath)
            if not pathlist[-1] in namedict.keys():
                namedict[pathlist[-1]] = []
        if '!' in line[0]:
            nameswitch = True
        elif nameswitch:
            nameswitch = False
            namedict[pathlist[-1]].append(str(line[:-1]))
            invlist.append(str(line[:-1]))

    comlist = pathlist

    datalist = read_multiple_files(invlist, comlist,
                                   dabamode=True, errorlog=errorlog)
    datalist2 = [i for i in datalist if i is not None]
    # ===========================================================================
    # invlist2=[invlist[i] for i in xrange(len(invlist))\
    #                      if not datalist[i]==None]
    #===========================================================================
    pathlist2 = [pathlist[i] for i in xrange(len(pathlist)) \
                 if datalist[i] is not None]
    invmollist = []
    for path in pathlist2:
        invmollist.append(path.split('/')[-4])
    print 'Parsing frequency information...'
    global alldata
    alldata1, warninglist = extract_single_freqencies_from_list(datalist2,
                                                                invmollist,
                                                                cutoff=frequency_cutoff)
    for warning in warninglist:
        errorlog.write \
            ('\n!!!WARNING!!! Could not parse frequencies in file :' \
             + pathlist2[warning][:-11])

    for path in pathlist2:
        invmollist.append(path.split('/')[-4])

    print 'Setting up data structure...'
    dabacounter = 0
    for invmol in invmollist:
        dabacounter += 1
        if dabacounter % 400 == 0: print '...'
        try:
            i = invmollist.index(invmol)
            data.add_molecule(str(vars()['invmol']), daba=True)
            pathlist2[i] = pathlist2[i].replace('home', 'user')
            cell, pos, keylist = cg.read_coordinates(pathlist2[i] + '/')
            data[invmol].give_cell(cell)
            invnames = cg.read_invout_database(pathlist2[i] + '/')
            for p in keylist:
                data[invmol].add_atom(name=p, frac=pos[p])
                data[invmol].atoms[-1].molecule = data[invmol]
                data[invmol].atoms[-1].invname = invnames[p]
                data[invmol].inv = data[invmol]
                data[invmol].freq = []
                for freq in alldata1[invmol]:
                    if len(freq) > 3:
                        data[invmol].freq.append([freq[0], freq[1]])
                        num = len(data[invmol].atoms) - 1
                        data[invmol].atoms[-1].add_disps(freq[0],
                                                         freq[4 + num * 3:7 + num * 3])
        except:
            errorlog.write('\n!!!WARNING!!! Could not initialize ' + \
                           'classes.molecule instance for ' + invmol)
    #===========================================================================
    # count=0
    #===========================================================================
    print 'Starting calculations...'
    data.update(dabamode=True, errorlog=errorlog)


# ===============================================================================
# def micro_daba_generator(data,frequency_cutoff):
#     """
#     Generates a small database file containing the information of
#     a single molecule.
#     """
#     errorlog=open('error.log','w')
#     datalist=[]
#     datalist.append(read_frequency_block('g.out',errorlog))
#     alldata,warninglist=extract_single_freqencies_from_list(datalist,\
#                                                      ['xylitol'],delnegfreq=True)
#     data.add_molecule('xylitol',daba=True)
#     cell,pos,keylist=cg.read_coordinates('./')
#     data['xylitol'].give_cell(cell)
#     invnames=cg.read_invout_database('./')
#     invmol='xylitol'
#     for p in keylist:
#         data[invmol].add_atom(name=p,frac=pos[p])
#         data[invmol].atoms[-1].molecule=data[invmol]
#         data[invmol].atoms[-1].invname=invnames[p]
#         data[invmol].inv=data[invmol]
#         data[invmol].freq=[]
#         for freq in alldata[invmol]:
#             if  len(freq)>3:
#                 data[invmol].freq.append([freq[0],freq[1]])
#
#                 num=len(data[invmol].atoms)-1
#                 data[invmol].atoms[-1].add_disps(freq[0],\
#                              freq[4+num*3:7+num*3])
#     data.update(dabamode=True,errorlog=errorlog)
#===============================================================================




def read_frequency_block(filename, errorlog):
    """
    Reads the atomic positions and the freqency data from a gaussian log filename (filename.log).
    Needs the log filename name as an argument.
    Returns a list with the atomic positions as its first element and one of the frequency
    tables as each of the following elements. The second return value is the number of atoms
    of the molecule.
    """
    blocklist = []
    block = []
    read_switch = False
    coord_switch = 0
    #===========================================================================
    # filename=filename.replace('home','user')
    #===========================================================================
    try:
        #print filename
        filepointer = open(filename)
        #print 'a'
    except:
        errorlog.write('\n!!!WARNING!!! File not found: ' + filename)
        return
    for line in filepointer.readlines():
        if 'Input orientation:' in line:
            block = []
            block.append(line)
            coord_switch = 1
        elif coord_switch == 1:
            if not 'Symmetry' in line:
                block.append(line)
                if '----------------' in line:
                    try:
                        splitted = block[-2].split(' ')
                        _ = splitted[3]

                    except:
                        pass
            else:
                coord_switch = 2

        elif 'Harmonic frequencies (cm**-1)' in line and read_switch == True:
            blocklist.append(block)
            #blocklist[1]=del_head(blocklist[1])
            return blocklist  #,int(atomnumbers)
        elif ' Harmonic frequencies' in line and read_switch == False:
            blocklist.append(block)
            block = []
            block.append(line)
            read_switch = True
            lineslen = len(block)
        elif read_switch:

            if len(block) == 0:
                block.append(line)
            elif len(line) == len(block[-1]) or len(block) - lineslen <= 11:
                block.append(line)
            elif not 'Harmonic frequencies' in line:
                blocklist.append(block)

                block = []
                block.append(line)
    filepointer.close()

    blocklist.append(block)
    #blocklist[1]=del_head(blocklist[1])
    return blocklist


def read_multiple_files(filelist, comlist, dabamode=False, errorlog=None):
    """
    Reads multiple files from a list of files and returns the output from 'read_frequency_clock'
    for every file as a list.
    """
    #===========================================================================
    # totalatoms=0
    #===========================================================================
    datalist = []
    ##    print 'Reading database files...'
    count = 0
    for data in comlist:
        count += 1
        if count % 50 == 0: print '...' + str(count) + ' files read...'
        if dabamode:
            name = data.split('/')[-4]
            data = data[:-11] + name + '.log'
        else:
            data = data[:-3] + 'log'
        content = read_frequency_block(data, errorlog)
        datalist.append(content)
    return datalist


def extract_single_freqencies_from_list(datalist, filelist, cutoff=-1):
    """
    Converts the ASCII data in datalist to lists of floats and stores the data
    in a dictionary where every dataset is keyed to its filename.
    Every key holds a list of frequencies (lowest first).
    Every list of frequencies holds a list of floats. The first 4 floats are the
    Frequency, the Reduced Masses, the Force constants and the IR Intensities.
    Needs the datalist and the filenamelist returned by read_multiple_files as arguments.

    If True is given as a third argument, the function will delete all frequency lists
    of frequencies <=0.
    """
    alldata = {i: [] for i in filelist}
    print alldata
    #===========================================================================
    # counter=0
    #===========================================================================
    warninglist = []
    dabacounter = 0
    for j in xrange(len(datalist)):
        dabacounter += 1
        if dabacounter % 400 == 0: print '...'
        freqcounter = 0
        try:
            for block in datalist[j][1:]:

                for i in xrange(5):
                    alldata[filelist[j]].append([])
                freqheader = (False, False)
                for line in block:
                    try:
                        freqheader = [float(i) for i in line.split(' ') if '.' in i]
                    except:
                        pass
                    if len(freqheader) > 0:
                        for element in freqheader:
                            alldata[filelist[j]][freqcounter].append(element)
                            freqcounter += 1
                        freqcounter -= len(freqheader)
                freqcounter += 5
                for i in xrange(4):
                    if len(alldata[filelist[j]][-1]) == 0:
                        del alldata[filelist[j]][-1]
            if cutoff > 0:
                for freqlist in alldata[filelist[j]]:
                    if freqlist[0] <= cutoff:
                        #alldata[filelist[j]].remove(freqlist)
                        freqlist[0] = 9999999
        except:
            warninglist.append(j)
            pass
    return alldata, warninglist


def extract_single_freqency(data, compound_name, cutoff=0):
    """
    Converts the ASCII data in datalist to lists of floats and stores the data
    in a dictionary where every dataset is keyed to its filename.
    Every key holds a list of frequencies (lowest first).
    Every list of frequencies holds a list of floats. The first 4 floats are the
    Frequency, the Reduced Masses, the Force constants and the IR Intensities.
    Needs the datalist and the filenamelist returned by read_multiple_files as arguments.

    The optional 'cutoff' argument defines the minimum value for frequencies.
    Frequencies below 'cutoff' are set to 9999999.
    'cutoff' defaults to 0.
    """

    frequency_data = []

    freqcounter = 0

    for block in data[1:]:

        for i in xrange(5):
            frequency_data.append([])
        freqheader = (False, False)
        for line in block:
            if not 'Percent' in line:
                try:
                    freqheader = [float(i) for i in line.split(' ') if '.' in i]
                except:
                    pass
                if len(freqheader) > 0:
                    for element in freqheader:
                        frequency_data[freqcounter].append(element)
                        freqcounter += 1
                    freqcounter -= len(freqheader)
        freqcounter += 5
        for i in xrange(4):
            if len(frequency_data[-1]) == 0:
                del frequency_data[-1]
    if cutoff > 0:
        for freqlist in frequency_data:
            if freqlist[0] <= cutoff:
                #frequency_data.remove(freqlist)
                freqlist[0] = 9999999
    return frequency_data


def generate_database(data, frequency_cutoff, clean=True, temperatures=None,
                      path=None, apd_printer=None, root=None, frequency_scale=1,
                      newh=False):
    import lauescript.core.apd_printer as pr
    #===========================================================================
    # from config import DatabasePath
    #===========================================================================
    global printer
    if not apd_printer:

        printer = pr.apd_printer(5, __name__)
    else:
        printer = apd_printer
    errorlog = open('error.log', 'w')
    if not root:
        root = '/Euros/NEUE_Datenbank/Modellverbindungen'
    #===========================================================================
    # root='/home/jens/generator_test'
    #===========================================================================
    log_mask = 'D95++3df3pd'
    log_mask = 'TZVP'
    xd_mask = 'xd_k'
    xd_mask2 = 'tonto2'
    log = None
    res = None
    mas = None
    fchk = None
    #===========================================================================
    # printer.headline('             APD-Toolkit Database Generator           ')
    #===========================================================================
    if not clean:
        printer('  Loading saved database state from database.pkl...')
        import cPickle

        if path:

            picklepointer = open(path + '/database.pkl', 'r')
        else:
            picklepointer = open('database.pkl', 'r')
        data = cPickle.load(picklepointer)
        data.save = False
        data.set_temperature(temperatures)
        data.update(errorlog, printer, path=path)
        printer.bottomline('             Database generation completed            ')
        return
    printer('  Starting database generation...')
    printer('  Reading files from:\n  {}:\n'.format(root))
    #===========================================================================
    # progress=['|>       |',
    #           '|>>      |',
    #           '|>>>     |',
    #           '|>>>>    |',
    #           '|>>>>>   |',
    #           '|>>>>>>  |',
    #           '|>>>>>>> |',
    #           '|>>>>>>>>|']
    #===========================================================================
    progress = ['[C o o o o o o o o o o o o o o o o o o o o o o o o o o o o ]',
                '[ co o o o o o o o o o o o o o o o o o o o o o o o o o o o ]',
                '[  C o o o o o o o o o o o o o o o o o o o o o o o o o o o ]',
                '[   co o o o o o o o o o o o o o o o o o o o o o o o o o o ]',
                '[    C o o o o o o o o o o o o o o o o o o o o o o o o o o ]',
                '[     co o o o o o o o o o o o o o o o o o o o o o o o o o ]',
                '[      C o o o o o o o o o o o o o o o o o o o o o o o o o ]',
                '[       co o o o o o o o o o o o o o o o o o o o o o o o o ]',
                '[        C o o o o o o o o o o o o o o o o o o o o o o o o ]',
                '[         co o o o o o o o o o o o o o o o o o o o o o o o ]',
                '[          C o o o o o o o o o o o o o o o o o o o o o o o ]',
                '[           co o o o o o o o o o o o o o o o o o o o o o o ]',
                '[            C o o o o o o o o o o o o o o o o o o o o o o ]',
                '[             co o o o o o o o o o o o o o o o o o o o o o ]',
                '[              C o o o o o o o o o o o o o o o o o o o o o ]',
                '[               co o o o o o o o o o o o o o o o o o o o o ]',
                '[                C o o o o o o o o o o o o o o o o o o o o ]',
                '[                 co o o o o o o o o o o o o o o o o o o o ]',
                '[                  C o o o o o o o o o o o o o o o o o o o ]',
                '[                   co o o o o o o o o o o o o o o o o o o ]',
                '[                    C o o o o o o o o o o o o o o o o o o ]',
                '[                     co o o o o o o o o o o o o o o o o o ]',
                '[                      C o o o o o o o o o o o o o o o o o ]',
                '[                       co o o o o o o o o o o o o o o o o ]',
                '[                        C o o o o o o o o o o o o o o o o ]',
                '[                         co o o o o o o o o o o o o o o o ]',
                '[                          C o o o o o o o o o o o o o o o ]',
                '[                           co o o o o o o o o o o o o o o ]',
                '[                            C o o o o o o o o o o o o o o ]',
                '[                             co o o o o o o o o o o o o o ]',
                '[                              C o o o o o o o o o o o o o ]',
                '[                               co o o o o o o o o o o o o ]',
                '[                                C o o o o o o o o o o o o ]',
                '[                                 co o o o o o o o o o o o ]',
                '[                                  C o o o o o o o o o o o ]',
                '[                                   co o o o o o o o o o o ]',
                '[                                    C o o o o o o o o o o ]',
                '[                                     co o o o o o o o o o ]',
                '[                                      C o o o o o o o o o ]',
                '[                                       co o o o o o o o o ]',
                '[                                        C o o o o o o o o ]',
                '[                                         co o o o o o o o ]',
                '[                                          C o o o o o o o ]',
                '[                                           co o o o o o o ]',
                '[                                            C o o o o o o ]',
                '[                                             co o o o o o ]',
                '[                                              C o o o o o ]',
                '[                                               co o o o o ]',
                '[                                                C o o o o ]',
                '[                                                 co o o o ]',
                '[                                                  C o o o ]',
                '[                                                   co o o ]',
                '[                                                    C o o ]',
                '[                                                     co o ]',
                '[                                                      C o ]',
                '[                                                       co ]',
                '[                                                        C ]',
                '[                                                         c]',
    ]
    progress_counter = 0

    info_counter = 0
    dabaerror_log = open('DABAERROR.log', 'w')
    for (path, _, files) in walk(root):


        #=======================================================================
        # if info_counter==100:
        #     break
        #=======================================================================

        info_counter += 1
        if info_counter % 8 == 0:
            printer.noreturn('  ' + progress[progress_counter % len(progress)])
            progress_counter += 1

        if path.endswith(log_mask):
            #===================================================================
            # If the log flag is still True, there was a parsing problem and the other
            # flags need to be reset.
            #===================================================================
            if log:
                res, mas, fchk = None, None, None
            logfiles = []
            for filename in files:
                if filename.endswith('.log'):
                    logfiles.append(filename)

            #===================================================================
            # If more than one log file is available, the newest one
            # is selected.
            #===================================================================
            if len(logfiles) > 0:
                newest_logfile = max([f for f in listdir(path) if f.endswith('.log')])

                datalist = read_frequency_block(path + '/' + newest_logfile, errorlog)
                log = True
        elif path.endswith(xd_mask2) and log:
            for filename in files:
                if 'Test.FChk' == filename:
                    try:
                        properties = cg.get_compound_properties(path + '/' + filename)
                        fchk = True
                    except IOError:
                        fchk = False

        #=======================================================================
        # Reading the xd files associated with the log file.
        # If the log flag is None, their was a parsing error and the xd files
        # are skipped.
        #=======================================================================
        elif path.endswith(xd_mask) and log and xd_mask2 in path:
            for filename in files:
                if 'xd.res' == filename:
                    positions_dict, atom_names_list = cg.read_xd_parameter_file(path + '/' + filename, True)
                    res = True
                if 'xd.mas' == filename:
                    compound_name, cell = cg.read_xd_master_file(path + '/' + filename, dabaerror_log)
                    mas = True

        if res and mas and log and fchk:
            try:
                frequency_data = extract_single_freqency(datalist, compound_name, frequency_cutoff)
            except:
                errorlog.write('\nError: Failed to parse frequency information for {}'.format(path))
            add_molecule(data,
                         atom_names_list,
                         positions_dict,
                         compound_name,
                         cell,
                         frequency_data,
                         properties,
                         path,
                         frequency_scale,
                         newh)
            res, mas, log, fchk = None, None, None, None

    printer('  [----------------------All Files Read----------------------]')
    data.update(errorlog, printer)
    import lauescript.cryst.molgraph as mg
    graphs = []
    invdict = {}
    printer('  [----------------Generating Molgraph Library---------------]')
    for molecule in data.values():
        for graph, name in mg.Graph.molecule2Graphs(molecule):
            graphs.append(graph)
            invdict[str(graph)] = molecule[name].invarioms.keys()[0]
    mg.GraphStorage.writeDatabase(graphs, 'graphs2inv.dat', invdict)




    #data.release()
    #===========================================================================
    # import cPickle
    # f=open('APD_DABA.pkl','wb')
    # cPickle.dump(data,f)
    # f.close()
    #===========================================================================

    #===========================================================================
    # printer.bottomline('             Database generation completed            ')
    #===========================================================================


def add_molecule(data,
                 atom_names_list,
                 positions_dict,
                 compound_name,
                 cell,
                 frequency_data,
                 properties,
                 path,
                 frequency_scale,
                 newh):
    data.give_daba_molecule(compound_name, cell, properties)
    positions_list = []
    for atom_name in atom_names_list:
        positions_list.append(positions_dict[atom_name])
    #===========================================================================
    # invariom_dicts=[]
    # invariom_orientations=[]
    #===========================================================================
    first = True
    for names, orientations in get_invariom_names(atom_names_list,
                                                  frac=positions_list,
                                                  cell=cell,
                                                  dictionary=True,
                                                  orientations=True,
                                                  #==========================================
                                                  # corrections_directory=path+'/',
                                                  #==========================================
                                                  dynamic=True,
                                                  verbose=False,
                                                  output=printer,
                                                  newH=newh):
        #if 'purin-6-amine' in compound_name:
        #    print names['C(5)']
        #=======================================================================
        # invariom_dicts.append(names)
        # invariom_orientations.append(orientations)
        #=======================================================================


        #===========================================================================
        # invariom_dict=invariom_dict[0]
        #===========================================================================
        for atom_name in atom_names_list:
            if first:

                atom_element = atom_name.partition('(')[0]
                if '-' in atom_element:
                    atom_element = atom_element.replace('-', '')
                if '+' in atom_element:
                    atom_element = atom_element.replace('+', '')
                data[compound_name].give_atom(name=atom_name,
                                              element=atom_element,
                                              frac=positions_dict[atom_name],
                                              molecule=data[compound_name])

                for freq in frequency_data:
                    if len(freq) > 3:
                        if atom_name == atom_names_list[0]:
                            data[compound_name].freq.append([freq[0] * frequency_scale, freq[1]])
                        num = len(data[compound_name].atoms) - 1
                        data[compound_name].atoms[-1].add_disps(freq[0] * frequency_scale,
                                                                freq[4 + num * 3:7 + num * 3])

            data[compound_name][atom_name].add_invariom(names[atom_name],
                                                        orientations[atom_name])
        first = False


def generate_micro_database(data,
                            frequency_cutoff,
                            temperatures=None,
                            path=None,
                            clustersize=17,
                            printer=None,
                            frequency_scale=1.):
    import lauescript.core.apd_printer as pr
    if not printer:
        printer = pr.apd_printer(5, __name__)
    # printer.headline('          APD-Toolkit Micro-Database Generator        ')
    filepointer = open(path)
    switch = False
    matrix_buffer = None
    for line in filepointer.readlines():
        if switch and 'Rotational constants' in line:
            switch = False
        elif switch:
            matrix_buffer.append(line.rstrip('\n'))
        elif 'Coordinates (Angstroms)' in line:
            switch = True
            matrix_buffer = Log_Buffer(clustersize, data, path, frequency_cutoff, printer, frequency_scale)

    matrix_buffer.flush()
    printer.bottomline('             Database generation completed            ')


class Log_Buffer(list):
    exclude = ['Number', 'Type', '-----']

    def __init__(self, clustersize, data, path, frequency_cutoff, printer, frequency_scale):
        self.data = data
        self.frequency_cutoff = frequency_cutoff
        self.path = path
        self.printer = printer
        self.clustersize = clustersize
        self.errorlog = open('error.log', 'w')
        self.frequency_scale = frequency_scale
        super(Log_Buffer, self).__init__()

    def append(self, string):
        if not any(i in string for i in Log_Buffer.exclude):
            super(Log_Buffer, self).append([value for value in string.split(' ') if len(value) > 0])

    def flush(self):
        self.find_pattern()
        self.setup_data()
        self.data.update(self.errorlog, self.printer, parallel=False)

    def find_pattern(self):
        num_atoms = len(self) / self.clustersize
        self.molecule = self[:num_atoms]

    def setup_data(self):
        self.data.give_daba_molecule('micro', properties=[0, 0, 0, 0])
        self.data.set_temperature([100])
        datalist = read_frequency_block(self.path, self.errorlog)
        frequency_data = extract_single_freqency(datalist, 'micro', self.frequency_cutoff)
        positions_list = []
        atom_names_list = []
        for atom_data in self.molecule:
            atom_names_list.append(
                cg.number_proton['{0:{2}>{1}}'.format(atom_data[1], 3, '0')] + '(' + atom_data[0] + ')')
            positions_list.append(np.array([float(i) for i in atom_data[3:]]))
        invariom_dict, orientations = get_invariom_names_simple(atom_names_list,
                                                                cart=positions_list,
                                                                dictionary=True,
                                                                output=self.printer,
                                                                orientations=True,
                                                                newH=True)

        freq_num = len(atom_names_list) * 3 - 2
        for i, atom_name in enumerate(atom_names_list):
            atom_element = cg.number_proton['{0:{2}>{1}}'.format(atom_data[1], 3, '0')]
            self.data['micro'].give_atom(name=atom_name,
                                         element=atom_element,
                                         cart=positions_list[i],
                                         molecule=self.data['micro'])

            self.data['micro'][atom_name].add_invariom(invariom_dict[atom_name],
                                                        orientations[atom_name])



            for j, freq in enumerate(frequency_data[freq_num * -1:]):
                if len(freq) > 3:
                    #===========================================================
                    # print
                    # for f in freq[6:]:
                    #     if f>.1:
                    #         print f
                    #===========================================================
                    if atom_name == atom_names_list[0]:
                        if not freq[0] > 99999:
                            self.data['micro'].freq.append([freq[0] * self.frequency_scale, freq[1]])
                    num = len(self.data['micro'].atoms) - 1
                    if not freq[0] > 99999:
                        self.data['micro'].atoms[-1].add_disps(freq[0] * self.frequency_scale,
                                                               freq[4 + num * 3:7 + num * 3])
