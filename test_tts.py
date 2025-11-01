import time
from voice import speak

print('test_tts: start')
for i in range(1,6):
    msg = f'This is test call {i}'
    print('enqueue:', msg)
    speak(msg, True)
    time.sleep(0.7)
print('test_tts: done - waiting for queue to finish')
# wait a bit for the worker to process queued items
time.sleep(6)
print('test_tts: exit')
