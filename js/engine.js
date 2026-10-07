/* HyperAudio © 2026 Noushad M. All rights reserved. */
'use strict';

/* ============================================================
   CONSTANTS
   ============================================================ */
const TAIL_RMS_LIMIT_DB  = -90.0;
const TAIL_PEAK_LIMIT_DB = -80.0;
const IIR_FIR_TOLERANCE_DB = 0.25;
const IR_LENGTH = 8192;
const IR_TAIL = 128;
const SUPPORTED_FS = Object.freeze([44100, 48000]);
const SAFETY_MARGIN_DB = 0.5;      // single headroom requirement (fitter, audit, registry, export)
const PREAMP_STEP_DB = 0.001;      // fitter preamp resolution
const DC_FLOOR_DB = -90.0;       // DC responses below this are treated as equal (both effectively zero)
const FFT_N = 65536;               // zero-padded FFT size for exported-signal peak measurement
const VERSION = '5.1';
const CEIL = Object.freeze({ iem: -1.0, spk: -0.5 });   // single source for limiter ceilings (dBFS)

const FITTER_CONFIG = Object.freeze({
  minSepOctaves: 0.4,
  gainClampHiDb: 12.0,
  gainClampLoDb: -12.0,
  minGainDb: 0.4,
  speakerFcFloorHz: 308,
  refinementSteps: [0.75, 0.4, 0.2, 0.1],
  refinementIterations: 4,
  oppositeSignMinOctaves: 0.8,
  minBandwidthHz: 12,   // fc/Q floor: narrower low-frequency filters ring longer than the 8192-tap IR can represent
  resolvableBandHz: 250
});

/* Exact asset names */
const N = Object.freeze({
  eelIem:   'IEM HyperAudio™ Master v2.0.eel',
  eelSpk:   'Speaker HyperAudio™ Master v2.0.eel',
  eelSIem:  'S+ IEM HyperAudio™ Master.eel',
  eelSSpk:  'S+ Speaker HyperAudio™ Master.eel',
  vdcIem:   'IEM HyperAudio™ DDC.vdc',
  vdcSpk:   'Speaker HyperAudio™ DDC.vdc'
});

/* ============================================================
   SECTION 1 — PRESETS
   ============================================================ */
const PRESETS = Object.freeze({
  EDX_STUDIO_NEUTRAL: {
    id:"EDX_STUDIO_NEUTRAL", name:"Studio Neutral", classification:"Preference (Linear Monitor)",
    filters:[
      {type:'pk',fc:45,g:-5.5,q:0.80},{type:'pk',fc:180,g:-4.2,q:1.40},
      {type:'pk',fc:850,g:1.0,q:1.60},{type:'pk',fc:2250,g:-3.5,q:2.20},
      {type:'pk',fc:3350,g:3.0,q:1.80},{type:'pk',fc:4950,g:-7.5,q:3.60},
      {type:'pk',fc:6300,g:1.5,q:2.50},{type:'pk',fc:7950,g:-8.8,q:4.20},
      {type:'pk',fc:11900,g:-6.5,q:3.00}
    ],
    preampPolicy:{mode:"operator_fixed_conservative",appliedPreampDb:-3.50,safetyMarginDb:0.50},
    filenameBase:"HyperAudio™ KZ Edx Pro Studio Neutral"
  },
  EDX_HARMAN_REFERENCE: {
    id:"EDX_HARMAN_REFERENCE", name:"Harman Reference", classification:"Calibration Baseline (IE 2019)",
    filters:[
      {type:'pk',fc:45,g:-2.5,q:0.80},{type:'pk',fc:180,g:-3.8,q:1.40},
      {type:'pk',fc:850,g:1.8,q:1.60},{type:'pk',fc:2250,g:-3.5,q:2.20},
      {type:'pk',fc:3350,g:4.2,q:1.80},{type:'pk',fc:4950,g:-7.5,q:3.60},
      {type:'pk',fc:6300,g:2.0,q:2.50},{type:'pk',fc:7950,g:-8.8,q:4.20},
      {type:'pk',fc:11900,g:-6.5,q:3.00}
    ],
    preampPolicy:{mode:"operator_fixed_conservative",appliedPreampDb:-5.00,safetyMarginDb:0.50},
    filenameBase:"HyperAudio™ KZ Edx Pro Harman"
  },
  AUTOEQ_CRINACLE_HARMAN: {
    id:"AUTOEQ_CRINACLE_HARMAN", name:"AutoEQ Crinacle", classification:"Comparative Baseline (10-Band)",
    filters:[
      {type:'pk',fc:22,g:-2.1,q:0.52},{type:'pk',fc:170,g:-3.6,q:1.35},
      {type:'pk',fc:840,g:1.6,q:1.65},{type:'pk',fc:2200,g:-3.2,q:2.30},
      {type:'pk',fc:3400,g:5.8,q:1.50},{type:'pk',fc:4900,g:-7.8,q:3.40},
      {type:'pk',fc:6200,g:2.4,q:2.80},{type:'pk',fc:7900,g:-9.6,q:4.50},
      {type:'pk',fc:11800,g:-7.2,q:3.20},{type:'pk',fc:15000,g:2.1,q:1.20}
    ],
    preampPolicy:{mode:"operator_fixed_conservative",appliedPreampDb:-6.70,safetyMarginDb:0.50},
    filenameBase:"HyperAudio™ KZ Edx Pro AutoEQ"
  },
  EDX_WARM_BASS: {
    id:"EDX_WARM_BASS", name:"Warm Bass+", classification:"Preference (Audiophile Warmth)",
    filters:[
      {type:'pk',fc:45,g:0.5,q:0.80},{type:'pk',fc:180,g:-3.8,q:1.40},
      {type:'pk',fc:850,g:2.2,q:1.60},{type:'pk',fc:2250,g:-3.5,q:2.20},
      {type:'pk',fc:3350,g:3.8,q:1.80},{type:'pk',fc:4950,g:-8.0,q:3.60},
      {type:'pk',fc:6300,g:1.5,q:2.50},{type:'pk',fc:7950,g:-9.2,q:4.20},
      {type:'pk',fc:11900,g:-7.5,q:3.00}
    ],
    preampPolicy:{mode:"operator_fixed_conservative",appliedPreampDb:-5.50,safetyMarginDb:0.50},
    filenameBase:"HyperAudio™ KZ Edx Pro Warm Bass"
  },
  EDX_NIGHT_RELAXED: {
    id:"EDX_NIGHT_RELAXED", name:"Night Relaxed", classification:"Preference (Reduced-Treble)",
    filters:[
      {type:'pk',fc:45,g:-3.0,q:0.80},{type:'pk',fc:180,g:-3.5,q:1.40},
      {type:'pk',fc:850,g:1.5,q:1.60},{type:'pk',fc:2250,g:-4.0,q:2.20},
      {type:'pk',fc:3350,g:2.5,q:1.80},{type:'pk',fc:4950,g:-9.0,q:3.60},
      {type:'pk',fc:6300,g:1.0,q:2.50},{type:'pk',fc:7950,g:-10.5,q:4.20},
      {type:'pk',fc:11900,g:-9.0,q:3.00}
    ],
    preampPolicy:{mode:"operator_fixed_conservative",appliedPreampDb:-3.00,safetyMarginDb:0.50},
    filenameBase:"HyperAudio™ KZ Edx Pro Night Control"
  },
  REDMI12_SPEAKER: {
    id:"REDMI12_SPEAKER", name:"Redmi 12 Speaker", classification:"Device Protection & Correction",
    filters:[
      {type:'hpf',fc:220,q:0.70710678},
      {type:'pk',fc:510,g:4.5,q:1.80},
      {type:'pk',fc:1350,g:-3.5,q:2.00},
      {type:'pk',fc:2150,g:-5.0,q:2.20},
      {type:'pk',fc:3270,g:-9.2,q:3.50},
      {type:'pk',fc:5850,g:-5.5,q:2.50},
      {type:'pk',fc:9400,g:-8.0,q:3.00},
      {type:'pk',fc:13500,g:-4.0,q:2.00}
    ],
    preampPolicy:{mode:"operator_fixed_conservative",appliedPreampDb:-5.00,safetyMarginDb:0.50},
    filenameBase:"HyperAudio™ Redmi 12 Speaker"
  }
});

/* ============================================================
   SECTION 2 — EMBEDDED DATA
   ============================================================ */
