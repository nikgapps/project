from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
import xml.dom.minidom


class XmlOp:
    def __init__(self, package_name, permissions_list, import_path=None):
        self.root = Element("permissions")
        self.doc = SubElement(self.root, "privapp-permissions", package=package_name)
        for permission in permissions_list:
            SubElement(self.doc, "permission", name=permission)
        XmlOp.indent(self.root)
        if import_path is not None:
            with open(import_path, 'wb') as f:
                self.tree = ElementTree(self.root)
                self.tree.write(f)

    @staticmethod
    def indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                XmlOp.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def to_string(self):
        xml_str = tostring(self.root, 'utf-8')
        parsed_str = xml.dom.minidom.parseString(xml_str)
        pretty_str = parsed_str.toprettyxml(encoding="utf-8").decode("utf-8")
        pretty_str = "\n".join(
            line for line in pretty_str.splitlines() if line.strip() and not line.__contains__("utf-8"))
        pretty_str = pretty_str.replace("\r\n", "\n")  # Ensure LF line endings
        return pretty_str
