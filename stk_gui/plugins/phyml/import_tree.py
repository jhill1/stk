from stk_gui.plugins import register_plugin, cb_decorator
import stk_gui.interface
from stk_gui import dialogs
import gtk
import os.path
import sys
import gobject
import stk.supertree_toolkit as stk

def plugin_applies(xpath):
    # Allow plugin to be used at any element which is under a source dataset
    return (xpath.endswith('/tree_data'))

@cb_decorator

def handle_click(xml, xpath, path=None):
    from lxml import etree

    xml_root = etree.fromstring(xml)

    if (path == None):
        path = os.getcwd()

    filter_names_and_patterns = {}
    filter_names_and_patterns['Newick file'] = "*.nwk"
    filter_names_and_patterns['Nexus file'] = "*.nex"
    filter_names_and_patterns['Nexus tree file'] = "*.tre"
   
    filename = dialogs.get_filename(title = "Choose tree file", action = gtk.FILE_CHOOSER_ACTION_OPEN, 
            filter_names_and_patterns = filter_names_and_patterns,
            folder_uri = path)

    if filename == None:
        return

    # Track back along xpath to find the source element where we're going to set the name
    element = xml_root.xpath(xpath)[0]
    while (element.tag != 'tree_data'):
        element = element.getparent()

    tree = stk.import_tree(filename)
    tree_string_tag = element[0]
    tree_string_tag.text = tree
    
    stk_gui.interface.plugin_xml = etree.tostring(xml_root)
    stk_gui.interface.pluginSender.emit('plugin_changed_xml')
    return

register_plugin(plugin_applies, "Import Tree", handle_click)