const DEFAULT_TARGET_GEQ =
"20 -7.2; 21 -7.3; 22 -7.5; 23 -7.5; 24 -7.6; 26 -7.6; 27 -7.6; 29 -7.7; 30 -7.7; 32 -7.7; 34 -7.7; 36 -7.8; 38 -7.8; 40 -7.7; 43 -7.7; 45 -7.7; 48 -7.7; 50 -7.6; 53 -7.7; 56 -7.7; 59 -7.7; 63 -7.7; 66 -7.7; 70 -7.8; 74 -7.9; 78 -7.9; 83 -8.1; 87 -8.2; 92 -8.3; 97 -8.5; 103 -8.7; 109 -8.8; 115 -9.0; 121 -9.0; 128 -9.1; 136 -9.3; 143 -9.3; 151 -9.3; 160 -9.2; 169 -9.1; 178 -9.0; 188 -8.9; 199 -8.7; 210 -8.5; 222 -8.3; 235 -8.1; 248 -7.8; 262 -7.6; 277 -7.3; 292 -7.0; 309 -6.7; 326 -6.4; 345 -6.1; 364 -5.7; 385 -5.4; 406 -5.1; 429 -4.8; 453 -4.5; 479 -4.2; 506 -4.0; 534 -3.7; 565 -3.4; 596 -3.2; 630 -2.9; 665 -2.7; 703 -2.5; 743 -2.3; 784 -2.1; 829 -2.0; 875 -2.0; 924 -2.1; 977 -2.2; 1032 -2.4; 1090 -2.8; 1151 -3.2; 1216 -3.7; 1284 -4.0; 1357 -4.5; 1433 -4.8; 1514 -5.2; 1599 -5.6; 1689 -6.1; 1784 -6.5; 1885 -7.0; 1991 -7.5; 2103 -7.8; 2221 -7.9; 2347 -7.4; 2479 -6.4; 2618 -5.2; 2766 -4.0; 2921 -2.9; 3086 -2.0; 3260 -1.4; 3443 -1.1; 3637 -1.1; 3842 -1.5; 4058 -2.2; 4287 -3.4; 4528 -5.1; 4783 -6.7; 5052 -7.2; 5337 -5.5; 5637 -2.8; 5955 -1.2; 6290 -0.2; 6644 -0.5; 7018 -1.8; 7414 -2.5; 7831 -2.4; 8272 -1.9; 8738 -1.7; 9230 -1.6; 9749 -1.7; 10298 -2.2; 10878 -2.7; 11490 -3.3; 12137 -4.0; 12821 -4.8; 13543 -5.7; 14305 -6.7; 15110 -7.9; 15961 -9.1; 16860 -10.4; 17809 -11.9; 18812 -13.5; 19871 -15.1";

const DEFAULT_KZ_CSV =
`frequency,raw
20.00,13.99
22.09,13.91
24.40,13.85
26.96,13.72
29.78,13.57
32.89,13.38
36.33,13.16
40.14,12.90
44.33,12.64
48.97,12.34
54.10,11.98
59.76,11.57
66.01,11.11
72.91,10.63
80.54,10.13
88.97,9.59
98.28,9.00
108.56,8.38
119.92,7.78
132.46,7.11
146.32,6.37
161.63,5.75
178.54,5.31
197.22,4.70
217.85,4.02
240.64,3.40
265.82,2.81
293.63,2.22
324.35,1.63
358.28,1.06
395.77,0.60
437.18,0.16
482.91,-0.23
533.44,-0.58
589.25,-0.86
650.89,-1.00
718.99,-1.02
794.22,-1.21
877.31,-0.80
969.09,-0.23
1070.48,0.58
1182.48,1.50
1306.19,2.50
1442.85,3.70
1593.80,5.27
1760.55,7.17
1944.74,9.17
2148.20,10.94
2303.17,11.39
2544.13,10.46
2810.30,8.71
3104.32,7.28
3429.10,6.54
3787.86,6.71
4184.15,7.96
4621.91,10.66
5054.91,12.64
5528.49,9.84
6046.42,7.30
6612.88,5.40
7232.41,6.05
7909.98,10.63
8651.03,5.12
9461.51,-1.15
10347.91,-2.35
11317.36,4.29
12013.60,8.04
13139.10,-3.27
14370.04,-3.38
15716.30,2.46
17188.69,-1.45
18799.02,-10.94
20000.00,-13.92`;

const DEFAULT_SPK_CSV =
`frequency,raw
27.258,-30.408
44.348,-29.803
65.574,-21.598
91.616,-13.509
123.122,-12.380
160.746,-10.800
205.164,-7.127
257.068,-5.687
317.168,-8.128
386.189,-11.849
464.863,-17.922
553.931,-17.399
654.134,-10.998
766.209,-2.050
890.880,1.024
1028.86,3.050
1180.84,4.466
1347.49,7.075
1529.42,8.111
1727.23,8.729
1941.47,11.536
2172.62,13.030
2421.12,11.366
2687.33,5.708
2971.55,8.831
3274.01,15.828
3594.84,12.081
3934.11,5.314
4291.77,5.905
4667.69,7.936
5061.66,9.619
5473.35,12.235
5902.32,12.652
6348.04,11.354
6809.87,11.101
7287.07,11.799
7778.78,12.339
8284.06,11.883
8801.83,12.879
9330.94,14.674
9870.15,14.637
10418.1,12.665
10973.3,10.391
11534.4,9.455
12099.6,9.414
12667.3,8.383
13235.9,5.821
13803.4,2.135
14368.2,-2.130
14928.3,-6.109
15481.8,-8.874
16026.8,-10.881
16561.4,-13.129
17083.7,-15.349
17591.8,-17.101
18083.7,-18.381
18557.8,-19.490
19012,-20.412
19444.8,-21.095
19854.4,-21.509`;

/* ============================================================
   SECTION 3 — EEL2 (RootlessJamesDSP) + VIPER DDC
   Files live in assets/ and are fetched at startup. Download names are the keys of ASSET_SRC.
   The Master v2.0 scripts carry literal ceilings; EEL_OK confirms them against CEIL.
   ============================================================ */
const ASSET_SRC = Object.freeze({
  [N.eelIem]:  'assets/eel/iem-master-v2.0.eel',
  [N.eelSpk]:  'assets/eel/speaker-master-v2.0.eel',
  [N.eelSIem]: 'assets/eel/s-plus-iem-master.eel',
  [N.eelSSpk]: 'assets/eel/s-plus-speaker-master.eel',
  [N.vdcIem]:  'assets/ddc/iem.vdc',
  [N.vdcSpk]:  'assets/ddc/speaker.vdc'
});
const EEL = {}, VDC = {};
let ASSETS = [];   /* 4 EEL + 2 DDC + 12 WAV, built after load */
let EEL_OK = false;

async function loadAssets(){
  const keys = Object.keys(ASSET_SRC);
  const texts = await Promise.all(keys.map(async k => {
    const r = await fetch(ASSET_SRC[k]);
    if (!r.ok) throw new Error(ASSET_SRC[k] + ' (' + r.status + ')');
    return r.text();
  }));
  keys.forEach((k, i) => { (k.endsWith('.vdc') ? VDC : EEL)[k] = texts[i]; });
  ASSETS = [].concat(
    keys.map(f => ({file:f, kind:f.endsWith('.vdc') ? 'vdc' : 'eel'})),
    [].concat(...Object.keys(PRESETS).map(k => ['48k','44k'].map(t => ({file:PRESETS[k].filenameBase + ' ' + t + '.wav', kind:'wav'}))))
  );
  EEL_OK = true;
  [[N.eelIem, CEIL.iem], [N.eelSpk, CEIL.spk]].forEach(p => {
    const m = EEL[p[0]].match(/^limCeilDb\s*=\s*(-?[\d.]+)/m);
    if (!m || Math.abs(parseFloat(m[1]) - p[1]) > 1e-9){ EEL_OK = false; console.error('EEL ceiling != CEIL: ' + p[0]); }
  });
}

/* ============================================================
   SECTION 4 — STATE
   ============================================================ */
const STATE = { target: [], kzRaw: [], spkRaw: [], fitted: {} };
/* Render hooks, assigned by the UI script (no monkey-patching of engine functions). */
const UI_HOOKS = { registry(){}, badge(){}, data(){}, flash(){}, assets(){} };

/* ============================================================
   SECTION 5 — PARSERS
   ============================================================ */
function parseCSV(text){
  const out = [];
  for (const line of text.split(/\r?\n/)){
    if (!line || /^[a-zA-Z]/.test(line)) continue;
    const parts = line.split(',');
    if (parts.length < 2) continue;
    const f = parseFloat(parts[0]);
    const db = parseFloat(parts[1]);
    if (Number.isFinite(f) && Number.isFinite(db) && f > 0) out.push([f, db]);
  }
  out.sort((a,b) => a[0] - b[0]);
  return out;
}

function parseGraphicEQ(text){
  const m = String(text).match(/GraphicEQ:\s*(.+)/is);
  const body = m ? m[1] : text;
  const out = [];
  for (const chunk of body.split(';')){
    const parts = chunk.trim().split(/\s+/);
    if (parts.length < 2) continue;
    const f = parseFloat(parts[0]);
    const db = parseFloat(parts[1]);
    if (Number.isFinite(f) && Number.isFinite(db) && f > 0) out.push([f, db]);
  }
  out.sort((a,b) => a[0] - b[0]);
  return out;
}

