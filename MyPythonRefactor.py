import sys
import re
import platform
from os.path import dirname, realpath
import tempfile
from datetime import datetime
from collections import defaultdict
import subprocess
import sublime
import sublime_plugin
import os
import os.path
import json


ALL_SETTINGS = [
    'nodePath'
]

DEFAULT_HIGHTLIGHT_CODE_SMELL = True
DEFAULT_MIN = 20
DEFAULT_SPACE_IGNORED = True
DEFAULT_CASE_IGNORED = True
DEFAULT_LARGE_CLASS = 2000
DEFAULT_LONG_LINE = 50
DEFAULT_REPEAT_TIME = 3
DEFAULT_DUPLICATE_COLOR = "invalid"


NODE_PATH = "node"
DEFAULT_IS_ENABLED = True

DEFAULT_IS_DISABLED = False


'''
Load settings, the setting file is MyPythonRefactor.sublime-settings
It is in the same folder and is easy to find
This plugin also provide you a quick to open the file
Use Quick Open: Setting in Refactor menu
'''
def load_settings():
    return sublime.load_settings('MyPythonRefactor.sublime-settings')


def load_file_path():
    file_path = dirname(realpath(__file__)) + "/"
    return file_path



'''a flag to determine whether to highlight code smells'''
def highlight_code_smells():
    settings = load_settings()
    return bool(settings.get('highlight_code_smells', DEFAULT_HIGHTLIGHT_CODE_SMELL))


'''
Detect for exec_statemt is a typical example for detecting content related code smells
'''
def detect_for_exec(view):

    region_in_lines = view.lines(sublime.Region(0, view.size()))
    #pre_process remove the indent, spaces
    #all the words are set to lower case
    counts = pre_process(region_in_lines, view)
    bad_smell = dict()
    reg = 0
    for k, v in counts.items():
        if (re.findall(r'\bexec\b', k)):
            if (k[0] == "#"):
                continue
            bad_smell[k] = v
            yuanzu = v[0]
            reg = yuanzu.end()

    # lc = view.find_by_class(0, False, GotodefinitionCommand)

    exec_region = bad_smell.values()
    # print(exec_region)      
    current_regions = []
    exec_mark = current_regions
    view.add_regions("exec_mark", exec_mark, "exec_mark", "dot", sublime.DRAW_OUTLINED)
    for r in exec_region:
        current_regions.extend(r)
        yuanzu = r[0]
        reg = yuanzu.end()
        exec_mark = current_regions

        view.add_regions("exec_mark", exec_mark, "exec_mark", "dot", sublime.DRAW_OUTLINED)
        show_popup(view, 'Use of the exec statement could be dangerous, and should be avoided. Moreover, the statement was removed in Python 3.0', reg)


def show_popup(view, message, location):
	
	view.show_popup(
		message,
        flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
        location=location,
        max_width=1000,
        max_height=500,
        on_navigate=None
    )


def pre_process(region_in_lines, view):

    '''Counts line occurrences of a view using a hash.
    The lines are stripped and tested before count.
    '''
    processed_result = defaultdict(list)

    for line in region_in_lines:

        #read content
        content = view.substr(line)

        # remove space
        if spaceIgnored():
            content = content.strip()
        # adjust to lower case
        if caseIgnored():
            content = content.lower()

        processed_result[content].append(line)
    return processed_result


def spaceIgnored():
    settings = load_settings()
    return bool(settings.get('spaceIgnored', DEFAULT_SPACE_IGNORED))


def caseIgnored():
    settings = load_settings()
    return bool(settings.get('caseIgnored', DEFAULT_CASE_IGNORED))


# Detect for repr statement is similar
'''
The ideas for detecting content related code smells are similar,all you need to do is to add the key words.
This kind of job is not repeated in this project
'''
def detect_for_repr(view):
    region_in_lines = view.lines(sublime.Region(0, view.size()))
    counts = deep_pre_process(region_in_lines, view, minLineLength())
    filtered = dict()
    reg = 0
    for k, v in counts.items():
        if (re.findall(r'\breturn `\b', k)):
            filtered[k] = v
            yuanzu = v[0]
            reg = yuanzu.end()
            # print(v)
    #show_lines(filtered.values(), view)
    #show_popup(view, 'Backticks are a deprecated alias for repr(). Do not use them any more, the syntax was removed in Python 3.0.', reg)


'''
deep_pre_process, on the basic of pre_process, filter out some short lines
This is to reduce the workload of the listener, making the plugin respond faster
'''
def deep_pre_process(region_in_lines, view, length):

    pre_processed_result = defaultdict(list)

    for line in region_in_lines:
        content = view.substr(line)
        # print(string)
        # remove space
        if spaceIgnored():
            content = content.strip()
        # set to lower case
        if caseIgnored():
            content = content.lower()
        # remove short lines 
        if long_enough(content):
            pre_processed_result[content].append(line)
    return pre_processed_result


# current the value is 20, set in setting file
def minLineLength():
    settings = load_settings()
    minLength = settings.get('min', DEFAULT_MIN)
    if isinstance(minLength, int):
        return minLength
    else:
        return DEFAULT_MIN


