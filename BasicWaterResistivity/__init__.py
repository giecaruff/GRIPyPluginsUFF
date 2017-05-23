# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import wx

import numpy as np

try:
    from Plugins.Tools.AutoGenUI import _OMLogLikeInput
    float_type = 'omloglike'
    temperature_inputdesc = {'type': 'omloglike', 'name': 'temp', 'dispname': u'Temperatura'}
except:
    float_type = 'float'
    temperature_inputdesc = {'type': 'omsingle', 'name': 'temp', 'tids':['log'], 'dispname': u'Temperatura'}

inputdesc = [temperature_inputdesc,
             {'type': float_type, 'name': 'salinity', 'dispname': u'Salinidade (ppm)'}
             {'type': 'bool', 'name': 'iscelsius', 'dispname': u'É Celsius?', 'default': False},
             {'type': 'text', 'name': 'name', 'dispname': 'Nome'},
             {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}]

outputdesc = [{'type': 'log', 'name': 'rw'}]


def job(**kwargs):
    temp = kwargs.get('temp', None)
    salinity = kwargs.get('salinity', None)
    iscelsius = kwargs.get('iscelsius')
    name = kwargs.get('name', 'RW')
    unit = kwargs.get('unit', '')

    if (temp is None) or (salinity is None):
        return

    if iscelsius:
        temp_ = 32.0 + 1.8*temp
    else:
        temp_ = temp
    
    rwdata = (400000.0/temp_/salinity)**0.88

    output = {}
    output['rw'] = {}
    output['rw']['name'] = name
    output['rw']['unit'] = unit
    output['rw']['data'] = rwdata
    return output


class WaterResistivityPlugin(AutoGenDataPlugin):
    def __init__(self):
        super(WaterResistivityPlugin, self).__init__()
        self._OM = ObjectManager(self)
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc

    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Basic Water Resistivity Plugin")

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
