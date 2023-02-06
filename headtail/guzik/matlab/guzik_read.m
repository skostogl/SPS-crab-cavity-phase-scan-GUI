basename = 'Z:\SPS.BQHT\';
device = 'SPS.BQHT';
context = 'SPS.USER.ALL';

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

channel_count = 4;
rc_idx = 0;

while 1

disp('----------------------------------------')
disp(['[', datestr(now), '] Getting parameters'])

params = matlabJapc.staticGetSignal(context, [device, '/DeviceParameters']);

acq_len_ms = params.acqLength;
sectors = params.acqSegments;
gain_sum_v = params.verSumGain;
gain_sum_h = params.horSumGain;
gain_delta_v = params.verDeltaGain;
gain_delta_h = params.horDeltaGain;
cycle = params.cycle;
stamp = params.stamp;
enable = params.enabled;

disp(['[', datestr(now), ']', ...
    ' cycle=', cycle, ...
    ' stamp=', sprintf('%d', stamp) ...
])
disp(['[', datestr(now), ']', ...
    ' length=', num2str(acq_len_ms), ...
    ' sectors=', num2str(sectors), ...
    ' enable=', num2str(enable), ...
    ' verSum=', num2str(gain_sum_v), ...
    ' horSum=', num2str(gain_sum_h), ...
    ' verDel=', num2str(gain_delta_v), ...
    ' horDel=', num2str(gain_delta_h) ...
])

gains = [gain_sum_v, gain_sum_h, gain_delta_v, gain_delta_h];

acq_len = acq_len_ms * 1000 * 1000 * 10;

