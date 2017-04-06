# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import wx


inputdesc = [{'type': 'omsingle', 'name': 'dt', 'tids': ['log'], 'dispname': u'Sônico'},
             {'type': 'float', 'name': 'factor', 'dispname': u"Fator de conversão", 'default': 3.048E5},
             {'type': 'text', 'name': 'name', 'dispname': 'Nome'},
             {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}]

outputdesc = [{'type': 'log', 'name': 'vel'}]


def job(**kwargs):
    factor = kwargs.get('factor', None)
    dt = kwargs.get('dt', None)
    name = kwargs.get('name', 'VEL')
    unit = kwargs.get('unit', '')

    if factor is None or dt is None:
        return

    veldata = factor/dt

    output = {}
    output['vel'] = {}
    output['vel']['name'] = name
    output['vel']['unit'] = unit
    output['vel']['data'] = veldata
    return output


class DT2VPlugin(AutoGenDataPlugin):
    def __init__(self):
        super(DT2VPlugin, self).__init__()
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
