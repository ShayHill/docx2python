## 2.10.1 (2024-04-03)

### Fix

- move paragraphs to main dependencies

## 2.10.0 (2024-04-03)

### Feat

- support checkox "true"/"false" values

## 2.9.2 (2024-04-03)

### Fix

- extract hyperlinks in comments
- remove open_par limit in DepthCollector
- return empty list when comments fails

## 2.9.1 (2024-04-02)

### Refactor

- comb full-text and line-text formatting
- refactor element text extractors into methods

## 2.9.0 (2024-03-30)

### Feat

- extract comments from docx files
- capture comment ranges

### Refactor

- expose DepthCollector instance for File object
- expose DepthCollector instance when get_text

## 2.8.0 (2024-01-21)

### Feat

- capture hyperlink anchors

## 2.7.3 (2023-06-17)

### Fix

- sync commitizen and poetry version numbers

## 2.7.2 (2023-06-16)

### Fix

- update poetry lock file

## 2.7.1 (2023-05-02)

### Refactor

- update and pass pre-commit hooks

## 2.7.0 (2023-04-27)

### Feat

- preserve newlines in replace_docx_text
- add py.typed for typecheckers
- add argument duplicate_merged_cells for docx tables
- add context manager protocol
- allow type IOBytes for filename arguments
- add and mostly pass pre-commit hooks
- remove Python 3.7 support

### Fix

- move pre-commit to dev requirement
