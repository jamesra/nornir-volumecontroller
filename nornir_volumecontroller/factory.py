'''
Created on Apr 10, 2014

@author: u0490822
'''

import nornir_volumecontroller
import nornir_volumexml


def CreateVolumeController(vol_model):
    '''Given a volume model create a controller for the model'''

    if(isinstance(vol_model, str)):
        vol_model = nornir_volumexml.Load_Xml(vol_model)

    return nornir_volumecontroller.Volume(vol_model)