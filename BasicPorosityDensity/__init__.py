# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import wx

import numpy as np

inputdesc = [{'type': 'omsingle', 'name': 'rhob', 'tids': ['log'], 'dispname': u'Densidade (RHOB)'},
             {'type': 'float', 'name': 'rhoma', 'dispname': u"Densidade da matriz", 'default': 2.65},
             {'type': 'float', 'name': 'rhofl', 'dispname': u"Densidade do fluido", 'default': 1.00},
             {'type': 'bool', 'name': 'usevsh', 'dispname': u"Corrigir para argila?", 'default': True},
             {'type': 'omsingle', 'name': 'vsh', 'tids': ['log'], 'dispname': u'Volume de argila (VSH)'},
             {'type': 'float', 'name': 'rhosh', 'dispname': u"Densidade da argila", 'default': 2.60},
             {'type': 'text', 'name': 'name', 'dispname': 'Nome'},
             {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}]

outputdesc = [{'type': 'log', 'name': 'phid'}]


def job(**kwargs):
    rhob = kwargs.get('rhob', None)
    rhoma = kwargs.get('rhoma', None)
    rhofl = kwargs.get('rhofl', None)
    usevsh = kwargs.get('usevsh', None)
    vsh = kwargs.get('vsh', None)
    rhosh = kwargs.get('rhosh', None)
    name = kwargs.get('name', 'PHID')
    unit = kwargs.get('unit', '')

    if rhob is None or rhoma is None or rhofl is None:
        return
    
    if usevsh and (vsh is None or rhosh is None):
        return

    phiddata = (rhob - rhoma)/(rhofl - rhoma)
    
    if usevsh:
        phidsh = (rhosh - rhoma)/(rhofl - rhoma)
        phiddata -= vsh*phidsh

    output = {}
    output['phid'] = {}
    output['phid']['name'] = name
    output['phid']['unit'] = unit
    output['phid']['data'] = np.clip(phiddata, 0, 1)
    return output


class BasicPorosityDensityPlugin(AutoGenDataPlugin):
    def __init__(self):
        super(BasicPorosityDensityPlugin, self).__init__()
        self._OM = ObjectManager(self)
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc

    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Impedance Plugin")

        if agd.ShowModal() == wx.ID_OK:
            input = agd.get_input()
            well_uid = agd.get_well_uid()
            output = job(**input)
            if output is None:
                agd.Destroy()
                return
            for odesc in self.outputdesc:
                name = odesc['name']
                output_type = odesc['type']
                obj = self._OM.new(output_type, **output[name])
                self._OM.add(obj, well_uid)

        agd.Destroy()
