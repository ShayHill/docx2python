
## 3.3.0 (2024-12-05)

### Feat

- skip elements with invalid tags. Issue a warning. These are usually the
  result of faulty conversion software.

## 3.2.1 (2024-11-17)

### Feat

- add an `elem` attribute to `Par` instances, returning the xml element from
  which the paragraph was generated

## 3.0.0 (2024-07-27)

### BREAKING CHANGE

- The html and duplicate_merged_cells arguments to docx2python are now keyword
  only.
- Inserts empty cells and whitespace into exported
  tables.
- Removed IndexedItem class which was *probably* only used internally, but it
  was a part of the public interface.
- Function get_text was a public function. It mirrored the identical
  flatten_text from the docx_text module.
- This change breaks the way paragraph styles (internally pStyle) were handled.
  The input argument `do_pStyle` will no now raise an error.
- This doesn't change the interface and doesn't break any of my tests, but it
  took a lot of refactoring to make this change and it may break some
  unofficial patches I've made for clients.

### Feat

- improve type hints for DocxContent properties
- insert blank cells to match gridSpan
- add list_position attribute for Par instances
- explicate return types in iterators
- use input file namespace

### Fix

- eliminate double html tags for paragraph styles

### Refactor

- make boolean args keyword only
- use pathlib in lieu of os.path
- remove Any types from DocxContent close method
- convert HtmlFormatter lambdas to defs
- specialize join_leaves into join_runs
- insert html when extracting text
- make queuing text outside paragraphs explicit
- make _open_pars private
- stop accepting extract_image bool argument
- default duplicate_merged_cells to True
- remove unused helper functions
- use pathlib in conftest
- expose numPr, ilvl, and number in BulletGenerator
- remove redundant functions
- remove do_pStyle argument from flatten_text
- remove function get_text from iterators module
- store content table as nested list of Par instances
- move xml2html_format attrib from TagRunner to DepthCollector
- factor out DepthCollector.item_depth param
- make set_caret recursive
- remove unused `styled` param from insert_text_as_new_run
- remove relative imports in src modules

## 2.10.2 (2024-06-30)

### Refactor

- remove relative imports in src modules

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
