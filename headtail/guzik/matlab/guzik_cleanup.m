if libisloaded('GSA_SDK')
    % Call termination routine
    disp('Calling GSA_SysDone')
    calllib('GSA_SDK', 'GSA_SysDone', libpointer );

    % Clear workspace
    clear;

    % Unload GSA_SDK
    unloadlibrary('GSA_SDK');
end
