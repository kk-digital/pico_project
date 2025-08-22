import ctypes
import numpy as np
from picosdk.ps4000a import ps4000a as ps
from picosdk.functions import assert_pico_ok
from wavelet import *
from picosdk.functions import adc2mV, assert_pico_ok
import time


def normalize(x):
    x = np.asarray(x)
    L = max(abs(np.min(x)), abs(np.max(x)))
    if L == 0:
        return np.full_like(x, fill_value=128, dtype=np.uint8)  # 中点
    x_mapped = (x) / (L) * 32767
    return np.clip(np.round(x_mapped), -32768, 32767).astype(np.int16)


x = calculate_wavelet(9, 3, 16, 2)
random_list = [np.random.uniform(5.0, 10.0) for _ in range(1024)]
z = [0] * (256)

x = np.concatenate([z, x, z])
sig = normalize(x)
# 将列表转换为 NumPy 数组
data_array = np.array(sig)
# arbitraryWaveform = waveform.astype('uint8')
arbitraryWaveform = data_array.astype(np.int16)
arbitraryWaveformSize = ctypes.c_int32(len(arbitraryWaveform))
WaveformSize = len(arbitraryWaveform)

plt.plot(x)
plt.show()

# 打开设备
status = {}
handle = ctypes.c_int16()
idex_type = ps.PS4000A_INDEX_MODE["PS4000A_SINGLE"]
sweep_type = ps.PS4000A_SWEEP_TYPE["PS4000A_UP"]

# Opens the device/s
status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(handle), None)

try:
    assert_pico_ok(status["openunit"])
except:
    # powerstate becomes the status number of openunit
    powerstate = status["openunit"]

    # If powerstate is the same as 282 then it will run this if statement
    if powerstate == 282:
        # Changes the power input to "PICO_POWER_SUPPLY_NOT_CONNECTED"
        status["ChangePowerSource"] = ps.ps4000aChangePowerSource(handle, 282)
    # If the powerstate is the same as 286 then it will run this if statement
    elif powerstate == 286:
        # Changes the power input to "PICO_USB3_0_DEVICE_NON_USB3_0_PORT"
        status["ChangePowerSource"] = ps.ps4000aChangePowerSource(handle, 286)
    else:
        raise

    assert_pico_ok(status["ChangePowerSource"])

# # 生成一个正弦波形数据
# WaveformSize = 100
# t = np.linspace(0, 2 * np.pi, WaveformSize, endpoint=False)
# arbitraryWaveform = (32767 * np.sin(t)).astype(np.int16)

# 计算 deltaPhase
start_freq = 1000000  # 1 kHz
start_delta_phase = ctypes.c_uint32()
status["Phase"] = ps.ps4000aSigGenFrequencyToPhase(
    handle,
    ctypes.c_double(start_freq),
    idex_type,
    WaveformSize,
    ctypes.byref(start_delta_phase)
)
assert_pico_ok(status["Phase"])

