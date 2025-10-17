# Copyright (c) 2025 iFLYTEK CO.,LTD.
# SPDX-License-Identifier: Apache 2.0 License
import re


def extract_xml_content(xml_str: str, tag: str) -> list[str]:
    """
    Extract content from strings containing<xml>tags

    Parameters:
        xml_str: A string containing<xml>tags
        tag: Tags in XML
    return:
        If the content within the tag is not found, return None
    """

    matches = re\
        .compile(rf'<{tag}>(.*?)</{tag}>', re.DOTALL | re.IGNORECASE)\
        .findall(xml_str)
    if matches:
        return [match.strip() for match in matches]
    return None


if __name__ == '__main__':
    print(extract_xml_content(xml_str='<xml>test1</xml>\n<xml>test2</xml>', tag='xml'))
