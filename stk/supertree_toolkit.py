#!/usr/bin/env python
#
#    Supertree Toolkit. Software for managing and manipulating sources
#    trees ready for supretree construction.
#    Copyright (C) 2011, Jon Hill, Katie Davis
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Jon Hill. jon.hill@imperial.ac.uk. 
from Bio import Phylo
from StringIO import StringIO
import os
import sys
import math
import re
import numpy 
from lxml import etree
import yapbib.biblist as biblist
import string
from stk_exceptions import *
import traceback
from cStringIO import StringIO
 
# supertree_toolkit is the backend for the STK. Loaded by both the GUI and
# CLI, this contains all the functions to actually *do* something
#
# All functions take XML and a list of other arguments, process the data and return
# it back to the user interface handler to save it somewhere

def create_name(authors, year):
    """ From a list of authors and a year construct a sensible
    source name.
    Input: authors - list of last (family, sur) names (string)
           year - the year (string)
    Output: source_name - (string)"""

    source_name = None
    if (len(authors) == 1):
        # single name: name_year
        source_name = authors[0] + "_" + year
    elif (len(authors) == 2):
        source_name = authors[0] + "_" + authors[1] + "_" + year
    else:
        source_name = authors[0] + "_etal_" + year

    return source_name


def single_sourcename(XML):
    """ Create a sensible source name based on the 
    bibliographic data.
    xml_root should contain the xml_root etree for the source that is to be
    altered only"""

    xml_root = etree.fromstring(XML)

    find = etree.XPath("//authors")
    authors_ele = find(xml_root)[0]
    authors = []
    for ele in authors_ele.iter():
        if (ele.tag == "surname"):
            authors.append(ele.xpath('string_value')[0].text)
    
    find = etree.XPath("//year/integer_value")
    year = find(xml_root)[0].text
    source_name = create_name(authors, year)

    attributes = xml_root.attrib
    attributes["name"] = source_name

    XML = etree.tostring(xml_root,pretty_print=True)

    # Return the XML stub with the correct name
    return XML

def all_sourcenames(XML):
    """
    Create a sensible sourcename for all sources in the current
    dataset. 
    """

    xml_root = etree.fromstring(XML)

    # Find all "source" trees
    sources = []
    for ele in xml_root.iter():
        if (ele.tag == "source"):
            sources.append(ele)

    for s in sources:
        xml_snippet = etree.tostring(s,pretty_print=True)
        xml_snippet = single_sourcename(xml_snippet)
        parent = s.getparent()
        ele_T = etree.fromstring(xml_snippet)
        parent.replace(s,ele_T)

    XML = etree.tostring(xml_root,pretty_print=True)
    # gah: the replacement has got rid of line breaks for some reason
    XML = string.replace(XML,"</source><source ", "</source>\n    <source ")
    XML = string.replace(XML,"</source></sources", "</source>\n  </sources")    
    return XML

def import_bibliography(XML, bibfile):    
    
    # Out bibliography parser
    b = biblist.BibList()

    xml_root = etree.fromstring(XML)
    
    # Track back along xpath to find the sources where we're about to add a new source
    sources = xml_root.xpath('sources')[0]
    sources.tail="\n      "
    if (bibfile == None):
        raise BibImportError("Error importing bib file. There was an error with the file")

    try: 
        b.import_bibtex(bibfile)
    except UnboundLocalError:
        # This seems to be raised if the authors aren't formatted correctly
        raise BibImportError("Error importing bib file. Check all your authors for correct format")
    except AttributeError:
        # This seems to occur if the keys are not set for the entry
        raise BibImportError("Error importing bib file. Check all your entry keys")
    except: 
        raise BibImportError("Error importing bibliography") 

    items= b.sortedList[:]

    for entry in items:
        # for each bibliographic entry, create the XML stub and
        # add it to the main XML
        it= b.get_item(entry)
        xml_snippet = it.to_xml()
        if xml_snippet != None:
            # turn this into an etree
            publication = etree.fromstring(xml_snippet)
            # create top of source
            source = etree.Element("source")
            # now attach our publication
            source.append(publication)
            new_source = single_sourcename(etree.tostring(source,pretty_print=True))
            source = etree.fromstring(new_source)

            # now create tail of source
            s_tree = etree.SubElement(source, "source_tree")
            s_tree.tail="\n      "
           
            characters = etree.SubElement(s_tree,"character_data")
            c_data = etree.SubElement(characters,"character")
            analyses = etree.SubElement(s_tree,"analyses_used")
            a_data = etree.SubElement(analyses,"analysis")
            tree = etree.SubElement(s_tree,"tree_data")
            tree_string = etree.SubElement(tree,"string_value")

            source.tail="\n      "

            # append our new source to the main tree
            sources.append(source)
        else:
            raise BibImportError("Error with one of the entries in the bib file")

    # do we have any empty (define empty?) sources? - i.e. has the user
    # added a source, but not yet filled it in?
    # I think the best way of telling an empty source is to check all the
    # authors, title, tree, etc and checking if they are empty tags
    # Find all "source" trees
    sources = []
    for ele in xml_root.iter():
        if (ele.tag == "source"):
            sources.append(ele)

    for s in sources:
        xml_snippet = etree.tostring(s,pretty_print=True)
        if ('<string_value lines="1"/>' in xml_snippet and\
            '<integer_value rank="0"/>' in xml_snippet):

            parent = s.getparent()
            parent.remove(s)

    # sort sources in alphabetical order
    XML = etree.tostring(xml_root,pretty_print=True)
    
    return XML

