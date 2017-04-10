# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import wx

import numpy as np

inputdesc = [{'type': 'omsingle', 'name': 'rt', 'tids': ['log'], 'dispname': u'Resistividade profunda (RT)'},
             {'type': 'omsingle', 'name': 'phie', 'tids': ['log'], 'dispname': u'Porosidade efetiva (PHIE)'},
             {'type': 'float', 'name': 'A', 'dispname': u"Coeficiente de tortuosidade (A)", 'default': 1.0},
             {'type': 'float', 'name': 'M', 'dispname': u"Coeficiente de cimentação (m)", 'default': 2.0},
             {'type': 'float', 'name': 'N', 'dispname': u"Coeficiente de saturação (n)", 'default': 2.0},
             {'type': 'float', 'name': 'rw', 'dispname': u"Resistividade da água (RW)", 'default': 0.9},
             {'type': 'choice', 'name': 'method', 'dispname': u"Método", 'items': [u"Archie", u"Simandoux"], 'default': u"Archie"},
             {'type': 'omsingle', 'name': 'vsh', 'tids': ['log'], 'dispname': u'Volume de argila (VSH)'},
             {'type': 'float', 'name': 'rsh', 'dispname': u"Resistividade da argila (RSH)", 'default': 4.0},
             {'type': 'text', 'name': 'name', 'dispname': 'Nome'},
             {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}]

outputdesc = [{'type': 'log', 'name': 'sw'}]


def job(**kwargs):
    rt = kwargs.get('rt', None)
    phie = kwargs.get('phie', None)
    A = kwargs.get('A', None)
    M = kwargs.get('M', None)
    N = kwargs.get('N', None)
    rw = kwargs.get('rw', None)
    method = kwargs.get('method', None)
    vsh = kwargs.get('vsh', None)
    rsh = kwargs.get('rsh', None)
    name = kwargs.get('name', 'SW')
    unit = kwargs.get('unit', '')

    if None in (rt, phie, A, M, N, rw, method):
        return
    
    if method == u"Simandoux" and None in (vsh, rsh):
        return
    
    if method == u"Archie":
        swdata = (A*rw/(phie**M*rt))**(1.0/N)
    elif method == u"Simandoux":
        c = (1.0 - vsh)*A*rw/(phie**M)
        d = c*vsh/(2*rsh)
        e = c/rt
        swdata = ((d**2 + e)**0.5 - d)**(2.0/N)
    else:
        return

    output = {}
    output['sw'] = {}
    output['sw']['name'] = name
    output['sw']['unit'] = unit
    output['sw']['data'] = np.clip(swdata, 0.0, 1.0)
    return output


class BasicPorositySonicPlugin(AutoGenDataPlugin):
    def __init__(self):
        super(BasicPorositySonicPlugin, self).__init__()
        self._OM = ObjectManager(self)
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc

    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Basic Saturation Plugin")

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
