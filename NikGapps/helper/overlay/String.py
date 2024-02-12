import xml.etree.ElementTree as eT


class String:
    def __init__(self, name, value, comment=None, translatable=False):
        self.name = name
        self.value = value
        self.translatable = str(translatable).lower()
        self.comment = comment

    def to_xml(self):
        elem = eT.Element('string', name=self.name, translatable=self.translatable)
        elem.text = self.value
        return elem, eT.Comment(self.comment) if self.comment else None
