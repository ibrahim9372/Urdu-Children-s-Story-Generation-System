from generator import generate_story

try:
    prefix = "ایک دفعہ کا"
    print(f"Testing generation with prefix: {prefix}")
    story, seeds = generate_story(prefix, max_length=10)
    print("Success!")
    print(f"Seeds: {seeds}")
    print(f"Story: {story}")
except Exception as e:
    import traceback
    print("Failed!")
    traceback.print_exc()
