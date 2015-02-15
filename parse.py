import re
import glob
import platform

def parse(filename):
    institution, fice_code = "", ""
    with open(filename, "r") as fin:
        for i, line in enumerate(fin.readlines()):
            if i == 12:
                institution = line.strip()
            elif not fice_code:
                match = re.search("FICE Identification: \*(\d*)\*", line)
                if match:
                    fice_code = match.group(1)
            elif institution:
                break

        results = []        
        fin.seek(0)
        if platform.system() == 'Windows':
            candidates_pat = '(?s)\n(\d{2}\t.*>\n\t \n\n)'
            candidates_sep = '\n\t \n\n'
        else:
            #assume we unse *nix
            candidates_pat = '(?s)\r\n(\d{2}\t.*>\r\n\t \r\n\r\n)'
            candidates_sep = '\r\n\t \r\n\r\n'
        candidate_data = re.findall(candidates_pat, fin.read())[0].strip()
        for match in candidate_data.split(candidates_sep):
            person_data = [item.strip() for item in match.split("\t")]
            if len(person_data) < 6:
                try:
                    job_code, title, name, email, phone = person_data
                except ValueError:
                    job_code = person_data[0] 
                    title = person_data[1]
                    name = person_data[2] 
                    email, phone = '', ''
                    try:
                        contact_info = person_data[3]
                        if '@' in contact_info:
                            email = contact_info
                        elif re.match('.+<tel:\+\d{2,}', contact_info):
                            phone = contact_info
                        else:
                            print "\tNo useful contact info found for {}".format(name)
                    except IndexError:
                        print "\tNo contact info found for {}".format(name)
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
            
