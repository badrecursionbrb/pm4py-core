
from collections import Counter
from typing import TypeVar, List, Generic
from collections.abc import Iterable

from pm4py.objects.dfg.obj import DFG, DirectlyFollowsGraph
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL

from pm4py.algo.discovery.inductive.visualization.constants import OperatorType, signs_ls_im_custom

T = TypeVar('T', bound=list[DFG])
V = TypeVar('V', bound=list[IMDataStructureUVCL])


class ProcessTreeNode(Generic[V]):
    tree_nodes_ls = []
    node_id_counter = 0
    
    def __init__(self, value: str, dfg: DFG, parent, children_obj_ls: V, is_base_case: bool = False,
                operation_type:str=None, log: Counter=None) -> None:
        self.node_id = ProcessTreeNode.node_id_counter
        ProcessTreeNode.tree_nodes_ls.append(self)
        ProcessTreeNode.node_id_counter += 1
        self.case_type = self._determine_im_case(value, operation_type)
        self.value = value
        if self.case_type == OperatorType.TAU_SYMBOL:
            self.value = "tau"
        
        self.dfg = dfg
        self.dfg_groups = {}
        
        self.log = log
        
        self.is_base_case = is_base_case
        self.parent = parent
        
        if parent != None:
            # append oneself to parent children list
            self.parent.children.append(self)
            if len(self.parent.children_not_calculated) > 0:
                self.parent.children_not_calculated.pop(0)
        
        # there are children and not calculated children these exist due to the fact that even though 
        # parallelization is possible for visualization the process tree is built up step by step 
        # hence at each point on a subset of the log (i.e. DFG) the cut detection is performed 
        # on this subset. To signal the remaining work to be done the display of the not calculated 
        # children is done
        self.children = []        
        self.children_not_calculated = []
        
        
        for index_counter in range(len(children_obj_ls)):
            obj = children_obj_ls[index_counter]
            # having the activities here because of base cases (empty graph)
            keys_sets_ls =  list(obj.dfg.start_activities) + list(
                            obj.dfg.graph) +  list(obj.dfg.end_activities)
            keys_dict = {}
            for key in keys_sets_ls:
                # the following lines flatten the tuples in order to have the process tree better understandable
                if isinstance(key, tuple):
                    for k_elem in key:
                        keys_dict[k_elem] = None
                else:
                    keys_dict[key] = None
            key_set = list(set(keys_dict.keys()))
            
            if not self.is_base_case:
                self.children_not_calculated.append(key_set)
            
            self.dfg_groups[index_counter + 1] = key_set # adding one to initial group, because of start/ end node group
            #print(key_set)
        print(self.dfg_groups)
        self.pt_str_json = self._traverse_tree_json(self.__get_root_node())
        # print(str(self.pt_str_json).replace("()", "").replace("'", "")) 
        
    def _traverse_tree_json(self, pt_node) -> str:
        pre_s = '{{ "value": "{}"'.format(pt_node.value)
        s = ""
        if len(pt_node.children) > 0 or len(pt_node.children_not_calculated) > 0: 
            s += ', "children": ['
            for child in pt_node.children:
                s += self._traverse_tree_json(child) + ", "
            for child in pt_node.children_not_calculated:
                s += str(child).replace("{", "[").replace("}", "]") + ", " #+ "%"
            s = s[:-2]
            s += " ] "
        return pre_s + s + "}"
    
    def __get_root_node(self):
        if self.parent == None:
            return self
        else:
            return self.parent.__get_root_node()
        
    def _determine_im_case(self, value, operator_type: str) -> str:
        """ with this function a mapping from the pm4py operators to the desired operators for displaying 
            the explanation 

        Args:
            value (_type_): _description_
            operator_type (str): _description_

        Returns:
            str: _description_
        """
        if value in signs_ls_im_custom or operator_type == OperatorType.CUT:
            return OperatorType.CUT.value
        else:
            # either base case, other or tau 
            if value == None:
                return OperatorType.TAU_SYMBOL.value
            elif operator_type == OperatorType.BC:
                return OperatorType.BC.value
            else:
                return OperatorType.FT.value 