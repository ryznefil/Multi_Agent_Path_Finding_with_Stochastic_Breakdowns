from heapq import heappush, heappop


class PriorityNonDuplicateHeap:
    """Priority non duplicate heap used for conlict detection in the conflict based planning"""

    def __init__(self):
        self.queue = []
        self.content_set = set()

    def push(self, object):
        if object not in self.content_set:
            self.content_set.add(object)
            heappush(self.queue, object)
            return True
        return False

    def pop(self):
        if self.queue:
            popped = heappop(self.queue)
            self.content_set.remove(popped)
            return popped
        else:
            return None

    def remove(self):
        pass
