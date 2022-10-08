import os

edit_this_file = 'chia-blockchain/chia/plotting/util.py'
edit_line_if_contain = '("*.plot")'
with_this_file = 'chia-blockchain/chia/plotting/util_edited.py'
config_file_destination_path = '/root/.chia/mainnet/config/config.yaml'
config_file_path = 'config.yaml'

with open(edit_this_file, 'r') as read_file:
    with open(with_this_file, 'w') as write_file:
        for line in read_file:
            if edit_line_if_contain in line:
                line = line.replace('.plot', '.csv')
            write_file.write(line)

os.system(f'rm -rf {edit_this_file}')
os.system(f'mv {with_this_file} {edit_this_file}')
os.system(f'mv {config_file_path} {config_file_destination_path}')

