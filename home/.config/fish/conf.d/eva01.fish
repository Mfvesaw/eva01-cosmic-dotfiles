# EVA01 interactive shell: lavender text, violet structure, lime accents.
# Global values apply per shell; existing universal settings remain backed up.
if not status is-interactive
    return
end

set -g fish_autosuggestion_enabled 1
set -g fish_color_normal ecdcff
set -g fish_color_command 8edf5f --bold
set -g fish_color_keyword 995cd0 --bold
set -g fish_color_quote 62c77b
set -g fish_color_redirection e9a23b
set -g fish_color_end 995cd0 --bold
set -g fish_color_error f07891 --bold
set -g fish_color_param ecdcff
set -g fish_color_option a8bfff
set -g fish_color_valid_path b59ad9 --underline
set -g fish_color_comment 927da9 --italics
set -g fish_color_selection ecdcff --background=533773
set -g fish_color_operator 995cd0
set -g fish_color_escape e9a23b
set -g fish_color_autosuggestion 927da9
set -g fish_color_cwd 995cd0
set -g fish_color_cwd_root f07891
set -g fish_color_user 8edf5f
set -g fish_color_host b59ad9
set -g fish_color_host_remote e9a23b
set -g fish_color_status f07891
set -g fish_color_cancel f07891
set -g fish_color_search_match ecdcff --background=533773 --bold
set -g fish_color_history_current 8edf5f --bold

# Searchable completion/history menus with a soft violet selection.
set -g fish_pager_color_progress 8edf5f --bold
set -g fish_pager_color_prefix 8edf5f --bold
set -g fish_pager_color_completion ecdcff
set -g fish_pager_color_description b59ad9
set -g fish_pager_color_background --background=211928
set -g fish_pager_color_secondary_background --background=281e32
set -g fish_pager_color_selected_background --background=533773
set -g fish_pager_color_selected_prefix 8edf5f --bold
set -g fish_pager_color_selected_completion ecdcff --bold
set -g fish_pager_color_selected_description ecdcff

# Keep the requested steady I-beam in every editing mode.
set -g fish_cursor_default line
set -g fish_cursor_insert line
set -g fish_cursor_replace line
set -g fish_cursor_replace_one line
set -g fish_cursor_visual line
set -g fish_cursor_external line
set -g fish_cursor_unknown line

# COSMIC Terminal implements the standard DECSCUSR cursor sequence.
# Reapply after external programs, which may have changed the cursor shape.
function __eva01_ibeam --on-event fish_prompt --on-event fish_postexec --description 'Restore EVA01 I-beam cursor'
    if isatty stdout; and not contains -- "$TERM" dumb linux
        printf '\e[6 q'
    end
end
__eva01_ibeam
