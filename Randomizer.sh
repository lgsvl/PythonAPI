#!/bin/bash
if [ $# -eq 0 ]
  then
    SEARCH="Mouse"
    if [ "$SEARCH" = "" ]; then 
        exit 1
    fi
    Yaxis=$(xrandr --current | grep '*' | uniq | awk '{print $1}' | cut -d 'x' -f2)
    ids=$(xinput --list | awk -v search="$SEARCH" \
    '$0 ~ search {match($0, /id=[0-9]+/);\
                  if (RSTART) \
                    print substr($0, RSTART+3, RLENGTH-3)\
                 }'\
     )

    for i in $ids
    do
        xinput set-prop $i 'Device Enabled' 0
    done
    #fix launching gui
    version=$(find ~ 2>&1 -type d -name "lgsvlsimulator*" -not -path "*/Trash/*" | grep -v "Permission denied" | head -1)
    $version/simulator >/dev/null 2>&1 & gnome-terminal -- roslaunch rosbridge_server rosbridge_websocket.launch
    sleep 0.3
    wid=$(xdotool search --name "LGSVL Simulator Configuration")
    sleep 0.1 && xdotool windowfocus $wid && xdotool key --window $wid Tab Tab Tab Tab Tab KP_Enter
    sleep 4
    Xaxis=$(xrandr --current | grep '*' | uniq | awk '{print $1}' | cut -d 'x' -f1)
    Yaxis=$(xrandr --current | grep '*' | uniq | awk '{print $1}' | cut -d 'x' -f2)
    Xaxis=$[$Xaxis/2]
    Yaxis=$[10*$Yaxis/18]
    xdotool mousemove --sync $Xaxis $Yaxis
    sleep 0.25
    xdotool click 1
    #Re-enable mouse
    sleep 0.2
    for i in $ids
    do
        xinput set-prop $i 'Device Enabled' 1
    done
    sleep 0.1
    python3 ~/PythonAPI/RS_scripts/GUI.py
fi

if [[ $1 = "-r" ]];
then
    version=$(find ~ 2>&1 -type d -name "lgsvlsimulator*" -not -path "*/Trash/*" | grep -v "Permission denied" | head -1)
    $version/simulator & gnome-terminal -- roslaunch rosbridge_server rosbridge_websocket.launch
    python3 ~/PythonAPI/RS_scripts/GUI.py
fi

