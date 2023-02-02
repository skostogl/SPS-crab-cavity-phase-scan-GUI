#!/bin/bash

# Launcher script for BBQ Trigger Viewer
# T. Levens <tom.levens@cern.ch>

DIR=$( dirname $( which $0 ))

ulimit -c 0

if [ "$#" -eq "0" ]; then
    SYS=$( zenity \
        --list \
        --title="BBQ Selector" \
        --text="Select a BBQ system:" \
        --radiolist \
        --column=" " \
        --column="System" \
        --height=210 \
        FALSE "Continuous HS" \
        FALSE "Continuous Gated" \
        TRUE  "On-Demand HS" \
        FALSE "On-Demand Gated" )

    if [ "$SYS" == "" ]; then
        exit 1
    fi

    case $SYS in
        "Continuous HS")    SYS="CONT"      ;;
        "Continuous Gated") SYS="GATED"     ;;
        "On-Demand HS")     SYS="ONDEMAND"  ;;
        "On-Demand Gated")  SYS="GATED_OD"  ;;
    esac
else
    SYS=$1
fi

for BEAM in B1 B2; do
    for PLANE in H V; do
        CMD="$DIR/bqtrig_viewer $SYS $BEAM $PLANE"
        echo "$CMD &"
        $CMD &
    done
done
