#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python script implementing a collection of useful text handling functions

import codecs
import os
import subprocess
import sys
import time

VERSION = 0.6

def join_lines(new_lines, txt):
    """Joins lines, adding a trailing return if the original text had one."""
    return add_ending('\n'.join(new_lines), txt)

def add_ending(new_txt, txt):
    """Adds a trailing return if the original text had one."""
    if txt.endswith('\n'):
        new_txt = "%s\n" % new_txt
    if txt.endswith('\r'):
        new_txt = "%s\r" % new_txt
    return new_txt


class Tasks(object):

    def run_task(self, argument, parameter):
        """Dispatch method"""
        # Prefix the method_name with 'task_', replacing hyphens with underscores
        method_name = 'task_' + str(argument).replace('-', '_').replace(' ', '_').replace('\'', '').lower()
        # Get the method from 'self'.
        method = getattr(self, method_name, '')
        if method:
            # Call the method as we return it
            return method(parameter)
        else:
            raise Exception("Error: script task '%s' not found." % argument)

    def task_bold(self, txt):
        new_txt = txt.strip()
        if new_txt.startswith('**') and new_txt.endswith('**'):
            new_txt = new_txt[2:-2]
        elif new_txt.startswith('*') and new_txt.endswith('*'):
            new_txt = "*%s*" % new_txt
        else:
            new_txt = "**%s**" % new_txt
        return add_ending(new_txt, txt)

    def task_brace(self, txt):
        new_txt = txt.strip()
        if new_txt.startswith('{') and new_txt.endswith('}'):
            new_txt = new_txt[1:-1]
        else:
            new_txt = "{%s}" % new_txt
        return add_ending(new_txt, txt)

    def task_clean_clipboard(self, txt):
        if txt:
            new_txt = str(txt)
        else:
            new_txt = ''
        return new_txt

    def task_emphasize(self, txt):
        new_txt = txt.strip()
        if new_txt.startswith('*') and new_txt.endswith('*'):
            new_txt = new_txt[1:-1]
        else:
            new_txt = "*%s*" % new_txt
        return add_ending(new_txt, txt)

    def task_literal(self, txt):
        new_txt = txt.strip()
        if new_txt.startswith('``') and new_txt.endswith('``'):
            new_txt = new_txt[2:-2]
        else:
            new_txt = "``%s``" % new_txt
        return add_ending(new_txt, txt)

    def task_markdown_literal(self, txt):
        new_txt = txt.strip()
        if new_txt.startswith('```') and new_txt.endswith('```'):
            new_txt = new_txt[2:-2]
        elif new_txt.startswith('``') and new_txt.endswith('``'):
            new_txt = new_txt[1:-1]
        elif new_txt.startswith('`') and new_txt.endswith('`'):
            new_txt = new_txt[1:-1]
        elif new_txt.startswith('\'') and new_txt.endswith('\''):
            new_txt = "`%s`" % new_txt[1:-1]
        else:
            new_txt = "`%s`" % new_txt
        return add_ending(new_txt, txt)

#     Changing Text Case

    def task_case_lower(self, txt):
        return txt.lower()

    def task_lowercase(self, txt):
        return self.task_case_lower(txt)

    def task_case_upper(self, txt):
        return txt.upper()

    def task_uppercase(self, txt):
        return self.task_case_upper(txt)

