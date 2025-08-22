"""
Simple microphone diagnostic tool
This will help identify the exact microphone issue
"""
import speech_recognition as sr
import sys


def test_basic_microphone():
    """Test basic microphone functionality"""
    print("🔍 Basic Microphone Test")
    print("-" * 30)

    try:
        # Test default microphone first
        print("Testing default microphone...")
        r = sr.Recognizer()

        # Try without specifying device index
        with sr.Microphone() as source:
            print("✅ Default microphone created successfully")
            r.adjust_for_ambient_noise(source, duration=0.5)
            print("✅ Default microphone ambient noise adjustment successful")
            return True

    except Exception as e:
        print(f"❌ Default microphone failed: {e}")
        return False


def test_specific_microphones():
    """Test specific microphone indices"""
    print("\n🔍 Specific Microphone Test")
    print("-" * 30)

    r = sr.Recognizer()
    mic_list = sr.Microphone.list_microphone_names()

    # Focus on likely microphone devices
    microphone_candidates = []

    for i, name in enumerate(mic_list):
        name_lower = name.lower()
        # Look for actual microphone devices
        if (('microphone' in name_lower or 'mic' in name_lower) and
                'speaker' not in name_lower and
                'output' not in name_lower and
                'mapper' not in name_lower):
            microphone_candidates.append((i, name))

    print(f"Found {len(microphone_candidates)} potential microphones:")
    for idx, name in microphone_candidates:
        print(f"  {idx}: {name}")

    # Test each candidate
    for mic_idx, mic_name in microphone_candidates:
        try:
            print(f"\nTesting microphone {mic_idx}: {mic_name}")

            # Create microphone object
            mic = sr.Microphone(device_index=mic_idx)
            print("  ✅ Microphone object created")

            # Test opening the microphone
            with mic as source:
                print("  ✅ Microphone opened successfully")

                # Test ambient noise adjustment
                print("  🔧 Adjusting for ambient noise...")
                r.adjust_for_ambient_noise(source, duration=0.5)
                print("  ✅ Ambient noise adjustment successful")

                print(f"  🎉 Microphone {mic_idx} is WORKING!")
                return mic_idx

        except Exception as e:
            print(f"  ❌ Microphone {mic_idx} failed: {type(e).__name__}: {e}")
            continue

    return None


def test_audio_recording():
    """Test actual audio recording"""
    working_mic = test_specific_microphones()

    if working_mic is None:
        print("\n❌ No working microphones found")
        return False

    print(f"\n🎤 Testing audio recording with microphone {working_mic}")
    print("-" * 50)

    try:
        r = sr.Recognizer()
        with sr.Microphone(device_index=working_mic) as source:
            print("🔴 Recording for 2 seconds... (speak now or stay quiet)")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=3, phrase_time_limit=2)

        print("✅ Audio recorded successfully")

        # Try to recognize the audio
        try:
            print("🧠 Attempting speech recognition...")
            text = r.recognize_google(audio)
            print(f"✅ Recognized: '{text}'")
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio (but recording worked)")
        except sr.RequestError as e:
            print(f"⚠️ Recognition service error: {e}")

        return True

    except Exception as e:
        print(f"❌ Audio recording failed: {e}")
        return False


def check_system_info():
    """Check system information"""
    print("💻 System Information")
    print("-" * 30)
    print(f"Python version: {sys.version}")

    try:
        import speech_recognition
        print(f"SpeechRecognition version: {speech_recognition.__version__}")
    except:
        print("SpeechRecognition version: Unknown")

    try:
        import pyaudio
        print("PyAudio: Available")
    except ImportError:
        print("PyAudio: NOT INSTALLED")
        print("💡 Install with: pip install pyaudio")


def main():
    print("🔧 JARVIS Microphone Diagnostic Tool")
    print("=" * 50)

    # Check system info
    check_system_info()

    print("\n" + "=" * 50)

    # Test basic functionality
    basic_works = test_basic_microphone()

    if not basic_works:
        print("\n❌ Basic microphone test failed")
        print("💡 Possible solutions:")
        print("   1. Install PyAudio: pip install pyaudio")
        print("   2. Check Windows microphone permissions")
        print("   3. Ensure microphone is not being used by other apps")
        return

    # Test specific microphones and recording
    recording_works = test_audio_recording()

    if recording_works:
        print("\n🎉 SUCCESS: Microphone system is working!")
        print("You should be able to run JARVIS now.")
    else:
        print("\n⚠️ Microphone detected but recording failed")
        print("Check your microphone permissions and hardware.")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()