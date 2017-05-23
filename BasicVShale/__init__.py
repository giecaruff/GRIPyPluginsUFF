# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import wx

import numpy as np
from .Algo import calcgrlimits   

try:
    from Plugins.Tools.AutoGenUI import _OMLogLikeInput
    float_type = 'omloglike'
except:
    float_type = 'float'

inputdesc = [{'type': 'omsingle', 'name': 'gr', 'tids': ['log'], 'dispname': u'Raios gama (GR)'},
             {'type': float_type, 'name': 'grmin', 'dispname': u"GRmin"},
             {'type': float_type, 'name': 'grmax', 'dispname': u"GRmax"},
             {'type': 'bool', 'name': 'auto', 'dispname': u"Calcular automaticamente?", 'default': False},
             {'type': 'text', 'name': 'name', 'dispname': 'Nome'},
             {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}]

outputdesc = [{'type': 'log', 'name': 'vsh'}]


def job(**kwargs):
    gr = kwargs.get('gr', None)
    grmin = kwargs.get('grmin', None)
    grmax = kwargs.get('grmax', None)
    auto = kwargs.get('auto', None)
    name = kwargs.get('name', 'VSH')
    unit = kwargs.get('unit', '')

    if gr is None:
        return
    
    if (not auto) and (None in (grmin, grmax)):
        return
    
    if auto:
        grmin, grmax = calcgrlimits(gr)

    vshdata = (gr - grmin)/(grmax - grmin)
    vshdata = np.clip(vshdata, 0.0, 1.0)

    output = {}
    output['vsh'] = {}
    output['vsh']['name'] = name
    output['vsh']['unit'] = unit
    output['vsh']['data'] = vshdata
    return output


class VShalePlugin(AutoGenDataPlugin):
    def __init__(self):
        super(VShalePlugin, self).__init__()
        self._OM = ObjectManager(self)
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc

    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Basic VShale Plugin")

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
