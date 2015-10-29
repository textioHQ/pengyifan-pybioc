# -*- coding: utf-8 -*-

"""
Data structures and code to read/write BioC XML.
"""

__author__ = 'Yifan Peng'

import time

import lxml.etree as ET
from lxml.etree import tostring


class BioCNode:
    """
    The annotations and/or other relations in the relation.
    """

    def __init__(self, refid, role):
        """
        :param refid: the id of an annotated object or another relation
        :type refid: str
        :param role: the role of how the referenced annotation or other relation participates in the current relation
        :type role: str
        """
        self.refid = refid
        self.role = role

    def __str__(self):
        return 'BioCNode[refid=%s,role=%s]' % (self.refid, self.role)


class BioCLocation:
    """
    The connection to the original text can be made through the offset and length fields.
    """

    def __init__(self, offset, length):
        """
        :param offset: the offset of annotation
        :type offset: int
        :param length: the length of the annotated text
        :type length: int
        """
        self.offset = offset
        self.length = length

    def __str__(self):
        return 'BioCLocation[offset=%s,length=%s]' % (self.offset, self.length)


class BioCAnnotation:
    """
    Stand off annotation.
    """

    def __init__(self):
        self.infons = dict()
        self.locations = list()
        self.id = ''
        self.text = ''

    def add_location(self, location):
        """
        Adds the location at the specified position in this annotation.

        :param location: The location at the specified position in this annotation
        :type location: BioCLocation
        """
        self.locations.append(location)

    def __str__(self):
        s = 'BioCAnnotation['
        s += 'id=%s,' % self.id
        s += 'text=%s,' % self.text
        s += 'infons=[%s],' % ','.join('%s=%s' % (k, v) for (k, v) in self.infons.items())
        s += 'locations=[%s],' % ','.join(str(l) for l in self.locations)
        s += ']'
        return s


class BioCRelation:
    """
    Relationship between multiple BioCAnnotations and possibly other BioCRelations
    """

    def __init__(self):
        self.id = ''
        self.infons = dict()
        self.nodes = set()

    def __str__(self):
        s = 'BioCRelation['
        s += 'id=%s,' % self.id
        s += 'infons=[%s],' % ','.join('%s=%s' % (k, v) for (k, v) in self.infons.items())
        s += 'nodes=[%s],' % ','.join(str(n) for n in self.nodes)
        s += ']'
        return s

    def add_node(self, node):
        """
        Add the node to this relation

        :param node: node to be added to this relation
        :type node: BioCNode
        """
        self.nodes.add(node)


class BioCSentence:
    """
    One sentence in a {@link BioCPassage}.

    It may contain the original text of the sentence or it might be BioCAnnotations and possibly
    BioCRelations on the text of the passage.

    There is no code to keep those possibilities mutually exclusive. However the currently available
    DTDs only describe the listed possibilities.
    """

    def __init__(self):
        self.offset = -1
        self.text = ''
        self.infons = dict()
        self.annotations = list()
        self.relations = list()

    def __str__(self):
        s = 'BioCSentence['
        s += 'offset=%s,' % self.offset
        s += 'text=%s,' % self.text
        s += 'infons=[%s],' % ','.join('%s=%s' % (k, v) for (k, v) in self.infons.items())
        s += 'annotations=[%s],' % ','.join(str(a) for a in self.annotations)
        s += 'relations=[%s],' % ','.join(str(r) for r in self.relations)
        s += ']'
        return s

    def clear_infons(self):
        """
        Clears all information.
        """
        self.infons.clear()

    def clear_annotations(self):
        """
        Clears all annotations.
        """
        del self.annotations[:]

    def clear_relations(self):
        """
        Clears all relations.
        """
        del self.relations[:]

    def add_annotation(self, annotation):
        """
        Adds annotation in this sentence.

        :param annotation: annotation
        :type annotation: BioCAnnotation
        """
        self.annotations.append(annotation)

    def add_relation(self, relation):
        """
        Adds relation in this sentence.

        :param relation: relation
        :type relation: BioCRelation
        """
        self.relations.append(relation)