# 设置任意波形发生器
status["AWGwave"] = ps.ps4000aSetSigGenArbitrary(
    handle,
    0,  # offsetVoltage
    1000000,  # pkToPk
    start_delta_phase.value,  # startDeltaPhase
    start_delta_phase.value,  # stopDeltaPhase
    0,  # deltaPhaseIncrement
    0,  # dwellCount
    # waveform.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),  # arbitraryWaveform
    arbitraryWaveform.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
    WaveformSize,  # arbitraryWaveformSize
    ps.PS4000A_SWEEP_TYPE["PS4000A_UP"],
    ps.PS4000A_EXTRA_OPERATIONS["PS4000A_ES_OFF"],
    ps.PS4000A_INDEX_MODE["PS4000A_SINGLE"],
    0,  # shots
    0,  # sweeps
    ps.PS4000A_SIGGEN_TRIG_TYPE["PS4000A_SIGGEN_RISING"],
    ps.PS4000A_SIGGEN_TRIG_SOURCE["PS4000A_SIGGEN_NONE"],
    0  # extInThreshold
)
# status = ps.ps4000aSetSigGenArbitrary(
#     handle,
#     offsetVoltage=0,
#     pkToPk=2000000,  # 2 V (单位：μV)
#     startDeltaPhase=start_delta_phase.value,
#     stopDeltaPhase=start_delta_phase.value,
#     deltaPhaseIncrement=0,
#     dwellCount=0,
#     arbitraryWaveform=waveform.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
#     arbitraryWaveformSize=waveform_size,
#     sweepType=ps.PS4000A_SWEEP_TYPE["PS4000A_UP"],
#     operation=ps.PS4000A_EXTRA_OPERATIONS["PS4000A_ES_OFF"],
#     indexMode=ps.PS4000A_INDEX_MODE["PS4000A_SINGLE"],
#     shots=0,
#     sweeps=0,
#     triggerType=ps.PS4000A_SIGGEN_TRIG_TYPE["PS4000A_SIGGEN_RISING"],
#     triggerSource=ps.PS4000A_SIGGEN_TRIG_SOURCE["PS4000A_SIGGEN_NONE"],
#     extInThreshold=0
# )
assert_pico_ok(status["AWGwave"])
# status["trigger"] = ps.ps4000aSetSimpleTrigger(handle, 1, 0, 1024, 2, 0, 1000)
# assert_pico_ok(status["trigger"])
print("任意波形发生器设置成功。")
time.sleep(3)
# Set up channel A
# handle = handle
# channel = PS4000a_CHANNEL_A = 0
# enabled = 1
# coupling type = PS4000a_DC = 1
# range = PS4000a_2V = 7
# analogOffset = 0 V
chARange = 7
status["setChA"] = ps.ps4000aSetChannel(handle, 0, 1, 1, chARange, 0)
assert_pico_ok(status["setChA"])

# Set up channel B
# handle = handle
# channel = PS4000a_CHANNEL_B = 1
# enabled = 1
# coupling type = PS4000a_DC = 1
# range = PS4000a_2V = 7
# analogOffset = 0 V
# chBRange = 7
# status["setChB"] = ps.ps4000aSetChannel(handle, 1, 1, 1, chBRange, 0)
# assert_pico_ok(status["setChB"])

# Set up single trigger
# handle = handle
# enabled = 1
# source = PS4000a_CHANNEL_A = 0
# threshold = 1024 ADC counts
# direction = PS4000a_RISING = 2
# delay = 0 s
# auto Trigger = 1000 ms
status["trigger"] = ps.ps4000aSetSimpleTrigger(handle, 1, 0, 1024, 2, 0, 1000)
assert_pico_ok(status["trigger"])

# Set number of pre and post trigger samples to be collected
preTriggerSamples = 0
postTriggerSamples = 4096
maxSamples = preTriggerSamples + postTriggerSamples

# Get timebase information
# WARNING: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.  
# To access these Timebases, set any unused analogue channels to off.
# handle = handle
# timebase = 8 = timebase
# noSamples = maxSamples
# pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
# pointer to maxSamples = ctypes.byref(returnedMaxSamples)
# segment index = 0
timebase = 1
timeIntervalns = ctypes.c_float()
returnedMaxSamples = ctypes.c_int32()
oversample = ctypes.c_int16(1)
status["getTimebase2"] = ps.ps4000aGetTimebase2(handle, timebase, maxSamples, ctypes.byref(timeIntervalns),
                                                ctypes.byref(returnedMaxSamples), 0)
assert_pico_ok(status["getTimebase2"])

# Set memory segments
# handle = handle
# nSegments = 10
nMaxSamples = ctypes.c_int32(0)
status["setMemorySegments"] = ps.ps4000aMemorySegments(handle, 10, ctypes.byref(nMaxSamples))
assert_pico_ok(status["setMemorySegments"])

# Set number of captures
# handle = handle
# nCaptures = 10
status["SetNoOfCaptures"] = ps.ps4000aSetNoOfCaptures(handle, 10)
assert_pico_ok(status["SetNoOfCaptures"])

