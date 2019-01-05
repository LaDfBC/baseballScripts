
def combine_files():
    output_file = "/home/george/Documents/mlnReports/mln_master_log_combined.csv"
    input_file_template = '/home/george/Documents/mlnReports/MLN Master Log- Season 1 - Sxxx PAs.csv'

    output_file = open(output_file, 'w+')
    for i in range(1, 15):
        input_file = input_file_template.replace("xxx", str(i))
        current_file = open(input_file, 'r+')
        current_file.readline()

        for line in current_file:
            if len(line.split(",")) == 23:
                modified_line = line.replace('\n', "," + str(i) + '\n')
                output_file.write(modified_line)

        current_file.close()
    output_file.close()

combine_files()