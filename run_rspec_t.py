import sublime
import sublime_plugin
import os, errno
import re

def get_twin_path(path):
  spec_file = path.find("/spec/") >= 0

  if spec_file:
    if path.find("/lib/") > 0:
      return path.replace("/spec/lib/","/lib/").replace("_spec.rb", ".rb")
    else:
      return path.replace("/spec/","/app/").replace("_spec.rb", ".rb")
  else:
    if path.find("/lib/") > 0:
      return path.replace("/lib/", "/spec/lib/").replace(".rb", "_spec.rb")
    else:
      return path.replace("/app/", "/spec/").replace(".rb", "_spec.rb")

class OpenRspecFileCommand(sublime_plugin.WindowCommand):
  def run(self, option):
    self.views = []
    window = self.window
    current_file_path = self.window.active_view().file_name()

    twin_path = get_twin_path(current_file_path)

    if os.path.exists(twin_path):
      view = window.open_file(twin_path)
    else:
      matches = self.find_twin_candidates(current_file_path)
      matches.append("Create "+twin_path)

      def process_selection(option):
        if( option == matches.__len__() - 1):
          self.create_new_file(twin_path)
        elif( option == -1):
          print "Cancelled dialog"
          # do nothing
        else:
          window.open_file(matches[option])
      window.show_quick_panel(matches, process_selection)

  def create_new_file(self, path):
    window = self.window
    path_parts = path.split("/")
    dirname = "/".join(path_parts[0:-1])
    basename = path_parts[-1]

    try:
        os.makedirs(dirname)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

    twin_file = open(path, "w")

    constant_name = self.camelize(basename.replace(".rb", "").replace("_spec", ""))

    if basename.find("_spec") > 0:
      twin_file.write("class " + constant_name + "\nend")
    else:
      twin_file.write("require \"spec_helper\"\n\ndescribe " + constant_name + " do\nend")
    twin_file.close()

    print(path)

    view = window.open_file(twin_file)
    self.views.append(view)


  def find_twin_candidates(self, file_path):
    is_spec = file_path.find("/spec/") > 0

    base_name = re.search(r"\/(\w+)\.(\w+)$", file_path).group(1)
    base_name = re.sub('_spec', '', base_name)

    if is_spec:
      matcher = re.compile("[/\\\\]" + base_name + "\.rb$")
    else:
      matcher = re.compile("[/\\\\]" + base_name + "_spec\.rb$")

    window = self.window
    candidates = []
    for root, dirs, files in os.walk(window.folders()[0]):
      for f in files:
        if re.search(r"\.rb$", f):
          cur_file = os.path.join(root, f)
          if matcher.search(cur_file):
            candidates.append(cur_file)

    return candidates

  def camelize(self, string):
    return re.sub(r"(?:^|_)(.)", lambda x: x.group(0)[-1].upper(), string)


class RunTerminalTestCommand(sublime_plugin.TextCommand):
  def run(self, edit, single=False):
    path = self.view.file_name()
    
    if path.find("/spec/") < 0:
      twin_path = get_twin_path(path)
      if os.path.exists(twin_path):
        path = twin_path
      else:
        return sublime.error_message("You're not in a spec, bro.")
    print ("path = "+path) 
    root_path = re.sub("\/spec\/.*", "", path)
    print("rootpath = "+root_path)
    if single:
      line_number, column = self.view.rowcol(self.view.sel()[0].begin())
      line_number += 1
      path += ":" + str(line_number)

    self.run_in_terminal('cd ' + root_path)
    self.run_in_terminal('bundle exec rspec ' + path + ' --drb')

  def run_in_terminal(self, command):
    osascript_command = 'osascript '
    osascript_command += '"' + sublime.packages_path() + '/User/run_command.applescript"'
    osascript_command += ' "' + command + '"'
    osascript_command += ' "Ruby Tests"'
    print(osascript_command)
    print os.system(osascript_command)