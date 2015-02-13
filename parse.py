import re
import glob


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
        candidate_data = re.findall("(?s)\r\n(\d{2}\t.*>\r\n\t \r\n\r\n)", fin.read())[0].strip()
        for match in candidate_data.split("\r\n\t \r\n\r\n"):
            person_data = [item.strip() for item in match.split("\t")]
            try:
                job_code, title, name, email, phone = person_data
            except ValueError:
                job_code, title, name, phone = person_data
                email = ""
            job_code = job_code.lstrip("0")
            if email: email = email.split()[0]
            phone = phone.split(" <")[0]    
            results.append("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
                institution, fice_code, job_code, title, name, email, phone))
    
    return results


if __name__ == '__main__':
    with open("output.tab", "w") as fout:
        fout.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
            "Institution" ,"ficeCode" ,"jobCode" ,"title" ,"fullName" ,"email" ,"phone"))
        for infile in glob.glob("input (*).txt"):
            print "Working on file `{}`".format(infile)
            [fout.write("{}\n".format(line)) for line in parse(infile)] 
            