function interpLog(curve, f){
  if (!curve || !curve.length) return 0;
  if (f <= curve[0][0]) return curve[0][1];
  if (f >= curve[curve.length-1][0]) return curve[curve.length-1][1];
  let lo = 0, hi = curve.length - 1;
  while (hi - lo > 1){
    const mid = (lo + hi) >> 1;
    if (curve[mid][0] < f) lo = mid; else hi = mid;
  }
  const f1 = curve[lo][0], db1 = curve[lo][1];
  const f2 = curve[hi][0], db2 = curve[hi][1];
  const t = (Math.log(f) - Math.log(f1)) / (Math.log(f2) - Math.log(f1));
  return db1 + t * (db2 - db1);
}

/* ============================================================
   SECTION 6 — BIQUAD ENGINE
   ============================================================ */
function assertSampleRate(fs){
  if (SUPPORTED_FS.indexOf(fs) === -1) throw new Error('Unsupported sample rate: ' + fs);
}
function assertFilters(filters, fs){
  assertSampleRate(fs);
  if (!Array.isArray(filters)) throw new Error('Filter list is invalid');
  filters.forEach((f, i) => {
    const n = 'Filter ' + (i + 1);
    if (!f || (f.type !== 'pk' && f.type !== 'hpf')) throw new Error(n + ': unsupported type');
    if (!Number.isFinite(f.fc) || f.fc < 10 || f.fc >= fs / 2) throw new Error(n + ': invalid frequency');
    const q = f.q === undefined ? 0.70710678 : f.q;
    if (!Number.isFinite(q) || q < 0.1 || q > 20) throw new Error(n + ': invalid Q');
    if (f.type === 'pk' && (!Number.isFinite(f.g) || Math.abs(f.g) > 36)) throw new Error(n + ': invalid gain');
  });
}

function evalBiquad(f, filt, fs){
  const w = 2*Math.PI*f/fs;
  const w0 = 2*Math.PI*filt.fc/fs;
  const c = Math.cos(w0), s = Math.sin(w0);
  let b0,b1,b2,a0,a1,a2;
  if (filt.type === 'hpf'){
    const Q = filt.q || 0.70710678;
    const alpha = s/(2*Q);
    b0 = (1+c)/2; b1 = -(1+c); b2 = (1+c)/2;
    a0 = 1+alpha; a1 = -2*c; a2 = 1-alpha;
  } else {
    const alpha = s/(2*filt.q);
    const A = Math.pow(10, filt.g/40);
    b0 = 1+alpha*A; b1 = -2*c; b2 = 1-alpha*A;
    a0 = 1+alpha/A; a1 = -2*c; a2 = 1-alpha/A;
  }
  const numRe = b0 + b1*Math.cos(w) + b2*Math.cos(2*w);
  const numIm = -(b1*Math.sin(w) + b2*Math.sin(2*w));
  const denRe = a0 + a1*Math.cos(w) + a2*Math.cos(2*w);
  const denIm = -(a1*Math.sin(w) + a2*Math.sin(2*w));
  const dMag2 = denRe*denRe + denIm*denIm;
  const re = (numRe*denRe + numIm*denIm)/dMag2;
  const im = (numIm*denRe - numRe*denIm)/dMag2;
  return Math.sqrt(re*re + im*im);
}

function filterChainDb(f, filters, fs, preampDb){
  let m = Math.pow(10, (preampDb || 0)/20);
  for (const flt of filters) m *= evalBiquad(f, flt, fs);
  return 20*Math.log10(Math.max(1e-30, m));
}

/* Headroom: single measurement used by fitter, WAV audit, registry, QA and UI.
   Peak magnitude response (dB) of the exported Float32 impulse (left channel,
   preamp included), over 20 Hz..20 kHz at FFT_N-point resolution.
   margin = -peakDb; a profile passes only when margin >= safetyMarginDb (unrounded). */
function fftInPlace(re, im){
  const n = re.length;
  for (let i = 1, j = 0; i < n; i++){
    let bit = n >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j){ let t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; }
  }
  for (let len = 2; len <= n; len <<= 1){
    const ang = -2*Math.PI/len, wr = Math.cos(ang), wi = Math.sin(ang), half = len >> 1;
    for (let i = 0; i < n; i += len){
      let cr = 1, ci = 0;
      for (let k = 0; k < half; k++){
        const a = i + k, b = a + half;
        const xr = re[b]*cr - im[b]*ci, xi = re[b]*ci + im[b]*cr;
        re[b] = re[a] - xr; im[b] = im[a] - xi;
        re[a] += xr; im[a] += xi;
        const nr = cr*wr - ci*wi; ci = cr*wi + ci*wr; cr = nr;
      }
    }
  }
}

function exportedHeadroom(payload, nF, fs){
  const re = new Float64Array(FFT_N), im = new Float64Array(FFT_N);
  for (let i = 0; i < nF; i++) re[i] = payload[i*2];
  fftInPlace(re, im);
  const k0 = Math.ceil(20*FFT_N/fs), k1 = Math.floor(20000*FFT_N/fs);
  let best = -1, bk = k0;
  for (let k = k0; k <= k1; k++){
    const m = re[k]*re[k] + im[k]*im[k];
    if (m > best){ best = m; bk = k; }
  }
  const peakDb = 10*Math.log10(Math.max(1e-60, best));
  return { peakDb: peakDb, peakFreq: bk*fs/FFT_N, marginDb: -peakDb };
}

/* Limiter engage level: fixed device ceiling minus the exported impulse's peak response. */
function deviceOf(p){ return (p.id.indexOf('SPK') > -1 || p.id.indexOf('SPEAKER') > -1) ? 'spk' : 'iem'; }
function limiterEngagesAboveDbfs(p, a){ return CEIL[deviceOf(p)] - a.respPeakDb; }

/* ============================================================
   SECTION 7 — FITTER v5.1
   ------------------------------------------------------------
   Objective (single source of truth):
     corr[f]         = target_shape[f] − raw_shape[f]   (both @ 1 kHz normalized)
     fixed_shape[f]  = Σ fixed_filter_responses[f]      (normalized @ 1 kHz)
     peq_shape[f]    = Σ peq_responses[f]               (normalized @ 1 kHz)
     fitted_shape[f] = fixed_shape[f] + peq_shape[f]
     error[f]        = corr[f] − fitted_shape[f]
     RMS / max are computed on error[]. Preamp is NOT included.

   Pipeline:
     Stage 1 — Greedy selection with strict constraints
               (min 0.4 octave separation, ±12 dB clamp, speaker fc floor 308 Hz)
     Stage 2 — Coordinate-descent gain refinement (fc, Q fixed)
   ============================================================ */
const GRID_N = 220;
const GRID = (() => {
  const g = [];
  for (let i = 0; i < GRID_N; i++) g.push(20 * Math.pow(1000, i/(GRID_N-1)));
  return g;
})();

function greedySelectPEQ(residualIn, targetN, fs, isSpeaker){
  const filters = [];
  const pickedFc = [];
  const MIN_SEP = Math.pow(2, FITTER_CONFIG.minSepOctaves);
  const FLOOR = isSpeaker ? FITTER_CONFIG.speakerFcFloorHz : 20;
  const GAIN_HI = FITTER_CONFIG.gainClampHiDb;
  const GAIN_LO = FITTER_CONFIG.gainClampLoDb;
  const MIN_GAIN = FITTER_CONFIG.minGainDb;

  const fcCands = [];
  const NUM_FC = 72;
  for (let i = 0; i < NUM_FC; i++) fcCands.push(20 * Math.pow(1000, i/(NUM_FC-1)));
  const qCands = [0.5, 0.7, 1.0, 1.4, 2.0, 2.8, 4.0, 6.0];

  const res = new Float64Array(residualIn);

  for (let n = 0; n < targetN; n++){
    let best = null;
    for (const fc of fcCands){
      if (fc < FLOOR) continue;
      let tooClose = false;
      for (const pf of pickedFc){
        if (fc/pf < MIN_SEP && fc/pf > 1/MIN_SEP){ tooClose = true; break; }
      }
      if (tooClose) continue;

      for (const q of qCands){
        if (fc / q < FITTER_CONFIG.minBandwidthHz) continue;
        const kernel = new Float64Array(GRID_N);
        const kf = {type:'pk', fc, g:1, q};
        for (let j = 0; j < GRID_N; j++){
          kernel[j] = 20*Math.log10(Math.max(1e-30, evalBiquad(GRID[j], kf, fs)));
        }
        let num = 0, den = 0;
        for (let j = 0; j < GRID_N; j++){
          num += res[j] * kernel[j];
          den += kernel[j] * kernel[j];
        }
        if (den < 1e-8) continue;
        let g = num / den;
        g = Math.max(GAIN_LO, Math.min(GAIN_HI, g));
        if (Math.abs(g) < MIN_GAIN) continue;
        let cancels = false;
        for (const pf of filters){
          if (Math.sign(pf.g) !== Math.sign(g) && Math.abs(Math.log2(fc / pf.fc)) < FITTER_CONFIG.oppositeSignMinOctaves){ cancels = true; break; }
        }
        if (cancels) continue;

        const filt = {type:'pk', fc, g, q};
        let loss = 0;
        for (let j = 0; j < GRID_N; j++){
          const db = 20*Math.log10(Math.max(1e-30, evalBiquad(GRID[j], filt, fs)));
          const r = res[j] - db;
          loss += r * r;
        }
        if (!best || loss < best.loss) best = {filt, loss};
      }
    }
    if (!best) break;
    filters.push(best.filt);
    pickedFc.push(best.filt.fc);
    for (let j = 0; j < GRID_N; j++){
      const db = 20*Math.log10(Math.max(1e-30, evalBiquad(GRID[j], best.filt, fs)));
      res[j] -= db;
    }
    let rms = 0;
    for (let j = 0; j < GRID_N; j++) rms += res[j]*res[j];
    rms = Math.sqrt(rms / GRID_N);
    if (rms < 0.3) break;
  }
  return filters;
}

