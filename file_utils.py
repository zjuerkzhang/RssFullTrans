import codecs
import time
import os

def write_to_log_file(file_name, str):
    log_file = codecs.open(file_name, 'a+','utf-8')
    log_file.write(time.ctime()+'   '+str+'\n')
    log_file.close()

def delete_file(file_name):
    if os.name.lower() == 'posix':
        os.system('rm -f ' + file_name)
    if os.name.lower() == 'nt':
        os.system('del ' + file_name)

def move_file(file_name, to_dir):
    if not os.path.exists(file_name):
        return
    if not os.path.exists(to_dir):
        os.system('mkdir ' + to_dir)
    if os.name.lower() == 'posix':
        os.system('mv '+file_name+' '+to_dir+'/')
    if os.name.lower() == 'nt':
        os.system('move '+file_name+' '+to_dir+'/')

def rename_file(old_name, new_name):
    if not os.path.exists(old_name):
        return
    if os.name.lower() == 'posix':
        os.system('mv ' + old_name + ' ' + new_name)
    if os.name.lower() == 'nt':
        os.system('rename ' + old_name + ' ' + new_name)

def copy_file(src_file, dst_file):
    if not os.path.exists(src_file):
        return
    if os.name.lower() == 'posix':
        os.system('cp ' + src_file + ' ' + dst_file)
    if os.name.lower() == 'nt':
        os.system('copy ' + src_file + ' ' + dst_file)

