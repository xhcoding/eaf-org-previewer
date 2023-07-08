#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2018 Andy Stewart
#
# Author:     Andy Stewart <lazycat.manatee@gmail.com>
# Maintainer: Andy Stewart <lazycat.manatee@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import tempfile

from core.utils import *
from core.webengine import BrowserBuffer
from PyQt6.QtCore import QUrl, QTimer, QFileSystemWatcher


class AppBuffer(BrowserBuffer):
    def __init__(self, buffer_id, url, arguments):
        BrowserBuffer.__init__(self, buffer_id, url, arguments, False)

        self.url = url
        self.html_file = self.get_html_file_path()

        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath(self.html_file)
        self.file_watcher.fileChanged.connect(self.update_file)

        self.load_org_html_file()

    def get_html_file_path(self):
        org_filename = os.path.basename(self.url)
        html_filename = os.path.splitext(org_filename)[0] + ".html"
        return os.path.join(tempfile.gettempdir(), html_filename)

    @interactive
    def update_theme(self):
        self.load_org_html_file()
        self.refresh_page()

    def load_org_html_file(self):
        (self.text_selection_color,
         self.dark_mode_theme
         ) = get_emacs_vars(["eaf-org-text-selection-color",
                             "eaf-org-dark-mode"])

        background_color = get_emacs_theme_background()
        foreground_color = get_emacs_theme_foreground()

        self.buffer_widget.init_dark_mode_js(__file__,
                                             self.text_selection_color,
                                             self.dark_mode_theme,
                                             {
                                                 "brightness": 100,
                                                 "constrast": 90,
                                                 "sepia": 10,
                                                 "mode": 0,
                                                 "darkSchemeBackgroundColor": background_color,
                                                 "darkSchemeForegroundColor": foreground_color})

        with open(self.html_file, "r") as f:
            html = f.read().replace("</style>", "\n  a, p, h1, h2, h3, h4, h5, h6, li { color: " + f'''{foreground_color};''' + "}\n\n" + "  body { background: " + f'''{background_color};''' + "}\n</style>")

            self.buffer_widget.setHtml(html, QUrl("file://"))

    def update_file(self, file):
        self.load_org_html_file()
        QTimer.singleShot(500, lambda : self.buffer_widget.scroll_to_bottom())
