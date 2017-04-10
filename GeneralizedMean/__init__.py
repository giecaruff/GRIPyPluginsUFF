# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import wx

import numpy as np

from Algo import meantypes, calcmeanbykey

inputdesc = [{'type': 'ommulti', 'name': 'logs', 'tids': ['log'], 'dispname': u'Perfis'},
             {'type': 'choice', 'name': 'meantype', 'dispname': u"Tipo de média", 'items': meantypes, 'default': u"Aritimética"},
             {'type': 'text', 'name': 'name', 'dispname': 'Nome'},
             {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}]

outputdesc = [{'type': 'log', 'name': 'meanlog'}]


def job(**kwargs):
    logs = kwargs.get('logs', None)
    meantype = kwargs.get('meantype', None)
    
    if not logs or meantype is None:
        return
    
    where = np.ones(len(logs[0]), dtype=bool)
    
    for log in logs:
        where *= np.isfinite(log)
    
    meanlogdata = np.empty_like(logs[0])
    meanlogdata[:] = np.nan
    
    
    
    meanlogdata[where] = calcmeanbykey(np.transpose(np.array(logs))[where], meantype)
    
    name = kwargs.get('name', 'MEAN')
    unit = kwargs.get('unit', '')

    output = {}
    output['meanlog'] = {}
    output['meanlog']['name'] = name
    output['meanlog']['unit'] = unit
    output['meanlog']['data'] = meanlogdata
    return output


class GeneralizedMeanPlugin(AutoGenDataPlugin):
    def __init__(self):
        super(GeneralizedMeanPlugin, self).__init__()
        self._OM = ObjectManager(self)
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc

    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Generalized Mean Plugin")

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
