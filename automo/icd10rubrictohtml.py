"""Convert icd10 rubric xml to html"""
import re
from bs4 import BeautifulSoup, Tag


def icd10rubric_to_html(soup):
    """Convert icd10 rubric xml to html"""
    kind = ""

    rubric_tags = soup.find_all("Rubric")
    for tag in rubric_tags:
        if "kind" in tag.attrs.keys():
            kind = tag['kind']
        tag.replace_with_children()

    table_tags = soup.find_all("Table")
    for table_tag in table_tags:
        table_tag['border'] = "1"
        table_tag['cellspacing'] = "0"
        row_tags = table_tag.find_all("Row")
        for tag in row_tags:
            tag.name = "tr"
        cell_tags = table_tag.find_all("Cell")
        for tag in cell_tags:
            tag.name = "td"

    para_tags = soup.find_all("Para")
    for tag in para_tags:
        tag.replace_with_children()

    label_tags = soup.find_all("Label")
    if kind in ['inclusion', 'exclusion']:
        for tag in label_tags:
            tag.name = "div"
    else:
        for tag in label_tags:
            tag.replace_with_children()

    fragment_tags = soup.find_all("Fragment")
    for tag in fragment_tags:
        tag.name = "span"

    reference_tags = soup.find_all("Reference")
    for tag in reference_tags:
        ref_text = (u" ".join(unicode(x) for x in tag.stripped_strings)).strip()

        try:
            code = tag['code']
        except KeyError:
            code = ref_text

        href = ""
        if re.match("[A-Z][0-9][0-9]\.[0-9]", code) is not None:
            #is sub category
            href = "category?code={0}".format(code)
        else:
            if len(code) == 3:
                #is main category
                href = "category?code={0}".format(code)
            else:
                if re.match("[A-Z][0-9][0-9]-[A-Z][0-9][0-9]", code):
                    #is block
                    href = "block?code={0}".format(code)
                else:
                    if re.match("[A-Z][0-9][0-9]\.-", code):
                        #is dot range
                        main_code = re.search("[A-Z][0-9][0-9]", code).group()
                        href = "category?code={0}".format(main_code)
                    else:
                        href = "modifier?code={0}".format(code)

        brackets = False
        try:
            if tag['class'] == 'in brackets':
                brackets = True
        except KeyError:
            brackets = False

        try:
            usage = tag['usage']
        except KeyError:
            usage = ""

        if usage == "aster":
            #add aster
            pass
        elif usage == "dagger":
            #add dagger
            pass

        link_tag = Tag(soup, name="a")
        link_tag['href'] = href
        link_tag.append(ref_text)

        new_tag = Tag(soup, name="span")
        if brackets:
            new_tag.append(" (")
        else:
            new_tag.append(" ")
        new_tag.append(link_tag)
        if brackets:
            new_tag.append(") ")
        else:
            new_tag.append(" ")

        tag.replace_with(new_tag)


def main():
    with open("icd10/icdClaML2016ens.xml") as xmlfile:
        print "Creating Soup"
        soup = BeautifulSoup(xmlfile, "lxml-xml")

        #print soup.prettify()

        icd10rubric_to_html(soup)


if __name__ == "__main__":
    main()
