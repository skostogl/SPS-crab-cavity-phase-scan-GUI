from cpymad.madx import Madx
import os

if os.path.exists('sps'):
        os.remove('sps')
os.symlink(os.path.abspath("/afs/cern.ch/eng/acc-models/sps/2021"), 'sps')

mad = Madx()
mad.input('''

system,"[ ! -e sps ] && [ -d /afs/cern.ch/eng/acc-models/sps/2021 ] && ln -nfs /afs/cern.ch/eng/acc-models/sps/2021 sps";
system,"[ ! -e sps ] && git clone https://gitlab.cern.ch/acc-models/acc-models-sps -b 2021 sps";

option, -echo;

call,file="sps/sps.seq";
call,file="sps/strengths/lhc_q26.str";

beam;

use,sequence=sps;

twiss;


 freq = 400;
 CRAVITY.1 : RFMULTIPOLE, VOLT=0, FREQ=freq, TILT=0, KNL:={knl1_cravity1}, PNL:={pnl1_cravity1};
 CRAVITY.2 : RFMULTIPOLE, VOLT=0, FREQ=freq, TILT=0, KNL:={knl1_cravity2}, PNL:={pnl1_cravity2};

 ! install crab cavities
 ! remove markers and instruments
 USE, period=SPS, range=#S/#E;
 select, flag=seqedit, class=instrument;
 select, flag=seqedit, class=marker;
 seqedit, sequence=SPS;
        !remove, element=BEGI.10010;             !zero length element
        !remove, element=VVFB.21801;             !zero length element
        !remove, element=VVFB.21877;             !zero length element
        !remove, element=QSPL.31809;             !zero length element
        !remove, element=VVFB.61801;             !zero length element
        !remove, element=QSPL.61809;             !zero length element
        !remove, element=VVFB.61877;             !zero length element
        !remove, element=selected;
        install, element=CRAVITY.1, at=6312.7213;
        install, element=CRAVITY.2, at=6313.3213;
        flatten;
 endedit;
 USE, period=SPS, range=#S/#E;



call,file="sps/toolkit/macro.madx";

qx0=26.13;
qy0=26.18;

exec, sps_match_tunes(qx0,qy0);

twiss;

system, "test -f lhc_q26.str && rm lhc_q26.str";
assign, echo="lhc_q26.str";
print, text="! Q26 Optics for LHC beams";
print, text="";
assign, echo="terminal";


exec,sps_save_optics("lhc_q26.str");
''')

mad.table["twiss"].dframe().to_parquet("twiss_SPS_q26.parquet")

print(f'CC1 bety (m)= {mad.table["twiss"].dframe().loc["cravity.1"].bety}')
print(f'CC1 muy (m)= {mad.table["twiss"].dframe().loc["cravity.1"].muy}')
print(f'CC2 bety (m)= {mad.table["twiss"].dframe().loc["cravity.2"].bety}')
print(f'CC2 muy (m)= {mad.table["twiss"].dframe().loc["cravity.2"].muy}')
print(f'WS bwsrc.51637 betx (m)= {mad.table["twiss"].dframe().loc["bwsrc.51637"].betx}')
print(f'WS bwsrc.51637 Dx (m)= {mad.table["twiss"].dframe().loc["bwsrc.51637"].dx}')
print(f'WS bwsrc.41678 bety (m)= {mad.table["twiss"].dframe().loc["bwsrc.41678"].bety}')
print(f'HT  muy (m)= {mad.table["twiss"].dframe().loc["bpcl.42171"].muy}, {mad.table["twiss"].dframe().loc["cravity.1"].muy-mad.table["twiss"].dframe().loc["bpcl.42171"].muy}')
print(f'HT  bety (m)= {mad.table["twiss"].dframe().loc["bpcl.42171"].bety}')
