import re
import glob2

'''
We are looking to find matches like:

13	Vice Chanc Info/Technical Services
	Mr. Timothy (Tim) Marshall
	timothy.marshall@tccd.edu <mailto:timothy.marshall@tccd.edu>
	(817) 515-5389 <tel:+18175155389>
'''

def get_lines_from_file(filename):
    fin = open(filename, "r")
    input_string = fin.read();
    fin.close()

    input_lines = input_string.split("\n")
    for i in range(0,len(input_lines)):
        matches = re.search("Unit ID: \*(\d*)\*",input_lines[i])
        if matches is not None:
            unit_id = matches.group(1)
            unit_name = input_lines[i-7][1:-4]
            #print unit_id+" --- " + unit_name
            break

    input_lines = input_string.split("\n\n")
    result_lines = []
    #pattern = "\d{2}\\t.*<tel:[+ \d]*>"
    pattern = "(?s)(\d{2}\t.*>)"
    for elem in input_lines:
        matches = re.search(pattern,elem.strip())
        if matches is not None:
            candidate_elem = matches.group(1)
            candidate_lines =  candidate_elem.split('\n')
            candidate_result_lines = []

            for line in candidate_lines:
                if re.search("mailto|tel",line):
                    tmp_line = line.split('<')
                    candidate_result_lines.append(tmp_line[0][:-1])
                else:
                    candidate_result_lines.append(line)

            result_lines.append(''.join(candidate_result_lines))

    return unit_id, unit_name, result_lines

if __name__ == '__main__':
    files_to_process = glob2.glob("input (*).txt")

    fout = open("output.txt", "w")
    fout.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
        "Institution" ,"ficeCode" ,"jobCode" ,"title" ,"fullName" ,"email" ,"phone"))
    for file in files_to_process:
        id, name, lines = get_lines_from_file(file)
        for elem in lines:
            fout.writelines(name+' '+id+'\t'+elem+'\n')
    fout.close()
