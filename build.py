#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright © 2017 John Jackson
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# Used to build BBEdit AppleScripts
#

import os
import subprocess
import sys
sys.dont_write_bytecode = True
# Avoids creating a .pyc file when importing from another file:
from pyscripts import VERSION as PYTHON_SCRIPT_VERSION

BUILD_VERSION = '0.0.3'

TARGET_DIR = 'target'
APPLICATION = 'BBEdit'
SCRIPTS_DIRECTORY = 'Scripts'
SCRIPTS_RESOURCES_DIRECTORY = 'Resources'

PYTHON_SCRIPT_SOURCE = 'pyscripts.py'
PYTHON_SCRIPT_SOURCE_NAME = PYTHON_SCRIPT_SOURCE[:-3]
PYTHON_SCRIPT_NAME = "%s-v%s" % (PYTHON_SCRIPT_SOURCE_NAME, PYTHON_SCRIPT_VERSION)
PYTHON_SCRIPT = "%s.py" % PYTHON_SCRIPT_NAME

PACKAGE = "%s.bbpackage" % PYTHON_SCRIPT_NAME

DOCUMENTATION_COMMAND = "•Documentation %s" % PYTHON_SCRIPT_NAME
SCRIPTS_README = "READ_ME_%s.md" % PYTHON_SCRIPT_NAME

INSTALL_SCRIPT = 'install.sh'

README_TEMPLATE = """<!-- -*- coding: utf-8; mode: markdown; version: 1; -*- -->

About the %(application)s pyscripts (%(python_script)s)
--------------------------------

This package ("%(package)s") contains scripts which extend %(application)s’s capabilities.
They are a collection of scripts that perform common tasks helpful when writing in RST or
Markdown. They also demonstrate techniques that can be used to extend %(application)s to
perform almost anything you might require.

(This document is written in [Markdown](http://www.daringfireball.net/projects/markdown/).
It's readable as plain text, but prettier if you choose "Preview in %(application)s" from
the "Markup" menu.)

To install the scripts, copy the package "%(package)s" to your application's "Application
Support/%(application)s/Packages" folder, creating the "Packages" folder if necessary. The
installation script ("%(install_script)s") will copy it to your iCloud drive, making it
available for all copies of %(application)s that you use.

You can add a keyboard shortcut for any of the scripts; in %(application)s’s
"Preferences -> Menus & Shortcuts", select "Scripts" from the left list, select a script
in the right pane, and then click the existing key combination shown (or the placeholder
text "none") and enter your desired combination.

Below is a description of each script:
"""

README_APPLESCRIPT_TEMPLATE = """
tell application "Finder" to set cPath to container of container of (path to me) as Unicode text
set my_doc_path to (POSIX path of (cPath & "%(scripts_resources_directory)s:%(scripts_readme)s"))

tell application "%(application)s"
    activate
    open {POSIX file my_doc_path} with read only
end tell
tell application "System Events" to tell process "%(application)s"
    set frontmost to true
    keystroke "p" using {command down, control down}
end tell
"""

APPLESCRIPT_TEMPLATE_WITH_SELECTION = """
tell application "Finder" to set cPath to container of container of (path to me) as Unicode text
set rPath to (quoted form of POSIX path of (cPath & "Resources:%(script)s"))

tell application "%(application)s"
    activate
    set oldClip to the contents of (get the clipboard)

    tell application "%(application)s"
        if not (exists text window 1) then
            display alert "The script '%(script)s' requires an open text window."
            return
        end if
        if length of selection of text window 1 is 0 then
            display alert "The command '%(command)s' of script '%(script)s' requires a selection in the text window."
            return
        end if
    end tell

    copy selection

    set command to "python " & rPath & " '%(command)s' " & quoted form of (text of (get the clipboard))
    set command to command as «class utf8»
    set the clipboard to (do shell script command)

    set firstCharacter to characterOffset of selection of text window 1
    set lastCharacter to (length of (get the clipboard)) + firstCharacter
    paste
    select (characters (firstCharacter) thru (lastCharacter - 1)) of text of the front window

    set the clipboard to oldClip
end tell
"""

APPLESCRIPT_TEMPLATE_NO_SELECTION_REQUIRED = """
tell application "Finder" to set cPath to container of container of (path to me) as Unicode text
set rPath to (quoted form of POSIX path of (cPath & "Resources:%(script)s"))

tell application "%(application)s"
    activate
    set oldClip to the contents of (get the clipboard)

    tell application "%(application)s"
        if not (exists text window 1) then
            display alert "The script '%(script)s' requires an open text window."
            return
        end if
    end tell

    set command to "python " & rPath & " '%(command)s'"
    set command to command as «class utf8»
    set the clipboard to (do shell script command)

    set firstCharacter to characterOffset of selection of text window 1
    set lastCharacter to (length of (get the clipboard)) + firstCharacter
    paste
    select (characters (firstCharacter) thru (lastCharacter - 1)) of text of the front window

    set the clipboard to oldClip
end tell
"""

