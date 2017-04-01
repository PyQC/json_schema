# A JSON Schema for Quantum Chemistry

The overall goal of this schema is provide programatic access and return for a variety of Quantum Chemistry programs. 

## Input

The overall input *requires* the following fields:
  - `molecule` (dict) - A JSON object that defines a given molecule (see below)
  - `driver` (str) - The requirested funciton to run (`energy`, `gradient`, etc). The following are explicitly defined;
    however, individual programs may define as others as necessary:
    - `energy` - The energy of the requested method.
    - `gradient` - The gradient of the requested method.
    - `hessian` - The Hessian of the requested method.
    - `optimize` - The moleucle specification of the optimized geometry of the requested method.
    - `frequency` - List of frequencies (in hartree) of the requested method.
  - `method` (str) - The requested method and basis seperated by a slash (`SCF/cc-pVDZ`, `B3LYP/sto-3g`, `MP2/def2-SVP`, etc)
    -  Alternatively if a complex basis is supplied a user can provide a key to another options field. For example,
    `SCF/key=mybasis` where `mybasis` is a nother field in the supplied JSON which is likely a list of strings
    `["sto-3g", "cc-pVDZ", ...]`, one for each atom in the molecule specification.
  - `options` (dict) - A dictionary of the requested generic options.
    - Note that this can be "blank": `json_data["options"] = {}`.

This spec also supports unlimited extra fields that a specific program may or may not support.
This is enabled to allow for "passthough" that is any part of the JSON not specified can simply
pass through the specification and provided in the return allowing for extra comments or validation
to be applied ontop of the exisiting value.

## Output

The output specified by this schema.

  - `return_value` (float, dict, list) - The requested return of the given `driver`.
  - `variables` (dict) - A dictionary of all variables created in the computation of the given methodology.
  - `schema` (str) - Link to this schema detailing its usage and convention.
  - `success` (bool) - If the computation successfully completed or not.
  - `error` (str) - If possible, an string explanation of the error raised internally within the program.
  - `provenance` (dict) - The program and version number that this computation was computed under. Fields:
    - `creator` (str) - Program used
    - `routine` (str) - Name of the routine used to compute this object (seperate from driver).
    - `version` (str) - The named version of the program or git hash if development version is used.
  - `raw_output` (str) - The raw product of the computation if requested.

## Example

The following is an example run from Psi4. 

```python
# Helium dimer energy in the STO-3G basis.

>>> json_mol = {}
>>> json_mol["symbols"] = ["He", "He"]
>>> json_mol["geometry"] = [[0, 0, 0], [0, 0, 1]]

>>> json_data = {}
>>> json_data["molecule"] = "He 0 0 0\n--\nHe 0 0 1"
>>> json_data["driver"] = "energy"   
>>> json_data["method"] = "SCF/STO-3G"                       # SCF/cc-pvdz, SCF/key=mybasis
>>> json_data["options"] = {"BASIS": "STO-3G"}        # Generic options

>>> psi4.driver.run_json(json_data)
{
    "raw_output": "Output storing was not requested.",
    "options": {
        "BASIS": "STO-3G"
    },
    "driver": "energy",
    "molecule": {"symbols": ["He", "He"], "geometry": [[0, 0, 0], [0, 0, 1]]}
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
}
```
