import re
import glob

'''
We are looking to find matches like:

13	Vice Chanc Info/Technical Services
	Mr. Timothy (Tim) Marshall
	timothy.marshall@tccd.edu <mailto:timothy.marshall@tccd.edu>
	(817) 515-5389 <tel:+18175155389>
'''

def parse(filename):
    institution, fice_code = "", ""
    with open(filename, "r") as fin:
        for i, line in enumerate(fin.readlines()):
            if i == 12:
                institution = line.strip()
            elif not fice_code:
                match = re.search("Unit ID: \*(\d*)\*", line)
                if match:
                    fice_code = match.group(1)
            elif institution:
                break

        results = []        
        fin.seek(0)
        candidate_data = re.findall("(?s)\r\n(\d{2}\t.*>\r\n\t \r\n\r\n)", fin.read())
        print candidate_data
        candidate_data = candidate_data[0].strip()
        for match in candidate_data.split("\r\n\t \r\n\r\n"):
            person_data = [item.strip() for item in match.split("\t")]
            try:
                job_code, title, name, email, phone = person_data
            except ValueError:
                job_code, title, name, phone = person_data
                email = ""
            results.append("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
                institution, fice_code, job_code, title, name, email, phone))
    
    return results


if __name__ == '__main__':
    with open("output.txt", "w") as fout:
        fout.writeline("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
            "Institution" ,"ficeCode" ,"jobCode" ,"title" ,"fullName" ,"email" ,"phone")
        for infile in glob.glob("input (*).txt"):
            print infile
            [fout.writeline("{}".format(line)) for line in parse(infile)]
                
