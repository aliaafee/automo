"""
Import Icd10 Classification ClaMl xml file into database
"""
import os.path
import re
from bs4 import BeautifulSoup, Tag
from sqlalchemy import and_


from icd10rubrictohtml import icd10rubric_to_html
from database import Session,\
                     Icd10ModifierClass,\
                     Icd10Modifier,\
                     Icd10Class

def get_rubrics(tag):
    rubrics_str_dict = {}
    rubrics = tag.find_all("Rubric")
    for rubric in rubrics:
        if 'kind' in rubric.attrs.keys():
            kind = rubric['kind']
            rubric_str = u"".join(unicode(x) for x in rubric.contents).strip()
            if kind not in rubrics_str_dict.keys():
                rubrics_str_dict[kind] = rubric_str
            else:
                rubrics_str_dict[kind] += rubric_str

    rubrics_converted_dict = {}
    for kind, rubric_str in rubrics_str_dict.items():
        rubric = BeautifulSoup(u'<Rubric kind="{1}">{0}</Rubric>'.format(rubric_str, kind),
                               "lxml-xml")

        icd10rubric_to_html(rubric)

        converted = u"".join(unicode(x) for x in rubric.contents).strip()
        converted_plain = u" ".join(unicode(x) for x in rubric.stripped_strings).strip()

        rubrics_converted_dict[kind] = converted
        rubrics_converted_dict["{0}_plain".format(kind)] = converted_plain

    return rubrics_converted_dict


def import_to_database(filename, session):
    """Import ClaMl file to database"""
    try:
        with open(filename) as xmlfile:
            print "Creating Soup"
            soup = BeautifulSoup(xmlfile, "lxml-xml")

            print "Importing Modifiers"

            modifiers = soup.find_all("Modifier")
            for modifier in modifiers:
                if 'code' in modifier.attrs.keys():
                    new_modifier = Icd10Modifier(code=modifier['code'])

                    rubrics = get_rubrics(modifier)

                    if 'text' in rubrics.keys():
                        new_modifier.text = rubrics['text']

                    if 'note' in rubrics.keys():
                        new_modifier.note = rubrics['note']

                    session.add(new_modifier)
            #session.commit()

            print "Importing Modifier Classification"

            modifier_classes = soup.find_all("ModifierClass")

            for modifier_class in modifier_classes:
                if 'code' in modifier_class.attrs.keys() and\
                    'modifier' in modifier_class.attrs.keys():
                    new_modifier_class =\
                        Icd10ModifierClass(code="{0}{1}".format(modifier_class['modifier'],
                                                                modifier_class['code']))
                    new_modifier_class.modifier_code = modifier_class['modifier']
                    new_modifier_class.code_short = modifier_class['code']

                    rubrics = get_rubrics(modifier_class)
                    

                    if 'preferred' in rubrics.keys():
                        new_modifier_class.preferred = rubrics['preferred']
                        new_modifier_class.preferred_plain = rubrics['preferred_plain']

                    if 'definition' in rubrics.keys():
                        new_modifier_class.definition = rubrics['definition']

                    if 'inclusion' in rubrics.keys():
                        new_modifier_class.inclusion = rubrics['inclusion']

                    if 'exclusion' in rubrics.keys():
                        new_modifier_class.exclusion = rubrics['exclusion']

                    session.add(new_modifier_class)
            session.commit()

            print "Importing Chapters Blocks and Categories"

            iclasses = soup.find_all("Class")

            for iclass in iclasses:
                if 'code' in iclass.attrs.keys() and 'kind' in iclass.attrs.keys():
                    new_iclass = Icd10Class(code=iclass['code'],
                                            kind=iclass['kind'])

                    if 'usage' in iclass.attrs.keys():
                        new_iclass.usage = iclass['usage']

                    super_iclass = iclass.find("SuperClass")
                    if super_iclass is not None:
                        if 'code' in super_iclass.attrs.keys():
                            new_iclass.parent_code = super_iclass['code']

                    rubrics = get_rubrics(iclass)

                    if 'preferred' in rubrics.keys():
                        new_iclass.preferred = rubrics['preferred']
                        new_iclass.preferred_plain = rubrics['preferred_plain']

                    if 'preferredLong' in rubrics.keys():
                        new_iclass.preferred_long = rubrics['preferredLong']

                    if 'inclusion' in rubrics.keys():
                        new_iclass.inclusion = rubrics['inclusion']

                    if 'exclusion' in rubrics.keys():
                        new_iclass.exclusion = rubrics['exclusion']

                    if 'text' in rubrics.keys():
                        new_iclass.text = rubrics['text']

                    if 'note' in rubrics.keys():
                        new_iclass.note = rubrics['note']

                    if 'coding-hint' in rubrics.keys():
                        new_iclass.coding_hint = rubrics['coding-hint']

                    session.add(new_iclass)

            print "Getting chapter codes for categories and blocks"

            def get_top_parent_code(iclass):
                """Recursively goes to the top parent, ie chapter"""
                if iclass.parent is None:
                    return iclass.code
                return get_top_parent_code(iclass.parent)

            categories = session.query(Icd10Class).filter(Icd10Class.kind != 'chapter')
            for category in categories:
                top_parent_code = get_top_parent_code(category)
                category.chapter_code = top_parent_code

            print "Getting block codes for categories"

            def get_parent_block_code(iclass):
                """Recursively goes to the parent block"""
                if iclass.kind == "block":
                    return iclass.code
                return get_parent_block_code(iclass.parent)

            categories = session.query(Icd10Class).filter(Icd10Class.kind == 'category')
            for category in categories:
                parent_block_code = get_parent_block_code(category)
                category.parent_block_code = parent_block_code

        print "Assigning Modifer Codes to Categories"
        print "This looks for a file named icd2016ens-category-modifiers.csv "\
                "in the same directory as the xml file."

        mod_filename = os.path.join(os.path.dirname(filename),
                                    "icd2016ens-category-modifiers.csv")

        with open(mod_filename, "r") as modfile:
            for line in modfile:
                line_lst = re.split(",", line, 1)
                mod_code = (line_lst[0]).strip()
                cats_str = line_lst[1]

                cats = re.split(",", cats_str)
                cats = [cat.strip() for cat in cats]
                for cat in cats:
                    m_cats = session.query(Icd10Class)\
                        .filter(
                            and_(
                                Icd10Class.kind == "category",
                                Icd10Class.code.like("{0}%".format(cat))
                            )
                        )
                    for m_cat in m_cats:
                        if m_cat.modifier_code is None:
                            m_cat.modifier_code = mod_code
                        else:
                            if m_cat.modifier_extra_code is None:
                                m_cat.modifier_extra_code = mod_code
                            else:
                                print "No space for mod {0} in cat {1}".format(mod_code, m_cat.code)

        session.commit()
    except IOError as e:
        print "Error {0}: {1}".format(e.errno, e.strerror)
        session.rollback()
