import sublime_plugin
from os import path
from operator import itemgetter
from datetime import datetime

class OrderedFilesCommand(sublime_plugin.WindowCommand):
   def run(self, index):
      OF = OrderedFilesCommand
      OF.file_views = []
      win = self.window
      for vw in win.views():
         if vw.file_name() and path.exists(vw.file_name()):
            head, tail = path.split(vw.file_name())
            modified = path.getmtime(vw.file_name())
            OF.file_views.append((tail, vw, modified))
      if index == 0:      # sort by file name (case-insensitive)
         OF.file_views.sort(key = lambda (tail, _, Doh): tail.lower())
         win.show_quick_panel([x for (x, y, z) in OF.file_views], self.on_chosen)
      else:            # sort by modified date (index == 2)
         OF.file_views.sort(key = itemgetter(2))
         win.show_quick_panel([
            (datetime.fromtimestamp(z)).strftime("%d-%m-%y %H:%M ") + x \
            for (x, y, z) in OF.file_views], self.on_chosen)

   def on_chosen(self, index):
      if index != -1:
         self.window.focus_view(OrderedFilesCommand.file_views[index][1])