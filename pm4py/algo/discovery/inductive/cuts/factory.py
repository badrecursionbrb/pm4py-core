'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from typing import List, Optional, Tuple, TypeVar, Dict, Any

from pm4py.algo.discovery.inductive.cuts.abc import Cut
from pm4py.algo.discovery.inductive.cuts.concurrency import ConcurrencyCutUVCL, ConcurrencyCutDFG
from pm4py.algo.discovery.inductive.cuts.loop import LoopCutUVCL, LoopCutDFG
from pm4py.algo.discovery.inductive.cuts.sequence import StrictSequenceCutUVCL, StrictSequenceCutDFG
from pm4py.algo.discovery.inductive.cuts.xor import ExclusiveChoiceCutUVCL, ExclusiveChoiceCutDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructure, IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree

T = TypeVar('T', bound=IMDataStructure)
S = TypeVar('S', bound=Cut)


class CutFactory:

    @classmethod
    def get_cuts(cls, obj: T, inst: IMInstance, parameters: Optional[Dict[str, Any]] = None) -> List[S]:
        if inst is IMInstance.IM or inst is IMInstance.IMf or IMInstance.IMcustom:
            if isinstance(obj, IMDataStructureUVCL):
                return [ExclusiveChoiceCutUVCL, StrictSequenceCutUVCL, ConcurrencyCutUVCL, LoopCutUVCL]
        if inst is IMInstance.IMd:
            if type(obj) is IMDataStructureDFG:
                return [ExclusiveChoiceCutDFG, StrictSequenceCutDFG, ConcurrencyCutDFG, LoopCutDFG]
        return list()

    @classmethod
    def find_cut(cls, obj: IMDataStructure, inst: IMInstance, parameters: Optional[Dict[str, Any]] = None) -> Optional[Tuple[ProcessTree, List[T]]]:
        for c in CutFactory.get_cuts(obj, inst):
            r = c.apply(obj, parameters)
            if r is not None:
                return r
        return None
