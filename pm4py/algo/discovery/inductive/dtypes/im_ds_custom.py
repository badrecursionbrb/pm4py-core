from abc import ABC
from typing import TypeVar, Generic, Optional

from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG
from pm4py.objects.dfg.obj import DFG
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG

T = TypeVar('T')


class IMDataStructureCustom(IMDataStructureUVCL):
    """
    The IMDataStructureCustom is a class 
    """

    def __init__(self, obj: UVCL, dfg: DFG = None):
        super().__init__(obj, dfg)
        self.tree_nodes_ls = []
        