def long_enough(string):
    # return len(string.strip('{}()[]/')) >= minLineLength
    return len(string.strip('{}()[]/')) >= DEFAULT_LONG_LINE
    # return True


'''
calculate is a class is too large.
'''
def detect_for_large_class(view):
    lines = view.lines(sublime.Region(0, view.size()))
    #print("Test for view.findbyclass")
    #test = re.findall(r'class')
    #print(test)
    counts = pre_process(lines, view)
    filtered = dict()
    reg = 0

    classlist = []
    all_large_class_region = []


    for k, v in counts.items():
        # This is a test for large class
        if (re.findall(r'class', k)):
            if (k[0:6] == "class "):
                # print(k)
                classlist.append(v[0].begin())
                
            
    sortedClasslist = sorted(classlist)
    # print(sortedClasslist)
    for index in range(len(sortedClasslist)) :
        if (index+2 > len(sortedClasslist)):
            break
        if ((sortedClasslist[index+1] - sortedClasslist[index]) > DEFAULT_LARGE_CLASS):
            large_class_region = sublime.Region(sortedClasslist[index], sortedClasslist[index+1])
            all_large_class_region.append(large_class_region)
            # print(large_class_region)
    # print(all_large_class_region)
    view.add_regions("large_class_mark",all_large_class_region, "large_class_mark", "dot", sublime.DRAW_OUTLINED)


def detect_for_long_parameter_list(view):
    lines = view.lines(sublime.Region(0, view.size()))
    #print("Test for view.findbyclass")
    #test = re.findall(r'class')
    #print(test)
    counts = pre_process(lines, view)
    filtered = dict()
    reg = 0


    classlist = []
    all_large_class_region = []
    # print("This is the test for long parameter list!")
    parameter = ","


    for k, v in counts.items():
        # This is a test for large class
        if (re.findall(r'def', k)):
            if (k[0:4] == "def "):
                if (k.count(parameter) >= 4):
                    filtered[k] = v
                    yuanzu = v[0]
                    reg = yuanzu.end()

    exec_region = filtered.values()  
    # print(exec_region)      
    current_regions = []
    mark = current_regions
    view.add_regions("mark", mark, "mark", "dot", sublime.DRAW_OUTLINED)
    for r in exec_region:
        current_regions.extend(r)
        yuanzu = r[0]
        reg = yuanzu.end()
        mark = current_regions

        view.add_regions("mark", mark, "mark", "dot", sublime.DRAW_OUTLINED)
        show_popup(view, 'This is a long parameter list', reg)
    view.add_regions("long_par_list_mark",all_large_class_region, "long_par_list_mark", "dot", sublime.DRAW_OUTLINED)


def detect_for_duplicate_code(view):

    # Scan the whole file in lines
    region_in_lines = view.lines(sublime.Region(0, view.size()))
    # print(lines)
    pre_process_result = deep_pre_process(region_in_lines, view, minLineLength())
    duplicate_code = find_duplicate_code(pre_process_result)
    result_dict = duplicate_code.values()
    # print(result_dict)
    highlight_duplicate_code(result_dict, view)



'''
Detect for duplicate code
If the same code repeat for more than 3 times
It will be highlighted
'''
def find_duplicate_code(pre_process_result, repeat_time=DEFAULT_REPEAT_TIME):

    duplicate_result = dict()

    for k, v in pre_process_result.items():
        if len(v) > repeat_time:
            duplicate_result[k] = v

    return duplicate_result


'''
An overall highlight method was expected to be developed.
The plan was canncled because of some conflication
'''
def highlight_duplicate_code(duplicate_code_regions, view):
    '''Merges all duplicated regions in one set and highlights them.'''
    whole_regions = []
    for r in duplicate_code_regions:
        whole_regions.extend(r)
        #all_regions.extend(my_region)
    new_whole_regions = whole_regions
    # for mr in my_region:
        # all_regions.extend(mr)
    color_scope_name = deplicate_code_color()
    view.add_regions('DuplicateCode', whole_regions, color_scope_name, '',sublime.DRAW_OUTLINED)


def deplicate_code_color():
    settings = load_settings()
    return settings.get('duplicate_code', DEFAULT_DUPLICATE_COLOR)




def merge_results(countsList):
    '''Merges the individual region lists
    into one list
    '''
    merged = []
    for k in countsList:
        for v in k:
            merged.append(v)
    return merged



def add_lines(regions, view):
    '''Merges all duplicated regions in one set and highlights them.'''
    view.sel().clear()
    all_regions = []
    for r in regions:
        for i in r:
            view.sel().add(i)


def remove_lines(regions, view, edit):
    all_regions = []
    for r in reversed(regions):
        view.erase(edit, sublime.Region(r.begin()-1, r.end()))



def select_duplicates(view):
    '''Main function that glues everything for hightlighting.'''
    # get all lines
    lines = view.lines((0, view.size()))
    # count and filter out non duplicated lines
    duplicates = find_duplicate_code(deep_pre_process(lines, view, minLineLength()))
    # select duplicated lines
    add_lines(duplicates.values(), view)



