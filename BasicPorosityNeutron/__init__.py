# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import wx

import numpy as np

try:
    from Plugins.Tools.AutoGenUI import _OMLogLikeInput
    float_type = 'omloglike'
except:
    float_type = 'float'

inputdesc = [{'type': 'omsingle', 'name': 'nphi', 'tids': ['log'], 'dispname': u'Nêutron (NPHI)'},
             {'type': 'omsingle', 'name': 'vsh', 'tids': ['log'], 'dispname': u'Volume de argila (VSH)'},
             {'type': float_type, 'name': 'nphish', 'dispname': u"Leitura do Nêutron na argila", 'default': 0.3},
             {'type': 'text', 'name': 'name', 'dispname': 'Nome'},
             {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}]

outputdesc = [{'type': 'log', 'name': 'phin'}]


def job(**kwargs):
    nphi = kwargs.get('nphi', None)
    vsh = kwargs.get('vsh', None)
    nphish = kwargs.get('nphish', None)
    name = kwargs.get('name', 'PHIN')
    unit = kwargs.get('unit', '')

    if nphi is None or vsh is None or nphish is None:
        return

    phindata = nphi - vsh*nphish

    output = {}
    output['phin'] = {}
    output['phin']['name'] = name
    output['phin']['unit'] = unit
    output['phin']['data'] = np.clip(phindata, 0, 1)
    return output


class BasicPorosityNeutronPlugin(AutoGenDataPlugin):
    def __init__(self):
        super(BasicPorosityNeutronPlugin, self).__init__()
        self._OM = ObjectManager(self)
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc

    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Basic Porosity Neutron Plugin")

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