INSTALL_SCRIPT_TEMPLATE = """#!/bin/bash
mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/Application\ Support/%(application)s/Packages/
rm -f
cp -R %(package)s ~/Library/Mobile\ Documents/com~apple~CloudDocs/Application\ Support/%(application)s/Packages/
"""

# FIXME: these should be completed
# Script name, help text, flag if selection is optional
APPLESCRIPTS = [
    ['Bold', 'Surrounds the selection with double-asterisks (**)'],
    ['Brace', 'Surrounds the selection in curved braces ({ })'],
    ['Build Table Markdown', 'Formats (pretty-prints) a table written in Markdown-format'],
    ['Build Table RST', 'Formats (pretty-prints) a table written in RST-format'],
    ['Case Lower', 'Changes the selection to lowercase'],
    ['Case Upper', 'Changes the selection to uppercase'],
    ['CSS', 'Reformats using BBEdit CSS rules'],
    ['Delete Left', 'Deletes the left-most character of each line'],
    ['Double Quotes', 'Surrounds the selection in double-quotes ("")'],
    ['Emphasize', 'Surrounds the selection with asterisks (*)'],
    ['Escape Backslashes', 'Escapes any backslashes in the selection'],
    ['Glossary'],
    ['Insert Today\'s Date', 'Inserts today\'s date at the insertion point or replaces selection', 'optional'],
    ['Literal', 'Surrounds the selection in double back-ticks (``)'],
    ['Markdown Literal', 'Surrounds the selection in single back-ticks (`)'],
    ['Over and Underlines',"""Inserts lines of characters (first character of second line, same length) before and after the first line.
If there are more than three lines, tries to determine if first two or three lines are an existing title or not."""],
    ['Replace Hyphens', 'Replaces hyphens (-) with underscores (_)'],
    ['Replace Spaces', 'Replaces spaces ( ) with hyphens (-)'],
    ['Replace with Hyphens', 'Replaces spaces ( ) and underscores (_) with hyphens (-)'],
    ['RST Comment', 'Toggles selection with leading RST comment markers (..)'],
    ['Search with DuckDuckGo', 'Searches for the selection using DuckDuckGo and the default browser'],
    ['Shift Left', 'Deletes the left-most character of each line, if a space character'],
    ['Shift Right', 'Adds a leading space character to each line'],
    ['Single Quotes', 'Surrounds the selection in single-quotes (\')'],
    ['Strip', 'Removes the leading and trailing characters if they match'],
    ['Swap Quotes', 'Swaps single-quotes for double-quotes and vice-versa'],
    ['Underline', 'Inserts a line of characters (first character of second line, same length) after the first line'],
    ['Wrap', 'Wraps and indents lines if first character of a line is a hyphen or asterisk'],
]

def shell(command):
    if command.count('\n') > 0:
        print "command: %s..." % command[:command.index('\n')]
    else:
        print "command: %s" % command
    try:
        output = ''
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT,)
    except:
        print "command: %s" % command
        raise Exception('shell', 'output: %s' % output)
    return output

def build_script(command, no_selection_required=False):
    command_cleaned = command.replace('-', '_').replace(' ', '_').replace('\'', '').lower()
    if no_selection_required:
        tmp = APPLESCRIPT_TEMPLATE_NO_SELECTION_REQUIRED % {'application': APPLICATION, 'command': command_cleaned,
            'script': PYTHON_SCRIPT}
    else:
        tmp = APPLESCRIPT_TEMPLATE_WITH_SELECTION % {'application': APPLICATION, 'command': command_cleaned,
            'script': PYTHON_SCRIPT}

    osacompile = """cat <<EOF | osacompile -o "%(target)s/%(application)s/%(package)s/Contents/%(scripts_directory)s/%(command)s.scpt"
%(tmp)s
EOF
""" % {'application': APPLICATION, 'command': command, 'package': PACKAGE,
            'scripts_directory': SCRIPTS_DIRECTORY, 'target': TARGET_DIR, 'tmp': tmp}

    shell(osacompile)

def build_documentation_script():
    command = DOCUMENTATION_COMMAND
    tmp = README_APPLESCRIPT_TEMPLATE % {'application': APPLICATION,
        'scripts_resources_directory': SCRIPTS_RESOURCES_DIRECTORY, 'scripts_readme': SCRIPTS_README}

    osacompile = """cat <<EOF | osacompile -o "%(target)s/%(application)s/%(package)s/Contents/%(scripts_directory)s/%(command)s.scpt"
%(tmp)s
EOF
""" % {'application': APPLICATION, 'command': command, 'package': PACKAGE,
            'scripts_directory': SCRIPTS_DIRECTORY, 'target': TARGET_DIR, 'tmp': tmp}

    shell(osacompile)

