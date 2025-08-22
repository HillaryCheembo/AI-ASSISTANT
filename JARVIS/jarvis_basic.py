import speech_recognition as sr
import pyttsx3
import time
import threading
import json
from datetime import datetime


class ImprovedJARVIS:
    def __init__(self, user_name="Sir", microphone_index=None):
        print("🤖 Initializing JARVIS...")

        # Initialize speech components
        self.tts_engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()

        # Set up microphone with specific index if provided
        if microphone_index is not None:
            try:
                self.microphone = sr.Microphone(device_index=microphone_index)
                print(f"✅ Using microphone index: {microphone_index}")
            except Exception as e:
                print(f"⚠️ Could not use microphone {microphone_index}, using default: {e}")
                self.microphone = sr.Microphone()
        else:
            self.microphone = sr.Microphone()

        self.user_name = user_name
        self.is_listening = True

        # Configure voice
        self.setup_voice()

        # Test microphone on startup
        self.test_microphone()

        print("✅ JARVIS initialized successfully!")

    def setup_voice(self):
        """Configure TTS voice"""
        voices = self.tts_engine.getProperty('voices')

        # Try to find a good voice (prefer David or male voices)
        preferred_voices = ['david', 'male', 'zira']

        for preference in preferred_voices:
            for voice in voices:
                if preference in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    print(f"✅ Selected voice: {voice.name}")
                    break
            else:
                continue
            break

        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 160)
        self.tts_engine.setProperty('volume', 0.9)

    def test_microphone(self):
        """Test if microphone is working"""
        try:
            with self.microphone as source:
                print("🎤 Testing microphone... (adjusting for ambient noise)")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Microphone test successful")
        except Exception as e:
            print(f"⚠️ Microphone test failed: {e}")
            print("You may need to check your microphone settings")

    def speak(self, text, priority="normal"):
        """Make JARVIS speak"""
        print(f"🗣️ JARVIS: {text}")

        # Add JARVIS formality
        if not text.startswith(self.user_name) and len(text) > 10:
            if priority == "urgent":
                text = f"{self.user_name}, urgent: {text}"
            elif "?" not in text and not text.endswith("."):
                text = f"{text}, {self.user_name}."

        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ TTS Error: {e}")

    def listen(self, timeout=5, phrase_limit=10):
        """Listen for user command with better error handling"""
        try:
            print("🎤 Listening...")

            with self.microphone as source:
                # Adjust for ambient noise quickly
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)

                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)

            # Try Google recognition first
            try:
                command = self.recognizer.recognize_google(audio)
                print(f"👤 You said: {command}")
                return command.lower()

            except sr.UnknownValueError:
                print("🤔 Could not understand audio")
                return None

            except sr.RequestError as e:
                print(f"⚠️ Google Speech Recognition error: {e}")
                # Could add offline recognition here if needed
                return None

        except sr.WaitTimeoutError:
            return "timeout"
        except Exception as e:
            print(f"❌ Listening error: {e}")
            return None

    def process_command(self, command):
        """Process user commands with JARVIS responses"""
        if not command or command == "timeout":
            return

        original_command = command

        # Wake word detection - more flexible
        wake_words = ["jarvis", "j.a.r.v.i.s", "hey jarvis", "ok jarvis"]
        has_wake_word = any(wake in command for wake in wake_words)

        if not has_wake_word:
            return

        # Remove wake words and clean command
        for wake in wake_words:
            command = command.replace(wake, "").strip()

        # Remove common prefixes
        prefixes = ["hey", "ok", "okay", "please", "can you", "could you"]
        for prefix in prefixes:
            if command.startswith(prefix):
                command = command[len(prefix):].strip()

        if not command:
            self.speak("Yes, how may I assist you today?")
            return

        print(f"🧠 Processing: '{command}'")

        # Enhanced command processing
        if any(word in command for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            time_of_day = self.get_time_of_day()
            responses = [
                f"Good {time_of_day}, {self.user_name}. How may I be of service?",
                f"Hello {self.user_name}. I am at your service.",
                f"Good {time_of_day}. What can I help you with today?"
            ]
            self.speak(responses[hash(command) % len(responses)])

        elif any(word in command for word in ["time", "what time"]):
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")

        elif any(word in command for word in ["date", "what date", "today"]):
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            self.speak(f"Today is {current_date}")

        elif any(word in command for word in ["how are you", "how do you feel", "status"]):
            responses = [
                "All systems are operating within normal parameters, thank you for asking",
                "I am functioning optimally and ready to assist",
                "All systems green. How may I help you today?"
            ]
            self.speak(responses[hash(command) % len(responses)])

        elif "weather" in command:
            self.speak(
                "I would need internet access to check the weather for you. Shall I help you with something else?")

        elif any(word in command for word in ["thank you", "thanks", "appreciate"]):
            responses = [
                f"You're most welcome, {self.user_name}. It's my pleasure to assist",
                "Happy to help anytime",
                f"My pleasure, {self.user_name}"
            ]
            self.speak(responses[hash(command) % len(responses)])

        elif any(word in command for word in ["goodbye", "exit", "quit", "shutdown", "stop"]):
            self.speak(f"Goodbye, {self.user_name}. It has been my pleasure serving you today.")
            return "exit"

        elif "test" in command:
            self.speak("Voice test successful. All systems operational and ready for service.")

        elif any(word in command for word in ["help", "what can you do", "commands"]):
            help_text = """I can help you with basic tasks. Try saying:
            JARVIS, what time is it?
            JARVIS, what's today's date?
            JARVIS, hello
            JARVIS, how are you?
            JARVIS, goodbye"""
            self.speak(
                "I can help with time, date, greetings, and basic conversation. Say JARVIS followed by your request.")

        else:
            # More intelligent unknown command handling
            if len(command.split()) <= 2:
                self.speak("I didn't quite understand that. Could you please rephrase?")
            else:
                self.speak(
                    f"I heard you say: {command}. I'm still learning new capabilities. How else may I assist you?")

    def get_time_of_day(self):
        """Get appropriate greeting based on time"""
        hour = datetime.now().hour
        if hour < 12:
            return "morning"
        elif hour < 17:
            return "afternoon"
        else:
            return "evening"

    def run(self):
        """Main JARVIS loop with better error handling"""
        print("\n🚀 JARVIS is now online!")
        print("💡 Say 'JARVIS' followed by your command")
        print("💡 Try commands like:")
        print("   - 'JARVIS, hello'")
        print("   - 'JARVIS, what time is it?'")
        print("   - 'JARVIS, help'")
        print("💡 Say 'JARVIS, goodbye' to exit")
        print("-" * 60)

        time_of_day = self.get_time_of_day()
        self.speak(f"Good {time_of_day}, {self.user_name}. JARVIS is now online and ready for service.")

        consecutive_errors = 0
        max_errors = 5

        while True:
            try:
                # Listen for commands with shorter timeout for responsiveness
                command = self.listen(timeout=3, phrase_limit=8)

                if command:
                    consecutive_errors = 0  # Reset error counter on successful command
                    result = self.process_command(command)
                    if result == "exit":
                        break
                elif command == "timeout":
                    # Don't count timeouts as errors
                    pass
                else:
                    consecutive_errors += 1

                # If too many consecutive errors, offer help
                if consecutive_errors >= max_errors:
                    self.speak(
                        "I'm having trouble hearing you clearly. Please check your microphone or try speaking louder.")
                    consecutive_errors = 0

            except KeyboardInterrupt:
                print("\n🛑 Keyboard interrupt detected")
                self.speak(f"Shutting down. Goodbye, {self.user_name}.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                consecutive_errors += 1
                if consecutive_errors < 3:
                    self.speak("I encountered a minor issue but I'm still operational.")
                time.sleep(1)  # Brief pause after error


def main():
    """Main function to start JARVIS"""
    print("🎉 Welcome to JARVIS - Improved Version!")
    print("🔧 Enhanced with better microphone handling")

    # Try to read configuration if available
    microphone_index = None
    try:
        with open('jarvis_config.txt', 'r') as f:
            content = f.read()
            # Extract microphone index from config
            if 'WORKING_MICROPHONE_INDEX' in content:
                line = [l for l in content.split('\n') if 'WORKING_MICROPHONE_INDEX' in l][0]
                microphone_index = int(line.split('=')[1].strip())
                print(f"📄 Loaded microphone index {microphone_index} from config")
    except:
        print("ℹ️ No config found, using default microphone")

    # You can change the user name here
    user_name = "Sir"  # Change this to your preferred name

    try:
        jarvis = ImprovedJARVIS(user_name=user_name, microphone_index=microphone_index)
        jarvis.run()
    except Exception as e:
        print(f"❌ Failed to start JARVIS: {e}")
        print("💡 Try running the test script first to check your setup")


if __name__ == "__main__":
    main()