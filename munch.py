#!/usr/bin/env python3
#############################################################
#
# TODO:
#
#############################################################


import sys
import os
from re import sub

class KaleInterp:

    def __init__(self):

        self.for_bool = False  # tells file_reader whether or not it should writeout loops
        self.while_bool = False # same as for_bool but for while loops

        #self.keywords is a dictionary of keywords and function calls
        self.keywords = {'write:' : self.write, 'var:' : self.variable,
                                                        'if:' : self.if_call, 'input:' : self.input,
                                                        'math:' : self.math, 'for:' : self.for_loop,
                                                        'while:' : self.while_loop}

        self.kale_variables = {}  # holds the variables from the kale program
        open_file = open(sys.argv[1], encoding='utf-8')

        # all variable must be declared above this method call
        self.file_reader(open_file)

    def file_reader(self, kale_file):
        for line in kale_file:
            split_line = line.split()  # turns the line into an array for iter
            if not self.for_bool and not self.while_bool:  # if this is satisfied, a standard call is made i.e. no loop
                self.read_key_words(split_line)
            elif self.for_bool:  # this is where looping info begins
                self.write_loop_files('END:', '.tmp.txt', split_line, line)
            elif self.while_bool:
                self.write_loop_files('END_LOOP:', '.tmp_while.txt', split_line, line)

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
        # should append the result_statement, I think
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
                        eval_buffer += ' ' + str(self.insert_apostrophe(self.kale_variables[var_name], apostrophe))
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
                python_key_word = [True, False, 'not', 'and', 'or', '==', '<', '>', '<=', '>=', '!=', 'True', 'False']
                if word not in python_key_word:
                    return '\'' + word.strip() + '\''
                # this is in case the operator is '=='
                else:
                    return word
        else:
            return word

    def for_loop(self, split_line):
        open('.tmp.txt', 'w').close()
        self.for_bool = True  # sets flag so next lines get written to .tmp.txt
        self.for_init_line = split_line

    def read_loop_file(self, split_line):
        count = int(split_line[1])  # the range for the kale loop
        for _ in range(count):  # controls how many time loop happens
            loop_file = open('.tmp.txt', encoding = 'utf-8')
            self.file_reader(loop_file)
        os.remove('.tmp.txt')

    def read_while_file(self, split_line):
        con_statement = []
        for item in split_line:
            if item != 'while:' and item != '->':  # writes and evals conditional
                con_statement.append(item)
        while True:
            # this if serves to break the loop if condition becomes false
            # in the kale file
            if self.operation_eval(con_statement, True) is True:
                pass
            else:
                break
            # read and execute tmp file
            while_loop_file = open('.tmp_while.txt', encoding = 'utf-8')
            self.file_reader(while_loop_file)
        os.remove('.tmp_while.txt')  # remove the tmp file
    
    def while_loop(self, split_line):
        open('.tmp_while.txt', 'w').close()
        self.while_bool = True  # flag to trigger files to be written
        self.while_init_line = split_line

    def write_loop_files(self, end_word, file_name, split_line, line):
        if split_line[0] == end_word:  # breaks out of loop and resets for_bool
            if end_word == 'END:':
                self.for_bool = False
                self.read_loop_file(self.for_init_line)
            elif end_word == 'END_LOOP:':
                self.while_bool = False
                self.read_while_file(self.while_init_line)
        else:  # this writes instructions for the loop into a separate file which will be deleted
            with open(file_name, 'a', encoding='utf-8') as loop_file:
                loop_file.write(line)


class Cleanup:
    def __init__(self):
        self.clean()

    def clean(self):
        try:
            os.remove('.tmp_while.txt')
            print('clean...')
        except FileNotFoundError:
            print('clean...')
        try:
            os.remove('.tmp.txt')
            print('clean...')
        except FileNotFoundError:
            print('clean...')


# class Refactor is the first addition that is ultimately designed to 
# turn the munch interpreter into a suite of system management tools
class Refactor:
    def __init__(self):
        try:
            original_file_name = sys.argv[2] 
            regex_pattern = sys.argv[3]
            new_phrase = sys.argv[4]
        except IndexError:
            print('Error: must pass arguments \nfile_name old_phrase new_phrase')
            sys.exit()
        with open(original_file_name + '.backup', 'w') as backup:  # creates the backup file
            # below, we begin to write out the backup file
            with open(original_file_name, 'r') as original:
                for line in original:
                    backup.write(line)

        # below rewrites the original file from backup.txt
        # but using the sub method to replace given word
        with open(original_file_name + '.backup', 'r') as backup:  # 'r' protects the file from being deleted
            with open(original_file_name, 'w') as rewrite:  # 'w' ensures that the file will be overwritten
                for line in backup:
                    new_line = sub(regex_pattern, new_phrase, line)
                    rewrite.write(new_line)

class HelpPage():
    def __init__(self):
        try:
            if sys.argv[1] == '-h':
                print('\n')
        except IndexError:
            print('\nERROR: must pass arguments\n')
        print('Execute kalefile\t\tmunch file_name.kale')
        print('-c\t\t\t\tClean up residual files munch occasionally makes')
        print('-h\t\t\t\tDisplay this help page')
        print('-r\t\t\t\tTo refactor a file: munch -r file_name old_phrase new_phrase')


try:
    if '.kale' in sys.argv[1]:
        KaleInterp()
    elif sys.argv[1] == '-c':
        Cleanup()
    elif sys.argv[1] == '-r':
        Refactor()
    elif sys.argv[1] == '-h':
        HelpPage()
except IndexError:
    HelpPage()