function refineGains(peqFilters, fixedFilters, corrCurve, fs){
  if (peqFilters.length === 0) return;

  const costAt = () => {
    let m1k = 1;
    for (const f of fixedFilters) m1k *= evalBiquad(1000, f, fs);
    for (const f of peqFilters) m1k *= evalBiquad(1000, f, fs);
    const ref1k = 20*Math.log10(Math.max(1e-30, m1k));
    let sumSq = 0;
    for (let j = 0; j < GRID_N; j++){
      let m = 1;
      for (const f of fixedFilters) m *= evalBiquad(GRID[j], f, fs);
      for (const f of peqFilters) m *= evalBiquad(GRID[j], f, fs);
      const db = 20*Math.log10(Math.max(1e-30, m)) - ref1k;
      const e = corrCurve[j] - db;
      sumSq += e * e;
    }
    return sumSq;
  };

  for (let it = 0; it < FITTER_CONFIG.refinementIterations; it++){
    const step = FITTER_CONFIG.refinementSteps[Math.min(it, FITTER_CONFIG.refinementSteps.length-1)];
    for (let fi = 0; fi < peqFilters.length; fi++){
      const f = peqFilters[fi];
      const origG = f.g;
      let bestG = origG;
      let bestC = costAt();

      f.g = Math.max(FITTER_CONFIG.gainClampLoDb, Math.min(FITTER_CONFIG.gainClampHiDb, origG + step));
      let cUp = costAt();
      if (cUp < bestC){ bestC = cUp; bestG = f.g; }

      f.g = Math.max(FITTER_CONFIG.gainClampLoDb, Math.min(FITTER_CONFIG.gainClampHiDb, origG - step));
      let cDn = costAt();
      if (cDn < bestC){ bestC = cDn; bestG = f.g; }

      f.g = bestG;
    }
  }
}

function fitPEQ(rawCurve, targetCurve, numFilters, fs, isSpeaker){
  const raw1k = interpLog(rawCurve, 1000);
  const tgt1k = interpLog(targetCurve, 1000);

  const corr = GRID.map(f =>
    (interpLog(targetCurve, f) - tgt1k) - (interpLog(rawCurve, f) - raw1k)
  );

  const fixedFilters = [];
  if (isSpeaker){
    fixedFilters.push({type:'hpf', fc:220, q:0.70710678});
  }

  // Residual for PEQ = corr − fixed_shape
  const residual = new Float64Array(GRID_N);
  for (let j = 0; j < GRID_N; j++) residual[j] = corr[j];
  if (isSpeaker){
    const hpf1k = 20*Math.log10(Math.max(1e-30, evalBiquad(1000, fixedFilters[0], fs)));
    for (let j = 0; j < GRID_N; j++){
      const db = 20*Math.log10(Math.max(1e-30, evalBiquad(GRID[j], fixedFilters[0], fs))) - hpf1k;
      residual[j] -= db;
    }
  }

  const peqTarget = isSpeaker ? Math.max(1, numFilters - 1) : numFilters;
  let peqFilters = greedySelectPEQ(residual, peqTarget, fs, isSpeaker);
  refineGains(peqFilters, fixedFilters, corr, fs);

  // Merge + sort, keeping HPF at index 0
  let allFilters = fixedFilters.concat(peqFilters);
  if (isSpeaker && fixedFilters.length === 1){
    const hpf = fixedFilters[0];
    const nonHpf = allFilters.filter(f => f.type !== 'hpf');
    nonHpf.sort((a,b) => a.fc - b.fc);
    allFilters = [hpf].concat(nonHpf);
  } else {
    allFilters.sort((a,b) => a.fc - b.fc);
  }

  // Preamp for headroom (not part of shape): same exported-signal measurement as the QA gate
  const preampDb = solvePreamp(allFilters, SAFETY_MARGIN_DB);

  // Shape error against full response
  let m1k = 1;
  for (const filt of allFilters) m1k *= evalBiquad(1000, filt, fs);
  const shape1k = 20*Math.log10(Math.max(1e-30, m1k));

  let sumSq = 0, maxErr = 0;
  let sumSqResolvable = 0, countResolvable = 0;
  for (let j = 0; j < GRID_N; j++){
    let m = 1;
    for (const filt of allFilters) m *= evalBiquad(GRID[j], filt, fs);
    const fitted = 20*Math.log10(Math.max(1e-30, m)) - shape1k;
    const e = corr[j] - fitted;
    sumSq += e*e;
    if (Math.abs(e) > maxErr) maxErr = Math.abs(e);
    if (GRID[j] >= FITTER_CONFIG.resolvableBandHz){
      sumSqResolvable += e*e;
      countResolvable++;
    }
  }
  const rmsErr = Math.sqrt(sumSq / GRID_N);
  const rmsResolvable = countResolvable > 0 ? Math.sqrt(sumSqResolvable / countResolvable) : NaN;

  let maxBoost = 0, maxCut = 0;
  for (const flt of peqFilters){
    if (flt.g === undefined) continue;
    if (flt.g > maxBoost) maxBoost = flt.g;
    if (-flt.g > maxCut) maxCut = -flt.g;
  }

  return { filters: allFilters, preampDb, rmsErr, rmsResolvable, maxErr, maxBoost, maxCut, peqCount: peqFilters.length };
}

/* ============================================================
   SECTION 8 — WAV ENCODER + AUDITOR
   ============================================================ */
const LANDMARKS = Object.freeze([20,22,45,100,180,220,510,850,1350,2250,3270,3350,4950,5850,6300,7950,9400,11900,13500,15000,18000]);

function landmarksFor(fs, filters){
  const set = new Set(LANDMARKS);
  for (const flt of filters) set.add(flt.fc);
  for (let i = 0; i < 40; i++) set.add(20 * Math.pow(0.49 * fs / 20, i / 39));
  return Array.from(set).filter(f => f >= 20 && f <= 0.49 * fs + 1e-6).sort((a, b) => a - b);
}

/* FIR magnitude (dB) of the left channel at exactly f, direct DFT with a rotation recurrence. */
function firMagDb(payload, nF, f, fs){
  const w = 2*Math.PI*f/fs, c = Math.cos(w), sn = Math.sin(w);
  let cr = 1, ci = 0, re = 0, im = 0;
  for (let n = 0; n < nF; n++){
    const x = payload[n*2];
    re += x*cr; im -= x*ci;
    const t = cr*c - ci*sn; ci = cr*sn + ci*c; cr = t;
  }
  return 20*Math.log10(Math.max(1e-30, Math.hypot(re, im)));
}

function fourCC(view, off){
  return String.fromCharCode(view.getUint8(off),view.getUint8(off+1),view.getUint8(off+2),view.getUint8(off+3));
}

