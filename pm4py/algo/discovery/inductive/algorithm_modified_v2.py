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
from enum import Enum
from typing import Optional, Dict, Any, Union, List

import pandas as pd

from pm4py import util as pmutil
#from pm4py.algo.discovery.inductive.variants.abc import InductiveMinerFramework
from pm4py.algo.discovery.inductive.dtypes.im_dfg import InductiveDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL, IMDataStructureDFG
from pm4py.algo.discovery.inductive.dtypes.im_ds_custom import IMDataStructureCustom
from pm4py.algo.discovery.inductive.variants.im import IMUVCL
from pm4py.algo.discovery.inductive.variants.imf import IMFUVCL
from pm4py.algo.discovery.inductive.variants.imd import IMD
from pm4py.algo.discovery.inductive.variants.imf_custom import IMFUVCL_Custom
from pm4py.algo.discovery.inductive.variants.im_custom import IMUVCL_Custom
from pm4py.algo.discovery.inductive.variants.instances import IMInstance
from pm4py.objects.dfg.obj import DFG
from pm4py.objects.log.obj import EventLog
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util import constants
from pm4py.util import exec_utils
from pm4py.util import xes_constants as xes_util
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UVCL
import warnings


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


class Variants(Enum):
    """ This Enum needs to be extended for each IM variant that shall be displayed in the 
            front-end
    """
    IM = IMInstance.IM
    IMf = IMInstance.IMf
    IMd = IMInstance.IMd
    IMcustom = IMInstance.IMcustom
    IMf_custom = IMInstance.IMf_custom

def apply(obj: Union[EventLog, pd.DataFrame, DFG, UVCL], parameters: Optional[Dict[Any, Any]] = None, variant=Variants.IMcustom) -> (ProcessTree, List):
    """ This method overwrites the corresponding apply method in the 

    Args:
        obj (Union[EventLog, pd.DataFrame, DFG, UVCL]): The Event Log
        parameters (Optional[Dict[Any, Any]], optional): additional parameters such as threshold.
                                                        Defaults to None.
        variant (_type_, optional): Gives the Variant of the Inductive Miner, see the Variants 
                        Enum above. Defaults to Variants.IMcustom.

    Raises:
        TypeError: If the type of the obj is not in the List of allowed  data types this method 
                    raises a TypeError

    Returns:
        ProcessTree: Returns a ProcessTree object containing also the information for each step 
                    via the pt_node attribute, present in each ProcessTree object 
    """
    
    if parameters is None:
        parameters = {}
    if type(obj) not in [EventLog, pd.DataFrame, DFG, UVCL]:
        raise TypeError('Inductive miner called with an incorrect data type as an input (should be a dataframe or DFG)')
    ack = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    tk = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY)
    cidk = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, pmutil.constants.CASE_CONCEPT_NAME)
    if type(obj) in [EventLog, pd.DataFrame, UVCL]:
        if type(obj) in [EventLog, pd.DataFrame]:
            uvcl = comut.get_variants(comut.project_univariate(obj, key=ack, df_glue=cidk, df_sorting_criterion_key=tk))
        else:
            uvcl = obj
        if variant is Variants.IMcustom:
            im = IMUVCL_Custom(parameters)
            dfg = comut.discover_dfg_uvcl(uvcl)
            return im.apply(IMDataStructureCustom(uvcl, dfg), parameters), im.tree_nodes_ls
        if variant is Variants.IMf_custom:
            im = IMFUVCL_Custom(parameters)
            dfg = comut.discover_dfg_uvcl(uvcl)
            return im.apply(IMDataStructureCustom(uvcl, dfg), parameters), im.tree_nodes_ls
        # if variant is Variants.IM:
        #     im = IMUVCL(parameters)
        #     return im.apply(IMDataStructureUVCL(uvcl), parameters)
        # if variant is Variants.IMf:
        #     imf = IMFUVCL(parameters)
        #     return imf.apply(IMDataStructureUVCL(uvcl), parameters)
        if variant is Variants.IMd:
            imd = IMD(parameters)
            idfg = InductiveDFG(dfg=comut.discover_dfg_uvcl(uvcl), skip=() in uvcl)
            return imd.apply(IMDataStructureDFG(idfg), parameters)
    elif type(obj) is DFG:
        if variant is not Variants.IMd:
            warnings.warn('Inductive Miner Variant requested for DFG artefact is not IMD, resorting back to IMD')
        imd = IMD(parameters)
        idfg = InductiveDFG(dfg=obj, skip=False)
        return imd.apply(IMDataStructureDFG(idfg), parameters)
