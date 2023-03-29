'''

'''
from typing import List, TypeVar, Generic, Dict, Any, Optional

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureLog
from pm4py.algo.discovery.inductive.dtypes.im_ds_custom import IMDataStructureCustom
from pm4py.algo.discovery.inductive.fall_through.empty_traces import EmptyTracesUVCL
from pm4py.algo.discovery.inductive.variants.abc import InductiveMinerFramework
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.algo.discovery.inductive.visualization.process_tree_node import ProcessTreeNode
from pm4py.algo.discovery.inductive.visualization.constants import OperatorType
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.dfg.obj import DFG
from copy import copy
from enum import Enum
from pm4py.util import exec_utils

from pm4py.algo.discovery.inductive.variants.instances import IMInstance


T = TypeVar('T', bound=IMDataStructureLog)


class IMFParameters(Enum):
    NOISE_THRESHOLD = "noise_threshold"


class IMF_Custom(Generic[T], InductiveMinerFramework[T]):

    def instance(self) -> IMInstance:
        return IMInstance.IMf


class IMFUVCL_Custom(IMF_Custom[IMDataStructureCustom]):
    """ Custom implementation of the UVCL version of the  Inductive Miner infrequent 
        At each step the corresponding ProcessTreeNode object storing all data for the step, is 
        added to the node list
     

    Args:
        IMF_Custom (_type_): Gets the data structure as an argument
    """
    def apply(self, obj: IMDataStructureCustom, parameters: Optional[Dict[str, Any]] = None, 
            second_iteration: bool = False, parent: ProcessTreeNode=None) -> ProcessTree:
        noise_threshold = exec_utils.get_param_value(IMFParameters.NOISE_THRESHOLD, parameters, 0.0)
        """  Application of the IM Framework algorithm, extended by saving the step data as 
            ProcessTreeNode to the ProcessTreeNode class list. 

        Args:
            obj (IMDataStructureCustom): gets an IMDataStructureCustom
            parameters (Optional[Dict[str, Any]], optional): Dictionary of parameters.
                    Is also used to store the dfg in it. Defaults to None.
            parent (ProcessTreeNode, optional): The parent ProcessTreeNode to connect the current
                                node with the previous steps / rest of the tree. Defaults to None.

        Returns:
            ProcessTree: Returns a ProcessTree after running the IM algorithm
        """
        empty_traces = EmptyTracesUVCL.apply(obj, parameters)
        
        parameters = self._parameter_assign(obj=obj, parameters=parameters)
        
        if empty_traces is not None:
            number_original_traces = sum(y for y in obj.data_structure.values())
            number_filtered_traces = sum(y for y in empty_traces[1][1].data_structure.values())

            if number_original_traces - number_filtered_traces > noise_threshold * number_original_traces:
                return self._recurse(empty_traces[0], empty_traces[1], parameters=parameters, parent=parent, operation_type=OperatorType.CUT)
            else:
                # TODO check this case 
                obj = empty_traces[1][1]
                parameters = self._parameter_assign(obj=obj, parameters=parameters)

        tree = self.apply_base_cases(obj, parameters)
        if tree is None:
            cut = self.find_cut(obj, parameters)
            if cut is not None:
                tree = self._recurse(cut[0], cut[1], parameters=parameters, parent=parent, operation_type=OperatorType.CUT)
            if tree is None:
                if not second_iteration:
                    filtered_ds = self.__filter_dfg_noise(obj, noise_threshold)
                    # used obj.dfg instead of filtered_ds.dfg before to see what happens before vs after filtering
                    obj.pt_node = ProcessTreeNode(value="PREFILTER", dfg=obj.dfg, parent=parent, 
                                    children_obj_ls=[filtered_ds], node_id=self.node_id_counter,
                                    operation_type=OperatorType.FILTER, log=parameters.get("log"))
                    self.append_node_and_raise(pt_node=obj.pt_node)
                    # Filtering afterwards, to observe the difference in the dfg in the front-end
                    # TODO the data_structure does not reflect (signal) the filtering step, display of traces in table not meaningful then
                    filtered_ds.pt_node = ProcessTreeNode(value="FILTER", dfg=filtered_ds.dfg, parent=obj.pt_node, 
                                    children_obj_ls=[obj], node_id=self.node_id_counter,
                                    operation_type=OperatorType.FILTER, log=filtered_ds.data_structure)
                    self.append_node_and_raise(pt_node=filtered_ds.pt_node)
                    
                    tree = self.apply(filtered_ds, parameters=parameters, second_iteration=True, parent=filtered_ds.pt_node)
                    if tree is None:
                        # this only enters if tree is None that is the case when second iteraiton also yields nothing (line above)
                        ft = self.fall_through(obj, parameters)
                        tree = self._recurse(ft[0], ft[1], parameters=parameters, parent=parent, operation_type=OperatorType.FT)
        else:
            # TODO check with __repr__
            tree.pt_node = ProcessTreeNode(value=tree.label, dfg=parameters.get("old_dfg"), parent=parent, children_obj_ls=[obj],
                                        is_base_case=True, node_id=self.node_id_counter,
                                        operation_type=OperatorType.BC, log=parameters.get("log"))
            self.append_node_and_raise(pt_node=tree.pt_node)
            
        return tree
    
    def _recurse(self, tree: ProcessTree, objs: List[T], parent: ProcessTreeNode,
                    parameters: Optional[Dict[str, Any]] = None, operation_type:str=None):
        tree.pt_node = ProcessTreeNode(value=tree.operator.value, dfg=parameters.get("old_dfg"), parent=parent, 
                                    children_obj_ls=objs, node_id=self.node_id_counter, 
                                    operation_type=operation_type, log=parameters.get("log"))
        self.append_node_and_raise(pt_node=tree.pt_node)
        
        children = []
        for obj in objs:
            children.append(self.apply(obj, parameters=parameters, parent=tree.pt_node))
        for c in children:
            c.parent = tree
        tree.children.extend(children)
        return tree

    def __filter_dfg_noise(self, obj, noise_threshold):
        start_activities = copy(obj.dfg.start_activities)
        end_activities = copy(obj.dfg.end_activities)
        dfg = copy(obj.dfg.graph)
        outgoing_max_occ = {}
        for x, y in dfg.items():
            act = x[0]
            if act not in outgoing_max_occ:
                outgoing_max_occ[act] = y
            else:
                outgoing_max_occ[act] = max(y, outgoing_max_occ[act])
            if act in end_activities:
                outgoing_max_occ[act] = max(outgoing_max_occ[act], end_activities[act])
        dfg_list = sorted([(x, y) for x, y in dfg.items()], key=lambda x: (x[1], x[0]), reverse=True)
        dfg_list = [x for x in dfg_list if x[1] > noise_threshold * outgoing_max_occ[x[0][0]]]
        dfg_list = [x[0] for x in dfg_list]
        # filter the elements in the DFG
        graph = {x: y for x, y in dfg.items() if x in dfg_list}

        dfg = DFG()
        for sa in start_activities:
            dfg.start_activities[sa] = start_activities[sa]
        for ea in end_activities:
            dfg.end_activities[ea] = end_activities[ea]
        for act in graph:
            dfg.graph[act] = graph[act]

        return IMDataStructureCustom(obj.data_structure, dfg)
