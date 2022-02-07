# coding=utf-8

import re
from os import listdir, system
from os.path import isdir, isfile, join

PATH_TO_RAILS_APP="/home/user/programming/my_app"
PATH_TO_TEMP_RAILS_APP="/home/user/programming/temp_app"

DRY_RUN=True

DATABASE_SCHEMA = [
  "public",
  "schema1",
  "schema2",
  "schema3"
]

# ------------------------------------ Models ------------------------------------

def get_models():
  files = get_all_rb_files(PATH_TO_RAILS_APP + "/app/models")
  return files

def read_model(file_path):
  model_name = get_model_name(file_path)
  table_name = get_table_name(file_path)
  variables = get_table_variables(table_name)
  actions = get_actions(file_path)
  file_name = basename(file_path)

  if len(model_name) == 0:
    print("Model name is empty -- skipping file %s" % file_path)
    return
  
  if len(variables) == 0:
    print("Model variables are empty -- skipping file %s" % file_path)
    return

  create_model(file_name, model_name, variables, actions)

def get_model_name(file_path):
  regex = 'class\\s+(\\w+)\\s*<\\s*ActiveRecord::Base'

  for line in read_file(file_path):
    if "class" in line:
      model_search = re.search(regex, line.strip(), re.IGNORECASE)

      if model_search:
        return model_search.group(1).strip()

  return ""

def get_table_variables(table_name):
  variables = ""
  table_line_found = False

  for line in db_schema:
    if table_line_found == False:
      create_regex = "\\s*create_table\\s+[\"|'](\\w+)[\"|'].*"
      create_table_search = re.search(create_regex, line.strip(), re.IGNORECASE)

      if create_table_search:
        if table_name == create_table_search.group(1):
          table_line_found = True
          continue
    
    elif line.strip() == "end":
      table_line_found = False
      break

    if table_line_found == True:
      regex = 't\\.(\\w+)\\s"(\\w+)".*'
      table_search = re.search(regex, line.strip(), re.IGNORECASE)

      if table_search:
        typ = table_search.group(1).lower()
        name = table_search.group(2).lower()

        if typ != "index":
          variables = variables + " " + (name + ":" + typ)
  
  return variables

def get_table_name(file_path):
  for line in read_file(file_path):
    if "self.table_name" in line:
      regex = get_table_regex()
      group_count = len(DATABASE_SCHEMA) + 1
      table_search = re.search(regex, line.strip(), re.IGNORECASE)

      if table_search:
        table = table_search.group(group_count)
        return table.strip().lower()
  return ""

def get_table_regex():
  regex = 'self\\.table_name\\s*=\\s*[\'|"]'
  for schema in DATABASE_SCHEMA:
    regex = regex + "(" + schema + ".)*"
  return regex + '(.*)[\'|"]'

def read_db_schema():
  return read_file(PATH_TO_RAILS_APP + "/db/schema.rb")

def create_model(file_name, name, variables, actions):
  if DRY_RUN == True:
    print("cd %s && rails g model %s %s --skip-collision-check --skip --no-migration --skip-helper" % (PATH_TO_TEMP_RAILS_APP, name, variables))
  else:
    system("cd %s && rails g model %s %s --skip-collision-check --skip --no-migration --skip-helper" % (PATH_TO_TEMP_RAILS_APP, name, variables))
    populate_model(file_name, actions)

def populate_model(file_name, actions):
  name = file_name.replace(".rb", "")
  file_path = PATH_TO_TEMP_RAILS_APP + "/test/models/" + name + "_test.rb"
    
  try:
    lines = read_file(file_path)
  except:
    return

  f = open(file_path, "w")

  for line in lines:
    if line.strip() == "end":
      f.write('\n')
      f.write('  setup do\n')
      f.write('    @%s = %ss(:one)\n' % (name, name))
      f.write('  end\n\n')
      for action in actions:
        f.write('  test "%s" do\n' % action.replace("_", " ").replace("self.", ""))
        f.write('    # TODO: test %s\n' % action)
        f.write('    assert true\n')
        f.write('  end\n\n')
    f.write(line)
  f.close()

