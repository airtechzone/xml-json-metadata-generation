# XML-JSON Conversion Metadata Generation

This tool generates, from a XSD file (**xsdFile**), two JSON files and one text file:

* **xsdFile-sequences.json**: all the sequences (identified by xpath) with their ordered list of elements;
* **xsdFile-singletons.json**: the xpaths of all elements with maxOccurs = 1 (explicitly or implicitly);
* **xsdFile-xpaths.txt**: flat list of all the xpaths.

Usage:
```
./metadataGeneration.py <xsdFile> [-v]
```
(`-v`: verbose/debug mode)

In order to prevent infinite loops, the tree exploration does not exceed a depth of 50.

Example of command (on Linux) to process all XSDs in a folder:
```
cd path_to_metadataGeneration
for xsd in path_to_xsd/*.xsd; do ./metadataGeneration.py "$xsd"; done 
cat *.xsd-sequences.json > sequences.json
cat *.xsd-singletons.json > singletons.json
```

Then simply replace `}{` by `,\n ` in **sequences.json**, and `][` by `,\n `in **singletons.json**.
