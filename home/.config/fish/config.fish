if status is-interactive
    # Preserve the tools and paths used by this account.
    fish_add_path -g -p ~/develop/flutter/bin
    fish_add_path --global --append ~/.local/bin
    set -gx CHROME_EXECUTABLE /usr/bin/vivaldi

    set -g fish_greeting ''
    if command -q starship
        starship init fish | source
    end

    # Static EVA head and Fastfetch stay in normal terminal scrollback.
    # Nothing is printed for scripts, redirected shells, or nested sessions.
    set -l eva01_show_startup 1
    # Preserve explicit commands supplied to interactive Fish automation.
    # Read only argv option names; command text is never evaluated or printed.
    if test -r /proc/$fish_pid/cmdline
        set -l eva01_process_argv (string split0 </proc/$fish_pid/cmdline)
        for eva01_arg in $eva01_process_argv[2..-1]
            if test "$eva01_arg" = --
                break
            end
            if string match --quiet --regex '^--(command|init-command)(=|$)|^-[^-]*[cC]' -- "$eva01_arg"
                set eva01_show_startup 0
                break
            end
        end
    end
    if not isatty stdin; or not isatty stdout
        set eva01_show_startup 0
    end
    if set -q EVA01_STARTUP_DONE; or set -q EVA01_DASHBOARD; or set -q INSIDE_EMACS; or set -q TMUX; or set -q STY
        set eva01_show_startup 0
    end
    if contains -- "$TERM" dumb linux
        set eva01_show_startup 0
    end
    if contains -- "$TERM_PROGRAM" vscode vscode-insiders JetBrains-JediTerm
        set eva01_show_startup 0
    end
    if test "$EVA01_STARTUP" = 0
        set eva01_show_startup 0
    end

    if test $eva01_show_startup = 1
        set -gx EVA01_STARTUP_DONE 1
        if command -q eva01-greeting
            eva01-greeting
        else if command -q fastfetch
            fastfetch
        end
    end
end
