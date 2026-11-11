function steam --description 'Steam with the EVA01 user-local Millennium loader'
    if test -x ~/.local/bin/steam
        command ~/.local/bin/steam $argv
    else
        command /usr/bin/steam $argv
    end
end
