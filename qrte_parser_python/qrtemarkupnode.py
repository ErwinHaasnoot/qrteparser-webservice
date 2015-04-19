from qrtelogger import log
from qrtecsv import csvreader, csvwriter
import json,os
from collections import OrderedDict

class QRTEMarkUpNode():
    
    
    QRTE_exitQuestions  = 'QRTE_exitQuestions'
    QRTE_blockData      = 'QRTE_blockData'
    QRTE_idData         = 'QRTE_idData'
    QRTE_columns        = 'QRTE_columns'
    
    delimiter_exit      = ';'
    
    jsonCol = []
    
    def __init__(self,node):
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
            
    def writeData(self,file,postfix):
        outfile = file + postfix
        columns = self.getColNames()
        
        # Ensure removal of output file
        try:
            os.remove(outfile)
        except OSError:
            pass
        
        csvwriter(outfile, columns)
        
        global_data = OrderedDict([(col,'') for col in columns])
        
        csvgen = csvreader(file)
        
        #Skip first two lines
        headers = csvgen.next()
        csvgen.next()
        
        for row in csvgen:
            subject_data = OrderedDict(zip(headers, row))
            self._writeData(subject_data, global_data, columns, outfile)
    
    
    def _writeData(self, subject_data, level_data, columns, outfile):
        # Copy level_data
        level_data = OrderedDict([(k,level_data[k]) for k in level_data])
        
        for i in range(self.amount):
            level_data.update(self.getLevelData(subject_data, level_data, i))
            
            if len(self.childs) != 0:
                for child in self.childs:
                    child._writeData(subject_data, level_data, columns, outfile)
            else:
                csvwriter(outfile, level_data.values())
        
        
    def getLevelData(self, subject_data, level_data, index = -1):
        """
            Get data related to this node (this level)
        """
        
        # Get data based on columns related to this node
        for col in self.columns:
            index_name = col
            data_name = self.columns[col]
            if index_name != data_name:
                log('Mapping %s => %s' % (index_name, data_name))
            if self.addIndex == True:
                index_name += "(%s)" % (index + 1)
                
            if data_name in level_data and index_name in subject_data:
                level_data[data_name] = subject_data[index_name]
            else:
                log.spam('AddIndex: %s for name %s' % (self.addIndex,self.name))
                log.spam('Could not find %s in level_data or %s in subject_data' % (data_name, index_name))
                
        for col in self.data:
            level_data[col] = self.data[col]
        
        # Get data from jsonColumns associated with this node
        for key in self.jsonCol:
            if self.addIndex:
                key += "(%s)" % (index + 1)
                
                #print key, subject_data
                sdata = json.loads(subject_data[key])
                for key in sdata:
                    level_data[key] = sdata[key]
        # Add name index
        if self.addIndex:
            level_data[self.name] = index
        
        
        log.spam(level_data)
        
        return level_data
                
                
        
    
            
        
    
    
    @classmethod
    def create(node, file):
        """
            Creates a QRTEMarkUpNode based on a data file
            Markup nodes determine the structure of the output file
        """
        headers,blocks,ignore_columns, exit_questions = node.buildBlockMeta(file)
        
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
        log('top_level addIndex: %s' % top_level['addIndex'])
        
        return node(top_level)
        
    @classmethod 
    def isUnique(cls,L):
        return len(L) == len(set(L))
        
    @classmethod
    def buildBlockMeta(node, file):
        csvgen = csvreader(file)
        
        #Get headers
        headers = next(csvgen)
        
        #Initialise block dictionary
        blocks = {}
        ignore_columns = node.getIgnoreColumns()
        
        #Skip next line
        next(csvgen)
        
        subject_id = 1
        
        for values in csvgen:
            data = dict(zip(headers,values))
            
            predef_columns = json.loads(data[node.QRTE_columns])
            log.spam('Exit questions column data: %s' % (data[node.QRTE_exitQuestions],))
            exit_questions = data[node.QRTE_exitQuestions].split(node.delimiter_exit)
            
            assert node.isUnique(exit_questions), \
                "Expected unique exit questions, not unique! - %s" % exit_questions #TODO: Make this QRTEParserException
            
            block_ids = []
                
            for exit_q in exit_questions:
                
                trial_count = 1
                block_id = None
                log.spam('Checking ExitQuestion: %s' % (exit_q,))
                
                assert "%s_1_TEXT(1)" % (exit_q,) in data, \
                    "Missing index 1 for exit question %s, make sure the row index numbering starts at 1 for the block with exit question %s" % (exit_q, exit_q)
                while("%s_1_TEXT(%s)" % (exit_q, trial_count) in data):
                    trial_count += 1
                    block_id = block_id or data["%s_2_TEXT(%s)" % (exit_q, trial_count)]
                    log.spam('block_id so far: %s for exit_q %s' % (block_id, exit_q))
                assert block_id is not None, \
                    "block_id is missing for block with exit question: %s" % exit_q #TODO: Make this QRTEParserException
                
                block_ids += [block_id]
                
                if exit_q not in blocks:
                    blocks[exit_q] = node.getBottomLevelNode()
                    blocks[exit_q].update({
                        'jsonCol': ["%s_1_TEXT" % exit_q],
                        'name': '%sId' % exit_q,
                    })
                    
                    ignore_columns += ["%s_1_TEXT" % exit_q, "%s_2_TEXT" % exit_q]
                    
                if block_id not in predef_columns:
                    #TODO: Report warning
                    log.warning("Could not find %s in column list. Did respondent miss this block, or it a partial response?")
                    continue
                
                
                
                blocks[exit_q]['columns'] = dict(zip(predef_columns[block_id],predef_columns[block_id]))
                blocks[exit_q]['amount'] = max(trial_count-1,blocks[exit_q]['amount'])
                
                log.spam('Found %s trials' % (blocks[exit_q]['amount'],))
                    
                    
            
            assert node.isUnique(block_ids), \
                "Expected unique block ids, not unique! - %s" % block_ids #TODO: Make this QRTEParserException
                
            log('Parsed subject %s successfully!' % subject_id)
            
            log.silent('Found %s exit question%s for subject %s: %s' % (len(exit_questions),'' if len(exit_questions) == 1 else 's', subject_id, exit_questions))
            subject_id += 1
            
        return headers,blocks,ignore_columns, exit_questions

    # HELPER FUNCTIONS
    
    @classmethod
    def splitkey(cls,key):
        index = None
        tokens = key.split('(')
        
        if (len(tokens) < 2):
            key = ''.join(tokens[0:])
            if key[-2:-1] == 'V1': 
                key = 'V1'
            return key, index
        
        assert tokens[-1][-1] == ')', \
            "Expected key ending with ), instead got key with ( in it, but no ) for key %s" % key # TODO: Make this QRTEParserException
        
        index = int(tokens[-1][0:-1])
        key = ''.join(tokens[0:-1])
        return key, index
    
    @classmethod
    def getBottomLevelNode(cls):
        return dict(columns={},amount=1, addIndex = 1, name = None)
        
    @classmethod
    def getTopLevelNode(cls):
        return dict(childs=[],columns=cls.getPredefinedColumns(),amount=1,addIndex=0,name="topLevelId")
    
    @classmethod
    def getPredefinedColumns(cls):
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
        return [cls.QRTE_columns,cls.QRTE_idData,cls.QRTE_blockData,cls.QRTE_exitQuestions]
        
    @classmethod
    def makeUnique(cls,arr):
            
        seen = set()
        seen_add = seen.add
        return [x for x in arr if not (x in seen or seen_add(x))]
        
        