import pytest
import sys
sys.path.append('..')
from worker import getDiff


def test_getDiff():
    data = getDiff('files/prev.txt', 'files/curr.txt')
    # print(data)
    assert len(data) == 6