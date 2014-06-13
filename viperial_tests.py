import unittest
import datetime

from viperial import input_period

class TimePeriodTest(unittest.TestCase):
    @unittest.skip("no longer using own date class")
    def test_before_period(self):
        self.assertTrue(before_period(('2014', 'May', '11'),
                                       ('2015', 'May', '11')))
        self.assertTrue(before_period(('2014', 'May', '11'),
                                       ('2014', 'Dec', '11')))
        self.assertTrue(before_period(('2014', 'May', '11'),
                                       ('2014', 'May', '14')))
        self.assertFalse(before_period((('2015', 'May', '15'))))
        
        self.assertFalse(before_period(('2014', 'May', '11'),
                                       ('2014', 'May', '11')))
        self.assertFalse(before_period(('2014', 'May', '11'),
                                       ('2013', 'May', '11')))
        self.assertFalse(before_period(('2014', 'May', '11'),
                                       ('2014', 'Jan', '11')))
        self.assertFalse(before_period(('2014', 'May', '11'),
                                       ('2014', 'May', '04')))
        self.assertFalse(after_period((('2015', 'May', '11'))))
        

    @unittest.skip("no longer using own date class")
    def test_after_period(self):
        self.assertTrue(before_period(('2014', 'May', '11'),
                                       ('2015', 'May', '11')))
        self.assertTrue(before_period(('2014', 'May', '11'),
                                       ('2014', 'Oct', '11')))
        self.assertTrue(before_period(('2014', 'May', '11'),
                                       ('2014', 'May', '21')))
        self.assertFalse(after_period(('2014', 'May', '11'),
                                      ('2015', 'May', '11')))
        self.assertFalse(after_period(('2014', 'May', '11'),
                                      ('2014', 'Jun', '11')))
        self.assertFalse(after_period(('2014', 'May', '11'),
                                      ('2014', 'May', '15')))        
        
    @unittest.skip("no longer using own date class")
    def test_parse_date_correct(self):
        self.assertEqual(parse_date('May 10, 2014'), ('2014', 'May', '10'))

    @unittest.skip("implementation changed, otherwise was OK")
    def test_input_period(self):
        self.assertEqual(input_period("11 11 2014 12 11 2014"),
                         (datetime.datetime(2014,11,11),
                          datetime.datetime(2014,11,12)))

    

if __name__ == '__main__':
    unittest.main()
