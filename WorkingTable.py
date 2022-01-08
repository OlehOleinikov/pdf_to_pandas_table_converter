import os
from datetime import datetime, timedelta

from rich.table import Table
from rich.console import Console

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1


def get_pages_count(path: str) -> int:
    """Counts the number of pages in PDF file"""
    with open(path, 'rb') as f:
        parser = PDFParser(f)
        document = PDFDocument(parser)
        pages_count = resolve1(document.catalog['Pages'])['Count']
    return pages_count


class WorkingTable:
    """Forms a list of PDF files in the working directory. Keeps track of conversion progress. Prints the table"""
    def __init__(self):
        files_list = [x for x in os.listdir() if x.endswith('.pdf')]
        if not files_list:
            print("No PDF files in directory... ")
            os.abort()

        self.files = {}  # main dict with files info and convertion order
        for file in enumerate(files_list):
            num = int(file[0])
            print(f'\rCalculating files size... {round(num / len(files_list) * 100, 2)}%', end='')
            name = os.path.basename(file[1])
            size = str(round(os.path.getsize(name) / 1024.0)) + ' Kb'
            page = get_pages_count(name)
            file_dict = {num: {'number': num,
                               'name': name,
                               'size': size,
                               'page': page,
                               'time_s': None,
                               'time_f': None,
                               'speed': None,
                               'duration': None,
                               'status': None}}
            self.files.update(file_dict)
        print('\r ')

    def upd_file_start(self, file: str):
        """Updates information about the beginning of file conversion (in the table)"""
        pos = self._get_file_position_by_name(file)
        self.files[pos]['time_s'] = datetime.now()
        self.files[pos]['status'] = 0.00
        self._reprint_table()

    def upd_file_progress(self, file, pages_loaded, part_pages, part_time):
        """Updates information about the current file progress, speed, expected total time"""
        pos = self._get_file_position_by_name(file)
        self.files[pos]['duration'] = datetime.now() - self.files[pos]['time_s']
        self.files[pos]['speed'] = part_pages / part_time
        self.files[pos]['time_f'] = timedelta(seconds=((self.files[pos]['page'] - pages_loaded) /
                                                       self.files[pos]['speed'])) + datetime.now()
        self.files[pos]['status'] = round(pages_loaded / self.files[pos]['page'] * 100, 2)
        self._upd_other_files_est_time(self.files[pos]['speed'], pos)
        self._reprint_table()

    def _upd_other_files_est_time(self, speed, current_file_pos):
        """Calculates the estimated processing time for other files"""
        for pos in range(current_file_pos+1, len(self.files)):
            self.files[pos]['time_f'] = self.files[pos-1]['time_f'] \
                                        + timedelta(seconds=(self.files[pos]['page'] / speed))

    def upd_file_finish(self, file):
        """Updates information about the ending of file conversion (in the table)"""
        pos = self._get_file_position_by_name(file)
        self.files[pos]['time_f'] = datetime.now()
        self.files[pos]['duration'] = datetime.now() - self.files[pos]['time_s']
        self.files[pos]['speed'] = self.files[pos]['page'] / (self.files[pos]['duration'].total_seconds())
        self.files[pos]['status'] = 100.00
        self._reprint_table()

    def get_files_count(self):
        """Returns count of PDF files in directory"""
        return len(self.files)

    def get_pages_count(self, file_number: int):
        """Returns pages count by file order position"""
        return self.files[file_number]['page']

    def get_file_name_by_position(self, file_number: int):
        return self.files[file_number]['name']

    def _get_file_position_by_name(self, file_name):
        for key in self.files.keys():
            if self.files[key]["name"] == file_name:
                return key

    def _reprint_table(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        table = Table(title='FILES STATUS')
        table.add_column('№')
        table.add_column('File')
        table.add_column('Size')
        table.add_column('Pages')
        table.add_column('Start')
        table.add_column('Finish')
        table.add_column('Dur')
        table.add_column('Speed\n(page/sec)')
        table.add_column('Status')

        console = Console(width=110)
        for pos in range(len(self.files)):
            rec = self.files[pos]
            time_s = rec['time_s'].strftime("%H:%M:%S") if rec['time_s'] else '-'
            time_f = rec['time_f'].strftime("%H:%M:%S") if rec['time_f'] else '-'
            dur = str(rec['duration']).split('.')[0] if rec['duration'] else '-'
            speed = str(round(rec['speed'], 2)) if rec['speed'] else '-'
            status = str(round(rec['status'], 2)) + ' %' if rec['status'] else '-'

            files_to_print = [str(pos + 1),
                              rec['name'],
                              rec['size'],
                              str(rec['page']),
                              time_s,
                              time_f,
                              dur,
                              speed,
                              status]
            table.add_row(*files_to_print)
        console.print(table, justify='center')
