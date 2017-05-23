# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import wx

import numpy as np

try:
    from DT.DataTypes import Depth
    depthtid = Depth.tid
except:
    from DT.DataTypes import IndexCurve
    depthtid = IndexCurve.tid
    

inputdesc = [{'type': 'omsingle', 'name': 'depth', 'tids':[depthtid], 'dispname': u'Profundidade'},
             {'type': 'float', 'name': 't0', 'dispname': u'Temperatura 1'},
             {'type': 'float', 'name': 'z0', 'dispname': u'Profundidade 1'},
             {'type': 'float', 'name': 't1', 'dispname': u'Temperatura 2'},
             {'type': 'float', 'name': 'z1', 'dispname': u'Profundidade 2'},
             {'type': 'text', 'name': 'name', 'dispname': 'Nome'},
             {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}]

outputdesc = [{'type': 'log', 'name': 'temp'}]


def job(**kwargs):
    depth = kwargs.get('depth', None)
    t0 = kwargs.get('t0', None)
    z0 = kwargs.get('z0', None)
    t1 = kwargs.get('t1', None)
    z1 = kwargs.get('z1', None)
    name = kwargs.get('name', 'TEMP')
    unit = kwargs.get('unit', '')

    if depth is None:
        return
    
    if t0 is None or z0 is None or t1 is None or z1 is None:
        return

    tempdata = t0 + (t1 - t0)*(depth - z0)/(z1 - z0)

    output = {}
    output['temp'] = {}
    output['temp']['name'] = name
    output['temp']['unit'] = unit
    output['temp']['data'] = tempdata
    return output


class TemperaturePlugin(AutoGenDataPlugin):
    def __init__(self):
        super(TemperaturePlugin, self).__init__()
        self._OM = ObjectManager(self)
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc

    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Basic Temperature Plugin")

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
