#!/usr/bin/env python3
"""
Ultrasonic phased array — 8-element receive beamforming at ~40 kHz
using ADALM2000 (libm2k).

Hardware wiring:
  W1  (DAC ch0)  -> transmitter transducer (continuous ~40 kHz drive)
  1+  (ain ch0)  -> muxed receive element  (selected by DIO 0,1,2)
  2+  (ain ch1)  -> transmit drive signal  (phase reference)
  DIO 0,1,2      -> mux address bits 0,1,2 (DIO0 = LSB)
  V+  (+4.5 V)   -> mux Vcc
  V-  (-4.5 V)   -> mux Vss
"""

import libm2k
import numpy as np
import matplotlib.pyplot as plt
import time

# ── Mode & calibration files ─────────────────────────────────────────────
do_cal         = False                   # True = capture calibration, False = normal operation
# do_cal         = True
CAL_PHASE_FILE = 'cal_phase_offsets.csv'
CAL_AMP_FILE   = 'cal_amplitudes.csv'

# ── Signal / timing constants ─────────────────────────────────────────────
FS_DAC  = 750_000.0
FS_ADC  = 1_000_000.0
N_DAC   = 3072           # exactly M complete cycles at FS_DAC
N_ADC   = 4096           # ADC capture length (coherent at FS_ADC)
M       = 163            # cycles in DAC buffer (prime -> clean spectrum)
F_SIG   = M * FS_DAC / N_DAC    # 39794.921875 Hz

# ADC bin = F_SIG / bin_width = F_SIG * N_ADC / FS_ADC = 1630 (exact integer)
SIG_BIN = round(F_SIG * N_ADC / FS_ADC)

# ── Array geometry ────────────────────────────────────────────────────────
N_ELEM     = 8

# Hand-built prototype, or 
# D_M        = 0.400 * 0.0254   # 400 mil pitch -> metres (10.16 mm)
# Offset elements
D_M        = 0.200 * 0.0254   # 400 mil pitch -> metres (10.16 mm)

C_MS       = 343.0             # speed of sound in air, m/s
LAM        = C_MS / F_SIG
MUX_SETTLE = 0.2              # seconds to wait after switching mux

print(f"Signal:  {F_SIG:.4f} Hz")
print(f"ADC bin: {SIG_BIN}  (bin centre {SIG_BIN * FS_ADC / N_ADC:.4f} Hz)")
print(f"d/λ:     {D_M / LAM:.3f}  (λ={LAM*1000:.2f} mm, d={D_M*1000:.2f} mm)")
if D_M / LAM > 0.5:
    print("  Note: d > λ/2 — expect grating lobes in beam pattern")

# ── Connect & configure ────────────────────────────────────────────────────
ctx = libm2k.m2kOpen()
if ctx is None:
    print("No ADALM2000 found.")
    exit(1)

ain  = ctx.getAnalogIn()
aout = ctx.getAnalogOut()
dig  = ctx.getDigital()
ps   = ctx.getPowerSupply()

ain.reset()
aout.reset()
dig.reset()

ctx.calibrateADC()
ctx.calibrateDAC()

# Power supply for mux
ps.enableChannel(0, True);  ps.pushChannel(0,  4.5)
ps.enableChannel(1, True);  ps.pushChannel(1, -4.5)

# ADC: both channels synchronized at FS_ADC
ain.setSampleRate(int(FS_ADC))
ain.enableChannel(0, True);  ain.setRange(0, -2, 2)
ain.enableChannel(1, True);  ain.setRange(1, -2, 2)
ain.setKernelBuffersCount(1)  # default is 4; avoid reading stale buffered captures

# DAC: W1 = continuous transmit, W2 = idle zeros
aout.setSampleRate(0, int(FS_DAC))
aout.setSampleRate(1, int(FS_DAC))
aout.enableChannel(0, True)
aout.enableChannel(1, True)

n_buf  = np.arange(N_DAC)
buf_tx = np.sin(2 * np.pi * M * n_buf / N_DAC)   # exactly M cycles
aout.setCyclic(True)
aout.push([buf_tx, buf_tx * -1.0]) # np.zeros(N_DAC)])

# Digital mux address: DIO 8,9,10 as push-pull outputs (bit 0 = DIO8)
# MUX_PINS = [8, 9, 10] # Hand wired prototype
MUX_PINS = [0, 1, 2]
dig.setSampleRateOut(1000)   # low rate is fine; we use setValueRaw not push
for pin in MUX_PINS:
    dig.setDirection(pin, libm2k.DIO_OUTPUT)
    dig.setOutputMode(pin, libm2k.DIO_PUSHPULL)
    dig.setValueRaw(pin, libm2k.LOW)
    dig.enableChannel(pin, True)