def import_tree(filename, gui=None, tree_no = -1):
    """Takes a NEXUS formatted file and returns a list containing the tree
    strings"""
  
# Need to add checks on the file. Problems include:
# TreeView (Page, 1996):
# TreeView create a tree with the following description:
#
#   UTREE * tree_1 = ((1,(2,(3,(4,5)))),(6,7));
# UTREE * is not a supported part of the NEXUS format (as far as BioPython).
# so we need to replace the above with:
#   tree_1 = [&u] ((1,(2,(3,(4,5)))),(6,7));
#
# BioPython doesn throw an exception or anything on these files,
# So for now glob the file, replace the text, and create a StringIO 
# object to pass BioPython - MESSY!!
    f = open(filename)
    content = f.read()                 # read entire file into memory
    f.close()
    treename = m = re.search(r'\UTREE\s?\*\s?(.+)\s?=\s', content)
    treedata = re.sub("\UTREE\s?\*\s?(.+)\s?=\s","tree "+m.group(1)+" = [&u] ", content)
    handle = StringIO(treedata)
    
    if (filename.endswith(".nex") or filename.endswith(".tre")):
        trees = list(Phylo.parse(handle, "nexus"))
    elif (filename.endswith("nwk")):
        trees = list(Phylo.parse(handle, "newick"))
    elif (filename.endswith("phyloxml")):
        trees = list(Phylo.parse(handle, "phyloxml"))

    if (len(trees) > 1 and tree_no == -1):
        message = "Found "+len(trees)+" trees. Which one do you want to load (1-"+len(trees)+"?"
        if (gui==None):
            tree_no = raw_input(message)
            # assume the user counts from 1 to n
            tree_no -= 1
        else:
            #base this on a message dialog
            dialog = gtk.MessageDialog(
		        None,
		        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
		        gtk.MESSAGE_QUESTION,
		        gtk.BUTTONS_OK,
		        None)
            dialog.set_markup(message)
            #create the text input field
            entry = gtk.Entry()
            #allow the user to press enter to do ok
            entry.connect("activate", responseToDialog, dialog, gtk.RESPONSE_OK)
            #create a horizontal box to pack the entry and a label
            hbox = gtk.HBox()
            hbox.pack_start(gtk.Label("Tree number:"), False, 5, 5)
            hbox.pack_end(entry)
            #add it and show it
            dialog.vbox.pack_end(hbox, True, True, 0)
            dialog.show_all()
            #go go go
            dialog.run()
            text = entry.get_text()
            dialog.destroy()
            tree_no = int(text) - 1
    else:
        tree_no = 0

    h = StringIO()
    Phylo.write(trees[tree_no], h, "newick")
    tree = h.getvalue()

    return tree

def draw_tree(tree_string):
    
    h = StringIO(tree_string)
    tree = Phylo.read(h, 'newick')
    tree.ladderize()   # Flip branches so deeper clades are displayed at top
    Phylo.draw(tree)


def obtain_trees(XML):
    """ Parse the XML and obtain all tree strings
    Output: distionay of tree strings, with key indicating treename (unique)
    """

    xml_root = etree.fromstring(XML)
    
    # loop through all sources
        # for each source, get source name
        # loop through trees
        # append to dictionary, with source_name_tree_no = tree_string


    return #trees




################ PRIVATE FUNCTIONS ########################