class BioCPassage:
    """
    One passage in a BioCDocument.

    This might be the text in the passage and possibly BioCAnnotations over that text. It could be
    the BioCSentences in the passage. In either case it might include BioCRelations over annotations
    on the passage.
    """

    def __init__(self):
        self.offset = -1
        self.text = ''
        self.infons = dict()
        self.sentences = list()
        self.annotations = list()
        self.relations = list()

    def __str__(self):
        s = 'BioCPassage['
        s += 'offset=%s,' % self.offset
        if self.text is not None:
            s += 'text=%s,' % self.text
        s += 'infons=[%s],' % ','.join('%s=%s' % (k, v) for (k, v) in self.infons.items())
        s += 'sentences=[%s],' % ','.join(str(s) for s in self.sentences)
        s += 'annotations=[%s],' % ','.join(str(a) for a in self.annotations)
        s += 'relations=[%s],' % ','.join(str(r) for r in self.relations)
        s += ']'
        return s

    def add_sentence(self, sentence):
        """
        Adds sentence in this passage.

        :param sentence: sentence
        :type sentence: BioCSentence
        """
        self.sentences.append(sentence)

    def add_annotation(self, annotation):
        """
        Adds annotation in this passage.

        :param annotation: annotation
        :type annotation: BioCAnnotation
        """
        self.annotations.append(annotation)

    def add_relation(self, relation):
        """
        Adds relation in this passage.

        :param relation: relation
        :type relation: BioCRelation
        """
        self.relations.append(relation)


class BioCDocument:
    """
    One document in the BioCCollection.

    An id, typically from the original corpus, identifies the particular document. It includes
    BioCPassages in the document and possibly BioCRelations over annotations on the document.
    """

    def __init__(self):
        self.id = ''
        self.infons = dict()
        self.passages = list()
        self.annotations = list()
        self.relations = list()

    def __str__(self):
        s = 'BioCDocument['
        s += 'id=%s,' % self.id
        s += 'infons=[%s],' % ','.join('%s=%s' % (k, v) for (k, v) in self.infons.items())
        s += 'passages=[%s],' % ','.join(str(p) for p in self.passages)
        s += 'annotations=[%s],' % ','.join(str(a) for a in self.annotations)
        s += 'relations=[%s],' % ','.join(str(r) for r in self.relations)
        s += ']'
        return s

    def add_passage(self, passage):
        """
        Adds passage in this document.

        :param passage: passage
        :type passage: BioCPassage
        """
        self.passages.append(passage)

    def add_annotation(self, annotation):
        """
        Adds annotation in this document.

        :param annotation: annotation
        :type annotation: BioCAnnotation
        """
        self.annotations.append(annotation)

    def add_relation(self, relation):
        """
        Adds relation in this document.

        :param relation: relation
        :type relation: BioCRelation
        """
        self.relations.append(relation)


class BioCCollection:
    """
    Collection of documents.

    Collection of documents for a project. They may be an entire corpus or some portion of a corpus.
    Fields are provided to describe the collection.

    Documents may appear empty if doing document at a time IO.
    """

    def __init__(self):
        self.encoding = 'utf-8'
        self.version = '1.0'
        self.standalone = True

        self.source = ''
        self.date = time.strftime("%Y-%m-%d")
        self.key = ''

        self.infons = dict()
        self.documents = list()

    def add_document(self, document):
        """
        Adds document in this collection.

        :param document: document
        :type document: BioCDocument
        """
        self.documents.append(document)

    def clear_infons(self):
        """
        Clears all information.
        """
        self.infons.clear()

    def __str__(self):
        s = 'BioCCollection['
        s += 'source=%s,' % self.source
        s += 'date=%s,' % self.date
        s += 'key=%s,' % self.key
        s += 'infons=[%s],' % ','.join('%s=%s' % (k, v) for (k, v) in self.infons.items())
        s += 'documents=[%s],' % ','.join(str(d) for d in self.documents)
        s += ']'
        return s


def read_bioc(filename):
    """
    Reads the entire BioC file into one collection.

    :param filename: the name of the file to read from
    :type filename: str
    :return: BioC collection
    :rtype: BioCCollection
    """
    tree = ET.parse(filename)
    collection = __read_collection(tree.getroot())
    collection.encoding = tree.docinfo.encoding
    collection.standalone = tree.docinfo.standalone
    collection.version = tree.docinfo.xml_version
    return collection


def __read_collection(ctree):
    collection = BioCCollection()
    collection.source = ctree.findtext('source')
    collection.date = ctree.findtext('date')
    collection.key = ctree.findtext('key')
    collection.infons = __read_infons(ctree)

    for dtree in ctree.findall('document'):
        collection.add_document(__read_document(dtree))

    return collection


def __read_document(dtree):
    document = BioCDocument()
    document.id = dtree.findtext('id')

    for ptree in dtree.findall('passage'):
        document.add_passage(__read_passage(ptree))

    for atree in dtree.findall('annotation'):
        document.add_annotation(__read_annotation(atree))

    for rtree in dtree.findall('relation'):
        document.add_relation(__read_relation(rtree))
    return document


