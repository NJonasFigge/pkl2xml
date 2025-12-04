
from xml.dom import minidom
from typing import Iterable


def __make_child_or_attribute(key, val, parent: minidom.Element, doc: minidom.Document):
    """
    Adds a child node or attribute to parent element, according to input values
    :param key: name of child node or attribute
    :param val: contents of child node or attribute
    :param parent: element to append child nodes or attributes to
    :param doc: document in which the element is located
    :return: None (xml building happens inplace)
    """
    # - Wrap key to be valid tag or attribute name while conserving their actual type
    if isinstance(key, int):
        valid_key = 'int-' + str(key)
    elif isinstance(key, float):
        valid_key = 'float-' + str(key)
    elif isinstance(key, complex):
        valid_key = 'complex-' + str(key)
    else:
        # - Strings may not contain whitespace and forward slashes, so we replace them by underscores
        valid_key = str(key).replace(' ', '_').replace('/', '_')
    # - If val is a simple literal, add as attribute, else add as child element
    if isinstance(val, (int, float, complex, str)):
        parent.setAttribute(valid_key, str(val))
    else:
        e = doc.createElement(valid_key)
        __build_xml_recursively(val, e, doc)
        parent.appendChild(e)


def __build_xml_recursively(obj: object, element: minidom.Element, doc: minidom.Document):
    """
    Decides what to use for child notes with contents or attribute keys with values, respectively (calls
    __make_child_or_attribute on them, which will recursively call this function again)
    :param obj: object to parse
    :param element: element to append child nodes or attributes to (will be passed on to __make_child_or_attribute())
    :param doc: document in which the element is located (will be passed on to __make_child_or_attribute())
    :return: None (xml building happens inplace)
    """
    # - In case of call with a basic literal (only happens in recursion depth 0, if it's the only thing in the pkl file)
    if isinstance(obj, (int, float, complex, str)):
        # - Add a new child node with the object as string
        t = doc.createTextNode(str(obj))
        element.appendChild(t)
        # - XML is completed already, since "obj" was the only thing in the pkl file
        return
    # - In case obj is a dictionary
    if isinstance(obj, dict):
        # - Use dict keys and values for child node or attribute
        for key, val in obj.items():
            __make_child_or_attribute(key, val, element, doc)
    # - In case obj is a sequence (list, tuple, etc.) or any other iterable type (also objects that are made iterable), but no dicts
    elif isinstance(obj, Iterable):
        # - Use indices and contents for child node or attribute
        for idx, val in enumerate(obj):
            __make_child_or_attribute(idx, val, element, doc)
    # - In case obj is of any other type
    else:
        # - Use attribute names and values for child node or attribute, but exclude methods
        for key in obj.__dir__():
            val = obj.__getattribute__(key)
            if key.startswith('__') or callable(val):
                continue
            __make_child_or_attribute(key, val, element, doc)


def build_xml(obj: object):
    """Wraps the recursive building of an XML from any python object"""
    # - Initialize document, root tag will be <pkl/>
    doc: minidom.Document = minidom.parseString('<pkl/>')
    # - Start recursive XML building
    root = doc.documentElement
    __build_xml_recursively(obj, root, doc)
    # - Return the XML document
    return doc
