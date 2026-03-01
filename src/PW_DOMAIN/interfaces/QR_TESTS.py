from QR import QR
from PW_UTILS.TESTS import TESTS
from PW_UTILS.LOG import LOG
   

class QR_TESTS(QR):
   
   
    @classmethod
    def Test__str__(cls):
        s = '🤝nlweb.org/QR,1,any-printer.com,7V8KD3G'
        q = QR(s)
        TESTS.AssertEqual(f'{q}', s)


    @classmethod
    def Test_parse(cls):
        q = QR('🤝nlweb.org/QR,1,any-printer.com,7V8KD3G')

        with TESTS.AssertValidation('Missing icon'):
            QR('nlweb.org/QR,1,any-printer.com,7V8KD3G')

        TESTS.AssertEqual(q.Obj(), {
            'QR': '🤝nlweb.org/QR,1,any-printer.com,7V8KD3G', 
            'Code': 'nlweb.org/QR', 
            'Version': '1', 
            'Domain': 'any-printer.com', 
            'Locator': '7V8KD3G'
        })
            

    @classmethod
    def TestIsHostCode(cls):

        q = QR('🤝nlweb.org/QR,1,any-printer.com,7V8KD3G')
        TESTS.AssertFalse(q.IsHostCode())

        q = QR('🤝nlweb.org/HOST,1,any-printer.com,7V8KD3G')
        TESTS.AssertTrue(q.IsHostCode())
    

    @classmethod
    def TestAllQR(cls):
        LOG.Print('QR_TESTS.TestAllQR() ==============================')

        cls.Test__str__()
        cls.Test_parse()
        cls.TestIsHostCode()
    