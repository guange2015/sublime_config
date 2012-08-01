on appIsRunning(appName)
  tell application "System Events" to (name of processes) contains appName
end appIsRunning
 
on execInNewTab(_terminal, _title, _command)
  tell application "iTerm"
    activate
    tell _terminal
      launch session _title
      set _session to current session
      tell _session
        set name to _title
        write text _command
      end tell
    end tell
  end tell
end execInTerminalTab

on execInItermTab(_terminal, _session, _command)
  tell application "iTerm"
    activate
    set current terminal to _terminal
    tell _session
      select _session
      write text _command
    end tell
  end tell
end selectTerminalTab
 
on run argv
  set _command to item 1 of argv
  set _foundTab to false
  set _expected_title to (item 2 of argv)

  -- Second argument should be the tty to look for
  if length of argv is 2
    if appIsRunning("iTerm") then
      tell application "iTerm"
        activate
        repeat with t in terminals
          tell t
            set _terminal to t
            repeat with s in sessions
              set _tty to (name of s)
              if _tty starts with _expected_title then
                set _foundTab to true
                set _session to s
                set _terminal to t
                exit repeat
              end if
            end repeat
          end tell
          if _foundTab then
            exit repeat
          end if
        end repeat
      end tell
      if _foundTab then
        execInItermTab(_terminal, _session, _command)
      else
        execInNewTab(_terminal, _expected_title, _command)
      end if
    end if
  end if
end run