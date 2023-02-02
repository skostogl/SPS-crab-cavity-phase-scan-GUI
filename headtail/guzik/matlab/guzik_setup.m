% Load GSA_SDK
if ~libisloaded('GSA_SDK')
    disp('Loading GSA_SDK')
    loadlibrary('C:\Guzik\GSA Toolkit\x64\GSA_SDK.dll', 'C:\Guzik\GSA Toolkit\GSA_SDK\include\GSA_SDK_MATLAB.h');
end

% Call initialization routine
disp('Calling GSA_SysInit')
calllib('GSA_SDK', 'GSA_SysInit', libpointer);
