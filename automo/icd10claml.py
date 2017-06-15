"""
Import Icd10 Classification ClaMl xml file into database
"""
import os.path
import re
from bs4 import BeautifulSoup
from sqlalchemy import and_


from database import Session,\
                     Icd10ModifierClass,\
                     Icd10Modifier,\
                     Icd10Class


def get_rubriks(tag):
    rubriks_dict = {}
    rubriks = tag.find_all("Rubric")
    for rubrik in rubriks:
        if 'kind' in rubrik.attrs.keys():
            kind = rubrik['kind']
            #rubriks_dict[kind] = ("".join(str(x) for x in rubrik.contents)).strip()
            #TODO: Need to convert to html for display, not just stripping tags only
            rubriks_dict[kind] = (u" ".join(unicode(x) for x in rubrik.stripped_strings)).strip()

    return rubriks_dict



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

                    rubriks = get_rubriks(modifier)

                    if 'text' in rubriks.keys():
                        new_modifier.text = rubriks['text']

                    if 'note' in rubriks.keys():
                        new_modifier.note = rubriks['note']

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

                    rubriks = get_rubriks(modifier_class)

                    if 'preferred' in rubriks.keys():
                        new_modifier_class.preferred = rubriks['preferred']

                    if 'definition' in rubriks.keys():
                        new_modifier_class.definition = rubriks['definition']

                    if 'inclusion' in rubriks.keys():
                        new_modifier_class.inclusion = rubriks['inclusion']

                    if 'exclusion' in rubriks.keys():
                        new_modifier_class.exclusion = rubriks['exclusion']

                    session.add(new_modifier_class)
            #session.commit()

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

                    rubriks = get_rubriks(iclass)

                    if 'preferred' in rubriks.keys():
                        new_iclass.preferred = rubriks['preferred']

                    if 'preferredLong' in rubriks.keys():
                        new_iclass.preferred_long = rubriks['preferredLong']

                    if 'inclusion' in rubriks.keys():
                        new_iclass.inclusion = rubriks['inclusion']

                    if 'exclusion' in rubriks.keys():
                        new_iclass.exclusion = rubriks['exclusion']

                    if 'text' in rubriks.keys():
                        new_iclass.text = rubriks['text']

                    if 'note' in rubriks.keys():
                        new_iclass.note = rubriks['note']

                    if 'coding-hint' in rubriks.keys():
                        new_iclass.coding_hint = rubriks['coding-hint']

                    session.add(new_iclass)
            #session.commit()

            print "Getting chapter codes for categories and blocks"

            categories = session.query(Icd10Class).filter(Icd10Class.kind != 'chapter')

            def get_top_parent_code(iclass):
                #Recursively goes to the top parent, ie chapter
                if iclass.parent is None:
                    return iclass.code
                return get_top_parent_code(iclass.parent)

            for category in categories:
                top_parent_code = get_top_parent_code(category)

                category.chapter_code = top_parent_code

            #session.commit()

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
    except:
        print "Error occured while importing icd10codes."
        session.rollback()
