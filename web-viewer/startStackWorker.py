from browser import self as worker
import sys
import stackWorker

worker.stackWorker = stackWorker.StackWorker()
sys.stdout = worker.stackWorker
sys.stderr = worker.stackWorker
