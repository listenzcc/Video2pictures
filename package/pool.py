# %%
class Pool(object):
    def __init__(self):
        self.buffer = []

    def length(self):
        return len(self.buffer)

    def append(self, value):
        self.buffer.append(value)

    def pop(self, idx=0):
        '''
        Keep idx=0, to make it FIFO
        '''
        if self.length() == 0:
            print('E: Cannot pop from the Empty buffer')
            return None

        return self.buffer.pop(idx)