def build():
    print "Building AppleScripts for %(python_script)s, v%(version)s" % {'python_script': PYTHON_SCRIPT, 'version': PYTHON_SCRIPT_VERSION}

    print 'Creating target directories (removing any existing directories)'
    shell("rm -rf %s" % TARGET_DIR)
    shell("mkdir -p '%s/%s/%s/Contents/%s'" % (TARGET_DIR, APPLICATION, PACKAGE, SCRIPTS_DIRECTORY))
    shell("mkdir -p '%s/%s/%s/Contents/%s'" % (TARGET_DIR, APPLICATION, PACKAGE, SCRIPTS_RESOURCES_DIRECTORY))

    print 'Creating AppleScripts and creating README'
    readme_text = README_TEMPLATE
    for script in APPLESCRIPTS:
        script_name = script[0]
        if len(script) > 1 and script[1]:
            script_help_text = script[1]
        else:
            script_help_text = 'No description available.'
        script_help_text = script_help_text.replace('`', '\`')
        no_selection_required = bool(len(script) > 2)
        print "Script '%s'" % script_name
        build_script(script_name, no_selection_required)

        readme_text += "\n- **%s**\n\n" % script_name
        lines = script_help_text.splitlines()
        for line in lines:
            readme_text += "  %s\n" % line
        readme_text += '\n'
    print "Script '%s'" % DOCUMENTATION_COMMAND
    build_documentation_script()

    print 'Copying script library'
    shell("cp %(python_script_source)s '%(target_dir)s/%(app)s/%(package)s/Contents/Resources/%(python_script)s'" %
        {'app': APPLICATION, 'package': PACKAGE,
         'python_script_source': PYTHON_SCRIPT_SOURCE, 'python_script': PYTHON_SCRIPT, 'target_dir': TARGET_DIR})

    print 'Writing README'
    app_readme_text = (readme_text % {'application': APPLICATION, 'install_script': INSTALL_SCRIPT, 'package': PACKAGE,
        'python_script': PYTHON_SCRIPT_NAME})
    app_readme_filepath = ("%(target_dir)s/%(application)s/%(package)s/Contents/Resources/%(readme_file)s" %
        {'application': APPLICATION, 'package': PACKAGE, 'readme_file': SCRIPTS_README, 'target_dir': TARGET_DIR})
    write_readme = """cat <<EOF > "%(app_readme_filepath)s"
%(app_readme_text)s
EOF
""" % {'app_readme_filepath': app_readme_filepath, 'app_readme_text': app_readme_text}

    shell(write_readme)

    print 'Copying README'
    shell("cp %(app_readme_filepath)s %(target_dir)s/%(application)s/%(readme_file)s" %
        {'application': APPLICATION, 'app_readme_filepath': app_readme_filepath, 'readme_file': SCRIPTS_README,
            'target_dir': TARGET_DIR})

    print 'Writing install script'
    install_script_text = INSTALL_SCRIPT_TEMPLATE % {'application': APPLICATION, 'package': PACKAGE}
    install_script_path = ("%(target_dir)s/%(application)s/%(install_script)s" %
        {'target_dir': TARGET_DIR, 'application': APPLICATION, 'install_script': INSTALL_SCRIPT})
    write_install = """cat <<EOF > "%(install_script_path)s"
%(install_script_text)s
EOF
""" % {'install_script_path': install_script_path, 'install_script_text': install_script_text}

    shell(write_install)
    shell("chmod +x %(install_script_path)s" % {'install_script_path': install_script_path})

    print 'Building ZIP'
#     app_scripts = "%s-pyscripts" % APPLICATION
#     zipped_file = "%s-pyscripts-v%s.zip" % (APPLICATION, PYTHON_SCRIPT_VERSION)
    app_scripts = "%s-pyscripts-v%s" % (APPLICATION, PYTHON_SCRIPT_VERSION)
    zipped_file = "%s.zip" % app_scripts
    shell("mv %(target_dir)s/%(app)s %(target_dir)s/%(app_scripts)s" %
        {'app': APPLICATION, 'app_scripts': app_scripts, 'target_dir': TARGET_DIR})
    shell("cd %(target_dir)s; zip -qr %(zipped_file)s %(app_scripts)s/* --exclude *.DS_Store*" %
        {'app_scripts': app_scripts, 'target_dir': TARGET_DIR, 'zipped_file': zipped_file})

    print 'Completed building'

def startup_checks():
    if sys.version_info < (2, 7):
        raise Exception('Must use Python 2.7 or greater')

#
# Main function
#

def main():
    """ Main program entry point
    """

    try:
        startup_checks()
        build()
    except Exception, e:
        sys.stderr.write("Error: %s\n" % e)
        sys.exit(1)


if __name__ == '__main__':
    main()
