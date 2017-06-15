# ICD-10 Code Import

Use the -i option to import ICD-10 ClaML xml file. The importer expects the file "icd2016ens-category-modifiers.csv" to be located in the same folder ast the ClaML xml file. This file contains the modifers codes for the categories, for some reason this relation is not present in the ClaML files (? issue with the ClaML format). Only the 2016 version of the ClaML xml file (icdClaML2016ens.xml) is currently supported. This does not mean others wont work, but there may be errors in importing, also the "icd2016ens-category-modifiers.csv" file may not work for other versions.
