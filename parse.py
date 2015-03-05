import re
from glob import glob
from platform import system
from argparse import ArgumentParser


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

def get_common_info(flines):
    """
    Get institution name, last updated date and  FICE code

    :input: list of file lines as returned by readlines()
    """
    institution, fice_code, last_updated = "", "", ""
    rex = Re()
    for i, line in enumerate(flines):
        if i == 12:
            institution = line.strip()
        if not last_updated:
            if rex.match("Last updated (\d{2}/\d{2}/\d{4})", line):
                last_updated = rex.result.group(1)
        elif not fice_code:
            if rex.match("FICE Identification: \*0*(\d*)\*", line):
                fice_code = rex.result.group(1)
        elif institution:
            break
    return institution, fice_code, last_updated

def get_line_sep():
    """
    Get the correct line separator depending on the OS in use
    """
    if system() == 'Windows':
        return '\n'
    else:
        #assume we unse *nix
        return '\r\n'


def parse_people(fh):
    """
    Get info about people (Phase 2)

    :input: input file handler (as returned by open)
    :output: Returns a list of person details each element representing
             one (tab separated) line in the future output file)
    """
    institution, fice_code, last_updated = get_common_info(fh.readlines())
    fh.seek(0)
    results = []        
    lsep = get_line_sep()
    candidates_pat = '(?s){0}(\d{{2}}\t.*>{0}\t {0}{0})'.format(lsep)
    candidates_sep = '{0}\t {0}{0}'.format(lsep)
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
            results.append("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
                institution, fice_code, job_code, title, name, email, phone, 
                last_updated))
    return results

def parse_institution_data(fh):
    """
    Get info about people (Phase 3)

    :input: input file handler (as returned by open)
    :output: a list of needed info, in the appropriate order
    """
    rex = Re()
    flines = fh.readlines()
    institution, fice_code, last_updated = get_common_info(flines)
    phone, unit_id, hi_off, cal_sys, website = ['' for i in range(5)]
    established , fees, enroll, aff, c_class = ['' for i in range(5)]
    fs_link = ''
    lsep = get_line_sep()
    for idx, line in enumerate(flines):
        if phone \
                and unit_id \
                and hi_off \
                and cal_sys \
                and website \
                and established \
                and fees \
                and enroll \
                and aff \
                and c_class \
                and fs_link:
            break
        if ": *" in line:
            if not phone:
                if rex.match("Phone: \*(.*)\*", line):
                    phone = rex.result.group(1)
                    continue
            if not unit_id:
                if rex.match("Unit ID: \*(\d*)\*", line):
                    unit_id = rex.result.group(1)
                    continue
            if not hi_off:
                if rex.match("Highest Offering: \*(.*)\*", line):
                    hi_off = rex.result.group(1)
                    continue
            if not cal_sys:
                if rex.match("Calendar System: \*(.*)\*", line):
                    cal_sys = rex.result.group(1)
                    continue
            if not website:
                if rex.match("Web Site: \*(.*)\*", line):
                    website = rex.result.group(1).split(" <")[0]
                    continue
            if not established:
                if rex.match("Established: \*(\d*)\*", line):
                    established = rex.result.group(1)
                    continue
            if not fees:
                if rex.match("Annual Undergraduate Tuition and Fees .*: \*(.*)\*", line):
                    fees = rex.result.group(1)
                    continue
            if not enroll:
                if rex.match("Enrollment: \*(.*)\*", line):
                    enroll = rex.result.group(1)
                    continue
            if not aff:
                if rex.match("Affiliation: \*(.*)\*", line):
                    aff = rex.result.group(1)
                    continue
            if not c_class:
                if rex.match("Carnegie Class: \*(.*)\*", line):
                    c_class = rex.result.group(1)
                    continue
        elif '*Faculty & Staff link*' in line:
            fs_link = flines[idx+1].split('>')[0].lstrip('<')
            continue
        # elif not fs_link:
        #     pattern = "\*Faculty \& Staff link\*{}<(.*)>".format(lsep)
        #     if rex.match(pattern, line):
        #         fs_link = rex.result.group(1)
        #         continue
    return [institution, phone, fice_code, unit_id, hi_off, cal_sys, website, 
            established, fees, enroll, aff, c_class, last_updated, fs_link]


if __name__ == '__main__':
    """
    Wrap all together in a minimal cli interface.
    """
    arg_parser = ArgumentParser(description='Get person and institution info')
    arg_parser.add_argument('-gp', '--get_people', help='''Get people info.
Creates `output-people.tab` in CWD''', action="store_true")
    arg_parser.add_argument('-gi', '--get_insts', help='''Get institution info.
Creates `output-institutions.tab` in CWD''', action="store_true")
    args = arg_parser.parse_args()
    if not args.get_people and not args.get_insts:
        print "Error: Too few args: -gp and/or -gi must be specified. \n\tUse -h for help."
        exit(1)

    infile_list = glob("input (*).txt")
    # phase 2
    if args.get_people:
        print '\n Getting people...'
        out_file = 'output-people.tab'
        with open(out_file, "w") as fout:
            fout.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                    "Institution", "ficeCode", "jobCode", "title",
                    "fullName", "email", "phone", "lastUpdated"))
            for infile in infile_list:
                print "Working on file `{}`".format(infile)
                try:
                    with open(infile, "r") as fh:
                        [fout.write("{}\n".format(line)) 
                         for line in parse_people(fh)] 
                except Exception as e:
                    print "\tERROR: `{}`".format(e)
                    print "\t!! Skipping input file `{}`...".format(infile)
                    continue
    # phase 3
    if args.get_insts:
        print "\n Getting institutions... "
        out_file = 'output-institutions.tab'
        header = ['InstitutionName', 'Phone', 'FICE Identification', 
                  'Unit ID', 'Highest Offering', 'Calendar System', 'webSite',
                  'Established', 'TuitionAndFees', 'Enrollment', 'Affiliation', 
                  'Carnegie Class', 'Last Updated', 'FacultyStaffLink']
        out_line_bp = "\t".join(["{}" for i in range(len(header))]) + "\n"
        with open(out_file, "w") as fout:
            fout.write(out_line_bp.format(*header))
            for infile in infile_list:
                print "Working on file `{}`".format(infile)
                with open(infile, "r") as fh:
                    fout.write(out_line_bp.format(*parse_institution_data(fh))) 

