#!/usr/bin/env python3
"""
TTS 性能对比测试 - CosyVoice3 vs kokoro-onnx
使用《玄鉴仙族》第一章进行测试
"""

import os
import sys
import time
import json
import psutil
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, '/tmp/CosyVoice')

CHAPTER1_TEXT = """陆江仙做了一个很长很长的梦，梦见田间种稻，梦见刀光剑影，梦见仙宗、女子、大湖。

将《太阴吐纳练气诀》与《月华纪要秘旨》交出，我等可以只废去你修为。

一道悦耳又冰冷的女声在耳边响起，陆江仙隐隐约约看见一张朦胧的脸庞，却什么也看不清楚。

咣当。

剧烈的摇晃感一下子将陆江仙惊醒。

光怪陆离的色彩在脑海中浮现，陆江仙想睁开眼，想起身，身体如同鬼压床般对他的指挥毫不理睬。

这时，一道灿烂的白光划破眼前的浓密的黑暗，虽然黑暗如同潮水一般不断涌来，但那道光柱始终矗立着，太阳一般亘古不变。

密密麻麻的金色咒文从中迸发而出，在黑暗中舒展着身体，像星辰一样撒满天空。

好美。陆江仙呆呆地想着

随着咒文越来越多，彷佛到达了某个极限，他听到了如同玻璃破碎的卡察声

世界，亮了。

陆江仙看见了蔚然如大海的天空，茂密的无边无际的原始森林，不远处是弯月型的小湖，在那个方向，一道白色的流光滑落在波光粼粼的小湖中。

下方坐落着一小片秸秆扎成顶的小屋和成片的稻田。

剧烈翻滚的视角中，他像一只轻飘飘的燕雀飞过褐黄色的小小的村落和烟火，从清澈的小河上空划过。

惊鸿一瞥中，陆江仙望见了小河中自己的倒影。

好像是一个圆形的，闪闪发光的东西。陆江仙迷茫地想着，一种隐约的预兆浮现在心头。

我不做人了？

哗啦。剧烈的摇晃再次袭来，陆江仙迅速沉入水中，小河太浅不足以化解所有冲击力，于是他轻轻地磕在了小河底的青石之上。

这么一磕让陆江仙感觉像是被人在胸前干了一拳，有些胸闷气短，倒是自己的身体借助激荡的河水和撞击的反冲力稳稳的翻了个身，成了正面朝上，正对着河面上水波荡漾的太阳。

我不是在出租房中熬夜改方桉么？

陆江仙默默地看着河面上的太阳，水波湍急地流动着，让水底的光纹不断扭动。

默默地回忆着记忆中的过去，陆江仙头疼不已，只记得自己虚脱地倒在床上，出租房里的烟气和霓虹灯的辉光在身侧穿行。

开了瓶啤酒，坐在昏暗的电脑桌前，随着天旋地转般的眩晕感升起，感觉心脏飞速跳动，呼吸渐渐困难。

我好像挂了？

这样也挺好的，不用担心未来，不用担心生活。

也许是压抑了太久，陆江仙脑海中竟然浮现出这样的念头，心情甚至有些雀跃。

观察了一下周边，头顶上墨绿色的垂着气根的树梢，时不时从面上快速游过的灵巧鱼儿，隐隐约约叮叮冬冬的水花撞击声。

陆江仙叹了口气。

只是这样下去会无聊到发疯的吧。

于是他呆呆地望着太阳慢慢从头顶滑落，灿烂的夕阳爬满天空，树梢下的水域一点一点暗澹下去。

期间有两只鱼好奇地在他身边巡梭，甚至有只螃蟹试图将他翻过来。

直到月亮移动到树梢上，清亮的月光柔和地飘在河面上，陆江仙惊喜地感觉到一股清凉的气息渗透到河底，隐约带来一种舒适感。

看着月光一点点汇聚在身体上方，彷佛活过来般形成了一抹澹白色的月晕，陆江仙大惊失色，心境发生了截然不同的变化。

这算什么，吞吐日月精华么？这世界上真有仙人，有神妙的神通，有妖怪，有鬼神？他震惊地想着，我那成了什么，器灵么？

陆江仙内心深处升起一股好奇与喜悦，那一抹月晕彷佛也积蓄够了力量，飘落在他身上。

他只觉得周身一凉，陷入一种似睡非睡的冥想之中。

不知过了多久，气流越来越稀薄，陆江仙蓦然惊醒，月牙已经从天空中褪去，太阳跃出树梢，暖暖的晨曦撒在河面上。

好快。

陆江仙喜不自禁，仔细感受之下，体内果然有一股澹澹的气流在徘回，围绕着身体的圆边做圆周运动。

甚至陆江仙凝气沉神之下还能模模湖湖地看到一面灰青色的镜子静静地躺在河底，身下铺满了各色的石子，几条游鱼正在河底觅食。

那只河蟹正在一旁掘土。可以看见的范围大概在周身一米左右，不算清晰，像是小时候看的厚脑袋电视机。

这便是现在的我了吧。陆江仙苦笑着，接着他特意操控气流停滞在镜子中心，灰青色的镜子随之发出一丝丝毫光。

除了发光，倒也没发现什么用途。

先好好吞吐月华，说不定会有质变。他暗自计划着。不知道镜子的材质，也不知道外界怎么看待有灵智的器物，可别被哪个修仙者发现随手泯去了神智。"""

