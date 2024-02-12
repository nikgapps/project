import xml.etree.ElementTree as eT


class StringArray:
    def __init__(self, name, values, comment=None, translatable=False):
        self.name = name
        self.values = values
        self.translatable = str(translatable).lower()
        self.comment = comment

    def to_xml(self):
        elem = eT.Element('string-array', name=self.name, translatable=self.translatable)
        for value in self.values:
            item = eT.SubElement(elem, 'item')
            item.text = value
        return elem, eT.Comment(self.comment) if self.comment else None