def set_mux(ch):
    """Select receive element ch (0-7) by writing 3-bit address to DIO 8,9,10."""
    for bit, pin in enumerate(MUX_PINS):
        dig.setValueRaw(pin, libm2k.HIGH if (ch >> bit) & 1 else libm2k.LOW)
    vals = [dig.getValueRaw(pin) for pin in MUX_PINS]
    # print(f"    mux ch={ch}  DIO8={vals[0]} DIO9={vals[1]} DIO10={vals[2]}")

# ── FFT diagnostic: verify we're reading the right bin ────────────────────
print("\nRunning FFT diagnostic on element 0...")
set_mux(0)
time.sleep(MUX_SETTLE)
diag_data = ain.getSamples(N_ADC)
diag_rx   = np.fft.rfft(np.asarray(diag_data[0]))
diag_ref  = np.fft.rfft(np.asarray(diag_data[1]))
diag_freq = np.fft.rfftfreq(N_ADC, d=1.0/FS_ADC)

peak_rx  = int(np.argmax(np.abs(diag_rx)))
peak_ref = int(np.argmax(np.abs(diag_ref)))
print(f"  Expected SIG_BIN : {SIG_BIN}  ({F_SIG:.2f} Hz)")
print(f"  argmax rx  bin   : {peak_rx}  ({diag_freq[peak_rx]:.2f} Hz)")
print(f"  argmax ref bin   : {peak_ref}  ({diag_freq[peak_ref]:.2f} Hz)")

fig_d, axes_d = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
mag_rx_db  = 20 * np.log10(np.abs(diag_rx)  + 1e-12)
mag_ref_db = 20 * np.log10(np.abs(diag_ref) + 1e-12)
axes_d[0].plot(diag_freq, mag_rx_db)
axes_d[0].axvline(F_SIG, color='C1', lw=0.9, linestyle='--', label=f"F_SIG={F_SIG:.0f} Hz (bin {SIG_BIN})")
axes_d[0].axvline(diag_freq[peak_rx], color='C2', lw=0.9, linestyle=':', label=f"argmax={diag_freq[peak_rx]:.0f} Hz (bin {peak_rx})")
axes_d[0].set_ylabel("dB")
axes_d[0].set_title("Receive channel FFT (element 0)")
axes_d[0].legend(fontsize=8)
axes_d[0].grid(True, alpha=0.4)
axes_d[1].plot(diag_freq, mag_ref_db)
axes_d[1].axvline(F_SIG, color='C1', lw=0.9, linestyle='--', label=f"F_SIG={F_SIG:.0f} Hz (bin {SIG_BIN})")
axes_d[1].axvline(diag_freq[peak_ref], color='C2', lw=0.9, linestyle=':', label=f"argmax={diag_freq[peak_ref]:.0f} Hz (bin {peak_ref})")
axes_d[1].set_xlabel("Frequency (Hz)")
axes_d[1].set_ylabel("dB")
axes_d[1].set_title("Reference channel FFT")
axes_d[1].legend(fontsize=8)
axes_d[1].grid(True, alpha=0.4)
plt.tight_layout()
plt.show()

# Use the argmax bin if it's significantly different from SIG_BIN
if peak_ref != SIG_BIN:
    print(f"\n  *** SIG_BIN mismatch! Using argmax bin {peak_ref} instead of {SIG_BIN}. ***")
    print(f"      Check FS_ADC — actual rate may differ from {FS_ADC:.0f} Hz")
    SIG_BIN = peak_ref

# ── Sequential capture of all 8 elements ──────────────────────────────────
# Physical element order (left to right) → mux address to select:
#   phys 0→IN5, 1→IN7, 2→IN6, 3→IN4, 4→IN3, 5→IN0, 6→IN1, 7→IN2
# MUX_ORDER = [5, 7, 6, 4, 3, 0, 1, 2] # Hand wired Prototype board
MUX_ORDER = [2, 1, 4, 6, 7, 5, 0, 3] # First PCB Prototype board

if do_cal:
    input("\nCALIBRATION MODE — aim the array directly at the transmitter (boresight),\n"
          "then press Enter to capture...")
else:
    try:
        cal_phases = np.loadtxt(CAL_PHASE_FILE, delimiter=',', comments='#')
        cal_amps   = np.loadtxt(CAL_AMP_FILE,   delimiter=',', comments='#')
    except FileNotFoundError as e:
        print(f"\nCalibration file not found ({e}). Run with do_cal = True first.")
        libm2k.contextClose(ctx)
        exit(1)

print("\nCapturing elements...")
elements = np.zeros(N_ELEM, dtype=complex)

