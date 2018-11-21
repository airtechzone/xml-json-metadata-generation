#!/usr/bin/python
# -*-coding:utf-8 -*

from lxml import etree
from sys import stderr, argv
from json import dumps


def getElement(name):
    global roots
    for el in roots:
        if ("element" in el.tag or "complexType" in el.tag) and el.attrib["name"] == name:
            return el
    return None


def getName(el):
    if "ref" in el.attrib:
        return el.attrib["ref"]
    else:
        return el.attrib["name"]


def printDebug(proc, line, xpath):
    global debug
    if debug:
        print(proc + ":\t" + str(line) + "\t" + xpath, file=stderr)


def processElement(el, prevxpath, refd=False):
    printDebug("element", el.sourceline, prevxpath)
    # infinite loop prevention
    if prevxpath.count("/") > 50:
        print("Infinite loop detected: " + prevxpath, file=stderr)
        return
    xpath = prevxpath + getName(el) + "/"
    # xpaths
    if xpath not in xpaths:
        xpaths.append(xpath[:-1])
    # singletons
    if not refd and ("maxOccurs" not in el.attrib or el.attrib["maxOccurs"] == "1"):
        singletons.append(xpath)
    # sequences
    if "ref" in el.attrib:
        processElement(getElement(el.attrib["ref"]), prevxpath, refd=True)
    elif "type" in el.attrib:
        ty = getElement(el.attrib["type"])
        if ty is not None:
            processComplexType(ty, xpath)
    else:
        for ch in el.getchildren():
            if "complexType" in ch.tag:
                processComplexType(ch, xpath)


def processComplexType(ty, xpath):
    printDebug("complexType", ty.sourceline, xpath)
    for ch in ty.getchildren():
        if "sequence" in ch.tag:
            processSequence(ch, xpath)
        elif "choice" in ch.tag:
            processChoice(ch, xpath)
        elif "complexContent" in ch.tag:
            processComplexContent(ch, xpath)


def processSequence(sq, xpath):
    printDebug("sequence", sq.sourceline, xpath)
    seq = []
    if xpath in sequences:
        seq = sequences[xpath]
    for el in sq.getchildren():
        if "element" in el.tag:
            seq.append(getName(el))
            processElement(el, xpath)
        elif "sequence" in el.tag:
            processSequence(el, xpath)
            seq.extend(sequences[xpath])
        elif "choice" in el.tag:
            processChoice(el, xpath)
            seq.extend(sequences[xpath])
    sequences[xpath] = seq


def processChoice(choice, xpath):
    printDebug("  choice", choice.sourceline, xpath)
    seq = []
    if xpath in sequences:
        seq = sequences[xpath]
    for el in choice.getchildren():
        if "element" in el.tag:
            seq.append(getName(el))
            processElement(el, xpath)
        elif "sequence" in el.tag:
            processSequence(el, xpath)
            seq.extend(sequences[xpath])
        elif "choice" in el.tag:
            processChoice(el, xpath)
            seq.extend(sequences[xpath])
    sequences[xpath] = seq


def processComplexContent(cc, xpath):
    printDebug("complexContent", cc.sourceline, xpath)
    for ch in cc.getchildren():
        if "extension" in ch.tag:
            processExtension(ch, xpath)


def processExtension(ex, xpath):
    printDebug("extension", ex.sourceline, xpath)
    processComplexType(getElement(ex.attrib["base"]), xpath)
    for ch in ex.getchildren():
        if "sequence" in ch.tag:
            processSequence(ch, xpath)
        elif "choice" in ch.tag:
            processChoice(ch, xpath)


if __name__ == "__main__":
    debug = False
    print("Note: the xsd file has to be named as the root node of the message (e.g. AirShoppingRQ.xsd)", file=stderr)
    if len(argv) == 3:
        if argv[2] == "-v":
            debug = True
        else:
            print("Usage: ./metadataGeneration.py <xsd_file> [-v]")
    if len(argv) in [2, 3]:
        print("Processing", argv[1])
        parser = etree.XMLParser(ns_clean=True, remove_comments=True)
        xsd = etree.parse(argv[1], parser)
        roots = xsd.getroot().getchildren()
        msgRoot = getElement(argv[1].split("/")[-1].replace(".xsd", "")) #roots[0]
        sequences = {}
        singletons = []
        xpaths = []
        processElement(msgRoot, '')
        with open(argv[1]+"-sequences.json", 'w') as f:
            f.write(dumps(sequences).replace("],","],\n"))
        with open(argv[1]+"-singletons.json", 'w') as f:
            f.write(dumps(singletons).replace(",",",\n"))
        with open(argv[1]+"-xpaths.txt", 'w') as f:
            f.write('\n'.join(xpaths))
    else:
        print("Usage: .metadataGeneration.py <xsd_file> [-v]")
