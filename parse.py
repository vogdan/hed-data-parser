import re
import glob
import platform



def get_name_and_fice(flines):
    """
    Get institution name and FICE code

    :input: input file handler (as returned by open)
    """
    institution, fice_code = "", ""
    for i, line in enumerate(flines):
        if i == 12:
            institution = line.strip()
        elif not fice_code:
            match = re.search("FICE Identification: \*(\d*)\*", line)
            if match:
                fice_code = match.group(1)
        elif institution:
            break
    return institution, fice_code


def parse_people(fh):
    """
    Get info about people (Phase1)

    :input: input file handler (as returned by open)
    :output: Returns a list of person details each element representing
             one (tab separated) line in the future output file)
    """
    institution, fice_code = get_name_and_fice(fh.readlines())
    fh.seek(0)
    results = []        
    if platform.system() == 'Windows':
        candidates_pat = '(?s)\n(\d{2}\t.*>\n\t \n\n)'
        candidates_sep = '\n\t \n\n'
    else:
        #assume we unse *nix
        candidates_pat = '(?s)\r\n(\d{2}\t.*>\r\n\t \r\n\r\n)'
        candidates_sep = '\r\n\t \r\n\r\n'
    candidate_data = re.findall(candidates_pat, fh.read())[0].strip()
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

        

def parse_institutions(fh):
    """
    Get info about people (Phase2)

    :input: input file handler (as returned by open)
    """
    flines = fh.readlines()
    institution, fice_code = get_name_and_fice(flines)
    phone, unit_id, hi_off, cal_sys, website = ['' for i in range(5)]
    est, fees, enroll, aff, c_class = ['' for i in range(5)]
    for line in flines:
        if not phone:
            match = re.search("Phone: \*(\d*)\*", line)
            if match:
                fice_code = match.group(1)
        elif if not unit_id:
            match = re.search("Unit ID: \*(\d*)\*")
            if match:
                unit_id = match.group(1)
        elif if not hi_off:
            match = re.search("Highest Offering: \*(\d*)\*")
            if match:
                unit_id = match.group(1)
        elif if not unit_id:
            match = re.search("Unit ID: \*(\d*)\*")
            if match:
                unit_id = match.group(1)
        elif if not unit_id:
            match = re.search("Unit ID: \*(\d*)\*")
            if match:
                unit_id = match.group(1)
        elif if not unit_id:
            match = re.search("Unit ID: \*(\d*)\*")
            if match:
                unit_id = match.group(1)
        elif if not unit_id:
            match = re.search("Unit ID: \*(\d*)\*")
            if match:
                unit_id = match.group(1)
    
        


if __name__ == '__main__':
    with open("output-people.tab", "w") as fout:
        fout.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
            "Institution" ,"ficeCode" ,"jobCode" ,"title" ,"fullName" ,"email" ,"phone"))
        for infile in glob.glob("input (*).txt"):
                print "Working on file `{}`".format(infile)
                try:
                    with open(infile, "r") as fh:
                        [fout.write("{}\n".format(line)) for line in parse_people(fh)] 
                except Exception as e:
                    print "\tERROR: `{}`".format(e)
                    print "\t!! Skipping input file `{}`...".format(infile)
                    continue
            
