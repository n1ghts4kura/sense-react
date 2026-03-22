# extractor_and_executor.py
# Test the Extractor and Executor at the same time.
# 
# @author n1ghts4kura
# @date 2026-03-21
#

from src.react.executor import build_executor, build_extractor

extractor = build_extractor()
executor = build_executor('red')

resp = extractor(goals="四处逛逛然后开两枪")

print(resp)

resp = executor(tasks=resp.tasks)

print(resp)
