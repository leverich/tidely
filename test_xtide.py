#!/usr/bin/env python

import time
import unittest
import xtide

def make_levels(levels):
    ret = []
    for l in levels:
        ret.append([len(ret), l])
    return ret

class TestXTideInterface(unittest.TestCase):
    def test_run_xtide_basic(self):
        ret = xtide.run_xtide("San Francisco Bay Entrance", 1000000000)

        self.assertTrue(len(ret) > 10)
        self.assertEqual(len(ret[5]), 2)

    def test_run_xtide_start_stop(self): 
        ret = xtide.run_xtide("San Francisco Bay Entrance", 1000000000, 1000000600)
        self.assertEqual(len(ret), 10)

    def test_run_xtide_bad_station(self):
        with self.assertRaises(Exception):
            xtide.run_xtide("ASDFGHJKL", 1000000000)

    def test_run_xtide_bad_tcd_file(self):
        with self.assertRaises(Exception):
            xtide.run_xtide("ASDFGHJKL", 1000000000, tcd_file = "asdfqwer")

    def test_run_xtide_bad_start_time(self):
        with self.assertRaises(Exception):
            xtide.run_xtide("ASDFQWER", "foo")

    def test_span_basic(self):
        # ret = xtide.run_xtide("San Francisco Bay Entrance", 900000000, 900000000+12*60*60)
        ret = make_levels([2, 1, 0, -1, -2, -1, 0, 1, 2])
        spans = xtide.target_spans(ret)

        self.assertEqual(len(spans), 3)
        self.assertEqual(spans[0]['state'], 1)
        self.assertEqual(spans[1]['state'], 0)
        self.assertEqual(spans[2]['state'], 1)

        spans = xtide.target_spans(ret, 100000)
        self.assertEqual(len(spans), 1)

    def test_span_target(self):
        ret = make_levels([5, 4, 3, 2, 1, 0, -1, -2, -1, 0, 1, 2])
        spans = xtide.target_spans(ret, 0)
        self.assertEqual(len(spans), 3)

        spans = xtide.target_spans(ret, 4)
        self.assertEqual(len(spans), 2)

    def test_span_bad_pair(self):
        with self.assertRaises(Exception):
            # Wrong start time
            xtide.target_spans(
                make_levels([5, 4, 3, 2, 1]),
                levels2 = [(x+1, y) for (x,y) in make_levels([5, 4, 3, 2, 1])]
            )
            # xtide.run_xtide("Oyster Point Marina", 900000000),
            # levels2 = xtide.run_xtide("Oyster Point Marina", 900000000+1200)

        with self.assertRaises(Exception):
            # Different lengths
            xtide.target_spans(
                make_levels([5, 4, 3, 2, 1]),
                levels2 = make_levels([6, 5, 4, 3, 2, 1])
            )
            # xtide.run_xtide("Oyster Point Marina", 900000000, 900000120),
            # levels2 = xtide.run_xtide("Oyster Point Marina", 900000000, 900003000)

    def test_span_pair(self):
        # ret1 = xtide.run_xtide("Oyster Point Marina", 900000000, 900000000+12*60*60)
        # ret2 = xtide.run_xtide("San Francisco Bay Entrance", 900000000, 900000000+12*60*60)
        ret1 = make_levels([10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        ret2 = make_levels([2, 1, 0, -1, -2, -1, 0, 1, 2, 3])

        spans = xtide.target_spans(ret1, levels2 = ret2)

        self.assertEqual(len(spans), 3)
        self.assertEqual(spans[0]['state'], 3)
        self.assertEqual(spans[1]['state'], 1)
        self.assertEqual(spans[2]['state'], 3)

    def test_span_pair2(self):
        ret1 = make_levels([ 3,  2,  1,  0, -1, -2, -3, -2, -1,  0,  1,  2,  3])
        ret2 = make_levels([ 5,  4,  3,  2,  1,  0, -1, -2, -3, -2, -1,  0,  1])
        #                    3   3   3   3   2   2   0   0   0   1   1   3   3

        spans = xtide.target_spans(ret1, levels2 = ret2)
        self.assertEqual(len(spans), 5)
        self.assertEqual(spans[0]['state'], 3)
        self.assertEqual(spans[1]['state'], 2)
        self.assertEqual(spans[2]['state'], 0)
        self.assertEqual(spans[3]['state'], 1)
        self.assertEqual(spans[4]['state'], 3)

        # ret1 = xtide.run_xtide("Oyster Point Marina", 900000000, 900000000+12*60*60)
        # ret2 = xtide.run_xtide("San Francisco Bay Entrance", 900000000, 900000000+12*60*60)
        # spans = xtide.target_spans(ret1, 3.0, levels2 = ret2)
        #
        # self.assertEqual(len(spans), 6)
        # self.assertEqual(spans[0]['state'], 2)
        # self.assertEqual(spans[1]['state'], 3)
        # self.assertEqual(spans[2]['state'], 1)
        # self.assertEqual(spans[3]['state'], 0)
        # self.assertEqual(spans[4]['state'], 1)
        # self.assertEqual(spans[5]['state'], 3)

    def test_span_now(self):
        now_time = time.time()
        ret = xtide.run_xtide("San Francisco Bay Entrance",
                              start_time = now_time - 120,
                              stop_time = now_time + 24*60*60)
        spans = xtide.target_spans(ret, now = True)

        # 'now' appears exactly once
        filtered = filter(lambda x: 'now' in x, spans)
        self.assertEqual(len(filtered), 1)

    def test_span_maxima(self):
        ret = make_levels([1, 2, 3, 4, 3, 2, 1, 0, -1, -2, -3, -4, -3, -2, -1])
        spans = xtide.target_spans(ret, maxima = True)
        self.assertEqual(spans[0]['maximum'][0], 4)
        self.assertEqual(spans[1]['maximum'][0], -4)

        # ret = xtide.run_xtide("San Francisco Bay Entrance", 1000000000)
        # spans = xtide.target_spans(ret, maxima = True)
        #
        # filtered = filter(lambda x: 'maximum' in x, spans)
        # self.assertTrue(len(filtered) > 0)

if __name__ == '__main__':
    unittest.main()
