from .qrtelogger import log
from .qrteexception import QRTEParserException
from .qrtecsv import csvreader, csvwriter
import json, os
from collections import OrderedDict


class QRTEMarkUpNode():
    QRTE_exitQuestions = 'QRTE_exitQuestions'
    QRTE_blockData = 'QRTE_blockData'
    QRTE_idData = 'QRTE_idData'
    QRTE_columns = 'QRTE_columns'

    delimiter_exit = ';'

    jsonCol = []

    def __init__(self, columns={}, childs=[], amount=None, data={}, jsonCol=[], name='', addIndex=False):
        """

        :param columns:
        :param childs:
        :param amount:
        :param data:
        :param jsonCol:
        :param name:
        :param addIndex:
        :return:
        """
        self.colNames = None

        self.columns = {}
        for key in columns:
            try:
                int(key)
            except:
                self.columns[key] = columns[key]
            else:
                self.columns[columns[key]] = columns[key]

        self.childs = [QRTEMarkUpNode(**child) for child in childs]
        self.addIndex = addIndex

        if amount is None:
            self.amount = 0
            self.addIndex = False
        else:
            self.amount = amount

        self.jsonCol = jsonCol
        self.data = data
        self.name = name


    def get_column_names(self):
        if self.colNames is None:
            self.colNames = [self.columns[k] for k in self.columns] + [self.name] + [k for k in self.data]

            # Deduplicate and sort array
            self.colNames = sorted(self.colNames)

            for child in self.childs:
                self.colNames += child.get_column_names()

            # deduplicate:

            self.colNames = self.make_unique(self.colNames)

            return self.colNames
        else:
            return self.colNames

    def write_data(self, file, outfile):
        """

        :param file:
        :param outfile:
        :return:
        """
        columns = self.get_column_names()

        # Ensure removal of output file
        try:
            os.remove(outfile)
        except OSError:
            pass

        csvwriter.open(outfile)
        csvwriter.write(columns)

        global_data = OrderedDict([(col, '') for col in columns])

        csvgen = csvreader(file)

        # Skip first two lines
        headers = next(csvgen)
        # Fix file header
        headers[0] = 'V1'
        next(csvgen)
        for row in csvgen:
            subject_data = OrderedDict(zip(headers, row))
            self._write_data(subject_data, global_data, columns, outfile)

        csvwriter.close()

    def _write_data(self, subject_data, level_data, columns, outfile):
        """

        :param subject_data:
        :param level_data:
        :param columns:
        :param outfile:
        :return:
        """
        # Copy level_data
        level_data = OrderedDict([(k, level_data[k]) for k in level_data])
        subject = subject_data['V1']
        ignore_json_col_keys = []
        for key in self.jsonCol:
            if key+'(1)' not in subject_data or subject_data[key+'(1)'] == '':
                ignore_json_col_keys.append(key)
                log.warning(QRTEParserException(code=QRTEParserException.WARNING_MISSING_JSON_COL_KEY, subject=subject,
                                                Key=key.split('_')[0]).message)
        for i in range(self.amount):
            level_data.update(self.get_level_data(subject_data, level_data, i, ignore_json_col_keys))

            if len(self.childs) != 0:
                for child in self.childs:
                    child._write_data(subject_data, level_data, columns, outfile)
            else:
                csvwriter.write(level_data.values())

    def get_level_data(self, subject_data, level_data, index=-1, ignore_json_col_keys=[]):
        """

        :param subject_data:
        :param level_data:
        :param index:
        :param ignore_json_col_keys:
        :return:
        """

        subject = subject_data['V1']

        # Get data based on columns related to this node
        joinarr = ['', '(%s)' % index]
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

        for col in self.data:
            level_data[col] = self.data[col]

        # Get data from jsonColumns associated with this node
        for key in self.jsonCol:
            if key in ignore_json_col_keys:
                continue

            if self.addIndex:
                key += "(%s)" % (index + 1)

                # print key, subject_data
                try:
                    if key in subject_data and subject_data[key] != '':
                        sdata = json.loads(subject_data[key])
                    else:
                        raise QRTEParserException(code=QRTEParserException.ERR_MISSING_KEYS, subject=subject, Key=key)
                except QRTEParserException as e:
                    log.warning(e.message)
                    continue
                except:
                    raise QRTEParserException(code=QRTEParserException.ERR_LOAD_JSON_DATA, subject=subject, Key=key,
                                              Data=subject_data[key])
                for key in sdata:
                    level_data[key] = sdata[key]
        # Add name index
        if self.addIndex:
            level_data[self.name] = index

        return level_data


    @classmethod
    def create(node, file, exit_q_unique=True):
        """
            Creates a QRTEMarkUpNode based on a data file
            Markup nodes determine the structure of the output file

        :param node:
        :param file:
        :param exit_q_unique:
        :return:
        """
        headers, blocks, ignore_columns, exit_questions = node.build_block_meta(file, exit_q_unique)

        predef_columns = node.get_predefined_columns()

        top_level = node.get_top_level_node()

        for header in headers:
            if header == '':
                continue
            index = -1
            put_key = ""
            put_val = ""

            key, index = node.splitkey(header)

            if (index is None):
                # blocks[key]['amount'] = max(blocks[key]['amount'], index)
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
        log('top_level addIndex: %s', top_level['addIndex'])

        return node(**top_level)

    @classmethod
    def is_unique(cls, L):
        """

        :param L:
        :return:
        """
        return len(L) == len(set(L))


    @classmethod
    def build_block_meta(node, file, exit_q_unique=False):
        """
        Builds MarkUp nodes from given QRTE data file.
        :param node: Class definition
        :param String file: path/to/file
        :param Bool exit_q_unique: Whether Exit questions should be deduplicated, or raise error upon finding duplicate Exit Tags
        :return:
        """
        csvgen = csvreader(file)

        # Get headers
        headers = next(csvgen)
        headers[0] = 'V1'

        #Initialise block dictionary
        blocks = {}
        ignore_columns = node.get_ignore_columns()

        #Skip next line
        next(csvgen)

        subject_id = 0
        for values in csvgen:
            subject_id += 1
            try:
                data = dict(zip(headers, values))
                subject = data['V1']

                try:
                    predef_columns = json.loads(data[node.QRTE_columns])
                except KeyError:
                    raise QRTEParserException(code=QRTEParserException.ERR_MISSING_COLUMNS, subject=subject,
                                              SubjectId=subject_id, column=node.QRTE_columns)
                except Exception as e:
                    raise QRTEParserException(code=QRTEParserException.ERR_COLUMN_INVALID_JSON, subject=subject,
                                              SubjectId=subject_id, Data=data[node.QRTE_columns])
                exit_questions = data[node.QRTE_exitQuestions].split(node.delimiter_exit)

                if not node.is_unique(exit_questions):
                    if not exit_q_unique:
                        raise QRTEParserException(code=QRTEParserException.ERR_UNIQUE_EXITQ, subject=data['V1'],
                                                  ExitQuestions=exit_questions, SubjectId=subject_id)
                    else:
                        exit_questions = node.make_unique(exit_questions)

                block_ids = []

                for exit_q in exit_questions:

                    trial_count = 1
                    block_id = None
                    if "%s_1_TEXT(1)" % (exit_q,) not in data or data["%s_1_TEXT(1)" % (exit_q,)] == '':
                        raise QRTEParserException(code=QRTEParserException.ERR_MISSING_INDEX_1, subject=subject,
                                                  ExitQuestion=exit_q, SubjectId=subject_id)
                    while ("%s_1_TEXT(%s)" % (exit_q, trial_count) in data):
                        block_id = block_id or data["%s_2_TEXT(%s)" % (exit_q, trial_count)]
                        trial_count += 1
                    if block_id is None:
                        raise QRTEParserException(code=QRTEParserException.ERR_MISSING_BLOCKID, subject=subject,
                                                  SubjectId=subject_id)

                    block_ids += [block_id]

                    if exit_q not in blocks:
                        blocks[exit_q] = node.get_bottom_level_node()
                        blocks[exit_q].update({
                            'jsonCol': ["%s_1_TEXT" % exit_q],
                            'name': '%sId' % exit_q,
                        })

                        ignore_columns += ["%s_1_TEXT" % exit_q, "%s_2_TEXT" % exit_q]

                    if block_id not in predef_columns:
                        raise QRTEParserException(code=QRTEParserException.ERR_MISSING_BLOCKID_FROM_COLUMNS,
                                                  subject=subject, BlockId=block_id, SubjectId=subject_id)

                    blocks[exit_q]['columns'] = dict(zip(predef_columns[block_id], predef_columns[block_id]))
                    blocks[exit_q]['amount'] = max(trial_count - 1, blocks[exit_q]['amount'])

                if not node.is_unique(block_ids):
                    raise QRTEParserException(code=QRTEParserException.ERR_BLOCKID_NOT_UNIQUE, subject=subject,
                                              BlockIds=block_ids, SubjectId=subject_id)
            except QRTEParserException as e:
                log.error(e.__str__())
                continue

        return headers, blocks, ignore_columns, exit_questions

    # HELPER FUNCTIONS

    @classmethod
    def splitkey(cls, key):
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
            raise QRTEParserException(code=QRTEParserException.ERR_TAG_WITH_INVALID_PARENTHESES, subject='Unknown',
                                      Key=key)

        index = int(tokens[-1][0:-1])
        key = ''.join(tokens[0:-1])
        return key, index

    @classmethod
    def get_bottom_level_node(cls):
        """

        :return:
        """
        return dict(columns={}, amount=1, addIndex=1, name=None)

    @classmethod
    def get_top_level_node(cls):
        """

        :return:
        """
        return dict(childs=[], columns=cls.get_predefined_columns(), amount=1, addIndex=0, name="topLevelId")

    @classmethod
    def get_predefined_columns(cls):
        """

        :return:
        """
        return dict(
            V1="ResponseID",
            V2="ResponseSet",
            V3="Name",
            V4="ExternalDataReference",
            V5="EmailAddress",
            V6="IPAddress",
            V7="Status",
            V8="StartDate",
            V9="EndDate",
            V10="Finished")

    @classmethod
    def get_ignore_columns(cls):
        """

        :return:
        """
        return [cls.QRTE_columns, cls.QRTE_idData, cls.QRTE_blockData, cls.QRTE_exitQuestions]

    @classmethod
    def make_unique(cls, arr):
        """

        :param arr:
        :return:
        """

        seen = set()
        seen_add = seen.add
        return [x for x in arr if not (x in seen or seen_add(x))]
        
        