if enable == 1
    %Get configuration idenifier for specified device (with index 0)
    % and specified list of inputs ('CH1;CH2')
    rc_config = 0;
    [res_code, inp_list,rc_config] = calllib('GSA_SDK', 'GSA_ReadChBestConfigGet', rc_idx,'GSA_READ_CH_INP4','CH1;CH2;CH3;CH4',rc_config);

    if res_code ~= 0
        %Prepare structures for acquisition
        arg = libstruct('GSA_Data_ARG_TAG',struct('hdr', struct('version', 446000)));
        res = libstruct('GSA_Data_RES_Matlab_TAG', struct('res1', struct('common',struct('data_len', acq_len ) ) ) );

        %Fill structures with default values
        [res_code] = calllib('GSA_SDK','GSA_Data_Multi_Info', arg, channel_count, res, libpointer );

        if res_code ~= 0
            %Fill specific argument fields
            arg.common.rc_conf = rc_config;
            arg.common.rc_idx = rc_idx;
            arg.common.acq_len=acq_len;
            arg.common.trigger_mode =  'GSA_DP_TRIGGER_MODE_EXTERNAL';
            arg.common.sectors_num = 1;
            arg.common.input_gains_dB = [gain_sum_v, gain_sum_h, gain_delta_v, gain_delta_h];
            arg.common.gain_dB = 0;
            arg.common.trigger_input = 0;
            arg.common.trigger_condition = 'GSA_DP_TRIGGER_CONDITION_RISING_SLOPE';
            arg.common.trigger_threshold_V = 0.5;
            arg.common.acq_timeout = 1;
            arg.hdr.op_command = 'GSA_OP_FULFILL';

            %Create buffer for storing acquired data
            res.res1.common.data.size = acq_len;
            res.res1.common.data.arr = zeros(1,acq_len);
            res.res2.common.data.size = acq_len;
            res.res2.common.data.arr = zeros(1,acq_len);
            res.res3.common.data.size = acq_len;
            res.res3.common.data.arr = zeros(1,acq_len);
            res.res4.common.data.size = acq_len;
            res.res4.common.data.arr = zeros(1,acq_len);

            %Do acquisition
            disp(['[', datestr(now), '] Doing acquisition']);
            [res_code] = calllib('GSA_SDK', 'GSA_Data_Multi', arg, channel_count, res);

            if res_code ~= 0
                matlabJapc.staticSetSignal(context, [device, '/DeviceCommand#state'], 2);

                %dirname = '';
                dirname = datestr(now, 'yyyy_mm_dd');

                if ~exist([basename, dirname], 'dir')
                    mkdir(basename, dirname);
                end

                if ~strcmp(cycle, '')
                    cyclesplit = strsplit(cycle, '.');
                    cyclename = ['_', char(cyclesplit(3))];
                else
                    cyclename = '';
                end

                foutname = [device, cyclename, '_', datestr(now, 'yyyymmdd_HHMMSS') ,'.h5'];
                fname = [device, cyclename, '_', datestr(now, 'yyyymmdd_HHMMSS') ,'.h5.tmp'];
                fpath = [basename, dirname, '\', fname];

                disp(['[', datestr(now), '] Saving to: ', fpath]);

                %Handle acquired data
                r = res.res1.common;
                hwchname = ['/', regexprep(char(r.used_input_label), '\x0', '')];
                chname = '/vertical/sum';
                disp(['[', datestr(now), '] Saving: ', chname, ' (', hwchname, ')']);
                h5create(fpath, chname, r.data_len, 'Datatype', 'uint8');
                h5writeatt(fpath, chname, 'sampling_period', r.sampling_period_ns*1e-9);
                h5writeatt(fpath, chname, 'data_offset', r.data_offset);
                h5writeatt(fpath, chname, 'ampl_resolution', r.ampl_resolution*1e-3);
                h5writeatt(fpath, chname, 'segment_count', 1.0);
                %h5writeatt(fpath, chname, 'input_gain', r.input_gain);
                h5write(fpath, chname, r.data.arr(1:r.data_len))

                r = res.res2.common;
                hwchname = ['/', regexprep(char(r.used_input_label), '\x0', '')];
                chname = '/horizontal/sum';
                disp(['[', datestr(now), '] Saving: ', chname, ' (', hwchname, ')']);
                h5create(fpath, chname, r.data_len, 'Datatype', 'uint8');
                h5writeatt(fpath, chname, 'sampling_period', r.sampling_period_ns*1e-9);
                h5writeatt(fpath, chname, 'data_offset', r.data_offset);
                h5writeatt(fpath, chname, 'ampl_resolution', r.ampl_resolution*1e-3);
                h5writeatt(fpath, chname, 'segment_count', 1.0);
                %h5writeatt(fpath, chname, 'input_gain', r.input_gain);
                h5write(fpath, chname, r.data.arr(1:r.data_len))

                r = res.res3.common;
                hwchname = ['/', regexprep(char(r.used_input_label), '\x0', '')];
                chname = '/vertical/delta';
                disp(['[', datestr(now), '] Saving: ', chname, ' (', hwchname, ')']);
                h5create(fpath, chname, r.data_len, 'Datatype', 'uint8');
                h5writeatt(fpath, chname, 'sampling_period', r.sampling_period_ns*1e-9);
                h5writeatt(fpath, chname, 'data_offset', r.data_offset);
                h5writeatt(fpath, chname, 'ampl_resolution', r.ampl_resolution*1e-3);
                h5writeatt(fpath, chname, 'segment_count', 1.0);
                %h5writeatt(fpath, chname, 'input_gain', r.input_gain);
                h5write(fpath, chname, r.data.arr(1:r.data_len))

                r = res.res4.common;
                hwchname = ['/', regexprep(char(r.used_input_label), '\x0', '')];
                chname = '/horizontal/delta';
                disp(['[', datestr(now), '] Saving: ', chname, ' (', hwchname, ')']);
                h5create(fpath, chname, r.data_len, 'Datatype', 'uint8');
                h5writeatt(fpath, chname, 'sampling_period', r.sampling_period_ns*1e-9);
                h5writeatt(fpath, chname, 'data_offset', r.data_offset);
                h5writeatt(fpath, chname, 'ampl_resolution', r.ampl_resolution*1e-3);
                h5writeatt(fpath, chname, 'segment_count', 1.0);
                %h5writeatt(fpath, chname, 'input_gain', r.input_gain);
                h5write(fpath, chname, r.data.arr(1:r.data_len))

                matlabJapc.staticSetSignal(context, [device, '/DeviceCommand#path'], [dirname, '/', foutname]);
                matlabJapc.staticSetSignal(context, [device, '/DeviceCommand#state'], 4);

                %upfile = fopen([basename, '\.latest'], 'w');
                %fprintf(upfile, '%s\n', foutname);
                %fclose(upfile);
            end
        end
    end

    if res_code == 0
        disp(['[', datestr(now), '] Guzik timeout']);
        %calllib('GSA_SDK', 'GSA_ErrorHandle');
    end
else
    disp(['[', datestr(now), '] Timer expired, nothing to do']);
    pause(1);
end

fclose('all');

end