function auditWAV(buf, fs, preset, applied){
  if (!(buf instanceof ArrayBuffer)) throw new Error("Not ArrayBuffer");
  const v = new DataView(buf), len = buf.byteLength;
  if (len < 44) throw new Error("Truncated header");
  if (fourCC(v,0) !== 'RIFF') throw new Error("No RIFF");
  if (fourCC(v,8) !== 'WAVE') throw new Error("No WAVE");
  if (fourCC(v,12) !== 'fmt ') throw new Error("No fmt");
  if (v.getUint32(16,true) !== 16) throw new Error("fmt size != 16");
  if (v.getUint16(20,true) !== 3) throw new Error("Not IEEE Float32");
  if (v.getUint16(22,true) !== 2) throw new Error("Not stereo");
  if (v.getUint32(24,true) !== fs) throw new Error("Sample-rate mismatch");
  if (v.getUint32(28,true) !== fs*8) throw new Error("Byte-rate mismatch");
  if (v.getUint16(32,true) !== 8) throw new Error("Block-align != 8");
  if (v.getUint16(34,true) !== 32) throw new Error("Bits != 32");
  if (fourCC(v,36) !== 'data') throw new Error("No data chunk");
  const dSize = v.getUint32(40,true);
  if (dSize % 8 !== 0) throw new Error("Data not frame-aligned");
  if (len !== 44 + dSize) throw new Error("Data size mismatch");
  if (v.getUint32(4,true) !== 36 + dSize) throw new Error("RIFF size mismatch");

  const nF = dSize/8;
  const payload = new Float32Array(buf, 44, nF*2);
  let nan=0, inf=0, maxAbs=0, sum=0, tailE=0, tailP=0;
  const TAIL = 2048;
  for (let i=0;i<nF;i++){
    const L = payload[i*2], R = payload[i*2+1];
    if (!Number.isFinite(L) || !Number.isFinite(R)){
      if (isNaN(L) || isNaN(R)) nan++; else inf++;
    }
    const pk = Math.max(Math.abs(L), Math.abs(R));
    if (pk > maxAbs) maxAbs = pk;
    sum += L;
    if (i >= nF - TAIL){
      tailE += L*L + R*R;
      if (pk > tailP) tailP = pk;
    }
  }
  const peakDb = 20*Math.log10(Math.max(1e-30, maxAbs));
  const dcFirDb = 20*Math.log10(Math.max(1e-30, Math.abs(sum)));            // H(0) of the FIR = sum of taps
  const dcIirDb = filterChainDb(0, preset.filters, fs, applied);            // analytical H(0) of the intended chain
  const dcDb = dcFirDb;
  const tailRms = 10*Math.log10(Math.max(1e-30, tailE/(TAIL*2)));
  const tailPeak = 20*Math.log10(Math.max(1e-30, tailP));

  let maxDelta = 0, maxDeltaFreq = 0;
  for (const f of landmarksFor(fs, preset.filters)){
    const d = Math.abs(filterChainDb(f, preset.filters, fs, applied) - firMagDb(payload, nF, f, fs));
    if (d > maxDelta){ maxDelta = d; maxDeltaFreq = f; }
  }
  const dcDelta = Math.abs(Math.max(DC_FLOOR_DB, dcIirDb) - Math.max(DC_FLOOR_DB, dcFirDb));
  if (dcDelta > maxDelta){ maxDelta = dcDelta; maxDeltaFreq = 0; }

  const hr = exportedHeadroom(payload, nF, fs);
  const marginDb = hr.marginDb;
  const safetyDb = (preset.preampPolicy.safetyMarginDb !== undefined) ? preset.preampPolicy.safetyMarginDb : SAFETY_MARGIN_DB;
  const headroom = marginDb >= safetyDb;

  const pass = (nan===0 && inf===0 && peakDb<=0
    && tailRms<=TAIL_RMS_LIMIT_DB && tailPeak<=TAIL_PEAK_LIMIT_DB
    && maxDelta<=IIR_FIR_TOLERANCE_DB && headroom);

  return {nan,inf,peakDb,dcDb,dcIirDb,dcFirDb,maxDeltaFreq,tailRms,tailPeak,maxDelta,marginDb,safetyDb,headroom,
          respPeakDb: hr.peakDb, respPeakFreq: hr.peakFreq, filterPeakDb: hr.peakDb - applied, pass,
          checks: {finite: nan===0 && inf===0, peak: peakDb<=0, tail: tailRms<=TAIL_RMS_LIMIT_DB && tailPeak<=TAIL_PEAK_LIMIT_DB, iirFir: maxDelta<=IIR_FIR_TOLERANCE_DB, headroom}};
}

function synthesizeWAV(preset, fs){
  assertFilters(preset.filters, fs);
  if (!Number.isFinite(preset.preampPolicy.appliedPreampDb)) throw new Error('Invalid preamp');
  const N = IR_LENGTH, TAIL = IR_TAIL;
  const pre = Math.pow(10, preset.preampPolicy.appliedPreampDb/20);
  let sig = new Float64Array(N);
  sig[0] = pre;

  for (const f of preset.filters){
    const w0 = 2*Math.PI*f.fc/fs;
    const c = Math.cos(w0), s = Math.sin(w0);
    let b0,b1,b2,a0,a1,a2;
    if (f.type === 'hpf'){
      const Q = f.q || 0.70710678;
      const alpha = s/(2*Q);
      b0=(1+c)/2; b1=-(1+c); b2=(1+c)/2;
      a0=1+alpha; a1=-2*c; a2=1-alpha;
    } else {
      const alpha = s/(2*f.q);
      const A = Math.pow(10, f.g/40);
      b0=1+alpha*A; b1=-2*c; b2=1-alpha*A;
      a0=1+alpha/A; a1=-2*c; a2=1-alpha/A;
    }
    const nb0=b0/a0, nb1=b1/a0, nb2=b2/a0, na1=a1/a0, na2=a2/a0;
    const out = new Float64Array(N);
    let x1=0,x2=0,y1=0,y2=0;
    for (let i=0;i<N;i++){
      const xn = sig[i];
      const yn = nb0*xn + nb1*x1 + nb2*x2 - na1*y1 - na2*y2;
      x2=x1; x1=xn; y2=y1; y1=yn;
      out[i] = yn;
    }
    sig = out;
  }

  for (let i=0;i<TAIL;i++){
    const idx = N - TAIL + i;
    sig[idx] *= 0.5 * (1 + Math.cos(Math.PI * i / (TAIL - 1)));
  }

  const dSize = N*8;
  const ab = new ArrayBuffer(44 + dSize);
  const v = new DataView(ab);
  const wr = (off, s) => { for (let i=0;i<s.length;i++) v.setUint8(off+i, s.charCodeAt(i)); };
  wr(0,'RIFF'); v.setUint32(4, 36+dSize, true); wr(8,'WAVE'); wr(12,'fmt ');
  v.setUint32(16, 16, true);
  v.setUint16(20, 3, true);
  v.setUint16(22, 2, true);
  v.setUint32(24, fs, true);
  v.setUint32(28, fs*8, true);
  v.setUint16(32, 8, true);
  v.setUint16(34, 32, true);
  wr(36,'data'); v.setUint32(40, dSize, true);
  let off = 44;
  for (let i=0;i<N;i++){
    v.setFloat32(off, sig[i], true);
    v.setFloat32(off+4, sig[i], true);
    off += 8;
  }
  return ab;
}

/* Single authoritative pipeline: synthesize -> audit that exact buffer. Display, registry and download gate all use it. */
function buildAsset(preset, fs){
  const buf = synthesizeWAV(preset, fs);
  return { buf, audit: auditWAV(buf, fs, preset, preset.preampPolicy.appliedPreampDb) };
}
const AUDIT_CACHE = new Map();
function auditPreset(preset, fs){
  const ck = fs + '|' + preset.preampPolicy.appliedPreampDb + '|' + (preset.preampPolicy.safetyMarginDb) + '|' + JSON.stringify(preset.filters);
  if (!AUDIT_CACHE.has(ck)){
    if (AUDIT_CACHE.size > 64) AUDIT_CACHE.clear();
    AUDIT_CACHE.set(ck, buildAsset(preset, fs).audit);
  }
  return AUDIT_CACHE.get(ck);
}

/* Fitter preamp: largest preamp (0.001 dB steps) whose exported signal meets the
   safety margin at every supported sample rate, measured with auditWAV's headroom. */
function solvePreamp(filters, safetyDb){
  const probe = pre => ({ filters: filters, preampPolicy: { appliedPreampDb: pre, safetyMarginDb: safetyDb } });
  let worst = -Infinity;
  for (const fs of SUPPORTED_FS) worst = Math.max(worst, auditPreset(probe(0), fs).respPeakDb);
  let n = Math.floor(Math.min(0, -worst - safetyDb) / PREAMP_STEP_DB + 1e-9);   // never a boost   // integer 0.001 dB steps
  for (let i = 0; i < 400; i++, n--){
    const pre = n * PREAMP_STEP_DB;
    if (SUPPORTED_FS.every(fs => auditPreset(probe(pre), fs).marginDb >= safetyDb)) return pre;
  }
  throw new Error('No preamp meets the safety margin');
}

/* ============================================================
   SECTION 9 — HELPERS
   ============================================================ */
function sanitizeName(n){ return String(n).replace(/[^a-zA-Z0-9._ ™+-]/g, '_').replace(/^\.+/, '_'); }

let toastTimer = 0;
function toast(msg){
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.display = 'block';
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.style.display = 'none'; }, 2600);
}

function copyText(text){
  const fallback = () => {
    const ta = document.createElement('textarea');
    ta.value = text; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;opacity:0;top:0';
    document.body.appendChild(ta); ta.select();
    let ok = false;
    try { ok = document.execCommand('copy'); } catch(e){ ok = false; }
    document.body.removeChild(ta);
    return ok;
  };
  if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text).then(() => true, () => fallback());
  return Promise.resolve(fallback());
}

function download(blob, filename){
  const safe = sanitizeName(filename);
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = safe;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 30000);
  toast('Downloaded: ' + safe);
}

function allPresets(){ return Object.assign({}, PRESETS, STATE.fitted); }

