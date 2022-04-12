def create_textblock(rows_arr):
    output = ''
    for i in rows_arr:
        output = output + i.text
    return output.replace('\n', '')
    
#def splice(info_rows_arr):

        