#     Changing Enclosing Quotes

    def task_double_quotes(self, txt):
        new_txt = txt.strip()
        if new_txt.startswith('"') and new_txt.endswith('"'):
            new_txt = new_txt[1:-1]
        else:
            new_txt = "\"%s\"" % new_txt
        return add_ending(new_txt, txt)

    def task_single_quotes(self, txt):
        new_txt = txt.strip()
        if new_txt.startswith('\'') and new_txt.endswith('\''):
            new_txt = new_txt[1:-1]
        else:
            new_txt = "'%s'" % new_txt
        return add_ending(new_txt, txt)

    def task_less_greater_than(self, txt):
        new_txt = txt.strip()
        if new_txt.startswith('<') and new_txt.endswith('>'):
            new_txt = new_txt[1:-1]
        else:
            new_txt = "<%s>" % new_txt
        return add_ending(new_txt, txt)

    def task_strip(self, txt):
        # Removes outer character(s) if they match
        s = txt[0]
        s1 = txt[1]
        e = txt[-1]
        e1 = txt[-2]
        if s == e and s in ('\'', '"', '*', '_'):
            return txt[1:-1]
        elif s == s1 and s1 == e1 and s in ('`'):
            return txt[2:-2]
        else:
            return txt

    def task_wrap(self, txt):
        # Wraps and indents lines if first character of a line is a hyphen
        # FIXME: handle indented wraps
        new_txt = txt
        new_lines = []
        in_wrap = []
        lines = txt.splitlines()
        if len(lines) > 1:
            in_wrap = False
            for line in lines:
                line_clean = line.lstrip()
                if line_clean.startswith('- ') or line_clean.startswith('* '):
                    in_wrap = True
                    diff = len(line) - len(line_clean)
                elif line and in_wrap:
                    line = "%s  %s" % (' ' * diff, line_clean)
                else:
                    in_wrap = False
                    diff = 0
                new_lines.append(line)
            new_txt = join_lines(new_lines, txt)
        return new_txt

    def task_css(self, txt):
        # Format css so that each line ends with a {
        lines = []
        for line in txt.splitlines():
            line_clean = line.rstrip()
            left_brace = line_clean.find('{')
            right_brace = line_clean.find('}')
            if line_clean == '{':
                lines[-1] += ' {'
            elif (left_brace != -1) and (right_brace != -1):
                lines.append(line_clean[:left_brace+1])
                lines.append(' ' * 4 + line_clean[left_brace+1:right_brace].strip())
                lines.append('}')
                lines.append('')
            else:
                lines.append(line_clean)
        new_lines = []
        for i in range(len(lines)):
            new_lines.append(lines[i])
            if lines[i].endswith('*/'):
                if (i+1 < len(lines)) and lines[i+1]:
                    # Add an empty line after a comment
                    new_lines.append('')
        return join_lines(new_lines, txt)

    # Underline Methods

    def task_over_and_underlines(self, txt):
        # If either two or three lines provided, uses them to create an over-and-underline.
        # If more lines given, checks if an already-common char, and overwrites.
        lines = txt.splitlines()
        new_txt = txt
        overage = []
        common_line_chars = ('-','=','_','.')
        if len(lines) > 1:
            try:
                if len(lines) == 2:
                    text_line = lines[0]
                    over_under_char = lines[1][0]
                elif len(lines) == 3:
                    text_line = lines[1]
                    over_under_char = lines[2][0]
                else:
                    if lines[0][0] in common_line_chars and lines[2][0] in common_line_chars:
                        text_line = lines[1]
                        over_under_char = lines[2][0]
                        overage = lines[3:]
                    elif lines[1][0] in common_line_chars:
                        text_line = lines[0]
                        over_under_char = lines[1][0]
                        overage = lines[2:]
                over_under_line = over_under_char * len(text_line)
                new_lines = [over_under_line, text_line, over_under_line] + overage
                new_txt = join_lines(new_lines, txt)
            except:
                pass
        return new_txt

    def task_underline(self, txt):
        lines = txt.splitlines()
        new_txt = txt
        if len(lines) > 1:
            over_under_line = lines[1][0] * len(lines[0])
            new_lines = [lines[0], over_under_line]
            if len(lines) > 2:
                new_lines = new_lines + lines[2:]
            new_txt = join_lines(new_lines, txt)
        return new_txt

    #
    # Escaping Methods
    #

    def task_escape_backslashes(self, txt):
        if txt.endswith('\n') or txt.endswith('\r'):
            end = '\n'
        else:
            end = ''
        return "%s%s" % (txt.replace('\\', '\\\\'), end)

    #
    # Replacement Methods
    #

    def task_replace_with_hyphens(self, txt):
        return txt.lower().replace(' ', '-').replace('_', '-')

    def task_replace_hyphens(self, txt):
        return txt.lower().replace('-', '_')

    def task_replace_spaces(self, txt):
        return txt.lower().replace(' ', '-')

    def task_swap_quotes(self, txt):
        new_txt = ''
        for i in txt:
            if i == '\'':
                new_txt += '"'
            elif i == '"':
                new_txt += '\''
            else:
                new_txt += i
        return new_txt

    #
    # Misc. Methods
    #

    def task_rst_comment(self, txt):
        commented = False
        new_lines = []
        lines = txt.splitlines()
        for line in lines:
            if lines[0].startswith('..'):
                commented = True
            if commented: # Need to remove comments
                if line.startswith('.. '):
                    new_lines.append(line[3:])
                else:
                    new_lines.append(line)
            else: # Need to add comments
                new_lines.append('.. ' + line)
        return join_lines(new_lines, txt)

    def task_shift_left(self, txt):
        new_lines = []
        for line in txt.splitlines():
            if line.startswith(' '):
                new_lines.append(line[1:])
            else:
                new_lines.append(line)
        return join_lines(new_lines, txt)

    def task_shift_right(self, txt):
        new_lines = []
        for line in txt.splitlines():
            new_lines.append(" %s" % line)
        return join_lines(new_lines, txt)

    def task_delete_left(self, txt):
        new_lines = []
        for line in txt.splitlines():
            new_lines.append(line[1:])
        return join_lines(new_lines, txt)

    def task_search_with_duckduckgo(self, txt):
        os.system("open \"https://duckduckgo.com/?q=%s\"" % txt)
        return txt

    def task_insert_todays_date(self, txt):
        return time.strftime('%x')

    def task_build_table_rst(self, txt):
        self.fields = []
        self.fields_just = []
        new_lines = []
        for line in txt.splitlines():
            self._analyze_fields(line)
        for line in txt.splitlines():
            new_lines.append(self._build_line(line))
        return join_lines(new_lines, txt)

    # Build a Markdown Table

    def task_build_table_markdown(self, txt):
        self.fields = []
        self.fields_just = []
        new_lines = []
        for line in txt.splitlines():
            self._analyze_fields(line)
        for line in txt.splitlines():
            new_lines.append(self._build_line(line))
        return join_lines(new_lines, txt)

    def _analyze_fields(self, line):
        line_fields = line.split('|')
        if line_fields and line_fields[0] == u'':
            line_fields = line_fields[1:]
        if line_fields and line_fields[-1] == u'':
            line_fields = line_fields[:-1]
        if len(self.fields) < len(line_fields):
            self.fields += [0] * (len(line_fields) - len(self.fields))
        if len(self.fields_just) < len(line_fields):
            self.fields_just += [0] * (len(line_fields) - len(self.fields_just))
        for f in range(len(line_fields)):
            line_field = line_fields[f].strip()
            if line_field.startswith(':---') and line_field.endswith('---:'):
                # centered justification
                self.fields_just[f] = 'c'
            elif line_field.startswith(':---'):
                # left justification
                self.fields_just[f] = 'l'
            elif line_field.endswith('---:'):
                # right justification
                self.fields_just[f] = 'r'
            elif line_field.startswith('---'):
                # default justification
                self.fields_just[f] = 0
            if len(line_field) > self.fields[f] and not (line_field.startswith('--')
                    or line_field.startswith(':-') or line_field.endswith('-:')):
                self.fields[f] = len(line_field)
            if self.fields[f] < 3:
                self.fields[f] = 3

    def _build_line(self, line):
        line_fields = line.split('|')
        if line_fields and line_fields[0] == u'':
            line_fields = line_fields[1:]
        if line_fields and line_fields[-1] == u'':
            line_fields = line_fields[:-1]
        for f in range(len(line_fields)):
            line_field = line_fields[f].strip()
            if line_field.startswith(':---') and line_field.endswith('---:'):
                line_fields[f] = ":%s:" % ('-' * (self.fields[f] -2))
            elif line_field.startswith(':---'):
                line_fields[f] = ":%s" % ('-' * (self.fields[f] -1))
            elif line_field.endswith('---:'):
                line_fields[f] = "%s:" % ('-' * (self.fields[f] -1))
            elif line_field.startswith('---'):
                line_fields[f] = '-' * self.fields[f]
            else:
                if self.fields_just[f] == 'c':
                    space = self.fields[f] - len(line_field)
                    space_left = int(space/2) * ' '
                    space_right = (space - int(space/2)) * ' '
                    line_fields[f] = "%s%s%s" % (space_left, line_field, space_right)
                elif self.fields_just[f] == 'r':
                    line_fields[f] = line_field.rjust(self.fields[f], ' ')
                else:
                    line_fields[f] = line_field.ljust(self.fields[f], ' ')
        return "| %s |" % ' | '.join(line_fields)

    def task_(self, txt):
        return txt

    def task_test(self, txt):
        return txt


def main():
    if len(sys.argv) < 2:
        if len(sys.argv) == 1 and sys.argv[0].endswith('pyscript.py'):
            os.system("open \"%s\"" % sys.argv[0])
        else:
            raise Exception("Error: length of sys.argv: %s %s" % (len(sys.argv), sys.argv))
    else:
        parameter = sys.argv[2].decode('utf-8') if len(sys.argv) > 2 else ''
        new_txt = Tasks().run_task(sys.argv[1].decode('utf-8'), parameter)
        if new_txt:
            if parameter and parameter[-1].isspace():
                print new_txt.encode('utf-8') + parameter[-1].encode('utf-8')
            else:
                print new_txt.encode('utf-8')


if __name__ == '__main__':
    main()

