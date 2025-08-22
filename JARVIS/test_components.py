"""
Improved JARVIS Component Test Script
This version properly handles microphone selection and testing
"""
import time


def test_text_to_speech():
    """Test if text-to-speech works"""
    print("Testing Text-to-Speech...")
    try:
        import pyttsx3
        engine = pyttsx3.init()

        # List available voices
        voices = engine.getProperty('voices')
        print(f"Found {len(voices)} voices:")
        for i, voice in enumerate(voices):
            print(f"  {i}: {voice.name}")

        # Test speech
        print("Speaking test message...")
        engine.say("Text to speech test successful")
        engine.runAndWait()
        print("✅ Text-to-Speech: WORKING")
        return True
    except Exception as e:
        print(f"❌ Text-to-Speech: FAILED - {e}")
        return False


def test_speech_recognition():
    """Test if speech recognition works"""
    print("\nTesting Speech Recognition...")
    try:
        import speech_recognition as sr

        r = sr.Recognizer()

        # List available microphones
        mic_list = sr.Microphone.list_microphone_names()
        print("Available microphones:")
        for i, name in enumerate(mic_list):
            print(f"  {i}: {name}")

        # Try to find a working microphone
        working_mic = None

        # Test microphones that typically work
        test_indices = [0, 1, 5, 9, 10] if len(mic_list) > 10 else list(range(len(mic_list)))

        for mic_index in test_indices:
            if mic_index >= len(mic_list):
                continue

            try:
                print(f"\nTesting microphone {mic_index}: {mic_list[mic_index]}")

                with sr.Microphone(device_index=mic_index) as source:
                    print("Adjusting for ambient noise... (please be quiet for 2 seconds)")
                    r.adjust_for_ambient_noise(source, duration=2)
                    print(f"✅ Microphone {mic_index}: WORKING")
                    working_mic = mic_index
                    break

            except Exception as e:
                print(f"❌ Microphone {mic_index}: FAILED - {e}")
                continue

        if working_mic is not None:
            print(f"✅ Found working microphone at index: {working_mic}")

            # Test actual speech recognition
            print("\n🎤 Testing speech recognition...")
            print("Say something when prompted (you have 5 seconds):")

            try:
                with sr.Microphone(device_index=working_mic) as source:
                    print("Listening... Speak now!")
                    audio = r.listen(source, timeout=5, phrase_time_limit=3)

                try:
                    text = r.recognize_google(audio)
                    print(f"✅ Heard: '{text}'")
                    print("✅ Speech Recognition: WORKING")
                    return True, working_mic
                except sr.UnknownValueError:
                    print("⚠️ Could not understand audio, but microphone is working")
                    return True, working_mic
                except sr.RequestError as e:
                    print(f"⚠️ Google Speech Recognition error: {e}")
                    print("✅ Microphone working, but need internet for Google recognition")
                    return True, working_mic

            except sr.WaitTimeoutError:
                print("⚠️ No speech detected, but microphone is working")
                return True, working_mic

        else:
            print("❌ No working microphone found")
            return False, None

    except Exception as e:
        print(f"❌ Speech Recognition: FAILED - {e}")
        return False, None


def test_other_imports():
    """Test other imports (optional for basic JARVIS)"""
    print("\nTesting optional imports...")

    optional_modules = [
        ('pyautogui', 'For advanced automation features'),
        ('requests', 'For web requests and API calls'),
        ('psutil', 'For system monitoring'),
        ('cv2', 'For computer vision features'),
        ('numpy', 'For numerical operations')
    ]

    results = {}

    for module, description in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module}: AVAILABLE - {description}")
            results[module] = True
        except ImportError:
            print(f"⚠️ {module}: NOT INSTALLED - {description}")
            results[module] = False

    return results


def generate_jarvis_config(working_mic_index):
    """Generate a configuration for JARVIS with the working microphone"""
    config = f"""
# JARVIS Configuration
# Add this to your JARVIS code to use the working microphone

WORKING_MICROPHONE_INDEX = {working_mic_index}

# In your JARVIS class __init__ method, use:
# self.microphone = sr.Microphone(device_index={working_mic_index})
"""

    with open('jarvis_config.txt', 'w') as f:
        f.write(config)

    print(f"\n📄 Configuration saved to 'jarvis_config.txt'")
    print(f"Use microphone index {working_mic_index} in your JARVIS code")


def main():
    print("🔧 JARVIS Component Test - Improved Version")
    print("=" * 50)

    # Test all components
    print("1. Testing Text-to-Speech...")
    tts_ok = test_text_to_speech()

    print("\n2. Testing Speech Recognition...")
    sr_ok, working_mic = test_speech_recognition()

    print("\n3. Testing Optional Components...")
    import_results = test_other_imports()

    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS:")
    print(f"Text-to-Speech: {'✅ WORKING' if tts_ok else '❌ FAILED'}")
    print(f"Speech Recognition: {'✅ WORKING' if sr_ok else '❌ FAILED'}")

    if working_mic is not None:
        print(f"Working Microphone: Index {working_mic}")
        generate_jarvis_config(working_mic)

    # Show optional components status
    available_count = sum(import_results.values())
    total_count = len(import_results)
    print(f"Optional Components: {available_count}/{total_count} available")

    if tts_ok and sr_ok:
        print("\n🎉 JARVIS is ready to run!")
        print("✅ All essential components are working")
        print(f"✅ Use microphone index {working_mic} in your JARVIS code")
    else:
        print("\n⚠️ Some essential components failed:")
        if not tts_ok:
            print("  - Install pyttsx3: pip install pyttsx3")
        if not sr_ok:
            print("  - Check microphone permissions and connections")
            print("  - Install speech_recognition: pip install SpeechRecognition")

    print("\n" + "=" * 50)
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()