function exportWAV(presetKey, fs){
  if (SUPPORTED_FS.indexOf(fs) === -1){ const m = 'Unsupported sample rate: ' + fs; toast(m); return {ok:false, message:m}; }
  const preset = allPresets()[presetKey];
  if (!preset){ const m = 'Unknown preset: ' + presetKey; toast(m); return {ok:false, message:m}; }
  let buf, audit;
  try { const asset = buildAsset(preset, fs); buf = asset.buf; audit = asset.audit; }
  catch(e){ const m = 'Export failed: ' + e.message; toast(m); return {ok:false, message:m}; }

  const log = document.getElementById('qa_console');
  const tag = fs === 48000 ? '48k' : '44k';
  const ts = new Date().toISOString().substring(11,19);
  log.textContent =
'[' + ts + '] ' + preset.filenameBase + ' ' + tag + '.wav\n' +
'  header OK | NaN=' + audit.nan + ' Inf=' + audit.inf + '\n' +
'  peak=' + audit.peakDb.toFixed(2) + ' dBFS | DC FIR=' + audit.dcFirDb.toFixed(1) + ' dB, IIR=' + audit.dcIirDb.toFixed(1) + ' dB\n' +
'  tail RMS=' + audit.tailRms.toFixed(1) + ' dBFS (limit ' + TAIL_RMS_LIMIT_DB + ')\n' +
'  tail peak=' + audit.tailPeak.toFixed(1) + ' dBFS (limit ' + TAIL_PEAK_LIMIT_DB + ')\n' +
'  IIR<->FIR max delta=' + audit.maxDelta.toFixed(4) + ' dB @ ' + Math.round(audit.maxDeltaFreq) + ' Hz (limit ' + IIR_FIR_TOLERANCE_DB + ')\n' +
'  headroom margin=' + audit.marginDb.toFixed(3) + ' dB (required ' + audit.safetyDb.toFixed(3) + ' dB, peak response ' + audit.respPeakDb.toFixed(3) + ' dB @ ' + Math.round(audit.respPeakFreq) + ' Hz)\n' +
'  limiter engages above ' + limiterEngagesAboveDbfs(preset, audit).toFixed(3) + ' dBFS (ceiling ' + CEIL[deviceOf(preset)].toFixed(1) + ' dBFS)\n\n' + log.textContent;

  if (!audit.pass){ toast('QA FAIL - download blocked'); return {ok:false, message:'Quality check failed, download blocked.'}; }
  const fname = preset.filenameBase + ' ' + tag + '.wav';
  download(new Blob([buf], {type:'audio/wav'}), fname);
  return {ok:true, filename:sanitizeName(fname)};
}

/* EEL scripts and DDC files, keyed by their exact filename. */
function exportEEL(key, filename){
  const src = EEL[key] !== undefined ? EEL[key] : VDC[key];
  if (src === undefined) return {ok:false, message:'Unknown file: ' + key};
  download(new Blob([src], {type:'application/octet-stream'}), filename);
  return {ok:true, filename:sanitizeName(filename)};
}

function peqText(preset){
  let t = 'Preamp: ' + preset.preampPolicy.appliedPreampDb.toFixed(2) + ' dB\n';
  preset.filters.forEach((f,i) => {
    const q = (f.q || 0.70710678).toFixed(2);
    if (f.type === 'hpf') t += 'Filter ' + (i+1) + ': ON HPQ Fc ' + f.fc.toFixed(1) + ' Hz Q ' + q + '\n';
    else t += 'Filter ' + (i+1) + ': ON PK Fc ' + f.fc.toFixed(1) + ' Hz Gain ' + f.g.toFixed(2) + ' dB Q ' + q + '\n';
  });
  return t.trim();
}

function geqText(preset, fs){
  const pts = [];
  for (let i=0;i<127;i++){
    const f = 20 * Math.pow(1000, i/126);
    const db = filterChainDb(f, preset.filters, fs, 0);
    pts.push(f.toFixed(1) + ' ' + db.toFixed(1));
  }
  return 'GraphicEQ: ' + pts.join('; ');
}

/* ============================================================
   SECTION 10 — CANVAS
   ============================================================ */
function drawFitCanvas(){
  const cv = document.getElementById('fit_canvas');
  const dpr = window.devicePixelRatio || 1;
  const cssW = cv.clientWidth || 960;
  const cssH = 380;
  if (cv.width !== Math.round(cssW*dpr) || cv.height !== Math.round(cssH*dpr)){
    cv.width = Math.round(cssW*dpr);
    cv.height = Math.round(cssH*dpr);
  }
  const ctx = cv.getContext('2d');
  ctx.setTransform(dpr,0,0,dpr,0,0);
  const W = cssW, H = cssH;
  const padL = 50, padR = 10, padT = 10, padB = 30;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  ctx.fillStyle = '#06070a';
  ctx.fillRect(0,0,W,H);

  const fMin = 20, fMax = 20000;
  const xOf = f => padL + plotW * (Math.log10(f) - Math.log10(fMin)) / (Math.log10(fMax) - Math.log10(fMin));
  const dbMin = -35, dbMax = 25;
  const yOf = db => padT + plotH * (dbMax - db) / (dbMax - dbMin);

  ctx.strokeStyle = '#1c2233';
  ctx.lineWidth = 1;
  ctx.font = '10px ui-monospace,monospace';
  ctx.fillStyle = '#8492a6';
  ctx.textAlign = 'center';
  [20,50,100,200,500,1000,2000,5000,10000,20000].forEach(f => {
    const x = xOf(f);
    ctx.beginPath(); ctx.moveTo(x, padT); ctx.lineTo(x, padT+plotH); ctx.stroke();
    ctx.fillText(f >= 1000 ? (f/1000)+'k' : String(f), x, H-10);
  });
  ctx.textAlign = 'right';
  for (let db = -30; db <= 20; db += 10){
    const y = yOf(db);
    ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W-padR, y); ctx.stroke();
    ctx.fillText(db+'dB', padL-6, y+3);
  }

  function drawCurve(pts, color, width, dash){
    if (!pts || pts.length < 2) return;
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.setLineDash(dash || []);
    ctx.beginPath();
    let first = true;
    for (const pair of pts){
      const f = pair[0], db = pair[1];
      if (f < fMin || f > fMax) continue;
      const x = xOf(f), y = yOf(db);
      if (first){ ctx.moveTo(x,y); first = false; } else ctx.lineTo(x,y);
    }
    ctx.stroke();
    ctx.setLineDash([]);
  }

  if (STATE.kzRaw.length) drawCurve(STATE.kzRaw, '#38bdf8', 1.4);
  if (STATE.spkRaw.length) drawCurve(STATE.spkRaw, '#f59e0b', 1.4);
  if (STATE.target.length) drawCurve(STATE.target, '#10b981', 1.6, [6,4]);

  const drawFitted = (which, color) => {
    const preset = STATE.fitted[which];
    if (!preset) return;
    const raw = which === 'KZ' ? STATE.kzRaw : STATE.spkRaw;
    if (!raw || !raw.length) return;
    const raw1k = interpLog(raw, 1000);
    const pts_filter = [], pts_corrected = [];
    for (let i = 0; i < 300; i++){
      const f = fMin * Math.pow(fMax/fMin, i/299);
      const filtDb = filterChainDb(f, preset.filters, 48000, 0);
      const corrDb = interpLog(raw, f) - raw1k + filtDb + preset.preampPolicy.appliedPreampDb;
      pts_filter.push([f, filtDb]);
      pts_corrected.push([f, corrDb]);
    }
    drawCurve(pts_filter, color, 1.2, [4,3]);
    drawCurve(pts_corrected, color, 2, []);
  };
  drawFitted('KZ', '#a855f7');
  drawFitted('SPK', '#f43f5e');

  ctx.font = '10px ui-monospace,monospace';
  ctx.textAlign = 'left';
  let ly = padT + 14, lx = padL + 8;
  const legend = [];
  if (STATE.kzRaw.length) legend.push(['KZ EDX Pro raw', '#38bdf8']);
  if (STATE.spkRaw.length) legend.push(['Redmi 12 spk raw', '#f59e0b']);
  if (STATE.target.length) legend.push(['Target', '#10b981']);
  if (STATE.fitted.KZ) legend.push(['Fitted KZ + corrected', '#a855f7']);
  if (STATE.fitted.SPK) legend.push(['Fitted SPK + corrected', '#f43f5e']);
  legend.forEach(pair => {
    ctx.fillStyle = pair[1];
    ctx.fillRect(lx, ly-6, 12, 3);
    ctx.fillStyle = '#cbd5e1';
    ctx.fillText(pair[0], lx+18, ly);
    ly += 14;
  });
  UI_HOOKS.data();
}

/* ============================================================
   SECTION 11 — FIT WORKFLOW
   ============================================================ */
function runFit(which){
  try { runFitUnsafe(which); }
  catch(e){
    toast('Fit failed: ' + e.message);
    const log = document.getElementById('fit_log');
    log.textContent = 'Fit failed: ' + e.message + '\n\n' + log.textContent;
  }
}

