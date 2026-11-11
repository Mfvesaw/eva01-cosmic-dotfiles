function clear --description 'Clear the terminal and redraw the EVA01 Fastfetch card'
    command clear $argv
    set -l eva01_clear_status $status
    if test $eva01_clear_status -eq 0; and test (count $argv) -eq 0
        if status is-interactive; and isatty stdout; and isatty stdin
            if not contains -- "$TERM" dumb linux; and test "$EVA01_STARTUP" != 0
                if command -q eva01-greeting
                    command eva01-greeting
                else if command -q fastfetch
                    command fastfetch
                end
            end
        end
    end
    return $eva01_clear_status
end
