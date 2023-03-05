'''

'''
from typing import TypeVar, Generic, Dict, Any, Optional, List

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureLog, IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds_custom import IMDataStructureCustom
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL
from pm4py.algo.discovery.inductive.variants.abc import InductiveMinerFramework
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.process_tree.obj import ProcessTree

from pm4py.algo.discovery.inductive.visualization.process_tree_node import ProcessTreeNode
from pm4py.algo.discovery.inductive.visualization.constants import OperatorType

T = TypeVar('T', bound=IMDataStructureCustom)


class IM_Custom(Generic[T], InductiveMinerFramework[T]):

    def instance(self) -> IMInstance:
        return IMInstance.IMcustom
    
    def apply(self, obj: T, parameters: Optional[Dict[str, Any]] = None, parent=None) -> ProcessTree:
        """_summary_: This method overwrites the IM Framework superclass!

        Args:
            obj (T): _description_
            parameters (Optional[Dict[str, Any]], optional): _description_. Defaults to None.

        Returns:
            ProcessTree: _description_
        """    
        tree = self.apply_base_cases(obj, parameters)
        if not tree is None:
            # TODO check with __repr__
            tree.pt_node = ProcessTreeNode(value=tree.label, dfg=parameters.get("old_dfg"), parent=parent, children_obj_ls=[obj],
                                        is_base_case=True, operation_type=OperatorType.BC)
        if tree is None:
            cut = self.find_cut(obj, parameters)
            if cut is not None:
                tree = self._recurse(cut[0], cut[1], parameters=parameters, parent=parent, operation_type=OperatorType.CUT)
        if tree is None:
            ft = self.fall_through(obj, parameters)
            tree = self._recurse(ft[0], ft[1], parameters=parameters, parent=parent, operation_type=OperatorType.FT)
        return tree

    def _recurse(self, tree: ProcessTree, objs: List[T], parent, parameters: Optional[Dict[str, Any]] = None, operation_type:str=None):
        tree.pt_node = ProcessTreeNode(value=tree.operator.value, dfg=parameters.get("old_dfg"), parent=parent, 
                                    children_obj_ls=objs, operation_type=operation_type)
        children = []
        for obj in objs:
            children.append(self.apply(obj, parameters=parameters, parent=tree.pt_node))
        for c in children:
            c.parent = tree
        tree.children.extend(children)
        return tree

class IMUVCL_Custom(IM_Custom[IMDataStructureCustom]):
    def apply(self, obj: IMDataStructureCustom, parameters: Optional[Dict[str, Any]] = None, parent=None) -> ProcessTree:
        empty_traces = EmptyTracesUVCL.apply(obj, parameters)
        
        # saving the current dfg in the parameters to save it later in recurse or apply to the 
        # pt_node in the tree 
        if obj.dfg != None:
            parameters["old_dfg"] = obj.dfg
        else: 
            parameters["old_dfg"] = None
        
        if empty_traces is not None:
            # TODO check those two cases 
            return self._recurse(empty_traces[0], empty_traces[1], parameters=parameters, 
                                parent=parent, operation_type=OperatorType.CUT)
        return super().apply(obj, parameters, parent=parent)
