import glob
import numpy as np
import pandas as pd
import imp
import time
import sys
from matplotlib import cm
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib.gridspec as grd
import datetime
from scipy.interpolate import interp1d

from headtail.modules import bqht

def string2unix(s):
    return time.mktime(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f").timetuple())

def unix2string(f):
    return datetime.datetime.fromtimestamp(int(f)).strftime('%Y-%m-%d %H:%M:%S.%f')

def prep_file(name):
    htf = ht.open_file(f'{name}')
    htf.locate_bunches()
    htf.optimise_overlap()
    for p, s in htf.planes_signals:
        htf[p][s].remove_baseline = False # Don't remove baseline
        htf[p][s].align = True            # Get aligned to the same X points
    return htf

def calc_means(htf, N):
    pts = int(htf.horizontal.sigma.samples_per_bunch)
    M = int(htf.horizontal.sigma.number_of_turns/N)
    means_delta = []
    means_sigma = []
    for i in range(N):
        mean_delta = np.zeros(pts)
        mean_sigma = np.zeros(pts)
        for j in range(M):
            x, y = htf.vertical.sigma[i*M+j,0]
            #if j==0:
            #    print(x,y, "heree6")
            mean_sigma += y
            x, y = htf.vertical.delta[i*M+j,0]
            mean_delta += y
        mean_delta /= M
        mean_sigma /= M
        means_delta.append(mean_delta)
        means_sigma.append(mean_sigma)
    return (np.array(means_sigma), np.array(means_delta), x)


def getOrbitResponse(beta_ht, total_Q, beta_cc, dmuy):
    PAY=dmuy*(2*np.pi)
    orbitResponse1 = np.sqrt(beta_ht)/(2*np.sin(np.pi*total_Q))
    orbitResponse2 = np.sqrt(beta_cc)*np.cos(np.pi*total_Q - PAY)
    orbitResponse  = orbitResponse1*orbitResponse2
    return orbitResponse

def getHTtraces(sigma, delta, x_r, x_l, normPositionFactor): 
    mid = np.argmax(sigma[-1])
    a = mid - x_r
    b = mid + x_l

    amp_factor = 1/(normPositionFactor) 
    
    signal = (delta[-1] - delta[0])[a:b] / sigma[-1][a:b]
    return signal*amp_factor, sigma[-1][a:b]

def yGauss(x):
    sig = 2.22 #mm
    intensity = 1
    return intensity/(sig*np.sqrt(2*np.pi))*np.exp(-x*x/(2*sig*sig))

def gauss(x, *p):
    A, mu, sigma = p
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))

def varFunc(y,z, coeff):
    return yGauss(y)*gauss(z, coeff[0], coeff[1], coeff[2])

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx

def mirrored2(maxval, num):
    return np.linspace(-maxval, maxval, num)

