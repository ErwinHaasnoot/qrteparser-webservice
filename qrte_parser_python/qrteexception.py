class QRTEParserException(Exception):
    
    ERR_UNKNOWN = -1
    ERR_NONE = 0
    ERR_UNIQUE_EXITQ = 1
    ERR_MISSING_INDEX_1 = 2
    ERR_MISSING_COLUMNS = 3
    ERR_COLUMN_INVALID_JSON = 4
    ERR_MISSING_BLOCKID = 5
    ERR_MISSING_BLOCKID_FROM_COLUMNS = 6
    ERR_BLOCKID_NOT_UNIQUE = 7
    ERR_TAG_WITH_INVALID_PARENTHESES = 8
    ERR_LOAD_JSON_DATA = 9
    ERR_MISSING_KEYS = 10

    WARNING_MISSING_JSON_COL_KEY = 20


    ERR_ZIP_INVALID = 30
    ERR_ZIP_CONTAINS_NO_FILES = 31
    ERR_ZIP_CONTAINS_TWO_OR_MORE_FILES = 32
    ERR_READ_CSV_FAILED = 33
    ERR_ZIP_CONTAINS_NO_CSV = 34

    
    ERR_MSG = {
        ERR_UNKNOWN: 'ERR_UNKNOWN',
        ERR_NONE: 'ERR_NONE',
        # META BLOCK ERROR
        ERR_UNIQUE_EXITQ: 'ERR_UNIQUE_EXITQ',
        ERR_MISSING_INDEX_1: 'ERR_MISSING_INDEX_1',
        ERR_COLUMN_INVALID_JSON: 'ERR_COLUMN_INVALID_JSON',
        ERR_MISSING_BLOCKID: 'ERR_MISSING_BLOCKID',
        ERR_MISSING_BLOCKID_FROM_COLUMNS: 'ERR_MISSING_BLOCKID_FROM_COLUMNS',
        ERR_BLOCKID_NOT_UNIQUE: 'ERR_BLOCKID_NOT_UNIQUE',

        # PARSE ERRORS
        ERR_TAG_WITH_INVALID_PARENTHESES: 'ERR_TAG_WITH_INVALID_PARENTHESES',
        ERR_LOAD_JSON_DATA:'ERR_LOAD_JSON_DATA',
        ERR_MISSING_KEYS:'ERR_MISSING_KEYS',
        WARNING_MISSING_JSON_COL_KEY: 'WARNING_MISSING_JSON_COL_KEY',

        # CSV READ/WRITE ERROR
        ERR_ZIP_INVALID: 'ERR_ZIP_INVALID',
        ERR_ZIP_CONTAINS_NO_FILES: 'ERR_ZIP_CONTAINS_NO_FILES',
        ERR_ZIP_CONTAINS_TWO_OR_MORE_FILES: 'ERR_ZIP_CONTAINS_TWO_OR_MORE_FILES',
        ERR_ZIP_CONTAINS_NO_CSV: 'ERR_ZIP_CONTAINS_NO_CSV',
        ERR_READ_CSV_FAILED: 'ERR_READ_CSV_FAILED'
    }



    ERR_MSG_VERBOSE = {
        ERR_UNKNOWN: 'This is an unknown error. Please report immediately to support@qrtengine.com',
        ERR_NONE: 'No error! (Huh?)',
        ERR_UNIQUE_EXITQ: 'Exit questions have not been uniquely defined, or the respondent has run through the same block twice. Either way, causes very likely loss of data. Please fix.',
        ERR_MISSING_INDEX_1: 'Exit question with index 1 is missing. Either Subject did not go through Indicated block, or wrong row indices are used in Loop & Merge spreadsheet for Trial block with mentioned Exit Tag. Please fix.',
        ERR_COLUMN_INVALID_JSON: 'Column cache is not valid JSON. Likely that respondent quit the survey early. If this is not the case, please report immediately to support@qrtengine.com, with the survey .qsf and the original data file.',
        ERR_MISSING_BLOCKID: 'Block Id was not properly stored. Unknown cause, please report immediately to support@qrtengine.com, including survey .qsf file and original data file.',
        ERR_MISSING_BLOCKID_FROM_COLUMNS: 'Block Id was found, but not stored in columns cache. Unknown cause. Please report immediately to support@qrtengine.com, with the survey .qsf and the original data file.',
        ERR_BLOCKID_NOT_UNIQUE: 'Some of the block ids found were not Unique. Causes loss of data. Please give each Trial block a unique name blockId (Init question JavaScript)',
        ERR_TAG_WITH_INVALID_PARENTHESES: 'Question tag found with incorrectly matched parentheses (, ). Please refrain from using parentheses at all in question tags.',
        ERR_LOAD_JSON_DATA:'Could not Load JSON data from mentioned key. Unknown cause, perhaps the Exit question does not have 2 answer fields? Please report immediately to support@qrtengine.com, with the survey .qsf and the original data file.',
        ERR_MISSING_KEYS:'Json column key could not be found. Unknown cause. Please report immediately to support@qrtengine.com, with the survey .qsf and the original data file.',
        WARNING_MISSING_JSON_COL_KEY: 'The Subject seems to be missing a proper value for the mentioned Key column, This happens in partial responses, or when the subject simply hasn\'t run through the block.',

        ERR_ZIP_INVALID: 'Invalid zip file, please ZIP correctly and try again.',
        ERR_ZIP_CONTAINS_NO_FILES: 'Empty zip Archive. Please include at most one datafile in the zip archive.',
        ERR_ZIP_CONTAINS_TWO_OR_MORE_FILES: 'ERR_ZIP_CONTAINS_TWO_OR_MORE_FILES',
        ERR_ZIP_CONTAINS_NO_CSV: 'ERR_ZIP_CONTAINS_NO_CSV',
        ERR_READ_CSV_FAILED: 'ERR_READ_CSV_FAILED'
    }


    
    
    def __init__(self,subject, code = -1, **kwargs):
        formatstr = '[CODE:%s][TAG:%s] Subject: %s'
        args = (code, QRTEParserException.ERR_MSG[code], subject,QRTEParserException.ERR_MSG_VERBOSE[code])
        for k in kwargs:
            formatstr += ', %s: %s' % (k, kwargs[k])

        formatstr += ' - %s'
        super(QRTEParserException,self).__init__(formatstr % args)
        self.code = code
        self.subject = subject