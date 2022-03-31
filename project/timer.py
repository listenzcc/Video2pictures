# %%
import time
import pandas as pd

from pathlib import Path

# %%


class Timer(object):
    def __init__(self):
        self.lst = []
        self.RESET()

    def reset(self):
        self.t0 = time.time()
        print('D: Reset the latest time point.')

    def clear(self):
        num = len(self.lst)
        self.lst = []
        print('D: Cleared the {} records.'.format(num))

    def RESET(self):
        self.clear()
        self.reset()
        self.T0 = self.t0
        print('D: Reset the timer.')

    def check(self, target=None):
        '''
        When target is None, tell the current time since the latest time reset;
        When target is given, tell whether the current time is less than the target.
        '''
        if target is None:
            return time.time() - self.t0
        return (time.time() - self.t0) < target

    def append(self, contents=[]):
        '''
        Append the record
        '''
        record = [time.time() - self.T0] + contents
        self.lst.append(record)
        return len(self.lst)

    def save(self,
             contents_name=[],
             folder='.',
             filename=None,
             ):
        '''
        Save the records
        '''
        if filename is None:
            filename = '{}.csv'.format(time.ctime().replace(':', '-'))

        columns = ['time'] + contents_name
        csv = Path(folder, filename)
        self.table = pd.DataFrame(self.lst, columns=columns)
        self.table.to_csv(csv)
        print('D: Saved to {}'.format(csv))
        return csv
