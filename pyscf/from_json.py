#import importlib
#import collections
import StringIO
import numpy
import json
import pyscf
from pyscf import gto
from pyscf import dft

def json2pyscf(jstr):
    jdic = json2pydict(jstr)

    mol = load_jdict_mol(jdic)
    driver = jdic['driver']

    rawinp = to_pyscf_rawinput(jdic, mol)
    exec rawinp

    output = ('#INFO: **** input script ****\n' + rawinp +
              '#INFO: ******************** input script end ********************\n'
              + mol.stdout.getvalue())
    jdic.update(result_dic)
    update_result(jdic, rawinp, output)
    return json.dumps(jdic)
run_json = json2pyscf


def json2pydict(jstr):
    return json.loads(jstr)

def load_jdict_mol(jdic):
    jdicmol = jdic['molecule']
    #rawinp = ['mol = pyscf.gto.Mole()',
    #          'mol.atom = %s' % [("%s"%z,x) for z, x in zip(jdicmol['symbols'],
    #                                                        jdicmol['geometry'])],
    #          'mol.basis = "%s"' % str(jdic['options']['BASIS']),
    #          'mol.charge = %s' % int(jdic.get('charge', 0)),
    #          'mol.spin = %s' % int(jdic.get('multiplicity', 1) - 1),
    #          'mol.verbose = 4',
    #          'mol.stdout = StringIO.StringIO()',
    #          'mol.build(False, False)']
    #return '\n'.join(rawinp)

    mol = gto.Mole()
    mol.atom = [(z,x) for z, x in zip(jdicmol['symbols'], jdicmol['geometry'])]
    mol.basis = str(jdic['options']['BASIS'])
    mol.charge = int(jdic.get('charge', 0))
    mol.spin = int(jdic.get('multiplicity', 1) - 1)
    mol.build(False, False)
    return mol

def to_pyscf_rawinput(jdic, mol):
    driver = jdic['driver'].lower()
    method = jdic['method'].lower().split('/')[0]
    rawinp = ['import pyscf.gto',
              'import pyscf.scf',
              'import pyscf.dft']

    if method.startswith('mp'):
        rawinp.append('import pyscf.mp')
    if method.startswith('cc'):
        rawinp.append('import pyscf.cc')
    if method.startswith('ci'):
        rawinp.append('import pyscf.ci')

    rawinp.extend(['result_dic = {}',
                   'pyscf.gto.loads(\"\"\"%s\"\"\")' % mol.dumps(),
                   'mol.verbose = 4',
                   'mol.stdout = StringIO.StringIO()',
                  ])

    if method.startswith(('lda', 'lsda')):
        rawinp.append('meth = mol.apply(pyscf.scf.RKS).set(xc="lda,vwn").run() \\')
    elif method.upper() in dft.libxc.XC_CODES:
        rawinp.append('meth = mol.apply(pyscf.scf.RKS).set(xc="%s").run() \\' % method)
    else:
        rawinp.append('meth = mol.apply(pyscf.scf.RHF).run() \\')
        if method.startswith('scf'):
            rawinp.append('')
        elif method.startswith('mp2'):
            rawinp.append('.apply(pyscf.mp.MP2).run()')
        elif method.startswith('ccsd'):
            rawinp.append('.apply(pyscf.cc.CCSD).run()')
        elif method.startswith('cisd'):
            rawinp.append('.apply(pyscf.ci.CISD).run()')
        else:
            raise RuntimeError('Unknown method %s' % method)

    if driver == 'energy':
        rawinp.append('result_dic["return_value"] = meth.e_tot')
    elif driver == 'gradient':
        rawinp.append('meth = meth.get_grad().run()')
        rawinp.append('result_dic["return_value"] = meth.de')
    elif driver == 'hessian':
        rawinp.append('meth = meth.get_hessian().run()')
        rawinp.append('result_dic["return_value"] = meth.de')

    return '\n'.join(rawinp)

def update_result(jdic, rawinp, output, *args, **kwargs):
    jdic['variables'] = {}
    jdic['schema'] = ''
    jdic['success'] = True
    jdic['error'] = ''
    jdic['raw_output'] = output
    pro = {}
    pro['creator'] = 'pyscf'
    pro['routine'] = rawinp
    pro['version'] = pyscf.__version__
    jdic['provenance'] = pro


if __name__ == '__main__':
    jstr = '''{
    "raw_output": "Output storing was not requested.",
    "options": {
        "BASIS": "STO-3G"
    },
    "driver": "energy",
    "molecule": {"symbols": ["He", "He"], "geometry": [[0, 0, 0], [0, 0, 1]]},
    "method": "SCF",
    "variables": {
        "SCF N ITERS": 2.0,
        "SCF DIPOLE Y": 0.0,
        "CURRENT DIPOLE Y": 0.0,
        "HF TOTAL ENERGY": -5.433191881443323,
        "SCF TOTAL ENERGY": -5.433191881443323,
        "TWO-ELECTRON ENERGY": 4.124089347186247,
        "SCF ITERATION ENERGY": -5.433191881443323,
        "CURRENT DIPOLE X": 0.0,
        "CURRENT DIPOLE Z": 0.0,
        "CURRENT REFERENCE ENERGY": -5.433191881443323,
        "CURRENT ENERGY": 0.1839360538612116,
        "SCF DIPOLE Z": 0.0,
        "NUCLEAR REPULSION ENERGY": 2.11670883436,
        "SCF DIPOLE X": 0.0,
        "ONE-ELECTRON ENERGY": -11.67399006298957
    },
    "return_value": -5.433191881443323,
    "error": "",
    "success": true,
    "provenance": {
        "creator": "Psi4",
        "routine": "psi4.run_json",
        "version": "1.1a1"
    },
    "kwargs": {
        "bsse_type": "cp"
    }
}'''
    jdic = json2pydict(jstr)
    mol = load_jdict_mol(jdic)
    print to_pyscf_rawinput(jdic, mol)

    jstr = json2pyscf(jstr)
    print json2pydict(jstr)["return_value"]

