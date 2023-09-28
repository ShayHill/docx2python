from docx2python import docx2python

file_path = "/home/deayalar/Downloads/Contract ID 58605 - Immunoprecise Antibodies -  - Master Services Agreement (MSA)_IPAedits2.8.2023--v1 (2).docx"
file_path = "/home/deayalar/Downloads/Mock MSA counterparty edits for comparison.docx"

with docx2python(file_path, extract_comments=True) as docx_content:
    with open("docx2python.txt", "w+") as txt_file:
        txt_file.write(docx_content.text)