for ch, mux_addr in enumerate(MUX_ORDER):
    set_mux(mux_addr)
    time.sleep(MUX_SETTLE)

    data    = ain.getSamples(N_ADC)

    fft_rx  = np.fft.rfft(np.asarray(data[0]))
    fft_ref = np.fft.rfft(np.asarray(data[1]))

    # Normalize receive phasor to unit reference — removes inter-capture phase drift
    ref_unit     = fft_ref[SIG_BIN] / np.abs(fft_ref[SIG_BIN])
    elements[ch] = fft_rx[SIG_BIN] / ref_unit

    print(f"  [{ch}] (mux {mux_addr})  {20*np.log10(np.abs(elements[ch]) + 1e-12):6.1f} dBFS  "
          f"{np.degrees(np.angle(elements[ch])):+7.1f} deg")

# Inter-element phases relative to element 0 (raw, before any calibration)
elem0_unit = elements[0] / np.abs(elements[0])
rel_phases = np.degrees(np.angle(elements / elem0_unit))
print("\nRelative to element 0 (raw):")
for ch in range(N_ELEM):
    print(f"  [{ch}]  {20*np.log10(np.abs(elements[ch]) + 1e-12):6.1f} dBFS  {rel_phases[ch]:+7.1f} deg")

if do_cal:
    cal_phases = np.degrees(np.angle(elements))   # absolute phase per element (ref-normalised)
    cal_amps   = np.abs(elements)
    np.savetxt(CAL_PHASE_FILE, cal_phases, delimiter=',', fmt='%.4f',
               header='Per-element phase offsets (deg) — boresight calibration')
    np.savetxt(CAL_AMP_FILE,   cal_amps,   delimiter=',', fmt='%.6f',
               header='Per-element amplitudes — boresight calibration')
    print(f"\nCalibration saved to {CAL_PHASE_FILE} and {CAL_AMP_FILE}")
    print("Set do_cal = False and re-run for normal operation.")
    libm2k.contextClose(ctx)
    exit(0)

# ── Apply calibration ─────────────────────────────────────────────────────
elements = elements * np.exp(-1j * np.radians(cal_phases))   # zero out static phase offsets
elements = elements / cal_amps                                # equalise element gains

elem0_unit = elements[0] / np.abs(elements[0])
rel_phases_cal = np.degrees(np.angle(elements / elem0_unit))
print("\nRelative to element 0 (calibrated):")
for ch in range(N_ELEM):
    print(f"  [{ch}]  {20*np.log10(np.abs(elements[ch]) + 1e-12):6.1f} dBFS  {rel_phases_cal[ch]:+7.1f} deg")

# ── Beamforming ───────────────────────────────────────────────────────────
thetas_deg = np.linspace(-90, 90, 721)
sin_thetas = np.sin(np.radians(thetas_deg))
k          = np.arange(N_ELEM)

# Build steering matrix: phase_matrix[i, k] = phase shift for element k at angle i
phase_matrix = 2 * np.pi * (D_M / LAM) * np.outer(sin_thetas, k)  # (721, 8)
beam         = np.abs(np.exp(-1j * phase_matrix) @ elements)        # (721,)

beam_norm = beam / beam.max()
beam_db   = 20 * np.log10(beam_norm + 1e-12)

peak_idx = np.argmax(beam)
print(f"\nPeak at {thetas_deg[peak_idx]:.1f} deg  ({beam_db[peak_idx]:.1f} dB)")

# ── Plot ──────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 6))

ax1 = fig.add_subplot(121)
ax1.plot(thetas_deg, beam_db)
ax1.axvline(thetas_deg[peak_idx], color='C1', linestyle='--', lw=0.9,
            label=f"peak {thetas_deg[peak_idx]:.1f}°")
ax1.set_xlabel("Steering angle (deg)")
ax1.set_ylabel("Normalized response (dB)")
ax1.set_title(f"Beam Pattern — {N_ELEM} elements @ {F_SIG:.0f} Hz, "
              f"d={D_M*1000:.1f} mm")
ax1.set_ylim(-40, 3)
ax1.legend()
ax1.grid(True, alpha=0.4)

ax2 = fig.add_subplot(122, projection='polar')
ax2.plot(np.radians(thetas_deg), beam_norm)
ax2.set_theta_zero_location('N')    # 0 deg at top (boresight)
ax2.set_theta_direction(-1)          # clockwise positive
ax2.set_thetamin(-90)
ax2.set_thetamax(90)
ax2.set_title("Polar Beam Pattern", va='bottom', pad=20)

plt.tight_layout()
plt.show()

libm2k.contextClose(ctx)
