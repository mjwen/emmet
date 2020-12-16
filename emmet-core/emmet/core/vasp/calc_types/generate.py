""" Module to define various calculation types as Enums for VASP """
import datetime
from itertools import groupby, product
from pathlib import Path
from typing import Dict, Iterator, List

import bson
import numpy as np
from monty.json import MSONable
from monty.serialization import loadfn
from pydantic import BaseModel
from pymatgen.analysis.structure_matcher import ElementComparator, StructureMatcher
from pymatgen.core.structure import Structure
from typing_extensions import Literal

from emmet.core import SETTINGS
from emmet.core.utils import ValueEnum

_RUN_TYPE_DATA = loadfn(str(Path(__file__).parent.joinpath("run_types.yaml").resolve()))
_TASK_TYPES = [
    "NSCF Line",
    "NSCF Uniform",
    "Dielectric",
    "DFPT",
    "DFPT Dielectric",
    "NMR Nuclear Shielding",
    "NMR Electric Field Gradient",
    "Static",
    "Structure Optimization",
    "Deformation",
]

_RUN_TYPES = (
    [
        rt
        for functional_class in _RUN_TYPE_DATA
        for rt in _RUN_TYPE_DATA[functional_class]
    ]
    + [
        f"{rt}+U"
        for functional_class in _RUN_TYPE_DATA
        for rt in _RUN_TYPE_DATA[functional_class]
    ]
    + ["LDA", "LDA+U"]
)


def get_enum_source(enum_name, doc, items):
    header = f"""
class {enum_name}(ValueEnum):
    \"\"\" {doc} \"\"\"\n
"""
    items = [f'    {const} = "{val}"' for const, val in items.items()]

    return header + "\n".join(items)


run_type_enum = get_enum_source(
    "RunType",
    "VASP calculation run types",
    dict(
        {
            "_".join(rt.split()).replace("+", "_").replace("-", "_"): rt
            for rt in _RUN_TYPES
        }
    ),
)
task_type_enum = get_enum_source(
    "TaskType",
    "VASP calculation task types",
    {"_".join(tt.split()): tt for tt in _TASK_TYPES},
)
calc_type_enum = get_enum_source(
    "CalcType",
    "VASP calculation types",
    {
        f"{'_'.join(rt.split()).replace('+','_').replace('-','_')}_{'_'.join(tt.split())}": f"{rt} {tt}"
        for rt, tt in product(_RUN_TYPES, _TASK_TYPES)
    },
)


with open(Path(__file__).parent / "enums.py", "w") as f:
    f.write(
        """\"\"\"
Autogenerated Enums for VASP RunType, TaskType, and CalcType
Do not edit this by hand. Edit generate.py or run_types.yaml instead
\"\"\"
from emmet.core.utils import ValueEnum

"""
    )
    f.write(run_type_enum)
    f.write("\n\n")
    f.write(task_type_enum)
    f.write("\n\n")
    f.write(calc_type_enum)
    f.write("\n")