function runFitUnsafe(which){
  const raw = which === 'KZ' ? STATE.kzRaw : STATE.spkRaw;
  if (!raw || raw.length < 4){ toast('No measurement loaded for ' + which); return; }
  if (!STATE.target.length){ toast('No target loaded'); return; }

  const numFilters = Math.max(4, Math.min(16, parseInt(document.getElementById('num_filters').value, 10) || 10));
  const t0 = performance.now();
  const result = fitPEQ(raw, STATE.target, numFilters, 48000, which === 'SPK');
  const elapsed = (performance.now() - t0).toFixed(0);

  const name = which === 'KZ' ? 'AutoEQ Fitted KZ EDX Pro' : 'AutoEQ Fitted Redmi 12 Speaker';
  const filenameBase = which === 'KZ' ? 'HyperAudio™ Fitted KZ Edx Pro' : 'HyperAudio™ Fitted Redmi 12 Speaker';

  STATE.fitted[which] = {
    id: 'FITTED_' + which,
    name: name,
    classification: 'AutoEQ fit (' + (which === 'KZ' ? 'KZ EDX Pro' : 'Redmi 12 Speaker (HPF protected)') + ')',
    description: result.filters.length + ' bands; RMS=' + result.rmsErr.toFixed(2) + ' dB, max=' + result.maxErr.toFixed(2) + ' dB',
    filters: result.filters,
    preampPolicy: {
      mode: 'autoeq_fitted',
      appliedPreampDb: result.preampDb,
      safetyMarginDb: SAFETY_MARGIN_DB
    },
    filenameBase: filenameBase
  };

  const log = document.getElementById('fit_log');
  const lines = [];
  lines.push('--- ' + name + ' (' + result.peqCount + ' PEQ + ' + (which === 'SPK' ? 1 : 0) + ' fixed HPF, ' + elapsed + ' ms)');
  lines.push('    Preamp (headroom only, not part of shape error): ' + result.preampDb.toFixed(3) + ' dB');
  SUPPORTED_FS.slice().reverse().forEach(rate => {
    const a = auditPreset(STATE.fitted[which], rate);
    lines.push('    Headroom @ ' + (rate/1000) + ' kHz: margin ' + a.marginDb.toFixed(3) + ' dB vs required ' + a.safetyDb.toFixed(3) + ' dB -> ' + (a.headroom ? 'PASS' : 'FAIL'));
  });
  lines.push('    Shape error vs normalized full response (preamp excluded):');
  lines.push('      Full range    : RMS = ' + result.rmsErr.toFixed(2) + ' dB, max|delta| = ' + result.maxErr.toFixed(2) + ' dB');
  if (which === 'SPK'){
    lines.push('      Resolvable (>= ' + FITTER_CONFIG.resolvableBandHz + ' Hz) : RMS = ' + result.rmsResolvable.toFixed(2) + ' dB');
    lines.push('      (Residual bass error below ' + FITTER_CONFIG.resolvableBandHz + ' Hz is a physical limit of the 2nd-order HPF.)');
  }
  lines.push('    Max individual boost: +' + result.maxBoost.toFixed(2) + ' dB | Max individual cut: -' + result.maxCut.toFixed(2) + ' dB');
  lines.push('    Filter table (Hz / dB / Q):');
  result.filters.forEach(f => {
    const gStr = (f.g === undefined) ? 'HPF (fixed)' : ((f.g >= 0 ? '+' : '') + f.g.toFixed(2) + ' dB');
    lines.push('      ' + f.fc.toFixed(0).padStart(6) + ' Hz   ' + gStr.padStart(14) + '   Q ' + f.q.toFixed(2));
  });
  log.textContent = lines.join('\n') + '\n\n' + log.textContent;

  renderFitTable(which);
  drawFitCanvas();
  renderPresetRegistry();
  renderExportGroups();
  renderWAVGrid();
  updateBadge();
}

function renderFitTable(which){
  const preset = STATE.fitted[which];
  if (!preset){ document.getElementById('fit_table').innerHTML = ''; return; }
  const rows = preset.filters.map((f, i) => {
    const g = (f.g === undefined) ? 'HPF' : ((f.g >= 0 ? '+' : '') + f.g.toFixed(2));
    const q = f.q ? f.q.toFixed(2) : '0.71';
    return '<tr><td>' + (i+1) + '</td><td>' + f.type.toUpperCase() + '</td><td>' + f.fc.toFixed(1) + '</td><td>' + g + '</td><td>' + q + '</td></tr>';
  }).join('');
  document.getElementById('fit_table').innerHTML =
    '<div class="fit-table-title">' + preset.name + ' — fitted filter table</div>' +
    '<table><thead><tr><th>#</th><th>Type</th><th>Fc (Hz)</th><th>Gain (dB)</th><th>Q</th></tr></thead><tbody>' + rows + '</tbody></table>';
}

/* ============================================================
   SECTION 12 — RENDERERS
   ============================================================ */
function renderPresetRegistry(){
  const tbody = document.getElementById('reg');
  tbody.innerHTML = '';
  const all = allPresets();
  Object.keys(all).forEach(key => {
    const preset = all[key];
    const applied = preset.preampPolicy.appliedPreampDb;
    let a48, a44;
    try { a48 = auditPreset(preset, 48000); a44 = auditPreset(preset, 44100); }
    catch(e){
      const tr = document.createElement('tr');
      tr.innerHTML = '<td><b>' + preset.name + '</b></td><td>' + preset.classification + '</td><td colspan="5"><span style="color:var(--rose);">Audit error: ' + e.message + '</span></td>';
      tbody.appendChild(tr);
      return;
    }
    const safety = a48.safetyDb;
    const calcMin = -(Math.max(a48.filterPeakDb, a44.filterPeakDb) + safety);
    const cell = a => '<span style="color:' + (a.headroom ? 'var(--emerald)' : 'var(--rose)') + ';">' + (a.marginDb >= 0 ? '+' : '') + a.marginDb.toFixed(3) + ' dB ' + (a.headroom ? 'PASS' : 'FAIL') + '</span>';
    const tr = document.createElement('tr');
    tr.innerHTML =
      '<td><b>' + preset.name + '</b></td>' +
      '<td>' + preset.classification + '</td>' +
      '<td>' + (a48.filterPeakDb >= 0 ? '+' : '') + a48.filterPeakDb.toFixed(3) + ' dB<br><span class="muted-xs">@ ' + Math.round(a48.respPeakFreq) + ' Hz</span></td>' +
      '<td>' + calcMin.toFixed(3) + ' dB</td>' +
      '<td><b>' + applied.toFixed(3) + ' dB</b></td>' +
      '<td>48k: ' + cell(a48) + '<br>44.1k: ' + cell(a44) + '<br><span class="muted-xs">required ' + safety.toFixed(3) + ' dB</span></td>' +
      '<td><span class="emerald">48k: ' + a48.maxDelta.toFixed(3) + '</span><br>' +
      '<span class="emerald">44k: ' + a44.maxDelta.toFixed(3) + '</span></td>';
    tbody.appendChild(tr);
  });
  UI_HOOKS.registry();
}

function renderExportGroups(){
  const box = document.getElementById('exports');
  box.innerHTML = '';
  const all = allPresets();
  Object.keys(all).forEach(key => {
    const preset = all[key];
    const g = document.createElement('div');
    g.className = 'export-group';
    const peq = peqText(preset);
    const geq = geqText(preset, 48000);
    g.innerHTML =
      '<div class="export-label">' + preset.name + ' — Parametric EQ:</div>' +
      '<textarea readonly id="peq_' + key + '">' + peq + '</textarea>' +
      '<button class="copy" data-t="peq_' + key + '">Copy ' + preset.name + ' PEQ</button>' +
      '<div class="export-label mt-sm">' + preset.name + ' — GraphicEQ (127 pts @ 48 kHz):</div>' +
      '<textarea readonly id="geq_' + key + '">' + geq + '</textarea>' +
      '<button class="copy" data-t="geq_' + key + '">Copy ' + preset.name + ' GraphicEQ</button>';
    box.appendChild(g);
  });
  box.querySelectorAll('.copy').forEach(btn => {
    btn.addEventListener('click', () => {
      const el = document.getElementById(btn.getAttribute('data-t'));
      if (!el) return;
      copyText(el.value).then(ok => {
        toast(ok ? 'Copied to clipboard' : 'Copy failed. Select the text and copy it manually.');
        if (ok) UI_HOOKS.flash(btn, 'Copied');
      });
    });
  });
}

function renderWAVGrid(){
  const grid = document.getElementById('wav_export_grid');
  grid.innerHTML = '';
  const all = allPresets();
  Object.keys(all).forEach(key => {
    const preset = all[key];
    const b48 = document.createElement('button');
    b48.className = 'btn';
    b48.innerHTML = '<span>' + preset.filenameBase + ' 48k.wav</span><span class="sub">48.0 kHz - ' + preset.name + '</span>';
    b48.addEventListener('click', () => exportWAV(key, 48000));
    grid.appendChild(b48);
    const b44 = document.createElement('button');
    b44.className = 'btn';
    b44.innerHTML = '<span>' + preset.filenameBase + ' 44k.wav</span><span class="sub">44.1 kHz - ' + preset.name + '</span>';
    b44.addEventListener('click', () => exportWAV(key, 44100));
    grid.appendChild(b44);
  });
}

