vim9script

# run the main python file
# nnoremap <leader>m :update<CR>:ScratchTermReplaceU .venv/Scripts/python.exe src/docx2python/main.py<CR>
nnoremap <leader>l :call g:RunPrecommit()<CR>
nnoremap <leader>L :call g:RunPrecommitAll()<CR>

set grepprg=rg\ --vimgrep\ --no-heading\ --glob\ !tests/resources/**\ --glob\ !uv.lock
