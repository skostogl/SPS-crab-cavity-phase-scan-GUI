#!/bin/bash

HOST=$( basename $0 )
HOST=${HOST%%.*}

case $HOST in
    cfo-hca4-bqht)      ;&
    cfo-866-biguzik)
        USER=bqhtop
        DOMAIN=CERN     ;;
    cfo-ua47-bqhtb1)    ;&
    cfo-ua47-bqhtb2)    ;&
    cfo-hca4-bqht2)
        USER=Instrument
        DOMAIN=         ;;
esac

if [ ! -z "$DOMAIN" ]; then
    DOMAIN="-d $DOMAIN"
fi

ssh cs-ccr-oper -X -C xfreerdp --no-nla --ignore-certificate --plugin cliprdr -z $DOMAIN -u $USER -x 0x80 -a 32 -g 1024x768 -k en-us $* $HOST &
