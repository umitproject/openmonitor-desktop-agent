#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Authors: Rodolfo Carvalho <rodolfo.ueg@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import sys
import os
import os.path
import types

_SEARCH_ORDER = (
    ('.py', False),
    ('/__init__.py', True)
)

class UmitImporter(object):
    umit_cache = []
    def __init__(self, path):
        if 'umit' not in os.path.split(path):
            raise ImportError
        print "# UmitImporter: Found umit dir in", path
        self._build_cache()

    def _build_cache(self):
        """Searches in sys.path for 'umit' directories
        """
        for path in sys.path:
            if os.path.exists(os.path.join(path, 'umit')):
                self.umit_cache.append(path)

    def _get_info(self, fullmodname):
        # import pdb
        # pdb.set_trace()
        parts = fullmodname.split('.')
        submodname = parts[-1]
        rpath = os.sep.join(parts[1:])

        for suffix, is_package in _SEARCH_ORDER:
            # searches for submodules in umit subdirs
            for prefix in self.umit_cache:
                relpath = os.path.join(prefix, 'umit',
                                       rpath + suffix.replace('/', os.sep))
                if os.path.exists(relpath):
                    print "# UmitImporter: Found module %s in '%s'" % (submodname, relpath)
                    return submodname, is_package, relpath
        raise ImportError

    def _get_source(self, fullmodname):
        submodname, is_package, fullpath = self._get_info(fullmodname)
        source = open(fullpath, 'r').read()
        source = source.replace('\r\n', '\n') # windows line-endings
        source = source.replace('\r', '\n') # mac line-endings
        return submodname, is_package, fullpath, source

    def find_module(self, fullname, path=None):
        try:
            submodname, is_package, relpath = self._get_info(fullname)
        except ImportError:
            return None
        else:
            return self

    def load_module(self, fullmodname):
        submodname, is_package, fullpath, source = self._get_source(fullmodname)
        code = compile(source, fullpath, 'exec')
        mod = sys.modules.get(fullmodname)

        try:
            if mod is None:
                mod = sys.modules[fullmodname] = types.ModuleType(fullmodname)
            mod.__loader__ = self
            mod.__file__ = fullpath
            mod.__name__ = fullmodname

            if is_package:
                mod.__path__ = [os.path.dirname(mod.__file__)]
            exec code in mod.__dict__
        except:
            if fullmodname in sys.modules:
                del sys.modules[fullmodname]
            raise
        return mod

sys.path_hooks.insert(0, UmitImporter)
