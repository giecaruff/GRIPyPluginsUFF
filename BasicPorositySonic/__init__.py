# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import wx

import numpy as np

inputdesc = [{'type': 'omsingle', 'name': 'dt', 'tids': ['log'], 'dispname': u'Sônico (DT)'},
             {'type': 'float', 'name': 'dtma', 'dispname': u"Vagarosidade da matriz", 'default': 55.0},
             {'type': 'float', 'name': 'dtfl', 'dispname': u"Vagarosidade do fluido", 'default': 188.0},
             {'type': 'bool', 'name': 'usevsh', 'dispname': u"Corrigir para argila?", 'default': True},
             {'type': 'omsingle', 'name': 'vsh', 'tids': ['log'], 'dispname': u'Volume de argila (VSH)'},
             {'type': 'float', 'name': 'dtsh', 'dispname': u"Vagarosidade da argila", 'default': 100.0},
             {'type': 'choice', 'name': 'method', 'dispname': u"Método", 'items': [u"Wyllie", u"Hunt-Raymer"], 'default': u"Wyllie"},
             {'type': 'text', 'name': 'name', 'dispname': 'Nome'},
             {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}]

outputdesc = [{'type': 'log', 'name': 'phis'}]


def job(**kwargs):
    dt = kwargs.get('dt', None)
    dtma = kwargs.get('dtma', None)
    dtfl = kwargs.get('dtfl', None)
    usevsh = kwargs.get('usevsh', None)
    vsh = kwargs.get('vsh', None)
    dtsh = kwargs.get('dtsh', None)
    method = kwargs.get('method', None)
    name = kwargs.get('name', 'PHIS')
    unit = kwargs.get('unit', '')

    if dt is None or dtma is None or dtfl is None:
        return
    
    if usevsh and (vsh is None or dtsh is None):
        return
    
    if method == u"Wyllie":
        phisdata = (dt - dtma)/(dtfl - dtma)
        
        if usevsh:
            phissh = (dtsh - dtma)/(dtfl - dtma)
            phisdata -= vsh*phissh
    
    elif method == u"Hunt-Raymer":
        if usevsh:
            dtc = dt - vsh*(dtsh - dtma)
        else:
            dtc = dt
        
        C = dtma/(2.0*dtfl)
        
        phisdata = 1.0 - C - (C**2 - 2*C + dtma/dtc)**0.5

    output = {}
    output['phis'] = {}
    output['phis']['name'] = name
    output['phis']['unit'] = unit
    output['phis']['data'] = np.clip(phisdata, 0, 1)
    return output


class BasicPorositySonicPlugin(AutoGenDataPlugin):
    def __init__(self):
        super(BasicPorositySonicPlugin, self).__init__()
        self._OM = ObjectManager(self)
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc

    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Basic Porosity Sonic Plugin")

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
