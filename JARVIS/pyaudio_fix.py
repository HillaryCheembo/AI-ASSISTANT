"""
PyAudio Fix and Test Script
This addresses the common PyAudio 'NoneType' error on Windows
"""
import speech_recognition as sr
import pyaudio
import sys


def test_pyaudio_directly():
    """Test PyAudio directly to diagnose the issue"""
    print("🔍 Testing PyAudio Directly")
    print("-" * 30)

    try:
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        print("✅ PyAudio initialized successfully")

        # Get device count
        device_count = p.get_device_count()
        print(f"✅ Found {device_count} audio devices")

        # List input devices
        input_devices = []
        for i in range(device_count):
            try:
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    input_devices.append((i, info['name'], info['maxInputChannels']))
                    print(f"  Input Device {i}: {info['name']} (channels: {info['maxInputChannels']})")
            except:
                pass

        # Test opening an input stream
        if input_devices:
            device_id, device_name, channels = input_devices[0]
            print(f"\n🎤 Testing input stream with: {device_name}")

            try:
                # Try to open a stream
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    input_device_index=device_id,
                    frames_per_buffer=1024
                )
                print("✅ Audio stream opened successfully")

                # Test reading data
                data = stream.read(1024, exception_on_overflow=False)
                print("✅ Audio data read successfully")

                stream.stop_stream()
                stream.close()
                print("✅ Audio stream closed successfully")

                p.terminate()
                return True, device_id

            except Exception as e:
                print(f"❌ Stream test failed: {e}")
                p.terminate()
                return False, None
        else:
            print("❌ No input devices found")
            p.terminate()
            return False, None

    except Exception as e:
        print(f"❌ PyAudio initialization failed: {e}")
        return False, None


def test_speech_recognition_with_fix(device_id=None):
    """Test speech recognition with specific fixes"""
    print(f"\n🔍 Testing Speech Recognition with Device {device_id}")
    print("-" * 50)

    try:
        r = sr.Recognizer()

        # Configure recognizer for better performance
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.8
        r.operation_timeout = None
        r.phrase_threshold = 0.3
        r.non_speaking_duration = 0.5

        # Create microphone with specific device
        if device_id is not None:
            mic = sr.Microphone(device_index=device_id)
        else:
            mic = sr.Microphone()

        print("✅ Microphone object created")

        # Test opening microphone with error handling
        try:
            with mic as source:
                print("✅ Microphone opened successfully")

                # Shorter ambient noise adjustment
                print("🔧 Quick ambient noise adjustment...")
                r.adjust_for_ambient_noise(source, duration=0.2)
                print("✅ Ambient noise adjusted")

                # Quick listen test
                print("🎤 Quick 1-second listen test...")
                try:
                    audio = r.listen(source, timeout=1, phrase_time_limit=1)
                    print("✅ Audio captured successfully")
                    return True
                except sr.WaitTimeoutError:
                    print("✅ Timeout (this is good - microphone is working)")
                    return True

        except Exception as e:
            print(f"❌ Microphone access failed: {e}")
            return False

    except Exception as e:
        print(f"❌ Speech recognition setup failed: {e}")
        return False


def test_alternative_approach():
    """Test alternative speech recognition approach"""
    print("\n🔍 Alternative Approach Test")
    print("-" * 30)

    try:
        import speech_recognition as sr

        # Try different initialization approach
        r = sr.Recognizer()

        # Get microphone list
        mics = sr.Microphone.list_microphone_names()

        # Try microphones that look like actual input devices
        potential_devices = []
        for i, name in enumerate(mics):
            name_lower = name.lower()
            if 'microphone' in name_lower and 'usb' in name_lower:
                potential_devices.append(i)

        if not potential_devices:
            for i, name in enumerate(mics):
                name_lower = name.lower()
                if 'microphone' in name_lower and 'realtek' in name_lower:
                    potential_devices.append(i)

        print(f"Testing {len(potential_devices)} potential devices...")

        for device_id in potential_devices[:3]:  # Test max 3 devices
            try:
                print(f"\nTrying device {device_id}: {mics[device_id]}")

                # Create microphone with explicit parameters
                mic = sr.Microphone(
                    device_index=device_id,
                    sample_rate=16000,
                    chunk_size=1024
                )

                # Test with minimal operations
                with mic as source:
                    # Very quick test
                    r.adjust_for_ambient_noise(source, duration=0.1)

                print(f"✅ Device {device_id} working!")
                return True, device_id

            except Exception as e:
                print(f"❌ Device {device_id} failed: {e}")
                continue

        return False, None

    except Exception as e:
        print(f"❌ Alternative approach failed: {e}")
        return False, None


def main():
    print("🔧 PyAudio Fix and Diagnostic Tool")
    print("=" * 50)

    # Test PyAudio directly first
    pyaudio_works, device_id = test_pyaudio_directly()

    if not pyaudio_works:
        print("\n❌ PyAudio is not working properly")
        print("💡 Try these solutions:")
        print("   1. Reinstall PyAudio: pip uninstall pyaudio && pip install pyaudio")
        print("   2. Try: pip install --upgrade pyaudio")
        print("   3. Check if another app is using the microphone")
        print("   4. Restart your computer")
        return

    print(f"\n✅ PyAudio is working! Device ID: {device_id}")

    # Test speech recognition
    sr_works = test_speech_recognition_with_fix(device_id)

    if not sr_works:
        print("\nTrying alternative approach...")
        alt_works, alt_device = test_alternative_approach()

        if alt_works:
            print(f"\n🎉 SUCCESS with alternative method! Use device {alt_device}")

            # Save working configuration
            config = f"""# Working JARVIS Configuration
WORKING_MICROPHONE_INDEX = {alt_device}
ALTERNATIVE_METHOD = True
"""
            with open('jarvis_working_config.txt', 'w') as f:
                f.write(config)
            print("📄 Saved working config to 'jarvis_working_config.txt'")

        else:
            print("\n❌ All methods failed")
            print("💡 This might be a Windows permissions issue")
            print("   Try running as administrator or check antivirus settings")
    else:
        print(f"\n🎉 SUCCESS! Use device {device_id}")

        # Save working configuration
        config = f"""# Working JARVIS Configuration
WORKING_MICROPHONE_INDEX = {device_id}
ALTERNATIVE_METHOD = False
"""
        with open('jarvis_working_config.txt', 'w') as f:
            f.write(config)
        print("📄 Saved working config to 'jarvis_working_config.txt'")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()