ht         = bqht.BQHT(system='SPS')
def ht_analysis(HT_dataDir, EGeV, interesting_files, my_beta_ht, my_total_Q, my_beta_cc, my_dmuy, ht_calibration_factor, save_folder):
    
    Eb         = EGeV*1e9
    
    import pathlib
    pathlib.Path(save_folder).mkdir(parents=True, exist_ok=True)

    files_list = [f"{HT_dataDir}/{i}" for i in interesting_files["filename"]]

    time_stamp_list   = []
    deg_list          = []
    my_Vcc_list       = []
    ignore_files_list = [] 
    
    skipped           = []
    res_orbit = []
    message = "\n\nRunning HT analysis\n\n"    
    for i, name in enumerate(files_list[:]):
        message += str(interesting_files["deg"][i]) 
        message+="\n"
        current_filename = interesting_files["filename"][i]
        save_png_crab = f"{save_folder}/crab_{current_filename}.png"
        save_parquet_crab = f"{save_folder}/results_{current_filename}.parquet"
    
        if name.split("/")[-1] in ignore_files_list:
            print(f'file {name.split("/")[-1]} ignored')
            continue
    
        print(f'Chosen file for study: {name}')
        message += f'Chosen file for study: {name}' 
        message+="\n"
    
        # Compute timestamp from file name
        time_stamp_temp = name[-9:-3]
        time_stamp = ':'.join(time_stamp_temp[i:i+2] for i in range(0, len(time_stamp_temp), 2))
    
        htf_0 = prep_file(name)
    
        # Remove baseline from delta signals: split acquisitions in 2 parts, before and after RF synchronization to subtract baseline in delta signal, see Natalia's thesis
        N = 2
        sigma_0, delta_0, time = calc_means(htf_0, N) # time: time within the bunch [s]
        # Acquisitions filtering: if the signal is low, max of sigma_0 will be very small
        if np.sum(sigma_0/np.amax(sigma_0)) > 300: #another filtering for not good files
            print(f'{i} skipped')
            skipped.append(i)
            continue
    
        # Convert from arbitrary units to mm
        x_r = 15
        x_l = 16
        crabwave, sigma = getHTtraces(sigma_0,  delta_0, x_r, x_l, ht_calibration_factor)
        #print(len(crabwave), "crabwave")
    
        # The crabbing signal is around the maximum of the sigma signal, focus around this longitudinal regime as we are interested in t=z=0
        max_v = np.argmax(sigma_0[-1])
        x_min  = max_v - x_r
        x_max  = max_v + x_l
        maxval = time[x_min:x_max][-1]- time[x_min:x_max][0]
        num    = len(time[x_min:x_max])
        long_position = mirrored2(maxval/2, num)
        #print(np.diff(long_position*1e9))
        x = np.arange(long_position[0]*1e9, long_position[-1]*1e9, 0.1)
        #x = np.arange(long_position[0]*1e9, long_position[-1]*1e9, np.diff(long_position*1e9)[0])
        #print(len(x), " x", np.diff(long_position*1e9)[0])
    
        # Orbit signal interpolated
        crabInterp = interp1d(x, crabwave, bounds_error=False, fill_value=0)
    
        # To compute kick from orbit, calculates the other factors (cosine and sine) in formula
        orbitResponse = getOrbitResponse(my_beta_ht, my_total_Q, my_beta_cc, my_dmuy)
 
        # Fit sigma signal
        p0 = [2000., 0., 0.18]
        coeff, var_matrix = curve_fit(gauss, x, sigma, p0=p0)
    
        # Compute colorbar
        yvals = np.arange(-6,6,np.diff(long_position*1e9)[0])
        zvals = x
        yy,zz = np.meshgrid(yvals,zvals)
        aa = varFunc(yy-crabInterp(zz),zz, coeff)#/(np.trapz(gauss(zvals, coeff[0], coeff[1], coeff[2]),x=zvals))
    
        # Find index closer to t=z=0
        value_closer_to_zero, index_for_z_0 = find_nearest(zvals, 0)
        print(f'zvals for index {index_for_z_0} = {zvals[index_for_z_0]}')
        message += f'zvals for index {index_for_z_0} = {zvals[index_for_z_0]}' 
        message+="\n"
    
        # Voltage from orbit: Vcc = - kick* Eb/q, kick = orbit_meas/orbit_response
    
        message +=f"crab[z0]={crabInterp(zvals)[index_for_z_0]}"
        message+="\n"
        res_orbit.append(crabInterp(zvals)[index_for_z_0])
    
        Vcc_interp =  -crabInterp(zvals)*Eb/(orbitResponse*1e9)
        my_Vcc     = Vcc_interp[index_for_z_0] # Vcc at z=t=0
        my_Vcc_list.append(my_Vcc)
        print(f'Vcc for z=t=0 = {my_Vcc} MV')
        message +=f"Vcc for z=t=0 = {my_Vcc} MV"
        message+="\n"
        print("")
    
        # Plotting part
        fig = plt.figure(figsize=(8,8))
        gs  = grd.GridSpec(2, 2, height_ratios=[10,10], width_ratios=[8,1], wspace=0.1)
        ax1 = plt.subplot(gs[2])
        cax = ax1.pcolormesh(zz, yy, aa/np.amax(aa), cmap = cm.jet)
    
        colorax = plt.subplot(gs[3])
        cbar = plt.colorbar(cax, cax=colorax)
        cbar.set_label('Norm. Intensity', fontsize=16)
        colorax.tick_params(axis='both', labelsize=18)
        ax2 = plt.subplot(gs[0])
        ax2.plot(zvals, -crabwave*Eb/(orbitResponse*1e9), color='r')
        ax2.plot(zvals, -crabInterp(zvals)*Eb/(orbitResponse*1e9), color='g', ls='--')
    
    
        ax2.axes.get_xaxis().set_visible(False)
        ax22 = ax2.twinx()
        ax22.plot(x, sigma/np.amax(sigma), color='k', linestyle='dashed', label='Sum Signal')
        ax22.set_ylabel('Sum Signal [A.U.]', fontsize=16)
        ax22.tick_params(axis='both', which='both', labelsize=18)
        ax22.plot([0],[0.1],color='r', label=r'$V_{CC}$')
        ax22.legend(loc=1, frameon=False, fontsize=12)
        #ax22.set_ylim([0,1])
    
        ax2.set_ylim(-2.4,2.1)
        ax1.set_xlabel('t [ns]', fontsize=18)
        ax1.set_ylabel('y [mm]', fontsize=18)
        ax2.set_ylabel(r'$V_{CC}\ \mathrm{[MV]}$', fontsize=18)
        ax1.tick_params(axis='both', which='both', labelsize=18)
        ax2.tick_params(axis='both', which='both', labelsize=18)
        fig.subplots_adjust(left=0.16, hspace=0.05, top=0.905)
        plt.suptitle('Crabbing Voltage from Head-Tail Monitor \n' + unix2string(htf_0.acq_stamp/1e9)[:-7] + f' Phase {interesting_files["deg"][i]} deg', fontsize=18)
        #plt.savefig(f'figures/' + unix2string(htf_0.acq_stamp/1e9)[11:-7].replace(':','')+'.png')
        #plt.show()
        time_stamp_list.append(time_stamp)
        deg_list.append(interesting_files["deg"][i])
        fig.savefig(save_png_crab)
        pd.DataFrame({"time":[time_stamp_list[-1]], "voltage":[my_Vcc_list[-1]], "phase": [deg_list[-1]]}).to_parquet(save_parquet_crab) 
    df = pd.DataFrame(list(zip(time_stamp_list, my_Vcc_list, deg_list)), columns =['Time', 'myVcc at t zero[MV]', 'deg'])
    df.to_parquet(f"{save_folder}/results.parquet")
    return df, message

