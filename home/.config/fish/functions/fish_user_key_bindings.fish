function fish_user_key_bindings --description 'EVA01 searchable completion and history shortcuts'
    # Retain the selected editing mode, including vi command-mode keys.
    set -l eva01_binding_mode default
    if test "$fish_key_bindings" = fish_vi_key_bindings
        set eva01_binding_mode insert
    end

    bind --mode $eva01_binding_mode tab complete
    bind --mode $eva01_binding_mode shift-tab complete-and-search
    bind --mode $eva01_binding_mode ctrl-space complete-and-search
    bind --mode $eva01_binding_mode ctrl-r history-pager
    bind --mode $eva01_binding_mode ctrl-s pager-toggle-search
    bind --mode $eva01_binding_mode right forward-char
    bind --mode $eva01_binding_mode ctrl-f forward-char
    bind --mode $eva01_binding_mode alt-right forward-word
    bind --mode $eva01_binding_mode alt-f forward-word
    bind --mode $eva01_binding_mode alt-up history-token-search-backward
    bind --mode $eva01_binding_mode alt-down history-token-search-forward

    # Keep the static Fastfetch card after clearing, including vi editing modes.
    for eva01_mode in default insert visual
        bind --mode $eva01_mode ctrl-l __eva01_clear_screen
    end
end
