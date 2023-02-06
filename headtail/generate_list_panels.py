#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Script to automatically generate LIST Inspector panels

WARNING: This is very hacky and should not be trusted :-)

Copyright (c) CERN 2015-2016

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Authors:
    Tom Levens <tom.levens@cern.ch>
'''

import base64
import datetime
import os
import random

from modules.list_nodes import Nodes


def gen_uid():
    '''Returns an Inspector UID'''
    return '{0:08x}-{1:04x}-{2:04x}-{3:04x}-{4:08x}'.format(
        random.randint(0, 2**32-1),
        random.randint(0, 2**16-1),
        random.randint(0, 2**16-1),
        random.randint(0, 2**16-1),
        random.randint(0, 2**32-1)
    )


def gen_label(pos, size, angle, text, font, color='255,255,255,255'):
    '''Generate a label'''
    return (
        '<Label Class="cern.ade.inspector.gui.monitors.support.Label">\n'
        '<Configuration Font="{font[0]}#{font[1]}#{font[2]}" HorizontalAlignment="false" MaxSize="1600,1200" '
        'MinSize="40,40" Position="{pos[0]},{pos[1]}" ResizedByUser="false" Rotation="{angle}" ScaleX="1.0" '
        'ScaleY="1.0" Size="{size[0]},{size[1]}" ''SizeRatio="0.0" Text="{text}" TextColor="{color}" '
        'UID="{uid}" VerticalAlignment="false" XmlVersion="1" ZOrder="0"/>\n'
        '</Label>'.format(
            uid=gen_uid(), pos=pos, size=size, angle=angle, text=text, font=font, color=color
        )
    )


def gen_container(pos, size, parent_uid, contents=[], bgcolor='69,70,64,255'):
    '''Generate a container'''
    uids = [gen_uid() for _ in range(2)]

    return [
        '<Panel Class="cern.ade.inspector.gui.monitors.containers.SimpleContainer">\n'
        '<Configuration AlertColor="255,100,100,255" BackgroundColor="{bgcolor}" BorderColor="0,0,0,255" '
        'MaxSize="2147483647,2147483647" MinSize="10,10" NormalColor="100,255,100,255" OffColor="100,100,100,255" '
        'Position="{pos[0]},{pos[1]}" ReferenceValue="NaN" ResizedByUser="false" Rotation="0.0" ScaleX="1.0" '
        'ScaleY="1.0" Size="{size[0]},{size[1]}" SizeRatio="0.0" TextColor="255,255,255,255" '
        'Title="device/property#field" UID="{uids[0]}" WarningColor="225,225,60,255" XmlVersion="1" ZOrder="0"/>\n'
        '<Container PARENT="{parent_uid}" POSITION="3,3" SIZE="{isize[0]},{isize[1]}" UID="{uids[1]}">\n'.format(
            parent_uid=parent_uid, uids=uids, size=size, pos=pos, isize=(size[0]-6, size[1]-6), bgcolor=bgcolor
        )
    ] + contents + [
        '</Container>\n'
        '</Panel>\n'
    ]


def encode_replace(source, dest):
    '''For some reason, the action replacement value is base64 encoded'''
    return base64.b64encode(bytearray('{0}/{1}'.format(source, dest), 'UTF-8')).decode('UTF-8')


def gen_monitor_text(prop):
    '''Generate the text for a monitor'''
    return (
        '<Monitor Class="cern.ade.inspector.gui.monitors.components.synoptics.BaseSynMonitor">\n'
        '<Configuration Action="view:../{panel}" ActionForwardReplace="false" ActionPLS="" ActionReplace="{replace} " '
        'ActionTabName="{dest}" AlertColor="{dis_color}" BackgroundColor="255,255,255,0" '
        'BlinkerColor="60,100,255,255" BlinkerType="{blink}" BlockSize="25,25" '
        'Font="Dialog#0#12" LineHandlersEnabled="false" MaxSize="1600,1200" MaxValue="0.0" MinSize="8,8" '
        'MinValue="0.0" NormalColor="{ena_color}" OffColor="100,100,100,255" Position="{pos[0]},{pos[1]}" '
        'RangeType="{range}" ReferenceValue="NaN" ResizedByUser="true" Rotation="0.0" ScaleX="1.0" ScaleY="1.0" '
        'Size="35,35" SizeRatio="0.0" {string_range}Tab-Name="{dest}" TextColor="255,255,255,255" TextOrientation="0" '
        'TextPosition="0" Title="{name}" Type="BaseSynMonitor" UID="{uids[0]}" WarningColor="225,225,60,255" '
        'XmlVersion="1" ZOrder="0">\n'
        '<RangeProperty>\n' + prop + '</RangeProperty>\n'
        '{blink_prop}'
        '</Configuration>\n'
        '<Properties>\n' + prop + '</Properties>\n'
        '<HANDLER POSITION="5,17" UID="{uids[1]}"/>\n'
        '<HANDLER POSITION="30,17" UID="{uids[2]}"/>\n'
        '<HANDLER POSITION="17,5" UID="{uids[3]}"/>\n'
        '<HANDLER POSITION="17,30" UID="{uids[4]}"/>\n'
        '</Monitor>\n'
    )


def gen_monitor_trig(pos, name, panel, source, dest,
                     dis_color='255,100,100,255', ena_color='100,255,100,255'):
    '''Generate a monitor with one condition'''
    prop = (
        '<DataSubscriptionInfo ConvertToBitArray="false" DisplayName="{dest}/HwSettings#triggerEnabled" Index="-1" '
        'Information="" PrimaryDefaultType="NONE" SecondaryDefaultType="NONE" Type="ProxySubscriptionInfo">\n'
        '<PROPERTY_VALUE DEVICE_NAME="{dest}" FIELD_NAME="triggerEnabled" FLAVOR="PROPERTY_VALUE" '
        'PROPERTY_NAME="HwSettings" SELECTOR="NULL" VALUE_TYPE="BOOLEAN"/>\n'
        '</DataSubscriptionInfo>\n'
    )

    uids = [gen_uid() for _ in range(5)]

    mon = gen_monitor_text(prop).format(
        panel=panel, replace=encode_replace(source, dest), dis_color=dis_color, ena_color=ena_color, pos=pos,
        source=source, dest=dest, uids=uids, name=name, blink='Disabled', blink_prop='', range='Boolean',
        string_range=''
    )

    return (uids, mon)


def gen_monitor_io(pos, name, panel, source, dest,
                   dis_color='255,100,100,255', ena_color='100,255,100,255'):
    '''Generate a monitor with two conditions'''
    prop = (
        '<DataSubscriptionInfo ConvertToBitArray="false" DisplayName="SYNTHETIC_VALUE/{dest}" Index="-1" '
        'Information="" PrimaryDefaultType="INTEGER" SecondaryDefaultType="NONE" Type="ProxySubscriptionInfo">\n'
        '<PROPERTY_VALUE DESCRIPTION="" '
        'EQUATION="(toInteger(#{{P1}}) + (toInteger((#{{P2}} &amp;&amp; #{{P1}})) * 2))" '
        'FLAVOR="SYNTHETIC_VALUE" MACHINE="LIST" NAME="{dest}" UID="{uids[5]}" USER="tlevens" VALUE_TYPE="INTEGER">\n'
        '<BLOCK TYPE="parameter" UID="{uids[6]}" X="160" Y="50">\n'
        '<EQUATION_ELEMENT DEFINED="true" DEVICE_NAME="{dest}" FIELD_NAME="enabled" FLAVOR="PROPERTY_VALUE" NAME="P1" '
        'PROPERTY_NAME="HwSettings" SELECTOR="NULL" TYPE="parameter" VALUE_TYPE="BOOLEAN" VARIABLE="P1"/>\n'
        '</BLOCK>\n'
        '<BLOCK TYPE="operator" UID="{uids[7]}" X="800" Y="50">\n'
        '<OPERATOR FLAVOR="PROPERTY_VALUE" NAME="Operator" OPERATION="+" TYPE="operator" VALUE_TYPE="INTEGER"/>\n'
        '</BLOCK>\n'
        '<BLOCK TYPE="parameter" UID="{uids[8]}" X="160" Y="140">\n'
        '<EQUATION_ELEMENT DEFINED="true" DEVICE_NAME="{dest}" FIELD_NAME="armed" FLAVOR="PROPERTY_VALUE" NAME="P2" '
        'PROPERTY_NAME="HwSettings" SELECTOR="NULL" TYPE="parameter" VALUE_TYPE="BOOLEAN" VARIABLE="P2"/>\n'
        '</BLOCK>\n'
        '<BLOCK TYPE="function" UID="{uids[9]}" X="500" Y="50">\n'
        '<FUNCTION FLAVOR="PROPERTY_VALUE" FUNCTION="toInteger" NAME="Function" TYPE="function" '
        'VALUE_TYPE="INTEGER"/>\n'
        '</BLOCK>\n'
        '<BLOCK TYPE="function" UID="{uids[10]}" X="500" Y="140">\n'
        '<FUNCTION FLAVOR="PROPERTY_VALUE" FUNCTION="toInteger" NAME="Function" TYPE="function" '
        'VALUE_TYPE="INTEGER"/>\n'
        '</BLOCK>\n'
        '<BLOCK TYPE="operator" UID="{uids[11]}" X="410" Y="140">\n'
        '<OPERATOR FLAVOR="PROPERTY_VALUE" NAME="Operator" OPERATION="&amp;&amp;" TYPE="operator" '
        'VALUE_TYPE="BOOLEAN"/>\n'
        '</BLOCK>\n'
        '<BLOCK TYPE="constant" UID="{uids[12]}" X="590" Y="170">\n'
        '<CONSTANT FLAVOR="PROPERTY_VALUE" NAME="K0" TYPE="constant" VALUE="2" VALUE_TYPE="INTEGER" VARIABLE="K0"/>\n'
        '</BLOCK>\n'
        '<BLOCK TYPE="operator" UID="{uids[13]}" X="680" Y="140">\n'
        '<OPERATOR FLAVOR="PROPERTY_VALUE" NAME="Operator" OPERATION="*" TYPE="operator" VALUE_TYPE="INTEGER"/>\n'
        '</BLOCK>\n'
        '<LINE ANCHOR_A="0" ANCHOR_B="1" BLOCK_A="{uids[6]}" BLOCK_B="{uids[9]}"/>\n'
        '<LINE ANCHOR_A="0" ANCHOR_B="1" BLOCK_A="{uids[10]}" BLOCK_B="{uids[13]}"/>\n'
        '<LINE ANCHOR_A="0" ANCHOR_B="2" BLOCK_A="{uids[12]}" BLOCK_B="{uids[13]}"/>\n'
        '<LINE ANCHOR_A="0" ANCHOR_B="1" BLOCK_A="{uids[11]}" BLOCK_B="{uids[10]}"/>\n'
        '<LINE ANCHOR_A="0" ANCHOR_B="1" BLOCK_A="{uids[9]}" BLOCK_B="{uids[7]}"/>\n'
        '<LINE ANCHOR_A="0" ANCHOR_B="1" BLOCK_A="{uids[8]}" BLOCK_B="{uids[11]}"/>\n'
        '<LINE ANCHOR_A="0" ANCHOR_B="2" BLOCK_A="{uids[6]}" BLOCK_B="{uids[11]}"/>\n'
        '<LINE ANCHOR_A="0" ANCHOR_B="2" BLOCK_A="{uids[13]}" BLOCK_B="{uids[7]}"/>\n'
        '</PROPERTY_VALUE>\n'
        '</DataSubscriptionInfo>\n'
    )

    blink_prop = (
        '<BlinkerProperty>'
        '<DataSubscriptionInfo ConvertToBitArray="false" DisplayName="{dest}/Log#asString" Index="-1" Information="" '
        'PrimaryDefaultType="NONE" SecondaryDefaultType="NONE" Type="ProxySubscriptionInfo">\n'
        '<PROPERTY_VALUE DEVICE_NAME="{dest}" FIELD_NAME="asString" FLAVOR="PROPERTY_VALUE" PROPERTY_NAME="Log" '
        'SELECTOR="NULL" VALUE_TYPE="STRING"/>\n'
        '</DataSubscriptionInfo>\n'
        '</BlinkerProperty>\n'
    ).format(dest=dest)

    uids = [gen_uid() for _ in range(14)]

    mon = gen_monitor_text(prop).format(
        panel=panel, replace=encode_replace(source, dest), dis_color=dis_color, ena_color=ena_color, pos=pos,
        source=source, dest=dest, uids=uids, name=name, blink='OnUpdate', blink_prop=blink_prop, range='String',
        string_range='StringRangeAlert="0" StringRangeNormal="3" StringRangeOff="" StringRangeWarning="1" '
    )

    return (uids, mon)


def generate_panel(inputs, outputs, panel_name):
    '''Generate the complete panel'''

    print('generating {name} Inspector panel'.format(name=panel_name))

    # WRTD triggers
    #   format: (out, in)
    triggers = [(o, i) for o in outputs for i in inputs]

    # Seed the RNG to always get the same sequence of values between runs
    random.seed(0)

    # UID for panel
    parent_uid = gen_uid()

    # Reference list for UIDs of each monitor
    refs = [[None for i in range(len(inputs) + 1)] for o in range(len(outputs) + 1)]

    # Output string array
    fstr = []

    # Start of panel
    fstr.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    fstr.append(
        '<MonitorPanel AskForWritingConfirmation="false" BlinkingInterval="1000" Title="{name}" '
        'UID="{parent_uid}" WritingEnabled="true">'''.format(
            name="LHC Instability Trigger Network", parent_uid=parent_uid
        )
    )

    # ------------------------------------------------------------------------
    lab = 70            # Size of input/output labels
    sta_x = lab + 25    # Start X position of first monitor
    sta_y = 165         # Start Y position of first monitor
    inc_x = 40          # Increment X per monitor
    inc_y = 40          # Increment Y per monitor
    shift = 10          # Extra space between input/output monitors and trigger monitors
    win_x = 25          # Padding X required for window size
    win_y = 75          # Padding Y required for window size
    min_x = 655         # Minimum X window size
    min_y = 705         # Minimum Y window size
    # ------------------------------------------------------------------------

    # Calulate window sizes
    winsize_x = sta_x + 2*shift + win_x + ((len(inputs)+1) * inc_x)

    if winsize_x < min_x:
        sta_x += (min_x - winsize_x) // 2
        winsize_x = min_x

    winsize_y = sta_y + 2*shift + win_y + ((len(outputs)+1) * inc_y)

    if winsize_y < min_y:
        winsize_y = min_y

    # Position for title
    # label_x = sta_x + shift + inc_x + (len(inputs)//2 * inc_x) - 351 // 2
    title_x = winsize_x//2 - 374//2
    date_x = title_x + 374 - 66

    # Title
    fstr.append(gen_label((title_x, 25), (374, 34), '0.0', 'LHC Instability Trigger Network', ('Dialog', '0', '24')))

    # Datecode
    now = datetime.datetime.now()
    fstr.append(gen_label((date_x, 50), (66, 18), '0.0', '{0:%Y-%m-%d}'.format(now),
                          ('Dialog', '0', '9'), '128,128,128,255'))

    # Inputs/Outputs labels
    fstr.append(gen_label((sta_x+inc_x-15, sta_y-lab), (24, 51), '1.5707963267948966', 'Inputs',
                          ('Dialog', '0', '14')))
    fstr.append(gen_label((sta_x-lab, sta_y+inc_y-15), (64, 24), '0.0', 'Outputs',
                          ('Dialog', '0', '14')))

    # Inputs
    for i, name in enumerate(inputs):
        pos_x = sta_x + (i+1)*inc_x + shift
        pos_y = sta_y
        devname = 'HR.WRTD.{0}.IN'.format(name)
        print('--> input {0} generated'.format(devname))

        uids, mon = gen_monitor_io((pos_x, pos_y), '', 'WRTD-IN.xml', 'HR.WRTD.BQ-HB1.IN', devname)

        refs[0][i+1] = uids
        fstr.append(mon)

        fstr.append(gen_label((pos_x+7, pos_y-lab), (25, 75), '1.5707963267948966', name, ('Dialog', '0', '12')))

    # Outputs
    for i, name in enumerate(outputs):
        pos_x = sta_x
        pos_y = sta_y + (i+1)*inc_y + shift
        devname = 'HR.WRTD.{0}.OUT'.format(name)
        print('--> output {0} generated'.format(devname))

        uids, mon = gen_monitor_io((pos_x, pos_y), '', 'WRTD-OUT.xml', 'HR.WRTD.BQHT-B1.OUT', devname)

        refs[i+1][0] = uids
        fstr.append(mon)

        fstr.append(gen_label((pos_x-lab, pos_y+7), (75, 25), '0.0', name, ('Dialog', '0', '12')))

    # Triggers
    tstr = []
    for i, (out_name, in_name) in enumerate(triggers):
        ii = inputs.index(in_name)
        io = outputs.index(out_name)
        pos_x = ii*inc_x + shift - 3
        pos_y = io*inc_y + shift - 3
        devname = 'HR.WRTD.{0}.{1}.TRIG'.format(out_name, in_name)
        print('--> trigger {0} generated'.format(devname))

        # Colour coding based on if planes/beams match
        # Matching ------> ena=grn; dis=red
        # Not matching --> ena=grn; dis=gry
        in_plane = in_name.split('-')[-1]
        out_plane = out_name.split('-')[-1]
        l = min((len(in_plane), len(out_plane)))

        dis_color = '255,100,100,255' if in_plane[-l:] == out_plane[-l:] else '100,100,100,255'

        uids, mon = gen_monitor_trig((pos_x, pos_y), '', 'WRTD-TRIG.xml',
                                     'HR.WRTD.BQHT-B1.BQ-HB1.TRIG', devname, dis_color, '100,255,100,255')
        j = i % len(inputs)
        k = i // len(inputs)

        refs[k+1][j+1] = uids
        tstr.append(mon)

    container_x = sta_x + inc_x
    container_y = sta_y + inc_y
    container_w = len(inputs)*inc_x + shift*2
    container_h = len(outputs)*inc_y + shift*2

    fstr.extend(gen_container((container_x, container_y), (container_w, container_h), parent_uid, tstr, '0,0,0,255'))

    # End panel
    fstr.append('</MonitorPanel>')

    print('done!')
    print('recommended window size {0}x{1}'.format(winsize_x, winsize_y))

    # Write file
    outpath = os.path.dirname(__file__)

    with open(os.path.join(outpath, 'inspector', '{name}.xml'.format(name=panel_name)), 'w') as f:
        f.write('\n'.join(fstr))

    # # Write launcher script
    # fstr = [
    #     '#!/bin/bash',
    #     'DIR=$( dirname $( which $0 ))/inspector',
    #     '/mcr/bin/jws http://abwww/ap/dist/ade/ade-inspector/PRO/Inspector.jnlp?arg0=--panel='
    #     '$DIR/{name}.xml\&arg1=--viewmode\&arg2=--size={x}x{y}\&user.dir=$DIR'.format(
    #         name=panel_name, x=winsize_x, y=winsize_y
    #     ),
    #     ''
    # ]

    # with open(os.path.join(outpath, 'launch_{name}.sh'.format(name=panel_name.lower().replace('-', '_'))), 'w') as f:
    #     f.write('\n'.join(fstr))


if __name__ == '__main__':
    nodes = Nodes()

    # WRTD inputs
    inputs_b1 = nodes.get_names(direction='input', beam=1, type='oper')
    inputs_b2 = nodes.get_names(direction='input', beam=2, type='oper')
    lab_inputs_b1 = nodes.get_names(direction='input', beam=1, type='lab')
    lab_inputs_b2 = nodes.get_names(direction='input', beam=2, type='lab')

    # WRTD outputs
    outputs_b1 = nodes.get_names(direction='output', beam=1, type='oper')
    outputs_b2 = nodes.get_names(direction='output', beam=2, type='oper')
    lab_outputs_b1 = nodes.get_names(direction='output', beam=1, type='lab')
    lab_outputs_b2 = nodes.get_names(direction='output', beam=2, type='lab')

    generate_panel(inputs_b1 + inputs_b2,
                   outputs_b1 + outputs_b2,
                   'LIST-OPER')

    generate_panel(inputs_b1 + lab_inputs_b1 + inputs_b2 + lab_inputs_b2,
                   outputs_b1 + lab_outputs_b1 + outputs_b2 + lab_outputs_b2,
                   'LIST-LAB')

# EOF