# set up buffers
bufferA0 = (ctypes.c_int16 * maxSamples)()
# bufferA1 = (ctypes.c_int16 * maxSamples)()
# bufferA2 = (ctypes.c_int16 * maxSamples)()
# bufferA3 = (ctypes.c_int16 * maxSamples)()
# bufferA4 = (ctypes.c_int16 * maxSamples)()
# bufferA5 = (ctypes.c_int16 * maxSamples)()
# bufferA6 = (ctypes.c_int16 * maxSamples)()
# bufferA7 = (ctypes.c_int16 * maxSamples)()
# bufferA8 = (ctypes.c_int16 * maxSamples)()
# bufferA9 = (ctypes.c_int16 * maxSamples)()
#
# bufferB0 = (ctypes.c_int16 * maxSamples)()
# bufferB1 = (ctypes.c_int16 * maxSamples)()
# bufferB2 = (ctypes.c_int16 * maxSamples)()
# bufferB3 = (ctypes.c_int16 * maxSamples)()
# bufferB4 = (ctypes.c_int16 * maxSamples)()
# bufferB5 = (ctypes.c_int16 * maxSamples)()
# bufferB6 = (ctypes.c_int16 * maxSamples)()
# bufferB7 = (ctypes.c_int16 * maxSamples)()
# bufferB8 = (ctypes.c_int16 * maxSamples)()
# bufferB9 = (ctypes.c_int16 * maxSamples)()

# set data buffers
# handle = handle
# channel = PS4000A_CHANNEL_A = 0
# buffer = bufferAX (where X = segmentIndex)
# bufferLength = maxSamples
# segmentIndex = X
# mode = PS4000A_RATIO_MODE_NONE = 0

status["setDataBufferA0"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferA0), maxSamples, 0, 0)
# status["setDataBufferA1"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferA1), maxSamples, 1, 0)
# status["setDataBufferA2"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferA2), maxSamples, 2, 0)
# status["setDataBufferA3"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferA3), maxSamples, 3, 0)
# status["setDataBufferA4"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferA4), maxSamples, 4, 0)
# status["setDataBufferA5"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferA5), maxSamples, 5, 0)
# status["setDataBufferA6"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferA6), maxSamples, 6, 0)
# status["setDataBufferA7"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferA7), maxSamples, 7, 0)
# status["setDataBufferA8"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferA8), maxSamples, 8, 0)
# status["setDataBufferA9"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferA9), maxSamples, 9, 0)
#
# status["setDataBufferB0"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferB0), maxSamples, 0, 0)
# status["setDataBufferB1"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferB1), maxSamples, 1, 0)
# status["setDataBufferB2"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferB2), maxSamples, 2, 0)
# status["setDataBufferB3"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferB3), maxSamples, 3, 0)
# status["setDataBufferB4"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferB4), maxSamples, 4, 0)
# status["setDataBufferB5"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferB5), maxSamples, 5, 0)
# status["setDataBufferB6"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferB6), maxSamples, 6, 0)
# status["setDataBufferB7"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferB7), maxSamples, 7, 0)
# status["setDataBufferB8"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferB8), maxSamples, 8, 0)
# status["setDataBufferB9"] = ps.ps4000aSetDataBuffer(handle, 0, ctypes.byref(bufferB9), maxSamples, 9, 0)

# run block capture
# handle = handle
# number of pre-trigger samples = preTriggerSamples
# number of post-trigger samples = PostTriggerSamples
# timebase = 3 = 80 ns = timebase (see Programmer's guide for mre information on timebases)
# time indisposed ms = None (not needed in the example)
# segment index = 0
# lpReady = None (using ps4000aIsReady rather than ps4000aBlockReady)
# pParameter = None
status["gate"] = ps.ps4000aSigGenSoftwareControl(handle, 1)
status["runBlock"] = ps.ps4000aRunBlock(handle, preTriggerSamples, postTriggerSamples, timebase, None, 0, None, None)
assert_pico_ok(status["runBlock"])
status["gate"] = ps.ps4000aSigGenSoftwareControl(handle, 1)
# check for end of capture
ready = ctypes.c_int16(0)
check = ctypes.c_int16(0)
while ready.value == check.value:
    status["isReady"] = ps.ps4000aIsReady(handle, ctypes.byref(ready))

