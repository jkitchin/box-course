'''
Basic module for reading data out of PDF files using Adobe Pro and OLE automation via win32com.

Som useful websites with documentation
1. http://www.adobe.com/content/dam/Adobe/en/devnet/acrobat/pdfs/iac_api_reference.pdf
2. http://www.adobe.com/content/dam/Adobe/en/devnet/acrobat/pdfs/iac_developer_guide.pdf

'''

import os
from win32com.client.dynamic import Dispatch
pddoc = Dispatch("AcroExch.PDDoc")

def get_info(pdffile, infokey):
    src = os.path.abspath(pdffile)
    pddoc.Open(src)
    value = pddoc.GetInfo(infokey)
    pddoc.Close()
    return value

def set_info(pdffile, infokey, value):
    src = os.path.abspath(pdffile)
    pddoc.Open(src)
    value = pddoc.SetInfo(infokey, value)
    pddoc.Save(1, src)
    pddoc.Close()
    return True

def add_rubric(pdffile, rubricfile, force=False):
    src1 = os.path.abspath(pdffile)
    src2 = os.path.abspath(rubricfile)

    # We do not want to add rubrics more than once
    if get_info(src1, 'rubric') == rubricfile and not force:
        return True

    pddoc1 = pddoc
    pddoc2 = Dispatch("AcroExch.PDDoc")

    pddoc1.Open(src1)
    N1 = pddoc1.GetNumPages()

    pddoc2.Open(src2)
    N2 = pddoc2.GetNumPages()

    # Insert rubric after last page of the other doc. pages start at 0
    pddoc1.InsertPages(N1 - 1, pddoc2, 0, N2, 0)
    pddoc1.Save(1, src1)
    pddoc1.Close()
    pddoc2.Close()

    # store rubric so we know it is added
    set_info(pdffile, 'rubric', src2)
    return True

                       


if __name__ == '__main__':
    print get_info('tmp.pdf', 'Grade')
    set_info('tmp.pdf', 'Grade', 'A')
    set_info('tmp.pdf', 'Grade3', 'AAsdfadjio')
    print get_info('tmp.pdf', 'Grade')
    print get_info('tmp.pdf', 'Grade6')


    add_rubric('tmp.pdf', 'rubric.pdf')
    
