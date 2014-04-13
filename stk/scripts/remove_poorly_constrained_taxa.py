#!/usr/bin/env python
import argparse
import os
import sys
stk_path = os.path.join( os.path.realpath(os.path.dirname(__file__)), os.pardir )
sys.path.insert(0, stk_path)
import supertree_toolkit as stk
from lxml import etree


def main():

    # do stuff
    parser = argparse.ArgumentParser(
         prog="convert tree from specific to generic",
         description="""Converts a tree at specific level to generic level""",
         )
    parser.add_argument(
            '-v', 
            '--verbose', 
            action='store_true', 
            help="Verbose output: mainly progress reports.",
            default=False
            )
    parser.add_argument(
            '--delete_list', 
            help="Produce a deleted taxa list. Give filename."
            )
    parser.add_argument(
            'input_phyml', 
            metavar='input_phyml',
            nargs=1,
            help="Your input phyml"
            )
    parser.add_argument(
            'input_tree', 
            metavar='input_tree',
            nargs=1,
            help="Your tree"
            )
    parser.add_argument(
            'output_tree', 
            metavar='output_tree',
            nargs=1,
            help="Your output tree"
            )


    args = parser.parse_args()
    verbose = args.verbose
    delete_list_file = args.delete_list
    if (delete_list_file == None):
        dl = False
    else:
        dl = True
    input_tree = args.input_tree[0]
    output_tree = args.output_tree[0]
    input_phyml = args.input_phyml[0]

    XML = stk.load_phyml(input_phyml)
    # load tree
    supertree = stk.import_tree(input_tree)
    # grab taxa
    taxa = stk._getTaxaFromNewick(supertree)
    delete_list = []

    # loop over taxa in supertree and get some stats
    for t in taxa:
        #print "Looking at "+t
        nTrees = 0
        nResolved = 0
        nPoly = 0

        # search each source tree
        xml_root = stk._parse_xml(XML)
        # By getting source, we can then loop over each source_tree
        find = etree.XPath("//source")
        sources = find(xml_root)
        # loop through all sources
        for s in sources:
            # for each source, get source name
            name = s.attrib['name']
            for tr in s.xpath("source_tree/tree/tree_string"):
                tree = tr.xpath("string_value")[0].text
                current_taxa = stk._getTaxaFromNewick(tree)
                # if tree contains taxa
                if (t in current_taxa):
                    nTrees += 1
                    tree_obj = stk._parse_tree(tree,fixDuplicateTaxa=True)
                    siblings = stk._get_all_siblings(tree_obj.node(t))
                    
                    # check where it occurs - polytomies only?
                    if (len(siblings) > 3): #2?
                        nPoly += 1
                    else:
                        nResolved += 1

        # record stats for this taxon and decide if to delete it
        if (nPoly == nTrees ):#or # all in polytomies
           #  (nResolved == 1 and (nPoly+nResolved)==nTrees) # only 1 resolved and rest (if any) polytomies
           #):
            delete_list.append(t)

    print "Taxa: "+str(len(taxa))
    print "Deleting: "+str(len(delete_list))
    # done, so delete the problem taxa from the supertree
    for t in delete_list:
        #print "Deleting "+t
        # remove taxa from supertree
        supertree = stk._sub_taxa_in_tree(supertree,t)

    # save supertree
    tree = {}
    tree['Tree_1'] = supertree
    output = stk._amalgamate_trees(tree,format='nexus')
    # write file
    f = open(output_tree,"w")
    f.write(output)
    f.close()

    if (dl):
        # write file
        delete_list.sort()
        f = open(delete_list_file,"w")
        string = '\n'.join(delete_list)
        f.write(string)
        f.close()

if __name__ == "__main__":
    main()