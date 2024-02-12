import xml.etree.ElementTree as eT


class Bool:
    def __init__(self, name, value, comment=None):
        self.name = name
        self.value = str(value).lower()
        self.comment = comment

    def to_xml(self):
        elem = eT.Element('bool', name=self.name)
        elem.text = self.value
        return elem, eT.Comment(self.comment) if self.comment else None