function updateBadge(){
  let allPass = true;
  const log = document.getElementById('qa_console');
  log.textContent = '[INIT] Dual-rate QA on all presets (48 kHz + 44.1 kHz)...\n\n';
  const all = allPresets();
  Object.keys(all).forEach(key => {
    const preset = all[key];
    let a48, a44;
    try {
      a48 = auditPreset(preset, 48000);
      a44 = auditPreset(preset, 44100);
    } catch(e){
      log.textContent += '- ' + preset.name + ': EXCEPTION ' + e.message + '\n';
      allPass = false; return;
    }
    if (!(a48.pass && a44.pass)) allPass = false;
    const line = (tag, a) => '    ' + tag + ': tailRMS=' + a.tailRms.toFixed(1) + 'dBFS margin=' + a.marginDb.toFixed(3) + 'dB (req ' + a.safetyDb.toFixed(3) + ') d=' + a.maxDelta.toFixed(3) + 'dB ' + (a.pass ? 'PASS' : 'FAIL') + '\n';
    log.textContent += '- ' + preset.name + '\n' + line('48.0k', a48) + line('44.1k', a44);
  });
  if (!EEL_OK){ allPass = false; log.textContent += '- EEL ceiling check: FAIL (script ceiling differs from CEIL)\n'; }
  const badge = document.getElementById('qa_badge');
  if (allPass){
    badge.textContent = 'BROWSER QA: PASS (DUAL-RATE)';
    badge.className = 'badge b-emerald';
  } else {
    badge.textContent = 'BROWSER QA: FAIL';
    badge.className = 'badge b-rose';
  }
  UI_HOOKS.badge();
}

/* ============================================================
   SECTION 13 — EVIDENCE
   ============================================================ */
const EVIDENCE_TEXT =
'Operator-Reported Audio-Path Diagnostic - NOT independently certified.\n\n' +
'OPERATOR:           Noushad M. (author; devices: KZ EDX Pro IEM, Xiaomi Redmi 12)\n' +
'STREAM:             Output thread AudioOut_D (TID 1777, MIXER)\n' +
'HAL FORMAT:         0x3 (AUDIO_FORMAT_PCM_32_BIT)\n' +
'                    NOTE: "32-bit PCM" is the container type as reported by the HAL.\n' +
'                    It does NOT by itself prove IEEE-754 Float32 transport on the\n' +
'                    Android audio path. Exported convolver assets in this tool are\n' +
'                    IEEE Float32 WAV files, a distinct format.\n' +
'SAMPLE RATE:        48000 Hz\n' +
'BUFFER HEALTH:      partial=0, empty=0 during the reported diagnostic window;\n' +
'                    no underrun condition observed in the supplied capture.\n' +
'PROCESSED FRAMES:   3,755,635,712 (operator-supplied counter)\n' +
'EFFECT CHAIN:       Session 0 / Track Active / State: 003 / Registered: y / Enabled: y / Suspended: n\n\n' +
'INTERCEPTION:\n' +
'  reported by operator as\n' +
'  "Direct AudioFlinger Hook Verified Active"\n' +
'  The exact capture/interception mechanism is NOT independently\n' +
'  established by the effect-chain dump alone.\n\n' +
'RUNTIME VERIFICATION:\n' +
'  EEL2 scripts  - an earlier script build was loaded into RootlessJamesDSP on the Xiaomi\n' +
'                  Redmi 12 (Android 15) and confirmed executing without parse errors or\n' +
'                  audio artifacts (operator-supplied, previous build only). The Master v2.0,\n' +
'                  S+ and DDC files in this build are not covered by that report.\n' +
'  IR assets     - 48 kHz and 44.1 kHz convolver impulses loaded and processed audio\n' +
'                  without artifacts (operator-supplied, previous build only).\n' +
'  AutoEQ fits   - generated in this browser session; not covered by the operator report.\n\n' +
'LIMITATIONS:\n' +
'  - Point-in-time observation, not a lifetime or universal guarantee.\n' +
'  - Not independent laboratory certification.\n' +
'  - Browser-side QA is NOT RootlessJamesDSP native runtime validation.';

/* ============================================================
   SECTION 14 — SELF-TESTS
   ============================================================ */
function runSelfTests(){
  let ok = EEL_OK;
  const names = ASSETS.map(a => a.file);
  const expected = Object.keys(ASSET_SRC).length + 2 * Object.keys(PRESETS).length;
  if (names.length !== expected){ console.error('Asset count != ' + expected); ok = false; }
  if (new Set(names).size !== names.length){ console.error('Duplicate filenames'); ok = false; }
  if (names.some(n => n.includes('_'))){ console.error('Underscore in filename'); ok = false; }
  Object.keys(EEL).forEach(k => {
    const t = EEL[k];
    if (!/^desc:/m.test(t) || !/^\/\/tags:/m.test(t) || !/^[a-z_0-9]+:-?[\d.]+<-?[\d.]+,-?[\d.]+,[\d.]+>/m.test(t) || t.indexOf('@init') < 0 || t.indexOf('@sample') < 0 || t.indexOf('srate') < 0){ console.error('EEL grammar: ' + k); ok = false; }
    if (/@slider/.test(t) || /^\s*\/\/.*@/m.test(t)){ console.error('EEL forbidden token: ' + k); ok = false; }
    if (!/min\(max\(out_L, -ceil_lin\), ceil_lin\)/.test(t)){ console.error('EEL clamp missing: ' + k); ok = false; }
  });
  if (ok) console.log('HyperAudio Self-tests passed.');
}

/* ============================================================
   SECTION 15 — INIT
   ============================================================ */
document.addEventListener('DOMContentLoaded', async () => {
  try { await loadAssets(); }
  catch(e){ EEL_OK = false; console.error('Asset load failed: ' + e.message); toast('Assets failed to load. Serve the folder over http(s).'); }
  UI_HOOKS.assets();
  document.querySelector('.brand small').textContent = 'RootlessJamesDSP · engine v' + VERSION;
  document.querySelector('footer p:last-child').textContent = 'HyperAudio engine v' + VERSION + ' · all computation runs locally in your browser';
  STATE.target = parseGraphicEQ('GraphicEQ: ' + DEFAULT_TARGET_GEQ);
  STATE.kzRaw = parseCSV(DEFAULT_KZ_CSV);
  STATE.spkRaw = parseCSV(DEFAULT_SPK_CSV);

  document.getElementById('target_input').value = 'GraphicEQ: ' + DEFAULT_TARGET_GEQ;

  document.getElementById('target_input').addEventListener('input', e => {
    STATE.target = parseGraphicEQ(e.target.value);
    drawFitCanvas();
  });

  document.getElementById('raw_kz_input').addEventListener('change', e => {
    const f = e.target.files[0]; if (!f) return;
    const r = new FileReader();
    r.onload = ev => {
      STATE.kzRaw = parseCSV(ev.target.result);
      drawFitCanvas();
      toast('Loaded KZ EDX Pro FR (' + STATE.kzRaw.length + ' pts)');
    };
    r.readAsText(f);
  });
  document.getElementById('raw_spk_input').addEventListener('change', e => {
    const f = e.target.files[0]; if (!f) return;
    const r = new FileReader();
    r.onload = ev => {
      STATE.spkRaw = parseCSV(ev.target.result);
      drawFitCanvas();
      toast('Loaded Redmi 12 speaker FR (' + STATE.spkRaw.length + ' pts)');
    };
    r.readAsText(f);
  });
  document.getElementById('btn_reset_defaults').addEventListener('click', () => {
    STATE.kzRaw = parseCSV(DEFAULT_KZ_CSV);
    STATE.spkRaw = parseCSV(DEFAULT_SPK_CSV);
    STATE.target = parseGraphicEQ('GraphicEQ: ' + DEFAULT_TARGET_GEQ);
    document.getElementById('target_input').value = 'GraphicEQ: ' + DEFAULT_TARGET_GEQ;
    drawFitCanvas();
    toast('Reset to embedded defaults');
  });

  document.getElementById('btn_fit_kz').addEventListener('click', () => runFit('KZ'));
  document.getElementById('btn_fit_spk').addEventListener('click', () => runFit('SPK'));
  document.getElementById('btn_clear_fits').addEventListener('click', () => {
    STATE.fitted = {};
    document.getElementById('fit_table').innerHTML = '';
    document.getElementById('fit_log').textContent = 'Fits cleared.';
    drawFitCanvas();
    renderPresetRegistry();
    renderExportGroups();
    renderWAVGrid();
    updateBadge();
  });


  document.getElementById('evidence').textContent = EVIDENCE_TEXT;

  renderPresetRegistry();
  renderExportGroups();
  renderWAVGrid();
  updateBadge();
  drawFitCanvas();
  window.addEventListener('resize', drawFitCanvas);
  runSelfTests();
});