SHORT_TEXT = "陆江仙做了一个很长很长的梦，梦见田间种稻，梦见刀光剑影。"

class PerformanceMetrics:
    def __init__(self):
        self.process = psutil.Process()

    def get_memory_mb(self) -> float:
        return self.process.memory_info().rss / 1024 / 1024

    def measure(self, func, *args, **kwargs) -> tuple:
        mem_before = self.get_memory_mb()
        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()
        mem_after = self.get_memory_mb()

        return result, end_time - start_time, mem_after - mem_before


class CosyVoice3Tester:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.model = None
        self.sample_rate = None

    def load_model(self) -> Dict[str, float]:
        print("\n" + "=" * 70)
        print("📥 加载 CosyVoice3 模型...")
        print("=" * 70)

        metrics = PerformanceMetrics()

        def _load():
            from cosyvoice.cli.cosyvoice import CosyVoice
            model_dir = 'pretrained_models/CosyVoice-300M-SFT'
            self.model = CosyVoice(model_dir)
            self.sample_rate = self.model.sample_rate
            return self.model

        _, load_time, mem_delta = metrics.measure(_load)

        result = {
            "load_time": load_time,
            "memory_delta_mb": mem_delta,
            "memory_after_mb": metrics.get_memory_mb()
        }

        print(f"   ✅ 加载完成!")
        print(f"   ⏱️  加载时间: {load_time:.2f}s")
        print(f"   💾 内存占用: {mem_delta:.1f}MB")
        print(f"\n📋 可用音色:")
        for spk in self.model.list_available_spks():
            print(f"   - {spk}")

        return result

    def test_generation(self, text: str, voice: str = "中文男", output_file: str = None) -> Dict[str, Any]:
        print(f"\n🎤 生成中 (音色: {voice})...")
        print(f"   文本长度: {len(text)} 字符")

        metrics = PerformanceMetrics()

        def _generate():
            return self.model.inference_sft(text, voice, stream=False)

        result, gen_time, mem_delta = metrics.measure(_generate)

        if output_file:
            import torchaudio
            output_path = os.path.join(self.output_dir, output_file)
            torchaudio.save(output_path, result['tts_speech'], self.sample_rate)
            file_size = os.path.getsize(output_path) / 1024
        else:
            output_path = None
            file_size = 0

        audio_duration = result['tts_speech'].shape[1] / self.sample_rate
        rtf = audio_duration / gen_time if gen_time > 0 else 0

        print(f"   ✅ 生成完成!")
        print(f"   ⏱️  生成时间: {gen_time:.2f}s")
        print(f"   🎵 音频时长: {audio_duration:.2f}s")
        print(f"   ⚡ 实时因子: {rtf:.2f}x")
        print(f"   📦 文件大小: {file_size:.1f}KB")

        return {
            "text_length": len(text),
            "gen_time": gen_time,
            "audio_duration": audio_duration,
            "real_time_factor": rtf,
            "memory_delta_mb": mem_delta,
            "file_size_kb": file_size,
            "output_file": output_path
        }


