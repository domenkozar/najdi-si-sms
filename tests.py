import unittest

import najdisi_sms


class ValidateAttrsTest (unittest.TestCase):

    def setUp(self):
        self.obj = lambda x: x

        self.exception_dict = {
            "attr": najdisi_sms.NoMsgError
        }

    def test_validation_fail(self):
        self.assertRaises(
            najdisi_sms.NoMsgError,
            najdisi_sms.validate_attrs,
            self.obj, self.exception_dict
        )

    def test_validation_success(self):
        self.obj.attr = "Niii!"
        self.assertIs(
            najdisi_sms.validate_attrs(self.obj, self.exception_dict),
            None
        )

if __name__ == '__main__':
    unittest.main()
