import os
import xml.etree.ElementTree as eT


class Resources:
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def to_xml(self):
        root = eT.Element('resources')
        root.attrib['xmlns:xliff'] = "urn:oasis:names:tc:xliff:document:1.2"
        for item in self.items:
            item_element, item_comment = item.to_xml()
            if item_comment is not None:
                root.append(item_comment)
            root.append(item_element)
        return eT.ElementTree(root)

    def indent(self, elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def write(self, directory, filename):
        if not os.path.exists(directory):
            os.makedirs(directory)
        root = self.to_xml().getroot()
        self.indent(root)
        eT.ElementTree(root).write(os.path.join(directory, filename),
                                   encoding="utf-8",
                                   xml_declaration=True)
