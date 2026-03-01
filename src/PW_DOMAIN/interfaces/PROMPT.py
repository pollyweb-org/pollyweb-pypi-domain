from __future__ import annotations
from typing import Union
from PW import PW

from PW_UTILS.LOG import LOG
from PW_UTILS.STRUCT import STRUCT
from PROMPT_OPTION import PROMPT_OPTION
from PW_UTILS.UTILS import UTILS
from PW_UTILS.LOG import LOG


class PROMPT(STRUCT):
    '''💬 https://quip.com/CDrjAxNKwLpI/-Prompt
    {
        "PromptID": "<uuid>",
        "Format": "ONE",
        "Message": "Which credit card to use?", 
        "Options": [
            {
                "ID": "1",
                "Translation": "Personal"
            },
            {
                "ID": "2",
                "Translation": "Business"
            }
        ],
        "Appendix": "308826e3-a3a2-471e-84fd-c673c2e42e38"
    }
    '''

    @classmethod
    def SESSION(cls):
        from PROMPT_SESSION import PROMPT_SESSION
        return PROMPT_SESSION()
    

    @classmethod
    def REPLY(cls):
        from PROMPT_REPLY import PROMPT_REPLY
        return PROMPT_REPLY()
    

    @classmethod
    def REQUEST(cls, event:any=None):
        from PROMPT_REQUEST import PROMPT_REQUEST
        return PROMPT_REQUEST(event)


    @classmethod
    def OPTION(cls):
        from PROMPT_OPTION import PROMPT_OPTION
        return PROMPT_OPTION()



    @staticmethod
    def New(
        format:str, 
        message:str, 
        default:str= None,
        options:Union[str,list[str],any]= None, 
        appendix:str= None,
        locator:str= None
    ) -> PROMPT:
        '''
        Creates a new PROMPT.
        * format: e.g. INFO.
        * message: what appears to the user.
        * default: default answer.
        * options: if any, for the user to select.
        * appendix: a file or order.
        * locator: use for ephemerals - https://quip.com/Pcn4AGX8sHri
        '''

        LOG.Print(
            f'💬 PROMPT.New()',
            f'{format=}', f'{message=}', f'{options=}', 
            f'{default=}', f'{appendix=}', f'{locator=}')

        UTILS.RequireArgs([format, message])
        UTILS.AssertIsUUID(appendix)

        item = {
            "PromptID": UTILS.UUID(),
            "Format": format,
            "Message": message
        }

        if appendix != None: item["Appendix"] = appendix
        if locator != None: item["Locator"] = locator
        if default != None: item['Default'] = str(default)

        # Parse options.
        options = PROMPT_OPTION.ParseOptions(options)
        if options != None: item["Options"] = options
        
        ##LOG.Print(f'PROMPT.New(): item={item})')

        prompt = PROMPT(item)
        ##LOG.Print(f'PROMPT.New(): prompt={prompt})')

        prompt.VerifyPrompt()

        return prompt
    
    
    def RequireFormat(self) -> str:
        '''👉 https://quip.com/CDrjAxNKwLpI/-Prompt#temp:C:KSc184ca019e23d408393b0b591a'''
        return self.RequireStr('Format')
    
    def RequirePromptID(self, set:str=None) -> str:
        return self.RequireUUID('PromptID', set=set)

    def RequireMessage(self) -> str:
        '''👉 https://quip.com/CDrjAxNKwLpI/-Prompt#temp:C:KSc9760bdaee3a949b9acd38d6e4'''
        return self.RequireStr('Message')
    
    def GetDefault(self) -> str:
        return self.GetStr('Default')

    def GetAppendix(self):
        '''👉 https://quip.com/CDrjAxNKwLpI/-Prompt#temp:C:KSc3e3436c471a4426785f520b92'''
        return self.UUID('Appendix') 
    

    def RequireAppendix(self):
        '''👉 https://quip.com/CDrjAxNKwLpI/-Prompt#temp:C:KSc3e3436c471a4426785f520b92'''
        return self.RequireUUID('Appendix')
    

    def RequireLocator(self) -> str:
        '''👉 For Ephemeral 
        * https://quip.com/Pcn4AGX8sHri'''
        return self.RequireStr('Locator')
    

    def GetLocator(self) -> str:
        '''👉 For Ephemeral 
        * https://quip.com/Pcn4AGX8sHri'''
        return self.GetStr('Locator')

    
    def RequireWalletOptions(self):
        options = self.GetList('Options', mustExits=True)
        for item in options:
            UTILS.AssertIsType(item,str)
        return options 


    def RequireOptions(self) -> any:
        '''👉 Returns the inner options whithout any structs.'''
        return self.RequireAtt('Options')


    def RequireOptionList(self, msg:str=None) -> list:
        '''👉 Returns the list of options:
        * [A,B] -> [A,B]
        * {A:x, B:y} -> [{A:x}, {B:y}]
        * Ref: https://quip.com/CDrjAxNKwLpI/-Prompt#temp:C:KSce8ac7c8cdfd54249991baa11c'''
        self.RequireAtt('Options')
        return self.GetOptionList(msg=msg)
        
    
    def GetOptionList(self, msg:str=None) -> list:
        '''👉 Returns the list of options:
        * [A,B] -> [A,B]
        * {A:x, B:y} -> [{A:x}, {B:y}]
        * [{A:x}, {B:y}] -> [{A:x}, {B:y}]
        * Ref: https://quip.com/CDrjAxNKwLpI/-Prompt#temp:C:KSce8ac7c8cdfd54249991baa11c'''
        
        options = self.GetAtt('Options')
        
        if options == None:
            return []
        
        UTILS.AssertIsAnyType(options, [list,dict])
        
        if isinstance(options, list):
            return options
        
        else:
            ret = []
            for key in options:
                ret.append({key: options[key]})
            return ret
    

    def GetDownloadOptionList(self) -> list[str]:
        '''👉 https://quip.com/CDrjAxNKwLpI/-Prompt#temp:C:KSce8ac7c8cdfd54249991baa11c'''
        options = self.GetList('Options', mustExits=False)
        for item in options:
            UTILS.AssertIsType(item,str)
        return options


    def SetResults(self, results:list[str]):
        '''👉️ Sets the possible results, to help clients:'''
        UTILS.AssertIsType(results, list)
        self.GetAtt('Results', set=results)


    def SetOptions(self, options:Union[str,list[str]], override:bool=False):
        '''👉️ Sets the internal option list from multiple types of inputs:
        * String: '[a,b]' -> [{a,a},{b,b}]
        * List of strings: ['a','b'] -> [{a,a},{b,b}]
        '''
        current = self.GetAtt('Options')
        if current not in [None,[]] and override != True:
            LOG.RaiseValidationException(f'Options have values, you need to explicitly override. Current={current}')
        
        options = PROMPT_OPTION.ParseOptions(options)
        self.GetAtt('Options', set=options)


    def HasOptions(self):
        return len(self.GetOptionList()) > 0
    
    def EnsureNoOptions(self):
        if self.HasOptions():
            LOG.RaiseValidationException(f'Options should not be set on={self._obj}')


    def VerifyPrompt(self):
        '''👉 Verifies if all required properties have values.
        * Docs: https://quip.com/CDrjAxNKwLpI#temp:C:KSc3b3a2537dfeb48d2ad2848477
        '''
        format = self.RequireFormat()
        self.RequireMessage()
        self.RequirePromptID()
        self.GetDefault()

        # In case there are options...
        if not self.IsMissingOrEmpty('Options'):

            options = self.GetOptionList()

            # Only allow option items to be a string or dictionary.
            for option in options:
                UTILS.AssertIsAnyType(option, [str,dict])

            # Default should be one of the options.
            if len(options) > 0 and not self.IsMissingOrEmpty('Default'):
                UTILS.AssertIsAnyValue(
                    value= self.GetDefault(), 
                    options= self.GetOptionList(), 
                    msg= 'Default should be one of the options!')
        
        # Ensure Yes/No/Cancel results.
        if format in ['CONFIRM', 'LOCATION', 'TRACK']:
            self.EnsureNoOptions()
            self.SetResults(['YES', 'NO', 'CANCEL'])

        # Ensure OK/Cancel results.
        elif format in [
            'AMOUNT', 'DATE', 'EAN', 'INFO', 'INT', 'QUANTITY', 
            'OTP', 'RATE', 'SCAN', 'TEXT', 'TIME', 
            'UNTIL', 'UPLOAD', 'WAIT'
        ]:
            self.EnsureNoOptions()
            self.SetResults(['OK', 'CANCEL'])
            
            # Validate the default values.
            default = self.GetDefault()
            if default:
                if format == 'AMOUNT':
                    UTILS.RequireFloat(default)
                elif format == 'INT':
                    UTILS.RequireInt(default)
                elif format == 'QUANTITY':
                    UTILS.RequireInt(default)
                elif format == 'TEXT':
                    pass
                elif format in [
                    'EAN', 'DATE', 'INFO', 'OTP', 'RATE', 'SCAN', 
                    'TIME', 'UNTIL', 'UPLOAD', 'WAIT']:
                    LOG.RaiseValidationException(
                        f'Unexpected default in {format=} in message={self.RequireMessage()}!')

        # Ensure values for options.
        elif format in ['MANY', 'ONE']:
            self.SetResults(['OK', 'CANCEL'])
            options = self.RequireOptionList(
                msg='👉 ONE/MANY require options!')
            
            if len(options) == 0:
                LOG.RaiseValidationException(
                    'Options expected, empty list received!')
            
            for option in options:
                UTILS.Require(option)
                ##option.RequireID()
                ##option.RequireTranslation()

        elif format in ['SELFIE']:
            self.EnsureNoOptions()
            self.SetResults(['CANCEL'])
            self.RequireLocator()

        elif format in ['TOUCH']:
            self.SetResults(['CANCEL'])
            self.RequireLocator()

        elif format in ['DOWNLOAD']:
            if self.ContainsAtt('Locator'):
                self.RequireLocator()
            else:
                self.RequireAppendix()

        elif format in ['BIND', 'SHARE', 'ISSUE', 'CHARGE']:
            # Do not validate behaviours, these are just for archive.
            pass

        else:
            LOG.RaiseValidationException(
                f'Unexpected format: {format}',
                f'prompt=', self)


    def LookupOptionKey(self, optionTitle:str):
        '''👉 Returns the optionID of the option with the given title.'''
        UTILS.RequireArgs([optionTitle])
        
        options = STRUCT(self.RequireOptions())
        for optionID in options.Attributes():
            if options[optionID] == optionTitle:
                return optionID
            
        return LOG.RaiseException(
            f'Option not found with that title.', optionTitle)