# ------------------------------------ Controller ------------------------------------

def get_controllers():
  files = get_all_rb_files(PATH_TO_RAILS_APP + "/app/controllers")
  return files

def read_controller(file_path):
  controller_name = get_controller_name(file_path)
  actions = get_actions(file_path)
  file_name = basename(file_path)

  if len(controller_name) == 0:
    print("Controller name is empty -- skipping file %s" % file_path)
    return
  
  if len(actions) == 0:
    print("Controller actions are empty -- skipping file %s" % file_path)
    return

  create_controller(file_name, controller_name, actions)

def get_controller_name(file_path):
  regex = 'class\\s+(\\w+::)*(\\w+)\\s*<\\s*.+Controller'

  for line in read_file(file_path):
    if "class" in line:
      controller_search = re.search(regex, line.strip(), re.IGNORECASE)

      if controller_search:
        name = controller_search.group(2).strip()
        return  name.replace("Controller", "")

  return ""

def create_controller(file_name, name, actions):
  if DRY_RUN == True:
    print("cd %s && rails g controller %s --skip-collision-check --skip-routes --skip-template-engine --skip-helper --skip" % (PATH_TO_TEMP_RAILS_APP, name))
  else:
    system("cd %s && rails g controller %s --skip-collision-check --skip-routes --skip-template-engine --skip-helper --skip" % (PATH_TO_TEMP_RAILS_APP, name))
    populate_controller(file_name, actions)

def populate_controller(file_name, actions):
  name = file_name.replace("_controller.rb", "")
  file_path = PATH_TO_TEMP_RAILS_APP + "/test/controllers/" + name + "_controller_test.rb"

  try:
    lines = read_file(file_path)
  except:
    return

  f = open(file_path, "w")

  for line in lines:
    if line.strip() == "end":
      f.write('\n')
      f.write('  setup do\n')
      f.write('    @%s = %s(:one)\n' % (name, name))
      f.write('  end\n\n')
      for action in actions:
        f.write('  test "%s" do\n' % action.replace("_", " ").replace("self.", ""))
        f.write('    # TODO: test %s\n' % action)
        f.write('    assert true\n')
        f.write('  end\n\n')
    f.write(line)
  f.close()
  

# ------------------------------------ Helpers ------------------------------------

def get_actions(file_path):
  actions = []
  for line in read_file(file_path):
    if line.strip().startswith("def "):
      regex = '^\\s*def\\s+([^\\(]+)+(\\(.+\\))*$'
      actions_search = re.search(regex, line.strip(), re.IGNORECASE)

      if actions_search:
        action = actions_search.group(1)
        actions.append(action.strip())
  
  return actions

def get_all_rb_files(dir):
  files = []

  for element in listdir(dir):
    element_path = dir + "/" + element

    if isfile(element_path):
      if element.endswith('.rb'):
        files.append(element_path)
    if isdir(element_path):
      files = files + get_all_rb_files(element_path)

  return files

def read_file(file_path):
  file = open(file_path, 'r')
  return file.readlines()

def setup_tmp_app():
  print("Temp App Setup... ")
  system("rm -r %s" % PATH_TO_TEMP_RAILS_APP)
  system("gem install rails")
  system("rails new temp_app %s" % PATH_TO_TEMP_RAILS_APP)

def remove_tmp_app():
  system("rm -r %s" % PATH_TO_TEMP_RAILS_APP)

def main():
  for model in get_models():
    read_model(model)
  
  for controller in get_controllers():
    read_controller(controller)
  
db_schema = read_db_schema()

try:
  setup_tmp_app()
  main()
except Exception as e:
  print(e)
  print("Error! Cleaning up Project... ")
  remove_tmp_app()