class KokoroOnnxTester:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.model = None

    def load_model(self) -> Dict[str, float]:
        print("\n" + "=" * 70)
        print("📥 加载 kokoro-onnx 模型...")
        print("=" * 70)

        metrics = PerformanceMetrics()

        def _load():
            from kokoro_onnx import Kokoro
            model_path = "models/kokoro-v1.0.onnx"
            voices_path = "models/voices-v1.0.bin"
            self.model = Kokoro(model_path, voices_path)
            return self.model

        _, load_time, mem_delta = metrics.measure(_load)

        result = {
            "load_time": load_time,
            "memory_delta_mb": mem_delta,
            "memory_after_mb": metrics.get_memory_mb()
        }

        print(f"   ✅ 加载完成!")
        print(f"   ⏱️  加载时间: {load_time:.2f}s")
        print(f"   💾 内存占用: {mem_delta:.1f}MB")

        voices = self.model.get_voices()
        print(f"\n📋 可用音色数量: {len(voices)}")
        print("   (部分音色示例)")
        for v in voices[:10]:
            print(f"   - {v}")

        return result

    def test_generation(self, text: str, voice: str = "am_adam", output_file: str = None) -> Dict[str, Any]:
        print(f"\n🎤 生成中 (音色: {voice})...")
        print(f"   文本长度: {len(text)} 字符")

        metrics = PerformanceMetrics()

        def _generate():
            return self.model.create(text, voice=voice, speed=1.0)

        (samples, sample_rate), gen_time, mem_delta = metrics.measure(_generate)

        if output_file:
            import soundfile as sf
            output_path = os.path.join(self.output_dir, output_file)
            sf.write(output_path, samples, sample_rate)
            file_size = os.path.getsize(output_path) / 1024
        else:
            output_path = None
            file_size = 0

        audio_duration = len(samples) / sample_rate
        rtf = audio_duration / gen_time if gen_time > 0 else 0

        print(f"   ✅ 生成完成!")
        print(f"   ⏱️  生成时间: {gen_time:.2f}s")
        print(f"   🎵 音频时长: {audio_duration:.2f}s")
        print(f"   ⚡ 实时因子: {rtf:.2f}x")
        print(f"   📦 文件大小: {file_size:.1f}KB")

        return {
            "text_length": len(text),
            "gen_time": gen_time,
            "audio_duration": audio_duration,
            "real_time_factor": rtf,
            "memory_delta_mb": mem_delta,
            "file_size_kb": file_size,
            "sample_rate": sample_rate,
            "output_file": output_path
        }


