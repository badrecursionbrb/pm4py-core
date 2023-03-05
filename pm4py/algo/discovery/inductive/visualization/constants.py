
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from enum import Enum

signs_ls_im_custom = [Operator.SEQUENCE.__str__(),  Operator.XOR.__str__(), 
                        Operator.PARALLEL.__str__(), Operator.LOOP.__str__(), 
                        Operator.OR.__str__(),Operator.INTERLEAVING.__str__(), 
                        "tau"]
# "BASECASE": "BASECASE", "other": "other", "tau": "tau",


class OperatorType(Enum):
    FT= "FT"
    
    CUT="CUT"
    
    BC="BC"
    
    TAU_SYMBOL = "TAU"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value