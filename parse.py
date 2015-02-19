import re
import glob
import platform
from argparse import ArgumentParser



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
            match = re.search("FICE Identification: \*0*(\d*)\*", line)
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


class Re(object):
    """
    Enables cascading through multiple regex with if, elif, ..., else
    """
    def __init__(self):
        self.result = None
    def match(self,pattern,text):
        self.result = re.match(pattern,text)
        return self.result
    def search(self,pattern,text):
        self.result = re.search(pattern,text)
        return self.result

        
def parse_institution_data(fh):
    """
    Get info about people (Phase2)

    :input: input file handler (as returned by open)
    """
    rex = Re()
    flines = fh.readlines()
    institution, fice_code = get_name_and_fice(flines)
    phone, unit_id, hi_off, cal_sys, website = ['' for i in range(5)]
    established , fees, enroll, aff, c_class = ['' for i in range(5)]
    for i, line in enumerate(flines):
        if phone and unit_id and hi_off and cal_sys and website and \
                established  and fees and enroll and aff and c_class:
            break
        if not phone:
            if rex.match("Phone: \*(.*)\*", line):
                phone = rex.result.group(1)
        if not unit_id:
            if rex.match("Unit ID: \*(\d*)\*", line):
                unit_id = rex.result.group(1)
        if not hi_off:
            if rex.match("Highest Offering: \*(.*)\*", line):
                hi_off = rex.result.group(1)
        if not cal_sys:
            if rex.match("Calendar System: \*(.*)\*", line):
                cal_sys = rex.result.group(1)
        if not website:
            if rex.match("Web Site: \*(.*)\*", line):
                website = rex.result.group(1).split(" <")[0]
        if not established:
            if rex.match("Established: \*(\d*)\*", line):
                established = rex.result.group(1)
        if not fees:
            if rex.match("Annual Undergraduate Tuition and Fees \(In-District\): \*(.*)\*", line):
                fees = rex.result.group(1)
        if not enroll:
            if rex.match("Enrollment: \*(.*)\*", line):
                enroll = rex.result.group(1)
        if not aff:
            if rex.match("Affiliation: \*(.*)\*", line):
                aff = rex.result.group(1)
        if not c_class:
            if rex.match("Carnegie Class: \*(.*)\*", line):
                c_class = rex.result.group(1)
            
    return [institution, phone, fice_code, unit_id, hi_off, cal_sys, website, established, fees, enroll, aff, c_class]



if __name__ == '__main__':

    arg_parser = ArgumentParser(description='Get person and institution info')
    arg_parser.add_argument('-gp', '--get_people', help='''Get people info.
Creates `output-people.tab` in CWD''', action="store_true")
    arg_parser.add_argument('-gi', '--get_insts', help='''Get institution info.
Creates `output-institutions.tab` in CWD''', action="store_true")
    args = arg_parser.parse_args()

    if not args.get_people and not args.get_insts:
        print "Error: Too few args: -gp and/or -gi must be specified. \n\tUse -h for help."
        exit(1)
    if args.get_people:
        print '\n Getting people...'
        out_file = 'output-people.tab'
        with open(out_file, "w") as fout:
            fout.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                    "Institution", "ficeCode", "jobCode", "title",
                    "fullName", "email", "phone"))
            for infile in glob.glob("input (*).txt"):
                print "Working on file `{}`".format(infile)
                try:
                    with open(infile, "r") as fh:
                        [fout.write("{}\n".format(line)) 
                         for line in parse_people(fh)] 
                except Exception as e:
                    print "\tERROR: `{}`".format(e)
                    print "\t!! Skipping input file `{}`...".format(infile)
                    continue
    if args.get_insts:
        print "\n Getting institutions... "
        out_file = 'output-institutions.tab'
        with open(out_file, "w") as fout:
            out_line_bp = "\t".join(["{}" for i in range(12)]) + "\n"
            fout.write(out_line_bp.format(
                    'InstitutionName', 'Phone', 'FICE Identification', 'Unit ID', 
                    'Highest Offering', 'Calendar System', 'webSite', 'Established',
                    'TuitionAndFees', 'Enrollment', 'Affiliation', 'Carnegie Class'))
            for infile in glob.glob("input (*).txt"):
                print "Working on file `{}`".format(infile)
                with open(infile, "r") as fh:
                    fout.write(out_line_bp.format(*parse_institution_data(fh))) 



