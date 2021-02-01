#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
csv_to_moodle_xml.py

Print out calculated questions in Moodle XML format from a csv file.
"""

import sys
import argparse
from lxml import etree
import codecs
from collections import OrderedDict

VERSION = '20.05.2'
CATEGORY = u'$system$/Ερώτηση από αρχείο XML'
# context
TITLE = 1
STATEMENT = 2
DUMMY = 3
VARIABLES = 4
MINIMUM = 5
MAXIMUM = 6
DISPLAY = 7
DISPLAY_TYPE = 8
TOLERANCE = 9
TOLERANCE_TYPE = 10
POINTS = 11
TAGS = 12
FORMULAS = 13
DATA = 0

def main(arguments):
    arguments.sync = int(arguments.sync)
    if not arguments.xmldestfile:
        filename, extension = arguments.csvsourcefile.split('.')
        arguments.xmldestfile = '%s.xml' % filename
    xquiz = etree.Element('quiz')
    xquiz.append(etree.Comment('   Category   '))
    xquestion = etree.SubElement(xquiz,'question')
    xquestion.set('type','category')
    xcategory = etree.SubElement(xquestion,'category')
    xtext = etree.SubElement(xcategory,'text')
    xtext.text = CATEGORY

    with codecs.open(arguments.csvsourcefile, encoding='UTF-8') as csv:
        context = TITLE
        for line in csv:
            line = line.rstrip()
            context %= 14

            if context == STATEMENT:
                if line == 'END':
                    context += 1
                    enonce = ' '.join(lignes_enonce)
                    xenonce = etree.SubElement(xquestion,'questiontext')
                    xenonce.set('format','html')
                    xtext = etree.SubElement(xenonce,'text')
                    xtext.text = etree.CDATA(enonce)
                    xgfeedback = etree.SubElement(xquestion,'generalfeedback')
                    xgfeedback.set('format','html')
                    xtext = etree.SubElement(xgfeedback,'text')
                    xtext.text = ''
                    xpenalty = etree.SubElement(xquestion,'penalty')
                    xpenalty.text = '0.3333333'
                    xhidden = etree.SubElement(xquestion,'hidden')
                    xhidden.text = '0'
                    xsynchro = etree.SubElement(xquestion,'synchronize')
                    xsynchro.text = '%s' % arguments.sync
                    xsingle = etree.SubElement(xquestion,'single')
                    xsingle.text = '0'
                    xnumbering = etree.SubElement(xquestion,'answernumbering')
                    xnumbering.text = 'abc'
                    xshuffle = etree.SubElement(xquestion,'shuffleanswers')
                    xshuffle.text = '1'
                    xcorrectfb = etree.SubElement(xquestion,'correctfeedback')
                    xtext = etree.SubElement(xcorrectfb,'text')
                    xtext.text = ''
                    xpcorrectfb = etree.SubElement(xquestion,'partiallycorrectfeedback')
                    xtext = etree.SubElement(xpcorrectfb,'text')
                    xtext.text = ''
                    xicorrectfb = etree.SubElement(xquestion,'incorrectfeedback')
                    xtext = etree.SubElement(xicorrectfb,'text')
                    xtext.text = ''
                    xanswer = etree.SubElement(xquestion,'answer')
                    xanswer.set('fraction','100')
                    xanswer.set('format','moodle_auto_format')
                    xfeedback = etree.SubElement(xanswer,'feedback')
                    xfeedback.set('format','html')
                    xtext = etree.SubElement(xfeedback,'text')
                    xtext.text = ''
                else:
                    lignes_enonce.append(line)
                continue

            if context == DUMMY:
                context += 1
                continue

            if context == VARIABLES:
                context += 1
                variables = line.split('\t')
                answer = variables[-1]
                valeurs = [[] for i in range(len(variables))]
                for i in range(len(variables)):
                    valeurs[i] = []
                continue

            if context == MINIMUM:
                context += 1
                minimum = line.split('\t')
                minimum = dict(zip(variables,minimum))
                continue

            if context == MAXIMUM:
                context += 1
                maximum = line.split('\t')
                maximum = dict(zip(variables,maximum))
                continue

            if context == DISPLAY:
                context += 1
                display = line.split('\t')
                display = dict(zip(variables,display))
                xanslength = etree.SubElement(xanswer,'correctanswerlength')
                xanslength.text = '%s' % display[answer]
                continue

            if context == DISPLAY_TYPE:
                context += 1
                display_type = line.split('\t')
                display_type = dict(zip(variables,display_type))
                xansform = etree.SubElement(xanswer,'correctanswerformat')
                xansform.text = '%s' % display_type[answer]
                xunitgradingtype = etree.SubElement(xquestion,'unitgradingtype')
                xunitgradingtype.text = '0'
                xunitpenalty = etree.SubElement(xquestion,'unitpenalty')
                xunitpenalty.text = '0.0000000'
                xshowunits = etree.SubElement(xquestion,'showunits')
                xshowunits.text = '3'
                xunitsleft = etree.SubElement(xquestion,'unitsleft')
                xunitsleft.text = '0'
                xddefs = etree.SubElement(xquestion,'dataset_definitions')
                continue

            if context == TOLERANCE:
                context += 1
                tolerance = line.split('\t')
                tolerance = dict(zip(variables,tolerance))
                xtext = etree.SubElement(xanswer,'text')
                xtext.text = u'{%s}' % answer
                xtolerance = etree.SubElement(xanswer,'tolerance')
                xtolerance.text = '%s' % tolerance[answer]
                continue

            if context == TOLERANCE_TYPE:
                context += 1
                toltype = line.split('\t')
                toltype = dict(zip(variables,toltype))
                xtoltype = etree.SubElement(xanswer,'tolerancetype')
                xtoltype.text = '%s' % toltype[answer] 
                continue

            if context == POINTS:
                context += 1
                nbpoints = line.split('\t')
                nbpoints = dict(zip(variables,nbpoints))
                xnbpoints = etree.SubElement(xquestion,'defaultgrade')
                xnbpoints.text = '%s' % nbpoints[answer]
                continue

            if context == TAGS:
                context += 1
                tags = line.split('\t')
                tags = dict(zip(variables,tags))
                tags = tags[answer].split(',')
                cleantags = list()
                for tag in tags:
                    if tag != '':
                        cleantags.append(tag)
                if cleantags:
                    xtags = etree.SubElement(xquestion,'tags')
                    for tag in cleantags:
                        xtag = etree.SubElement(xtags,'tag')
                        xtagtext = etree.SubElement(xtag,'text')
                        xtagtext.text = '%s' % tag
                continue

            if context == FORMULAS:
                context += 1
                continue

            if context == DATA:
                temp = line.split('\t')
                try:
                    foo = float(temp[0])
                    for i in range(len(valeurs)):
                        valeurs[i].append(temp[i])
                except ValueError:
                    context += 1
                    valeurs = OrderedDict(zip(variables,valeurs))
                    for key in valeurs:
                        if key.startswith('dummy'):
                            continue
                        xddef = etree.SubElement(xddefs,'dataset_definition')
                        xstatus = etree.SubElement(xddef,'status')
                        xtext = etree.SubElement(xstatus,'text')
                        if arguments.sync:
                            xtext.text = 'shared'
                        else:
                            xtext.text = 'private'
                        xname = etree.SubElement(xddef,'name')
                        xtext = etree.SubElement(xname,'text')
                        xtext.text = key
                        xtype = etree.SubElement(xddef,'type')
                        xtype.text = 'calculated'
                        xdist = etree.SubElement(xddef,'distribution')
                        xtext = etree.SubElement(xdist,'text')
                        xtext.text = 'uniform'
                        xmini = etree.SubElement(xddef,'minimum')
                        xtextmini = etree.SubElement(xmini,'text')
                        xmaxi = etree.SubElement(xddef,'maximum')
                        xtextmaxi = etree.SubElement(xmaxi,'text')
                        xdeci = etree.SubElement(xddef,'decimals')
                        xtextdeci = etree.SubElement(xdeci,'text')
                        xitemc = etree.SubElement(xddef,'itemcount')
                        xitemc.text = '%s' % len(valeurs[key])
                        xtextdeci.text = display[key]
                        xtextmini.text = minimum[key]
                        xtextmaxi.text = maximum[key]
                        xitems = etree.SubElement(xddef,'dataset_items')
                        for (i,item) in enumerate(valeurs[key]):
                            xitem = etree.SubElement(xitems,'dataset_item')
                            xnum = etree.SubElement(xitem,'number')
                            xnum.text = '%s' % str(i+1)
                            xvalue = etree.SubElement(xitem,'value')
                            xvalue.text = '%s' % item
                        xnumber = etree.SubElement(xddef,'number_of_items')
                        xnumber.text = '%s' % len(valeurs[key])

            if context == TITLE:
                context += 1
                xquiz.append(etree.Comment('   Question    '))
                xquestion = etree.SubElement(xquiz,'question')
                xname = etree.SubElement(xquestion,'name')
                xtext = etree.SubElement(xname,'text')
                xtext.text = line
                xquestion.set('type','calculated')
                lignes_enonce = []
                continue

    valeurs = OrderedDict(zip(variables,valeurs))
    for key in valeurs:
        if key.startswith('dummy'):
            continue
        xddef = etree.SubElement(xddefs,'dataset_definition')
        xstatus = etree.SubElement(xddef,'status')
        xtext = etree.SubElement(xstatus,'text')
        if arguments.sync:
            xtext.text = 'shared'
        else:
            xtext.text = 'private'
        xname = etree.SubElement(xddef,'name')
        xtext = etree.SubElement(xname,'text')
        xtext.text = key
        xtype = etree.SubElement(xddef,'type')
        xtype.text = 'calculated'
        xdist = etree.SubElement(xddef,'distribution')
        xtext = etree.SubElement(xdist,'text')
        xtext.text = 'uniform'
        xmini = etree.SubElement(xddef,'minimum')
        xtextmini = etree.SubElement(xmini,'text')
        xmaxi = etree.SubElement(xddef,'maximum')
        xtextmaxi = etree.SubElement(xmaxi,'text')
        xdeci = etree.SubElement(xddef,'decimals')
        xtextdeci = etree.SubElement(xdeci,'text')
        xitemc = etree.SubElement(xddef,'itemcount')
        xitemc.text = '%s' % len(valeurs[key])
        xtextdeci.text = display[key]
        xtextmini.text = minimum[key]
        xtextmaxi.text = maximum[key]
        xitems = etree.SubElement(xddef,'dataset_items')
        for (i,item) in enumerate(valeurs[key]):
            xitem = etree.SubElement(xitems,'dataset_item')
            xnum = etree.SubElement(xitem,'number')
            xnum.text = '%s' % str(i+1)
            xvalue = etree.SubElement(xitem,'value')
            xvalue.text = '%s' % item
        xnumber = etree.SubElement(xddef,'number_of_items')
        xnumber.text = '%s' % len(valeurs[key])

    xtree = etree.ElementTree(xquiz)
    xtree.write(arguments.xmldestfile,encoding='UTF-8',xml_declaration=True,pretty_print=arguments.pretty_print)
    return 0

if __name__ == "__main__":

    p = argparse.ArgumentParser(
        description="""
        Print out calculated questions in XML Moodle format from a csv file.

        Create the questions file in a spreadsheet. The Answer
        should be in the last column. After creating the random values with a
        formula, those should be copied as values to avoid regenarating them any
        time the file is opened. This is especially important for synced questions.

        Then export as text or csv or whatever your spreadsheet calls it with the
        following parameters:
        Separator: Tab,
        Quoting: Never,
        Character encoding: Unicode (UTF-8),
        locale: United States/English (C).

        Finally, run:
        $ python csv_to_moodle_xml.py yourfile.csv
        to generate yourfile.xml with default params.
        $ python csv_to_moodle_xml.py --help
        for options and parameters.
        """)
    p.add_argument('--version', action='version', version='%(prog)s v{0}'.format(VERSION))
    p.add_argument('-p', '--pretty-print', action='store_true',
                    help='pretty-print xml file (produces bigger files!)')
    p.add_argument('-s', '--sync', action='store_true',
                    help='synchronize variables along questions')
    p.add_argument('csvsourcefile',
                    help='name of csv source file')
    p.add_argument('xmldestfile', nargs='?',
                    help='name of xml destination file')
    arguments = p.parse_args()

    sys.exit(main(arguments))