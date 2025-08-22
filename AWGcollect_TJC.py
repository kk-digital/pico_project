# coding=gbk
import ctypes
import os
import time

import matplotlib.pyplot as plt
import numpy as np

from dochelp import append_column_to_csv
from picosdk.functions import adc2mV, assert_pico_ok
from picosdk.ps4000a import ps4000a as ps
from wavelet import calculate_wavelet


class PicoScopeAWG:
    def __init__(self):
        self.handle = ctypes.c_int16()
        self.status = {}
        self.timeIntervalns = ctypes.c_float()
        self.returnedMaxSamples = ctypes.c_int32()
        self.maxADC = ctypes.c_int16(32767)

    def open_device(self):
        self.status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(self.handle), None)
        try:
            assert_pico_ok(self.status["openunit"])
        except:
            powerstate = self.status["openunit"]
            if powerstate in (282, 286):
                self.status["ChangePowerSource"] = ps.ps4000aChangePowerSource(self.handle, powerstate)
                assert_pico_ok(self.status["ChangePowerSource"])
            else:
                raise
        print("设备已连接")

    def close_device(self):
        self.status["close"] = ps.ps4000aCloseUnit(self.handle)
        assert_pico_ok(self.status["close"])
        print("设备已关闭")

    @staticmethod
    def normalize(x):
        x = np.asarray(x)
        L = max(abs(np.min(x)), abs(np.max(x)))
        if L == 0:
            return np.full_like(x, fill_value=128, dtype=np.uint8)
        x_mapped = (x / L) * 32767
        return np.clip(np.round(x_mapped), -32768, 32767).astype(np.int16)

    def generate_waveform(self, wtype, wA, wB, wC):
        x = calculate_wavelet(wtype, wA, wB, wC)
        z = [0] * (256 + 128)
        x = np.concatenate([z, x, z])
        return self.normalize(x)

    def set_awg(self, waveform, frequency):
        waveform = waveform.astype(np.int16)
        waveform_size = len(waveform)
        start_delta_phase = ctypes.c_uint32()
        self.status["Phase"] = ps.ps4000aSigGenFrequencyToPhase(
            self.handle, ctypes.c_double(frequency),
            ps.PS4000A_INDEX_MODE["PS4000A_SINGLE"],
            waveform_size,
            ctypes.byref(start_delta_phase)
        )
        assert_pico_ok(self.status["Phase"])
        self.status["AWGwave"] = ps.ps4000aSetSigGenArbitrary(
            self.handle, 0, 4000000,
            start_delta_phase.value, start_delta_phase.value,
            0, 0,
            waveform.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
            waveform_size,
            ps.PS4000A_SWEEP_TYPE["PS4000A_UP"],
            ps.PS4000A_EXTRA_OPERATIONS["PS4000A_ES_OFF"],
            ps.PS4000A_INDEX_MODE["PS4000A_SINGLE"],
            0, 0,
            ps.PS4000A_SIGGEN_TRIG_TYPE["PS4000A_SIGGEN_RISING"],
            ps.PS4000A_SIGGEN_TRIG_SOURCE["PS4000A_SIGGEN_NONE"],
            0
        )
        assert_pico_ok(self.status["AWGwave"])
        print(f"AWG 已配置，频率={frequency}Hz")

    def capture(self, timebase=3, samples=4096):
        self.status["setChA"] = ps.ps4000aSetChannel(self.handle, 0, 1, 1, 7, 0)
        self.status["setChB"] = ps.ps4000aSetChannel(self.handle, 1, 1, 1, 7, 0)
        assert_pico_ok(self.status["setChA"])
        assert_pico_ok(self.status["setChB"])

        self.status["trigger"] = ps.ps4000aSetSimpleTrigger(self.handle, 1, 0, 1024, 2, 0, 1000)
        self.status["getTimebase2"] = ps.ps4000aGetTimebase2(
            self.handle, timebase, samples,
            ctypes.byref(self.timeIntervalns),
            ctypes.byref(self.returnedMaxSamples), 0
        )
        assert_pico_ok(self.status["getTimebase2"])

        bufferA = (ctypes.c_int16 * samples)()
        bufferB = (ctypes.c_int16 * samples)()
        ps.ps4000aSetDataBuffer(self.handle, 0, ctypes.byref(bufferA), samples, 0, 0)
        ps.ps4000aSetDataBuffer(self.handle, 1, ctypes.byref(bufferB), samples, 0, 0)

        ps.ps4000aRunBlock(self.handle, 0, samples, timebase, None, 0, None, None)
        ready = ctypes.c_int16(0)
        while not ready.value:
            ps.ps4000aIsReady(self.handle, ctypes.byref(ready))

        cmaxSamples = ctypes.c_int32(samples)
        overflow = (ctypes.c_int16 * 10)()
        ps.ps4000aGetValuesBulk(self.handle, ctypes.byref(cmaxSamples), 0, 0, 1, 0, ctypes.byref(overflow))

        adcA = adc2mV(bufferA, 7, self.maxADC)
        adcB = adc2mV(bufferB, 7, self.maxADC)
        timeline = np.linspace(0, (samples - 1) * self.timeIntervalns.value, samples)

        return timeline, adcA, adcB

    def save_data(self, save_dir, wtype, wA, wB, wC, frequency, timeline, adcA, adcB):
        os.makedirs(save_dir, exist_ok=True)
        label = f"type={wtype},A={wA},B={wB},C={wC},f={frequency}"
        append_column_to_csv(os.path.join(save_dir, "channelA.csv"), label, adcA)
        append_column_to_csv(os.path.join(save_dir, "channelB.csv"), label, adcB)
        append_column_to_csv(os.path.join(save_dir, "timebase.csv"), label, timeline)
        print(f"数据已保存到 {save_dir}")

    @staticmethod
    def plot_waveform(timeline, adcA, adcB, title):
        """每次采集单独画图"""
        plt.figure(figsize=(10, 5))
        plt.plot(timeline, adcA, label="Channel A", color="b")
        plt.plot(timeline, adcB, label="Channel B", color="r")
        plt.xlabel("Time (ns)")
        plt.ylabel("Voltage (mV)")
        plt.title(title)
        plt.legend()
        plt.grid()
        plt.show()


# ================== 使用示例 ==================

if __name__ == "__main__":
    scope = PicoScopeAWG()
    scope.open_device()

    choose = [1, 4, 6]        # 小波类型
    freqs = [1000000, 200000] # 频率列表

    for wtype in choose:
        for f in freqs:
            wf = scope.generate_waveform(wtype, 1, 1, 1)
            scope.set_awg(wf, f)
            time.sleep(2)

            t, chA, chB = scope.capture()
            title = f"Wavelet type={wtype}, f={f}Hz"
            scope.plot_waveform(t, chA, chB, title)
            scope.save_data("AWG/output", wtype, 1, 1, 1, f, t, chA, chB)

    scope.close_device()
