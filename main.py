import os
from time import time

import pandas as pd
from tabula import read_pdf

from WorkingTable import WorkingTable
from range_generator import next_range_generator


if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    main_table = WorkingTable()
    files_count = main_table.get_files_count()
    for position in range(files_count):  # start next file convert
        file_name = main_table.get_file_name_by_position(position)
        pages_in_file = main_table.get_pages_count(position)
        main_table.upd_file_start(file_name)

        df = pd.DataFrame()  # init common df for pages' parts attaching
        gen = next_range_generator(pages_in_file)  # divide file by pages parts
        gen_status = True
        while gen_status:  # convert next part of pages
            try:
                gen_status = next(gen)
                page_start = gen_status[0]
                page_end = gen_status[-1]
                # Conversion:
                part_start = time()
                df_lst = read_pdf(file_name,
                                  pages=str(page_start)+'-'+str(page_end),
                                  pandas_options={'header': None},
                                  silent=True)
                for page_df in df_lst:
                    df = pd.concat([df, page_df], ignore_index=True)
                part_finish = time()
                # Update console table:
                main_table.upd_file_progress(file=file_name,
                                             pages_loaded=page_end,
                                             part_pages=page_end-page_start+1,
                                             part_time=part_finish-part_start)
            except StopIteration:
                gen_status = False
                new_file_name = "_".join(file_name.split(".")[0:-1])
                df.to_pickle(f'{new_file_name}.pk1')  # Save results
                # df.to_excel(f'{new_file_name}.xlsx')  # may exceed the maximum number of lines. Raises an error
        main_table.upd_file_finish(file_name)
