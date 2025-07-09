from faster_whisper import WhisperModel
import os

class WhisperTranscriber:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        print("Loading Whisper model...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("Model loaded.")

    def transcribe(self, audio_path):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        segments, _ = self.model.transcribe(audio_path)
        full_text = " ".join([segment.text.strip() for segment in segments])
        return full_text.strip(), segments


class SimpleEvaluator:
    def __init__(self, rubric_keywords=None):
        self.rubric_keywords = rubric_keywords or ["clarity", "organization", "relevance", "grammar"]

    def evaluate(self, transcript):
        score = 0
        feedback = []

        for keyword in self.rubric_keywords:
            if keyword.lower() in transcript.lower():
                score += 1
                feedback.append(f"✓ Mentioned: {keyword}")
            else:
                feedback.append(f"✗ Missing: {keyword}")

        return {
            "score": score,
            "total": len(self.rubric_keywords),
            "feedback": feedback
        }


def transcribe_and_evaluate(audio_path):
    """
    Combines transcription and evaluation into a single call.

    Returns:
        {
            "transcript": <str>,
            "evaluation": {
                "word_count": <int>,
                "contains_keyword": <bool>,
                "rubric_score": <int>,
                "rubric_feedback": <list of str>
            }
        }
    """
    transcriber = WhisperTranscriber()
    transcript, _ = transcriber.transcribe(audio_path)

    evaluator = SimpleEvaluator()
    rubric_result = evaluator.evaluate(transcript)

    result = {
        "transcript": transcript,
        "evaluation": {
            "word_count": len(transcript.split()),
            "contains_keyword": "important" in transcript.lower(),
            "rubric_score": rubric_result["score"],
            "rubric_feedback": rubric_result["feedback"]
        }
    }

    return result