def __read_passage(ptree):
    passage = BioCPassage()
    passage.offset = int(ptree.findtext('offset'))
    passage.infons = __read_infons(ptree)
    if ptree.find('text') is not None:
        passage.text = ptree.findtext('text')

    for stree in ptree.findall('sentence'):
        passage.add_sentence(__read_sentence(stree))

    for atree in ptree.findall('annotation'):
        passage.add_annotation(__read_annotation(atree))

    for rtree in ptree.findall('relation'):
        passage.add_relation(__read_relation(rtree))

    return passage


def __read_sentence(stree):
    sentence = BioCSentence()
    sentence.offset = int(stree.findtext('offset'))
    sentence.text = stree.findtext('text')
    sentence.infons = __read_infons(stree)

    for atree in stree.findall('annotation'):
        sentence.add_annotation(__read_annotation(atree))

    for rtree in stree.findall('relation'):
        sentence.add_relation(__read_relation(rtree))

    return sentence


def __read_annotation(atree):
    annotation = BioCAnnotation()
    annotation.id = atree.attrib['id']
    annotation.infons = __read_infons(atree)
    annotation.text = atree.findtext('text')
    for ltree in atree.findall('location'):
        annotation.add_location(
            BioCLocation(int(ltree.attrib['offset']), int(ltree.attrib['length'])))
    return annotation


def __read_relation(rtree):
    relation = BioCRelation()
    if 'id' in rtree.attrib:
        relation.id = rtree.attrib['id']

    relation.infons = __read_infons(rtree)
    for ntree in rtree.findall('node'):
        relation.add_node(BioCNode(ntree.attrib['refid'], ntree.attrib['role']))

    return relation


def __read_infons(tree):
    infons = dict()
    for infon_xml in tree.findall('infon'):
        infons[infon_xml.attrib['key']] = infon_xml.text
    return infons


def write_bioc(filename, collection):
    """
    Writes the entire collection into BioC file.

    :param filename: the name of the file to write to
    :type filename: str
    :param collection: the BioC collection
    :type collection: BioCCollection
    """
    doc = ET.ElementTree(__write_collection(collection))
    f = open(filename, 'w')
    f.write(tostring(doc, pretty_print=True, encoding=collection.encoding,
                     standalone=collection.standalone))
    f.close()


def __write_collection(collection):
    ctree = ET.Element('collection')
    ET.SubElement(ctree, 'source').text = collection.source
    ET.SubElement(ctree, 'date').text = collection.date
    ET.SubElement(ctree, 'key').text = collection.key
    __write_infons(ctree, collection.infons)

    for d in collection.documents:
        __write_document(ET.SubElement(ctree, 'document'), d)

    return ctree


def __write_document(dtree, document):
    ET.SubElement(dtree, 'id').text = document.id
    __write_infons(dtree, document.infons)

    for p in document.passages:
        __write_passage(ET.SubElement(dtree, 'passage'), p)
    for a in document.annotations:
        __write_annotation(dtree, a)
    for r in document.relations:
        __write_relation(dtree, r)


def __write_passage(ptree, passage):
    __write_infons(ptree, passage.infons)
    ET.SubElement(ptree, 'offset').text = str(passage.offset)
    if passage.text is not None:
        ET.SubElement(ptree, 'text').text = passage.text
    for s in passage.sentences:
        __write_sentence(ET.SubElement(ptree, 'sentence'), s)
    for a in passage.annotations:
        __write_annotation(ptree, a)
    for r in passage.relations:
        __write_relation(ptree, r)


def __write_sentence(stree, sentence):
    __write_infons(stree, sentence.infons)
    ET.SubElement(stree, 'offset').text = str(sentence.offset)
    if sentence.text is not None:
        ET.SubElement(stree, 'text').text = sentence.text
    for a in sentence.annotations:
        __write_annotation(stree, a)
    for r in sentence.relations:
        __write_relation(stree, r)


def __write_annotation(tree, annotation):
    atree = ET.SubElement(tree, 'annotation', {'id': annotation.id})
    __write_infons(atree, annotation.infons)
    for l in annotation.locations:
        ET.SubElement(atree, 'location', {'offset': str(l.offset), 'length': str(l.length)})
    ET.SubElement(atree, 'text').text = annotation.text


def __write_relation(tree, relation):
    rtree = ET.SubElement(tree, 'relation', {'id': relation.id})
    __write_infons(rtree, relation.infons)
    for n in relation.nodes:
        ET.SubElement(rtree, 'node', {'refid': n.refid, 'role': n.role})


def __write_infons(tree, infons):
    for k, v in infons.items():
        ET.SubElement(tree, 'infon', {'key': k}).text = v