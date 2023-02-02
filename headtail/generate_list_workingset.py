#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Script to automatically generate LIST Inspector workingset

WARNING: This is very hacky and should not be trusted :-)

Copyright (c) CERN 2016

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

import os

from modules.list_nodes import Nodes


def gen_input(name):
    return '''<DEVICE NAME="{name}">
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="deadTime_min" NAME="DeadTime"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="sequenceNo" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay_min" NAME="Delay"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="deadTime_max" NAME="DeadTime"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="hostName" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="deadTime" NAME="DeadTime"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="" NAME="Acquire"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay_max" NAME="Delay"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="deadTime_units" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="sentPackets" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="customTopic" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="armed" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestMessagePortId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="" NAME="Disarm"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="fwkTopic" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="systemId" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="timestampSecond" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="atTimePicoseconds" NAME="TrigAtTime"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestMessageTimestampSeconds" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="type" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="taggedPulses" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="deadTime_units" NAME="DeadTime"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="enabled" NAME="Enabled"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="enableDiagMode" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="portId" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="" NAME="Reset"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay_units" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestMessageSequenceCounter" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="traceDevices" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="deadTime" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="WRTimeOK" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="sequenceNumber" NAME="TrigAtTime"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay_units" NAME="Delay"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="triggerId" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="timestampPicosecond" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="requestState" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="enabledPoints" NAME="LogSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="mode" NAME="Mode"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestMessageSystemId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestMessageTimestampPicoseconds" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="requestConfig" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestMessageTriggerId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="portNumber" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="asString" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="" NAME="ReadHwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="triggered" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="mode" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="bypassActions" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="" NAME="Arm"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="sentTriggers" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay" NAME="Delay"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="enabled" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="atTimeSeconds" NAME="TrigAtTime"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay" NAME="HwSettings"/>
</DEVICE>'''.format(name=name)


def gen_output(name):
    return '''<DEVICE NAME="{name}">
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="receivedMessages" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestLostPortId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestReceivedPortId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="deadTime_units" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="triggerName" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestExecutedTimestampPicoseconds" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestExecutedTriggerId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="missedPulsesNoTiming" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestReceivedTriggerId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="traceDevices" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="deadTime" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestExecutedSystemId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="asString" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="triggerId" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="fwkTopic" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestEnqueuedTimestampSeconds" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="armed" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="enabledPoints" NAME="LogSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="customTopic" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="" NAME="Acquire"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="mode" NAME="Mode"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestExecutedPortId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="enableDiagMode" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="pulseWidth_units" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="hostName" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestLostTriggerId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="" NAME="ReadHwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestExecutedSequenceCounter" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="receivedLoopback" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="pulseWidth" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestEnqueuedTimestampPicoseconds" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestEnqueuedPortId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="requestConfig" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="timestampSecond" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestReceivedTimestampSeconds" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestLostSequenceCounter" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="timestampPicosecond" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestExecutedTimestampSeconds" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestReceivedTimestampPicoseconds" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="bypassActions" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="sequenceNo" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="missedPulsesDeadTime" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="deadTime_max" NAME="DeadTime"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="executedPulses" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="portId" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="portNumber" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="" NAME="Disarm"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="" NAME="Reset"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestEnqueuedTriggerId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="deadTime_units" NAME="DeadTime"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="mode" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="deadTime_min" NAME="DeadTime"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="type" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestReceivedSystemId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestEnqueuedSequenceCounter" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="" NAME="Arm"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="enabled" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="missedPulsesOverflow" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="deadTime" NAME="DeadTime"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="requestState" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="systemId" NAME="Log"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestReceivedSequenceCounter" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestLostTimestampSeconds" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="missedPulsesLate" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="enabled" NAME="Enabled"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestLostTimestampPicoseconds" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestEnqueuedSystemId" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latestLostSystemId" NAME="Acquisition"/>
</DEVICE>'''.format(name=name)


def gen_trig(name):
    return '''<DEVICE NAME="{name}">
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay_max" NAME="TriggerDelay"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="" NAME="ReadHwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="" NAME="Acquire"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay_min" NAME="ConditionDelay"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="hostName" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="portNumber" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="triggerDelay_units" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay_min" NAME="TriggerDelay"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="customTopic" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latencyAverage_units" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="requestState" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay_units" NAME="TriggerDelay"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="enabled" NAME="TriggerEnabled"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="enableDiagMode" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="conditionDelay" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay_max" NAME="ConditionDelay"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="conditionSystemId" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay" NAME="ConditionDelay"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="bypassActions" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="triggerEnabled" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay" NAME="TriggerDelay"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="executedPulses" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="triggerPortId" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="conditionEnabled" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="missedPulses" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="conditionTriggerId" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latencyAverage" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="traceDevices" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="requestConfig" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latencyWorst_units" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="fwkTopic" NAME="DiagnosticSetting"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="enabled" NAME="ConditionEnabled"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="triggerSystemId" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="conditionDelay_units" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="triggerDelay" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="triggerTriggerId" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="latencyWorst" NAME="Acquisition"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="conditionPortId" NAME="HwSettings"/>
<PROPERTY DEVICE_NAME="{name}" FIELD_NAME="delay_units" NAME="ConditionDelay"/>
</DEVICE>'''.format(name=name)


def generate_workingset(inputs, outputs):
    triggers = [(o, i) for o in outputs for i in inputs]

    fstr = []

    # Start of workingset
    fstr.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    fstr.append('<WORKINGSET NAME="LIST">')

    # Inputs
    fstr.append('<CATEGORY NAME="LIST Inputs">')
    for name in inputs:
        devname = 'HR.WRTD.{0}.IN'.format(name)
        print('adding device {0}'.format(devname))
        fstr.append(gen_input(devname))
    fstr.append('</CATEGORY>')

    # Outputs
    fstr.append('<CATEGORY NAME="LIST Outputs">')
    for name in outputs:
        devname = 'HR.WRTD.{0}.OUT'.format(name)
        print('adding device {0}'.format(devname))
        fstr.append(gen_output(devname))
    fstr.append('</CATEGORY>')

    # Triggers
    fstr.append('<CATEGORY NAME="LIST Triggers">')
    for out_name, in_name in triggers:
        devname = 'HR.WRTD.{0}.{1}.TRIG'.format(out_name, in_name)
        print('adding device {0}'.format(devname))
        fstr.append(gen_trig(devname))
    fstr.append('</CATEGORY>')

    # End of workingset
    fstr.append('</WORKINGSET>')

    dirname = os.path.expanduser('~/.inspector/')

    if not os.path.isdir(dirname):
        print('creating directory {0}'.format(dirname))
        os.mkdir(dirname)

    filename = os.path.join(dirname, 'LIST.dat')

    with open(filename, 'w') as f:
        f.write('\n'.join(fstr))

    print('workingset saved to {0}'.format(filename))


if __name__ == '__main__':
    nodes = Nodes()
    inputs = nodes.get_names(direction='input',)
    outputs = nodes.get_names(direction='output')
    generate_workingset(inputs, outputs)

# EOF