def test_func_B(x, a, b, phi, d):
    return a * np.sin(b * x + phi) + d

def run_fit(df, save_folder):
    df.sort_values(by='deg', inplace=True)
    
    #fig, ax = plt.subplots()
    fig, ax = plt.subplots(figsize=(10,7))
    plt.plot(df.deg, df["myVcc at t zero[MV]"], marker='o', c='b', lw=2, linestyle='', label="Measurements")
    
    df["deg"] = df["deg"].astype(float) 

    df["myVcc at t zero[MV]"] = df["myVcc at t zero[MV]"].astype(float)

    coe, pcov = curve_fit(test_func_B, df.deg, df["myVcc at t zero[MV]"], p0=[1,0, 0, 0])#, bounds=((0.7e6,-np.inf,-np.inf),(np.inf,np.inf,np.inf)))
    
    angle=np.arange(-180, 190, 10)
    plt.plot(angle, test_func_B(np.array(angle), coe[0], coe[1], coe[2], coe[3]), '--', lw=2,c='r', label=f'A={coe[0]:.2f} MV \n'+r'$\theta=$'+f'{coe[2]*180/np.pi:.2f} deg \n'+f'd={coe[3]:.2f} MV')
    
    #plt.plot(df.deg, test_func_B(np.array(df.deg), coe[0], coe[1], coe[2], coe[3]), '--', c='k', label=f'A={coe[0]:.2f} MV \n'+r'$\theta=$'+f'{coe[2]*180/np.pi:.2f} deg \n'+f'd={coe[3]:.2f} MV')
     
    plt.legend()
    plt.axhline(0.0, c='dimgray', lw=0.5)
    plt.axvline(0.0, c='dimgray', lw=0.5)
    
    plt.xlabel("Phase (deg.)")
    plt.ylabel("Voltage (V)")
    fig.savefig(f"{save_folder}/fit.png")
    return coe
