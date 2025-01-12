import unittest

import numpy as np

from viravis.vaudio import _stringify_serial  # type: ignore[reportPrivateUsage]


class Test(unittest.TestCase):
    def test_prepare_data_np(self) -> None:
        arr = np.array([0, 1, 2, 3, 4, 10, 16])
        self.assertEqual(_stringify_serial(arr), "[0,1,2,3,4,A,10]")  # noqa: PT009


if __name__ == "__main__":
    unittest.main()
