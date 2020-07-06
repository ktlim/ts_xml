import xml.etree.ElementTree as ET
from lsst.ts.xml import testutils
import pathlib


def main():
    pathlib.Path("sal_interfaces").mkdir(parents=True, exist_ok=True)
    f = open(pathlib.Path("sal_interfaces/index.rst"), "w")
    f.write("==============\n")
    f.write("SAL Interfaces\n")
    f.write("==============\n")
    f.write("\n")
    f.write(".. note:: This page is generated by the following python script ``generate_cet.py``.\n\n")
    f.write("This page provides an html display of the SAL Interfaces for the CSCs.\n"
            "After the index of the individual CSCs, you will find the generic commands and events.\n\n")
    f.write(".. toctree::\n  :glob:\n  :maxdepth: 1\n\n  *\n\n")
    for subsystem in testutils.subsystems:
        pathlib.Path("sal_interfaces").mkdir(parents=True, exist_ok=True)
        cf = open(pathlib.Path(f"sal_interfaces/{subsystem}.rst"), "w")
        cf.write(f"{'='*len(subsystem)}\n")
        cf.write(f"{subsystem}\n")
        cf.write(f"{'='*len(subsystem)}\n")
        for dds_type in ["Commands", "Events", "Telemetry"]:
            try:
                tree = ET.parse(f"../sal_interfaces/{subsystem}/{subsystem}_{dds_type}.xml")
            except FileNotFoundError:
                break
            cf.write(f"{dds_type}\n")
            cf.write(f"{'-'*len(dds_type)}\n")
            root = tree.getroot()
            for topic in root:
                if topic.tag == "Enumeration":
                    states = topic.text.split(',')
                    for state in states:
                        cf.write(f"* {state}\n")
                    cf.write("\n")
                    continue

                
                topic_name = topic.find('EFDB_Topic').text
                if dds_type in ["Commands", "Events"]:
                    short_name = topic_name.split("_", 2)[-1]
                else:
                    short_name = topic_name.split("_", 1)[-1]
                cf.write(f".. _{subsystem}:{dds_type}:{short_name}:\n\n")
                cf.write(f"{short_name}\n")
                cf.write(f"{'~'*len(short_name)}\n")
                if topic.find('Description') is not None:
                    cf.write("**Description**: ")
                    cf.write(f"{topic.find('Description').text}\n")
                    cf.write("\n")
                for field in topic:
                    if field.tag == "item":
                        cf.write("\n")
                        cf.write(f".. _{subsystem}:{dds_type}:{short_name}:{field.find('EFDB_Name').text}:\n\n")
                        cf.write(f"{field.find('EFDB_Name').text}\n")
                        cf.write(f"{'*'*len(field.find('EFDB_Name').text)}\n")
                        for attribute in field:
                            if attribute.tag in ["EFDB_Name", "Description"]:
                                pass
                            else:
                                cf.write(f":{attribute.tag}: {attribute.text}\n")
                        cf.write("\n")
                        cf.write("**Description**: ")
                        cf.write(f"{field.find('Description').text}\n")
                        cf.write("\n")
                    elif field.tag in ["Alias", "Description", "Device", "Property", "Action", "Value"]:
                        pass
                    else:
                        cf.write(f":{field.tag}: {field.text}\n")
                    cf.write("\n")
    gen_tree = ET.parse("../sal_interfaces/SALGenerics.xml")
    gen_root = gen_tree.getroot()
    f.write("Generics\n")
    f.write("========\n")
    for gen_set in gen_root:
        for gen_topic in gen_set:
            topic_name = gen_topic.find('EFDB_Topic').text
            short_name = topic_name.split("_")[-1]
            f.write(f"{short_name}\n")
            f.write(f"{'-'*len(short_name)}\n")
            if gen_topic.find('Description') is not None:
                f.write("**Description**: ")
                f.write(f"{gen_topic.find('Description').text}\n")
                f.write("\n")
            for gen_field in gen_topic:
                if gen_field.tag == "item":
                    f.write("\n")
                    f.write(f".. _{short_name}:{gen_field.find('EFDB_Name').text}:\n\n")
                    f.write(f"{gen_field.find('EFDB_Name').text}\n")
                    f.write(f"{'~'*len(gen_field.find('EFDB_Name').text)}\n")
                    for gen_attribute in gen_field:
                        if gen_attribute.tag in ["EFDB_Name", "Description"]:
                            pass
                        else:
                            f.write(f":{gen_attribute.tag}: {gen_attribute.text}\n")
                    f.write("\n")
                    f.write("**Description**: ")
                    f.write(f"{gen_field.find('Description').text}\n")
                    f.write("\n")
                elif gen_field.tag in ["Description", "Alias", "Device", "Property", "Action", "Value"]:
                    pass
                else:
                    f.write(f":{gen_field.tag}: {gen_field.text}\n")
                f.write("\n")


if __name__ == "__main__":
    main()