def main():
    print("=" * 70)
    print("🎙️  TTS 性能对比测试: CosyVoice3 vs kokoro-onnx")
    print("   文本：《玄鉴仙族》第一章")
    print("=" * 70)
    print(f"\n📝 测试文本长度: {len(CHAPTER1_TEXT)} 字符")

    results = {
        "test_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text_length": len(CHAPTER1_TEXT),
        "models": {}
    }

    output_dir = "tts_test_output"
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 70)
    print("🧪 测试 1: CosyVoice3 (中文男声)")
    print("=" * 70)

    try:
        cosyvoice = CosyVoice3Tester(output_dir)

        load_info = cosyvoice.load_model()
        results["models"]["CosyVoice3"] = {
            "load_info": load_info,
            "short_test": None,
            "full_test": None
        }

        print("\n" + "-" * 50)
        print("📊 短文本测试 (约50字)...")
        short_result = cosyvoice.test_generation(
            SHORT_TEXT,
            voice="中文男",
            output_file="cosyvoice_short.wav"
        )
        results["models"]["CosyVoice3"]["short_test"] = short_result

        print("\n" + "-" * 50)
        print("📊 完整第一章测试...")
        full_result = cosyvoice.test_generation(
            CHAPTER1_TEXT,
            voice="中文男",
            output_file="cosyvoice_chapter1.wav"
        )
        results["models"]["CosyVoice3"]["full_test"] = full_result

    except Exception as e:
        print(f"❌ CosyVoice3 测试失败: {e}")
        import traceback
        traceback.print_exc()
        results["models"]["CosyVoice3"] = {"error": str(e)}

    print("\n" + "=" * 70)
    print("🧪 测试 2: kokoro-onnx")
    print("=" * 70)

    try:
        kokoro = KokoroOnnxTester(output_dir)

        load_info = kokoro.load_model()
        results["models"]["kokoro-onnx"] = {
            "load_info": load_info,
            "short_test": None,
            "full_test": None
        }

        print("\n" + "-" * 50)
        print("📊 短文本测试 (约50字)...")
        short_result = kokoro.test_generation(
            SHORT_TEXT,
            voice="am_adam",
            output_file="kokoro_short.wav"
        )
        results["models"]["kokoro-onnx"]["short_test"] = short_result

        print("\n" + "-" * 50)
        print("📊 完整第一章测试...")
        full_result = kokoro.test_generation(
            CHAPTER1_TEXT,
            voice="am_adam",
            output_file="kokoro_chapter1.wav"
        )
        results["models"]["kokoro-onnx"]["full_test"] = full_result

    except Exception as e:
        print(f"❌ kokoro-onnx 测试失败: {e}")
        import traceback
        traceback.print_exc()
        results["models"]["kokoro-onnx"] = {"error": str(e)}

    results_file = os.path.join(output_dir, "benchmark_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)

    print(f"\n测试时间: {results['test_time']}")
    print(f"文本长度: {results['text_length']} 字符\n")

    for model_name, model_data in results["models"].items():
        print(f"\n【{model_name}】")
        if "error" in model_data:
            print(f"   ❌ 测试失败: {model_data['error']}")
            continue

        load_info = model_data.get("load_info", {})
        print(f"   加载时间: {load_info.get('load_time', 'N/A'):.2f}s")
        print(f"   加载内存: {load_info.get('memory_delta_mb', 'N/A'):.1f}MB")

        short_test = model_data.get("short_test")
        if short_test:
            print(f"\n   短文本测试:")
            print(f"      生成时间: {short_test['gen_time']:.2f}s")
            print(f"      音频时长: {short_test['audio_duration']:.2f}s")
            print(f"      实时因子: {short_test['real_time_factor']:.2f}x")

        full_test = model_data.get("full_test")
        if full_test:
            print(f"\n   第一章测试:")
            print(f"      生成时间: {full_test['gen_time']:.2f}s")
            print(f"      音频时长: {full_test['audio_duration']:.2f}s")
            print(f"      实时因子: {full_test['real_time_factor']:.2f}x")
            print(f"      文件大小: {full_test['file_size_kb']:.1f}KB")
            print(f"      输出文件: {full_test['output_file']}")

    print(f"\n\n📁 结果已保存: {results_file}")
    print(f"📁 音频文件目录: {output_dir}/")
    print("\n请播放以下音频文件对比效果:")
    print(f"   - {output_dir}/cosyvoice_chapter1.wav")
    print(f"   - {output_dir}/kokoro_chapter1.wav")


if __name__ == "__main__":
    main()
