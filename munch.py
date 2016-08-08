#############################################################
#
# TODO:
#
#############################################################


import sys
import os

class KaleInterp:

    def __init__(self):

        self.for_bool = False  # tells file_reader whether or not it should writeout loops

        #self.keywords is a dictionary of keywords and function calls
        self.keywords = {'write:' : self.write, 'var:' : self.variable,
                                                        'if:' : self.if_call, 'input:' : self.input,
                                                        'math:' : self.math, 'for:' : self.for_loop}

        self.kale_variables = {}  # holds the variables from the kale program
        open_file = open(sys.argv[1], encoding='utf-8')

        # all variable must be declared above this method call
        self.file_reader(open_file)

    def file_reader(self, kale_file):
        for line in kale_file:
            split_line = line.split()  # turns the line into an array for iter
            if not self.for_bool:  # if this is satisfied, a standard call is made i.e. no loop
                self.read_key_words(split_line)
            else:  # this is where looping info begins
                if split_line[0] == 'END:':  # breaks out of loop and resets for_bool
                    self.for_bool = False
                    self.read_loop_file(self.for_init_line)
                else:  # this writes instructions for the loop into a separate file which will be deleted
                    with open('.tmp.txt', 'a', encoding='utf-8') as loop_file:
                        loop_file.write(line)
        kale_file.close()

    def read_key_words(self, split_line):
        for key in self.keywords:  # iterate through self.keywords
            # try statement is to accomodate blank lines in the kale file
            try:
                if split_line[0] == key:  # compare first word to keys
                    self.keywords[key](split_line)  # make appropriate method call
            except IndexError:
                continue

    def write(self, current_line):
        buffer_string = ''  # declare variable
        for index in range(len(current_line)):
            try:
                # reassign string with words
                # if statements puts variables into printed strings
                if current_line[index + 1][0] == '_':
                    buffer_string += str(self.kale_variables[current_line[index + 1]])
                else:
                    buffer_string += current_line[index + 1] + ' '
            except IndexError:
                break
        print(buffer_string)

    def variable(self, current_line):
        # these assign variable to a dictionary to store them
        if current_line[1] == 'bool:':
            var_obj = self.bool_obj(current_line)
        elif current_line[1] == 'int:':
            var_obj = self.int_obj(current_line)
        else:
            var_obj = self.str_obj(current_line)

        self.kale_variables[current_line[2]] = var_obj

    # determines and returns the proper python type for each variable
    def bool_obj(self, current_line):
        if current_line[4] == 'True':
            return True
        else:
            return False

    # determines and returns the proper python type for each variable
    def int_obj(self, current_line):
        try:
            return int(current_line[4])
        except TypeError:
            math_statement = current_line[1:]
            return self.math(math_statement)
        except ValueError:
            if current_line[4][0] == '_':
                for var in self.kale_variables:
                    if var == current_line[4]:
                        return self.kale_variables[var]

    # determines and returns the proper python type for each variable
    # gets all of the string
    def str_obj(self, current_line):
        var_buffer = ''
        for line_index in range(len(current_line)):
            try:
                var_buffer += current_line[line_index + 4] + ' '
            except IndexError:
                break
        return var_buffer

    def if_call(self, whole_line):
        conditional_statement = []  # this is the conditional to evaluate
        result_statement = []  # this holds what the statement does
        for x in range(len(whole_line)):
            if whole_line[x + 1] == '->':
                result_index = x + 2  # this is where the product begins
                break
            conditional_statement.append(whole_line[x + 1])
        while result_index < len(whole_line):
            result_statement.append(whole_line[result_index])
            result_index += 1

        # evaluates the statement and acts on it
        if self.operation_eval(conditional_statement, True):
            self.read_key_words(result_statement)

    # the 'apostrophe' argument is because the method is multi use
    def operation_eval(self, operation, apostrophe):
    # evaluates the operational value and returns a simplified True or False
        eval_buffer = ''
        for item in operation:
            if item[0] == '_':
                for var_name in self.kale_variables:
                    if item == var_name:
                        eval_buffer += ' ' + str(
                                        self.insert_apostrophe(self.kale_variables[var_name], apostrophe))
                        break
            else:
                eval_buffer += ' ' + self.insert_apostrophe(item, apostrophe)
        return eval(eval_buffer)

    def input(self, split_line):
        innit_counter = 5  # this is the index at which the prompt starts
        prompt = ''  # the variable to hold the prompt
        while innit_counter < len(split_line):
            prompt += split_line[innit_counter] + ' '
            innit_counter += 1
        tmp = input(prompt + '\n')
        new_variable_line = [split_line[1], split_line[2], split_line[3],
                                                        split_line[4], tmp]
        self.variable(new_variable_line)

    def math(self, split_line):
        innit_counter = 5
        operation = []
        while innit_counter < len(split_line):
            operation.append(split_line[innit_counter])
            innit_counter += 1
        resolved_var = [split_line[1], split_line[2], split_line[3],
                                                split_line[4], self.operation_eval(operation, False)]
        self.variable(resolved_var)

    # this takes the apostrophe argument because not everything this is called
    # on actually needs this stuff
    def insert_apostrophe(self, word, apostrophe):
        if apostrophe:
            try:
                int(word)
                return word
            except ValueError:
                if word != True and word != False and word != 'not' and \
                                                word != 'and' and word != 'or' and word != '==':
                    return '\'' + word.strip() + '\''
                # this is in case the operator is '=='
                else:
                    return word
        else:
            return word

    def for_loop(self, split_line):
        os.system('touch .tmp.txt')
        self.for_bool = True  # sets flag so next lines get written to .tmp.txt
        self.for_init_line = split_line

    def read_loop_file(self, split_line):
        count = int(split_line[1])  # the range for the kale loop
        for _ in range(count):  # controls how many time loop happens
            loop_file = open('.tmp.txt', encoding = 'utf-8')
            self.file_reader(loop_file)
        os.system('rm .tmp.txt')

KaleInterp()

