import json
import os

from desicos.logger import *
from ccs import ccs as default_ccs
from allowables import allowables as default_allowables
from laminaprops import laminaprops as default_laminaprops
from ccs import include_in_GUI
from desicos.constants import DESHOME


DBHOME = os.path.join(DESHOME, 'conecylDB')

databases = json.load(open(os.path.join(DBHOME, 'databases.json')))

localDB_path = json.load(open(os.path.join(DBHOME, 'localDB_path.json')))

local_ccs_path = os.path.join(localDB_path, 'ccs.json')
local_laminaprops_path = os.path.join(localDB_path, 'laminaprops.json')
local_allowables_path = os.path.join(localDB_path, 'allowables.json')
which_path = {'ccs': local_ccs_path,
              'laminaprops': local_laminaprops_path,
              'allowables': local_allowables_path}

def myload(path):
    if not os.path.isfile(path):
        try:
            json.dump({}, open(path, 'w'))
        except:
            msg = error('{0} could not be loaded!'.format(path))
            return {}
    return json.load(open(path))

def mydump(obj, path):
    try:
        json.dump(obj, open(path, 'w'))
        return 0
    except:
        msg = error('{0} could not be dumped in {1}!'.format(obj, path))
        return 1

if not os.path.isdir(localDB_path):
    try:
        os.makedirs(localDB_path)
        mydump({}, local_ccs_path)
        mydump(local_laminaprops_path)
        mydump(local_allowables_path)
    except:
        msg = error('localDB not found and not created!')

def fetch(which, local_only=False):
    path = which_path[which]
    local = myload(path)
    if local_only:
        return local
    if which=='ccs':
        return dict(default_ccs.items() + local.items())
    elif which=='laminaprops':
        return dict(default_laminaprops.items() + local.items())
    elif which=='allowables':
        return dict(default_allowables.items() + local.items())
    else:
        raise ValueError('{0} is an invalid option to fetch'.format(which))


def update_imps():
    ccs = fetch('ccs')
    imps = {}
    imps_theta_z = {}
    t_measured = {}
    R_measured = {}
    H_measured = {}
    for cc in ccs.values():
        imp = None
        if 'msi' in cc.keys():
            db = cc['database']
            imp = cc['msi']

            path = os.path.join(DBHOME, 'files', db, imp, imp + '_msi.txt')
            if os.path.isfile(path):
                if not imp in imps.keys():
                    imps[imp] = {}
                imps[imp]['msi'] = path

            path_theta_z = os.path.join(DBHOME, 'files', db, imp,
                                        imp + '_msi_theta_z_imp.txt')
            if os.path.isfile(path_theta_z):
                if not imp in imps_theta_z.keys():
                    imps_theta_z[imp] = {}
                imps_theta_z[imp]['msi'] = path_theta_z

        if 'ti' in cc.keys():
            db = cc['database']
            imp = cc['ti']

            path = os.path.join(DBHOME, 'files', db, imp, imp + '_ti.txt')
            if os.path.isfile(path):
                if not imp in imps.keys():
                    imps[imp] = {}
                imps[imp]['ti'] = path

            path_theta_z = os.path.join(DBHOME, 'files', db, imp,
                                        imp + '_ti_theta_z_thick.txt')
            if os.path.isfile(path_theta_z):
                if not imp in imps_theta_z.keys():
                    imps_theta_z[imp] = {}
                imps_theta_z[imp]['ti'] = path_theta_z

        if imp:
            if 'lamt' in cc.keys():
                t_measured[imp] = cc['lamt']
            else:
                plyts = cc.get('plyts', [cc.get('plyt')])
                stack = cc['stack']
                if len(plyts) <> len(stack):
                    t_measured[imp] = sum([plyts[0] for i in stack])
                else:
                    t_measured[imp] = sum([i for i in plyts])

            if 'r_measured' in cc.keys():
                R_measured[imp] = cc['r_measured']
            else:
                R_measured[imp] = cc['r']

            H_measured[imp] = cc['h']

    return imps, imps_theta_z, t_measured, R_measured, H_measured

def save(which, name, value):
    """Save an entry to the dynamic database.

    Parameters
    ----------
    which : str
        A string that can be: ``ccs``, ``laminaprops``, ``allowables``.
    name : str
        The name of the new entry.
    value : object
        The object that will be stored in the dictionary pointed by ``which``
        under the key given by ``name``.

    """
    path = which_path[which]
    local = myload(path)
    if name in local.keys():
        msg = '{0} {1} already exists in the localDB'.format(which, name)
        msg = error(msg)
        return msg
    else:
        local[name] = value
        fail = mydump(local, path)
        if not fail:
            msg = '{0} {1} included in localDB'.format(which, name)
            msg = log(msg)
        else:
            msg = '{0} {1} could not be included in the localDB'.format(
                  which, name)
            msg = error(msg)
        return msg

def delete(which, name):
    """Delete an entry to the dynamic database.

    Parameters
    ----------
    which : str
        A string that can be: ``ccs``, ``laminaprops``, ``allowables``.
    name : str
        The name of the new entry.

    """
    path = which_path[which]
    local = myload(path)
    if not name in local.keys():
        msg = '{0} {1} does not exist in the localDB'.format(which, name)
        msg = error(msg)
        return msg
    else:
        local.pop(name)
        fail = mydump(local, path)
        if not fail:
            msg = '{0} {1} deleted from the localDB'.format(which, name)
            msg = log(msg)
        else:
            msg = '{0} {1} could not be deleted from the localDB'.format(
                  which, name)
            msg = error(msg)
        return msg

imps, imps_theta_z, t_measured, R_measured, H_measured = update_imps()

#TODO put in a better way
imperfection_amplitudes = {
            'degenhardt_2010_z15':1.6061230827442536,
            'degenhardt_2010_z17':1.3932307190764155,
            'degenhardt_2010_z18':1.0072464212485135,
            'degenhardt_2010_z20':0.76342116164039231,
            'degenhardt_2010_z21':1.7115336984360101,
            'degenhardt_2010_z22':0.63145023895181396,
            'degenhardt_2010_z23':0.70746632120089115,
            'degenhardt_2010_z24':0.80310340376595235,
            'degenhardt_2010_z25':0.63168845856972267,
            'degenhardt_2010_z26':0.68114518609623675,
            'zimmermann_1992_z33':1.0575795310555065 }
