from qrtelogger import log
from qrteexception import QRTEParserException
from qrtecsv import csvreader, csvwriter
import json,os
from collections import OrderedDict
from decimal import Decimal

class QRTEMarkUpNode():
    
    
    QRTE_exitQuestions  = 'QRTE_exitQuestions'
    QRTE_blockData      = 'QRTE_blockData'
    QRTE_idData         = 'QRTE_idData'
    QRTE_columns        = 'QRTE_columns'
    
    delimiter_exit      = ';'
    
    jsonCol = []
    
    def __init__(self,node, exit_q_unique = True):
        self.colNames = None
        self.columns = {}
        self.data = {}
        self.name = ''
        if 'columns' in node:
            for key in node['columns']:
                try:
                    int(key)
                except:
                    self.columns[key] = node['columns'][key]
                else:
                    self.columns[node['columns'][key]] = node['columns'][key]
        self.childs = []
        if 'childs' in node:
            self.childs = [QRTEMarkUpNode(child) for child in node['childs']]
        
        if 'amount' in node:
            self.amount = node['amount']
        else:
            self.amount = 0
            self.addIndex = False
            
            
        if 'addIndex' in node:
            self.addIndex = node['addIndex']
        else:
            if self.amount == 1:
                self.addIndex = True
            else:
                self.addIndex = False
                
        if 'jsonCol' in node:
            self.jsonCol = node['jsonCol']
        
        if 'data' in node:
            for key in node['data']:
                self.data[node['data'][key]] = node['data']['key']
        
        if 'name' in node:
            self.name = node['name']
            
            
    def getColNames(self):
        if self.colNames is None:
            self.colNames = [self.columns[k] for k in self.columns] + [self.name] + [k for k in self.data]
            
            # Deduplicate and sort array
            self.colNames = sorted(self.colNames)
            
            for child in self.childs:
                self.colNames += child.getColNames()
            
            # deduplicate:
            
            self.colNames = self.makeUnique(self.colNames)
            
            
            return self.colNames
        else:
            return self.colNames
            
    def writeData(self,file,outfile):
        """

        :param file:
        :param outfile:
        :return:
        """
        columns = self.getColNames()
        
        # Ensure removal of output file
        try:
            os.remove(outfile)
        except OSError:
            pass
        
        csvwriter.open(outfile)
        
        global_data = OrderedDict([(col,'') for col in columns])
        
        csvgen = csvreader(file)
        
        #Skip first two lines
        headers = csvgen.next()
        # Fix file header
        headers[0] = 'V1'
        csvgen.next()
        for row in csvgen:
            subject_data = OrderedDict(zip(headers, row))
            self._writeData(subject_data, global_data, columns, outfile)

        csvwriter.close()

    def _writeData(self, subject_data, level_data, columns, outfile):
        """

        :param subject_data:
        :param level_data:
        :param columns:
        :param outfile:
        :return:
        """
        # Copy level_data
        level_data = OrderedDict([(k,level_data[k]) for k in level_data])
        subject = subject_data['V1']
        ignore_json_col_keys = []
        for key in self.jsonCol:
            if key not in subject_data or subject_data[key] == '':
                ignore_json_col_keys.append(key)
                log.warning(QRTEParserException(code=QRTEParserException.WARNING_MISSING_JSON_COL_KEY,subject=subject, Key=key.split('_')[0]).message)
        for i in xrange(self.amount):
            level_data.update(self.getLevelData(subject_data, level_data, i,ignore_json_col_keys))
            
            if len(self.childs) != 0:
                for child in self.childs:
                    child._writeData(subject_data, level_data, columns, outfile)
            else:
                csvwriter.write(level_data.values())

    def getLevelData(self, subject_data, level_data, index = -1, ignore_json_col_keys = []):
        """

        :param subject_data:
        :param level_data:
        :param index:
        :param ignore_json_col_keys:
        :return:
        """

        subject = subject_data['V1']
        
        # Get data based on columns related to this node
        joinarr = ['','(%s)' % index]
        addIndexCache = self.addIndex

        for col in self.columns:
            index_name = col
            data_name = self.columns[col]
            if index_name != data_name:
                log('Mapping %s => %s', (index_name, data_name))
            if addIndexCache == True:
                joinarr[0] = index_name
                index_name = ''.join(joinarr)
                
            if data_name in level_data and index_name in subject_data:
                level_data[data_name] = subject_data[index_name]
            else:
                log.spam('AddIndex: %s for name %s', (self.addIndex,self.name))
                log.spam('Could not find %s in level_data or %s in subject_data', (data_name, index_name))
                
        for col in self.data:
            level_data[col] = self.data[col]
        
        # Get data from jsonColumns associated with this node
        for key in self.jsonCol:
            if key in ignore_json_col_keys:
                continue

            if self.addIndex:
                key += "(%s)" % (index + 1)
                
                #print key, subject_data
                try:
                    if key in subject_data and subject_data[key] != '':
                        sdata = json.loads(subject_data[key])
                    else:
                        raise QRTEParserException(code=QRTEParserException.ERR_MISSING_KEYS,subject=subject,Key=key)
                except QRTEParserException as e:
                    log.warning(e.message)
                    continue
                except:
                    raise QRTEParserException(code=QRTEParserException.ERR_LOAD_JSON_DATA,subject=subject,Key=key, Data=subject_data[key])
                for key in sdata:
                    level_data[key] = sdata[key]
        # Add name index
        if self.addIndex:
            level_data[self.name] = index
        
        
        #log.spam(level_data)
        
        return level_data
                
                
        
    
            
        
    
    
    @classmethod
    def create(node, file, exit_q_unique = True):
        """
            Creates a QRTEMarkUpNode based on a data file
            Markup nodes determine the structure of the output file

        :param node:
        :param file:
        :param exit_q_unique:
        :return:
        """
        headers,blocks,ignore_columns, exit_questions = node.buildBlockMeta(file,exit_q_unique)
        
        predef_columns = node.getPredefinedColumns()
        
        top_level = node.getTopLevelNode()
        
        for header in headers:
            if header == '':
                continue
            index = -1
            put_key = ""
            put_val = ""
            
            key, index =  node.splitkey(header)
            
            if(index is None):
            #     blocks[key]['amount'] = max(blocks[key]['amount'], index)
            #     put_key = key
            #     put_val = key
                
            #     if put_key in predef_columns:
            #         put_val = predef_columns[put_key]
            #     if not ( put_key in ignore_columns or put_val in ignore_columns or put_key == '' or put_val == ''):
            #         blocks[key]['columns'][put_key] = put_val
            # else:
                put_key = put_val = key
                
                if put_key in predef_columns:
                    put_val = predef_columns[put_key]
                if not ( put_key in ignore_columns or put_val in ignore_columns or put_key == '' or put_val == ''):
                    top_level['columns'][put_key] = put_val
                    
        top_level['childs'] = [blocks[k] for k in blocks]
        log('top_level addIndex: %s' , top_level['addIndex'])
        
        return node(top_level)
        
    @classmethod 
    def isUnique(cls,L):
        """

        :param L:
        :return:
        """
        return len(L) == len(set(L))
        
    @classmethod
    def buildBlockMeta(node, file, exit_q_unique):
        """

        :param node:
        :param file:
        :param exit_q_unique:
        :return:
        """
        csvgen = csvreader(file)
        
        #Get headers
        headers = next(csvgen)
        headers[0] = 'V1'
        
        #Initialise block dictionary
        blocks = {}
        ignore_columns = node.getIgnoreColumns()
        
        #Skip next line
        next(csvgen)
        
        subject_id = 0
        for values in csvgen:
            subject_id += 1
            try:
                data = dict(zip(headers,values))
                subject = data['V1']
                
                try:
                    predef_columns = json.loads(data[node.QRTE_columns])
                except KeyError:
                    raise QRTEParserException(code=QRTEParserException.ERR_MISSING_COLUMNS,subject=subject, SubjectId = subject_id)
                except Exception as e:
                    raise QRTEParserException(code=QRTEParserException.ERR_COLUMN_INVALID_JSON,subject=subject, SubjectId = subject_id, Data=data[node.QRTE_columns])
                #log.spam('Exit questions column data: %s' % (data[node.QRTE_exitQuestions],))
                exit_questions = data[node.QRTE_exitQuestions].split(node.delimiter_exit)
                
                if not node.isUnique(exit_questions):
                    if not exit_q_unique:
                        raise QRTEParserException(code=QRTEParserException.ERR_UNIQUE_EXITQ,subject=data['V1'],ExitQuestions=exit_questions, SubjectId = subject_id)
                    else:
                        exit_questions = node.makeUnique(exit_questions)
                
                block_ids = []
                    
                for exit_q in exit_questions:
                    
                    trial_count = 1
                    block_id = None
                    #log.spam('Checking ExitQuestion: %s' % (exit_q,))
                    if "%s_1_TEXT(1)" % (exit_q,) not in data or data["%s_1_TEXT(1)" % (exit_q,)] == '':
                        raise QRTEParserException(code=QRTEParserException.ERR_MISSING_INDEX_1,subject=subject,ExitQuestion=exit_q, SubjectId = subject_id)
                    while("%s_1_TEXT(%s)" % (exit_q, trial_count) in data):
                        block_id = block_id or data["%s_2_TEXT(%s)" % (exit_q, trial_count)]
                        trial_count += 1
                        #log.spam('block_id so far: %s for exit_q %s' % (block_id, exit_q))
                    if block_id is None:
                        raise QRTEParserException(code=QRTEParserException.ERR_MISSING_BLOCKID,subject=subject, SubjectId = subject_id)
                    
                    block_ids += [block_id]
                    
                    if exit_q not in blocks:
                        blocks[exit_q] = node.getBottomLevelNode()
                        blocks[exit_q].update({
                            'jsonCol': ["%s_1_TEXT" % exit_q],
                            'name': '%sId' % exit_q,
                        })
                        
                        ignore_columns += ["%s_1_TEXT" % exit_q, "%s_2_TEXT" % exit_q]

                    if block_id not in predef_columns:
                        raise QRTEParserException(code=QRTEParserException.ERR_MISSING_BLOCKID_FROM_COLUMNS, subject=subject,BlockId = block_id, SubjectId = subject_id)

                    blocks[exit_q]['columns'] = dict(zip(predef_columns[block_id],predef_columns[block_id]))
                    blocks[exit_q]['amount'] = max(trial_count-1,blocks[exit_q]['amount'])
                    
                    log.spam('Found %s trials', (blocks[exit_q]['amount'],))
                        
                        
                if not node.isUnique(block_ids):
                    raise QRTEParserException(code=QRTEParserException.ERR_BLOCKID_NOT_UNIQUE,subject=subject,BlockIds=block_ids, SubjectId = subject_id)
                    
                log('Parsed subject %s successfully!', subject)
                
                log.silent('Found %s exit question %s for subject %s: %s', (len(exit_questions),'' if len(exit_questions) == 1 else 's', subject_id, exit_questions))
            except QRTEParserException as e:
                log.error(e.message)
                continue
            except Exception as e:
                log.error('Could not check subject %s, due to error %s. This is a serious error, needs to be investigated.', (subject,e.message))
                raise e
            
        return headers,blocks,ignore_columns, exit_questions

    # HELPER FUNCTIONS
    
    @classmethod
    def splitkey(cls,key):
        """

        :param key:
        :return:
        """
        index = None
        tokens = key.split('(')
        
        if (len(tokens) < 2):
            key = ''.join(tokens[0:])
            if key[-2:-1] == 'V1': 
                key = 'V1'
            return key, index
        if tokens[-1][-1] != ')':
            raise QRTEParserException(code=QRTEParserException.ERR_TAG_WITH_INVALID_PARENTHESES,subject='Unknown',Key=key)

        index = int(tokens[-1][0:-1])
        key = ''.join(tokens[0:-1])
        return key, index
    
    @classmethod
    def getBottomLevelNode(cls):
        """

        :return:
        """
        return dict(columns={},amount=1, addIndex = 1, name = None)
        
    @classmethod
    def getTopLevelNode(cls):
        """

        :return:
        """
        return dict(childs=[],columns=cls.getPredefinedColumns(),amount=1,addIndex=0,name="topLevelId")
    
    @classmethod
    def getPredefinedColumns(cls):
        """

        :return:
        """
        return dict(
            V1 = "ResponseID",
            V2 = "ResponseSet",
            V3 = "Name",
            V4 = "ExternalDataReference",
            V5 = "EmailAddress",
            V6 = "IPAddress",
            V7 = "Status",
            V8 = "StartDate",
            V9 = "EndDate",
            V10 = "Finished")
    @classmethod        
    def getIgnoreColumns(cls):
        """

        :return:
        """
        return [cls.QRTE_columns,cls.QRTE_idData,cls.QRTE_blockData,cls.QRTE_exitQuestions]
        
    @classmethod
    def makeUnique(cls,arr):
        """

        :param arr:
        :return:
        """
            
        seen = set()
        seen_add = seen.add
        return [x for x in arr if not (x in seen or seen_add(x))]
        
        