
from unittest import TestCase

# Test 1    Test for detection of large class.
    '''
    Classes contain more than 3000 characters will be considered as large class
    '''
class TestLargeClass(TestCase):
    currentCursorPosition = -1
    def init(self, edit, active_group=False):
        '''Restores user settings.'''
        settings = sublime.load_settings('Refactor.sublime-settings')
        
        for setting in ALL_SETTINGS:
            if settings.get(setting) != None:
                self.view.settings().set(setting, settings.get(setting))

        NODE_PATH = self.view.settings().get('nodePath', 'node') 
        # print((__name__ + '.sublime-settings'))
        # print(NODE_PATH)

    def save(self):
        self.view.run_command("save")

    def executeNodeJsShell(self, cmd):
        out = ""
        err = ""
        result = ""
        if (platform.system() is "Windows"):
            newCmd = cmd
        else:
            newCmd = " ".join("'" + str(x) + "'" for x in cmd)

        p = subprocess.Popen(newCmd, shell=True, stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        (out, err) = p.communicate()
        if err.decode('utf-8') != '':
            sublime.error_message(str(err))
        else:
            result = out
        return result.decode('utf-8')

    def applyMultipleSelections(self, selections):
        for region in selections:
            r = sublime.Region(self.currentCursorPosition + region[0], self.currentCursorPosition + region[1])
            self.view.sel().add(r)

    def abortMultiselection(self):
        if len(self.view.sel()) != 1:
            sublime.error_message("Multiple selection is not supported.")
            return True
        else:
            return False

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

    def normalize_line_endings(self, string):
        string = string.replace('\r\n', '\n').replace('\r', '\n')
        line_endings = self.view.settings().get('default_line_ending')
        if line_endings == 'windows':
            string = string.replace('\n', '\r\n')
        elif line_endings == 'mac':
            string = string.replace('\n', '\r')
        return string

    def get_indent(self, pos):
        (row, col) = self.view.rowcol(pos)
        indent_region = self.view.find('^\s+', self.view.text_point(row, 0))
        if self.view.rowcol(indent_region.begin())[0] == row:
            indent = self.view.substr(indent_region)
        else:
            indent = ''
        return indent

    def get_indent(self, pos):
        (row, col) = self.view.rowcol(pos)
        indent_region = self.view.find('^\s+', self.view.text_point(row, 0))
        if self.view.rowcol(indent_region.begin())[0] == row:
            indent = self.view.substr(indent_region)
        else:
            indent = ''
        # Test for detecting the combination of code smells 
        test = print("This line repeat too many times, this is used for test code smell combination")
        test = print("This line repeat too many times, this is used for test code smell combination")
        test = print("This line repeat too many times, this is used for test code smell combination")
        test = print("This line repeat too many times, this is used for test code smell combination")
        return indent

class TestDetectionForCodeSmells(TestCase):

    # 1. Test for duplicate code
    '''
    Duplicate code should occur more than 3 times
    Duplicate code should contain at least 50 characters
    '''
    def test_duplicate_code(self):
        negative_test = print("duplicate code")
        negative_test = print("duplicate code")
        negative_test = print("duplicate code")
        negative_test = print("duplicate code")

        positive_test = print("duplicate code should be long enough")
        positive_test = print("duplicate code should be long enough")
        positive_test = print("duplicate code should be long enough")
        positive_test = print("duplicate code should be long enough")
        pass

# Uncomment the following line and it shall be highlighted.
    '''
    2. Test for long parameter list
    More than 4 parameters will be considered as long parameter list
    '''
    def test_long_parameter_list(parameter1,parameter2, parameter3, parameter4):
    #Uncomment the following line and it shall be highlighted.
    # def test_long_parameter_list(parameter1,parameter2, parameter3, parameter4, parameter5):
        pass



    # 3. Detect for exec statement
    def test_key_words(self):
        # exectest = exec statements 



class TestRefactorMethods(TestCase):
    '''
    4. Test for Goto definition
    '''
    def test_go_to_definition():
        test_duplicate_code()
        pass

    '''
    5. Test for extract method
    '''
    def test_extract_method():
        test = print("This line repeat too many times, extract it to avoid duplicate code")
        test = print("This line repeat too many times, extract it to avoid duplicate code")
        test = print("This line repeat too many times, extract it to avoid duplicate code")
        test = print("This line repeat too many times, extract it to avoid duplicate code")
        
        pass

    '''
    6. Test for selection
    '''
    def test_for_selection():
        test1 = expand selection to line
        pass

class TestInformalTestCases(object):

    '''
    # 7. Test for similar expression
    The following lines should not be highlighted
    '''
    def test_similar_key_words(self):
        test1 = testexec state
        test2 = exectest state
        test3 = test_exec state
        pass


    '''
    ITC-5. Test for the influence of format
    More than 4 parameters will be considered as long parameter list
    '''
    def test_long_parameter_list(parameter1,parameter2, parameter3, parameter4):
    #Test for 空格
    # def test_long_parameter_list(parameter1,parameter2,     parameter3,     parameter4,     parameter5):
        pass
    #Test for 换行
    def test_long_parameter_list(parameter1,parameter2,
                                parameter3,     parameter4,     parameter5):
        pass

