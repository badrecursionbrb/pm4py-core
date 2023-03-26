
from collections import Counter
from typing import TypeVar, List, Generic, Dict
from collections.abc import Iterable

from pm4py.objects.dfg.obj import DFG, DirectlyFollowsGraph
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL

from pm4py.algo.discovery.inductive.visualization.constants import OperatorType, signs_ls_im_custom

T = TypeVar('T', bound=list[DFG])
V = TypeVar('V', bound=list[IMDataStructureUVCL])


class ProcessTreeNode(Generic[V]):
    """ The ProcessTreeNode represents all the data that should be available for visualisation of 
        a certain step during running the inductive miner. 
    
    Attributes: 
        tree_nodes_ls       Contains all ProcessTreeNode objects created during running of the
                            algorithm
        node_id_counter     Counting up for each node added to the list, to give a unique id to 
                            each node 
    """
    tree_nodes_ls = []
    node_id_counter = 0
    
    def __init__(self, value: str, dfg: DFG, parent, children_obj_ls: V, is_base_case: bool = False,
                operation_type:OperatorType=None, log: Counter=None) -> None:
        """ Initializes the ProcessTreeNode object

        Args:
            value (str): The value of the node i.e. the action performed during the step
            dfg (DFG): The dfg present at the current node 
            parent (ProcessTreeNode): The parent of the object, also is a ProcessTreeNode
            children_obj_ls (V): The children of the node 
            is_base_case (bool, optional): _description_. Defaults to False.
            operation_type (OperatorType, optional): _description_. Defaults to None.
            log (Counter, optional): _description_. Defaults to None.
        """
        self.node_id = ProcessTreeNode.node_id_counter
        ProcessTreeNode.tree_nodes_ls.append(self)
        ProcessTreeNode.node_id_counter += 1
        self.case_type = self._determine_im_case(value, operation_type)
        self.value = value
        if self.case_type == OperatorType.TAU_SYMBOL.value:
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
        
    def _traverse_tree_json(self, pt_node) -> Dict:
        """ Traverses the tree and packs this tree into a dict structure, also traverses children 
            not calculated by the algorithm yet 

        Args:
            pt_node (ProcessTreeNode): gets the parent node as an argument

        Returns:
            Dict: Dict containing the information about the process tree including the children of 
                    the tree that have not been calculated 
        """
        traverse_pt_dict = {"value": pt_node.value}
        children_ls = []
        if len(pt_node.children) > 0 or len(pt_node.children_not_calculated) > 0: 
            for child in pt_node.children:
                children_ls.append(self._traverse_tree_json(child))
            for child in pt_node.children_not_calculated:
                children_ls.append(str(child).replace("{", "[").replace("}", "]"))
        
        traverse_pt_dict["children"] = children_ls
        return traverse_pt_dict
    
    def __get_root_node(self):
        if self.parent == None:
            return self
        else:
            return self.parent.__get_root_node()
        
    def _determine_im_case(self, value: str, operator_type: OperatorType) -> str:
        """ with this function a mapping from the pm4py operators to the desired operators for displaying 
            the explanation 

        Args:
            value (str): A string that represents the value of a certain node as string 
            operator_type (OperatorType): Enum value of the OperatorType enum 

        Returns:
            str: operator type as a string represenation
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