def hide_code_smells(view):
    '''Removes any region highlighted by this plugin accross all views.'''
    view.erase_regions('DuplicateCode')
    view.erase_regions('exec_mark')
    view.erase_regions('large_class_mark')
    view.erase_regions('mark')
    view.erase_regions('long_par_list_mark')

    
def update_settings(newSetting):
    settings = load_settings()
    settings.set('highlight_duplicates_enabled', newSetting)
    sublime.save_settings('MyPythonRefactor.sublime-settings')




def codeSmellList(view):
    detect_for_duplicate_code(view)
    detect_for_exec(view)
    detect_for_large_class(view)
    detect_for_long_parameter_list(view)


class CodeSmellListener(sublime_plugin.EventListener):
    '''Handles sone events to automatically run the command.'''
    def on_modified(self, view):
        if highlight_code_smells():
            codeSmellList(view)
        else:
            hide_code_smells(view)

    def on_activated(self, view):
        if highlight_code_smells():
            codeSmellList(view)
                   
        else:
            hide_code_smells(view)

    def on_load(self, view):
        if highlight_code_smells():
            codeSmellList(view)
        else:
            hide_code_smells(view)
            

class HighlightDuplicatesCommand(sublime_plugin.WindowCommand):

    def run(self):
        # If toggling on, go ahead and perform a pass,
        # else clear the highlighting in all views
        if highlight_code_smells():
            detect_for_duplicate_code(self.window.active_view())
        else:
            hide_code_smells(self.window)


'''This class itself is also used for testing large class'''

class RefactorBaseClass(sublime_plugin.TextCommand):
    currentCursorPosition = -1

    def init(self, edit, active_group=False):
        '''Restores user settings.'''
        settings = sublime.load_settings('MyPythonRefactor.sublime-settings')
        
        for setting in ALL_SETTINGS:
            if settings.get(setting) != None:
                self.view.settings().set(setting, settings.get(setting))

        NODE_PATH = self.view.settings().get('nodePath', 'node') 
        # print((__name__ + '.sublime-settings'))
        # print(NODE_PATH)


    def executeNodeJsShell(self, cmd):
        out = ""
        err = ""
        result = ""
        if (platform.system() is "Windows"):
            newCmd = cmd
        else:
            newCmd = " ".join("'" + str(x) + "'" for x in cmd)

        p = subprocess.Popen(newCmd, shell=True, stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        print(newCmd)
        (out, err) = p.communicate()
        if err.decode('utf-8') != '':
            sublime.error_message(str(err))
        else:
            result = out
        return result.decode('utf-8')



    def openJSONFile(self, filename):
        json_file = open(filename)
        data = json.load(json_file)
        json_file.close()
        return data

    def writeTextFile(self, data, filename):
        text_file = open(filename, "w")
        text_file.write(data)
        text_file.close()

    def replaceCurrentTextSelection(self, edit, text):
        startPos = 0
        for region in self.view.sel():
            startPos = region.a
            if region.b < startPos:
                startPos = region.b
            self.view.replace(edit, region, text)
            self.currentCursorPosition = startPos
        return startPos

    def get_indent(self, pos):
        (row, col) = self.view.rowcol(pos)
        indent_region = self.view.find('^\s+', self.view.text_point(row, 0))
        if self.view.rowcol(indent_region.begin())[0] == row:
            indent = self.view.substr(indent_region)
        else:
            indent = ''
        return indent


class ExtractmethodCommand(RefactorBaseClass):
    '''
    This part refers to the way used to extract method from javascript file.
    The same way can be implied to python file
    This part relies on Node.js make sure you set the node path in setting files correctly.
    '''
    def run(self, edit):
        self.init(edit)
        self.ExtractmethodCommand(edit)


    def ExtractmethodCommand(self, edit):

        if len(self.view.sel()) != 1:
            sublime.error_message("Can not extract at the same time.")
            return


        REFACTOR_PLUGIN_FOLDER = load_file_path()
        scriptPath = REFACTOR_PLUGIN_FOLDER + "js/script.js"
        tempFile = tempfile.gettempdir() + "/tmp.txt.js"
        jsonResultTempFile = tempfile.gettempdir() + "/resultCodePositions.json"
        settings = ' '.join([
            "indent_size:\ 2",
            "indent_char:\ ' '",
            "max_char:\ 80",
            "brace_style:\ collapse"
        ])

        cmd = [self.view.settings().get('nodePath', 'node'), scriptPath, tempFile, jsonResultTempFile, settings]
        code = self.view.substr(self.view.sel()[0])
        self.writeTextFile(code, tempFile)
        refactoredText = self.executeNodeJsShell(cmd)
        if len(refactoredText):
            pos = self.view.sel()[0].begin()
            indend = self.get_indent(pos)
            self.replaceCurrentTextSelection(edit, refactoredText.replace("\n", "\n" + indend))
            selections = [[12, 13]]  # self.openJSONFile(jsonResultTempFile)
            self.view.sel().clear()
        os.remove(tempFile)