# Creates a overlow location for data
overflow = (ctypes.c_int16 * 10)()
# Creates converted types maxsamples
cmaxSamples = ctypes.c_int32(maxSamples)

# collect data 
# handle = handle
# noOfSamples = cmaxSamples
# fromSegmentIndex = 0
# toSegmentIndex = 9
# downSampleRatio = 1
# downSampleRatioMode = PS4000A_RATIO_MODE_NONE
status["getValuesBulk"] = ps.ps4000aGetValuesBulk(handle, ctypes.byref(cmaxSamples), 0, 0, 1, 0, ctypes.byref(overflow))
assert_pico_ok(status["getValuesBulk"])

# find maximum ADC count value
# handle = handle
# pointer to value = ctypes.byref(maxADC)
maxADC = ctypes.c_int16(32767)

# convert from adc to mV
adc2mVChA0 = adc2mV(bufferA0, chARange, maxADC)
# adc2mVChA1 =  adc2mV(bufferA1, chARange, maxADC)
# adc2mVChA2 =  adc2mV(bufferA2, chARange, maxADC)
# adc2mVChA3 =  adc2mV(bufferA3, chARange, maxADC)
# adc2mVChA4 =  adc2mV(bufferA4, chARange, maxADC)
# adc2mVChA5 =  adc2mV(bufferA5, chARange, maxADC)
# adc2mVChA6 =  adc2mV(bufferA6, chARange, maxADC)
# adc2mVChA7 =  adc2mV(bufferA7, chARange, maxADC)
# adc2mVChA8 =  adc2mV(bufferA8, chARange, maxADC)
# adc2mVChA9 =  adc2mV(bufferA9, chARange, maxADC)
#
# adc2mVChB0 =  adc2mV(bufferB0, chARange, maxADC)
# adc2mVChB1 =  adc2mV(bufferB1, chARange, maxADC)
# adc2mVChB2 =  adc2mV(bufferB2, chARange, maxADC)
# adc2mVChB3 =  adc2mV(bufferB3, chARange, maxADC)
# adc2mVChB4 =  adc2mV(bufferB4, chARange, maxADC)
# adc2mVChB5 =  adc2mV(bufferB5, chARange, maxADC)
# adc2mVChB6 =  adc2mV(bufferB6, chARange, maxADC)
# adc2mVChB7 =  adc2mV(bufferB7, chARange, maxADC)
# adc2mVChB8 =  adc2mV(bufferB8, chARange, maxADC)
# adc2mVChB9 =  adc2mV(bufferB9, chARange, maxADC)

# Create time data
time = np.linspace(0, ((cmaxSamples.value) - 1) * timeIntervalns.value, cmaxSamples.value)

# plot data
plt.plot(time, adc2mVChA0)
# plt.plot(time, adc2mVChB1)
# plt.plot(time, adc2mVChA2)
# plt.plot(time, adc2mVChA3)
# plt.plot(time, adc2mVChA4)
# plt.plot(time, adc2mVChA5)
# plt.plot(time, adc2mVChA6)
# plt.plot(time, adc2mVChA7)
# plt.plot(time, adc2mVChA8)
# plt.plot(time, adc2mVChB9)
plt.xlabel('Time (ns)')
plt.ylabel('Voltage (mV)')
plt.show()

# Stop the scope
# handle = handle
status["stop"] = ps.ps4000aStop(handle)
assert_pico_ok(status["stop"])

# Close unitDisconnect the scope
# handle = handle
status["close"] = ps.ps4000aCloseUnit(handle)
assert_pico_ok(status["close"])

# display status returns
print(status)
