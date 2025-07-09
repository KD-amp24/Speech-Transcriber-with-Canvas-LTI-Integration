from whisper_eval import transcribe_and_evaluate

result = transcribe_and_evaluate("C:\\Users\\Amponsah\\Desktop\\Summer_Research\\New_folder\\longrecord.mp3")
print(result["transcript"])
print(result["evaluation"])