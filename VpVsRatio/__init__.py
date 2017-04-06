# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import wx


inputdesc = [{'type': 'omsingle', 'name': 'vp', 'tids': ['log'], 'dispname': u'Vp'},
             {'type': 'omsingle', 'name': 'vs', 'tids': ['log'], 'dispname': u"Vs"},
             {'type': 'bool', 'name': 'is_sonic', 'dispname': u"É sônico?", 'default': False},
             {'type': 'text', 'name': 'name', 'dispname': 'Nome'},
             {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}]

outputdesc = [{'type': 'log', 'name': 'vpvsratio'}]


def job(**kwargs):
    is_sonic = kwargs.get('is_sonic', None)
    vp = kwargs.get('vp', None)
    vs = kwargs.get('vs', None)
    name = kwargs.get('name', 'VPVSRATIO')
    unit = kwargs.get('unit', '')

    if is_sonic is None or vp is None or vs is None:
        return

    if is_sonic:
        vpvsdata = vs/vp
    else:
        vpvsdata = vp/vs

    output = {}
    output['vpvsratio'] = {}
    output['vpvsratio']['name'] = name
    output['vpvsratio']['unit'] = unit
    output['vpvsratio']['data'] = vpvsdata
    return output


class VpVsRatioPlugin(AutoGenDataPlugin):
    def __init__(self):
        super(VpVsRatioPlugin, self).__init__()
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
