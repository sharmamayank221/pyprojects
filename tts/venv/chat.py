import torchaudio as ta
import torch
from chatterbox.tts import ChatterboxTTS

# Force all model loading to go to CPU or MPS
torch_load = torch.load
def safe_load(path, *args, **kwargs):
    return torch_load(path, map_location=torch.device("mps"))

torch.load = safe_load

model = ChatterboxTTS.from_pretrained(device="mps")

text = """Announced simultaneously for iOS, iPadOS, macOS, watchOS, tvOS, visionOS, and CarPlay, Liquid Glass forms a new universal design language for the first time. At its WWDC 2025 keynote address, Apple's software chief Craig Federighi said "Apple Silicon has become dramatically more powerful enabling software, materials and experiences we once could only dream of."

Inspired by visionOS, Liquid Glass is layered throughout the system and features rounded corners have been matched to the curved screens of the devices. It behaves just like glass in the real world and morphs when you need more options or move between views."""
#wav = model.generate(text)
#ta.save("test-1.wav", wav, model.sr)

# If you want to synthesize with a different voice, specify the audio prompt
AUDIO_PROMPT_PATH="/Users/mayanksharma/Downloads/myttsvoice.wav"
wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
ta.save("IOS26.wav", wav, model.sr)
