import csv
import os
import argparse
from sqlalchemy import create_engine, inspect, and_
from sqlalchemy.ext.declarative import declarative_base
import sys
import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
import re
from typing import List, Dict


Base = declarative_base()


class UserData(Base):
    __tablename__ = 'user_data'
    id = Column(Integer, primary_key=True)
    fullname = Column(String)
    email = Column(String)
    number = Column(String)
    label = Column(String)

    def __repr__(self):
        return "<User(fullname='{}', email='{}')".format(
            self.fullname, self.email
        )


def is_personal_str(email: str) -> bool:

    personal_email_domains = [
        "@aol.com", "@att.net", "@comcast.net",
        "@facebook", "@gmail", "@gmx.com", "@googlemail",
        "@google", "@hotmail", "hotmail.co.uk", "@mac.com",
        "@me.com", "@mail.com", "@msn.com",
        "@live.com", "@sbcglobal.net", "@verizon.net",
        "@yahoo", "@btinternet.com",
        "@virginmedia.com", "@blueyonder.co.uk",
        "@freeserve.co.uk", "@live.co.uk",
        "@ntlworld.com", "@o2.co.uk", "@orange.net", "@sky.com",
        "@talktalk.co.uk", "@tiscali.co.uk", "@virgin.net",
        "@wanadoo.co.uk", "@bt.com",
    ]
    for domain in personal_email_domains:
        if domain in email:
            return True
    else:
        return False


def is_personal_list(emaillist: List) -> List[bool]:

    personal_email_domains = [
        "@aol.com", "@att.net", "@comcast.net",
        "@facebook", "@gmail", "@gmx.com", "@googlemail",
        "@google", "@hotmail", "hotmail.co.uk", "@mac.com",
        "@me.com", "@mail.com", "@msn.com",
        "@live.com", "@sbcglobal.net", "@verizon.net",
        "@yahoo", "@btinternet.com",
        "@virginmedia.com", "@blueyonder.co.uk",
        "@freeserve.co.uk", "@live.co.uk",
        "@ntlworld.com", "@o2.co.uk", "@orange.net", "@sky.com",
        "@talktalk.co.uk", "@tiscali.co.uk", "@virgin.net",
        "@wanadoo.co.uk", "@bt.com",
    ]

    return_vals = []

    for email in emaillist:
        for domain in personal_email_domains:
            if domain in email:
                return_vals.append(True)
        else:
            return_vals.append(False)

    return return_vals


def email_regex(word: str) -> str:
    pattern = re.compile(
        r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    )
    findings = re.findall(pattern, word)
    if len(findings) > 0:
        return findings[0]
    else:
        return None


def phone_regex(word: str) -> str:
    pattern = re.compile(
        r"(((\+44\s?\d{4}|\(?0\d{4}\)?)\s?\d{3}\s?\d{3})|((\+44\s?\d{3}|\(?0\d{3}\)?)\s?\d{3}\s?\d{4})|((\+44\s?\d{2}|\(?0\d{2}\)?)\s?\d{4}\s?\d{4}))(\s?\#(\d{4}|\d{3}))?"
    )
    findings = re.findall(pattern, word)
    if len(findings) > 0:
        return findings[0][0]
    else:
        return None


def return_workload(file_or_dir, extension=".csv") -> List[str]:
    if isinstance(file_or_dir, (str,)):
        if not file_or_dir.lower().endswith(extension):
            print("Sorry gotta be a .csv")
            sys.exit()
        return [file_or_dir]
    elif isinstance(file_or_dir, (list, tuple)):
        return [x for x in file_or_dir if x.lower().endswith(extension)]
    else:
        print("Something went wrong")
        sys.exit()


def check_csvs(csvs: List[str], method: str="emails") -> Dict:

    findings = {
        "emails": [],
        "numbers": [],
        "names": [],
        "personal": []
    }

    for idx, cs in enumerate(csvs):

        with open(cs, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if args.method == "contacts":
                    email = email_regex(row["E-mail Address"])
                    bphone = row["Business Phone"]
                    cphone = row["Company Main Phone"]
                    hphone = row["Home Phone"]
                    pphone = row["Primary Phone"]
                    mphone = row["Mobile Phone"]
                    personal = is_personal_str(str(email))
                    name = " ".join(
                        [
                            row["First Name"].strip(),
                            row["Middle Name"].strip(),
                            row["Last Name"].strip()
                        ]
                    )
                    group = [
                        x for x in [bphone, cphone, hphone, pphone, mphone]
                        if x
                    ]
                    for g in group:
                        findings["emails"].append(email)
                        findings["numbers"].append(g)
                        findings["names"].append(name)
                        findings["personal"].append(personal)

                elif args.method == "emails":
                    "Initial Emails"
                    from_email = email_regex(row["From: (Address)"])
                    if from_email:
                        from_name = row["From: (Name)"]
                        from_number = ""
                        from_personal = is_personal_str(from_email)

                        findings["emails"].append(from_email)
                        findings["numbers"].append(from_number)
                        findings["names"].append(from_name)
                        findings["personal"].append(from_personal)

                    else:
                        pass

                    "Get Body Emails"
                    "Skipping for Now"
                    # body_emails = email_regex(row["Body"])
                    # body_numbers = phone_regex(row["Body"])
                    # body_names = "UNKNOWN"
                    # body_personals = [
                    #     is_personal_str(x) for x in body_emails
                    # ]

                    "Get CC: Emails"
                    if row["CC: (Name)"]:
                        cc_names = [x for x, y in zip(
                            row["CC: (Name)"].split(";"),
                            row["CC: (Address)"].split(";")
                        )
                            if email_regex(y)]
                        cc_emails = [
                            email_regex(x)
                            for x in row["CC: (Address)"].split(";")
                            if email_regex(x)
                        ]
                        cc_numbers = ["" for x in cc_names]
                        cc_personals = [
                            is_personal_str(email)
                            for email in cc_emails
                        ]
                        for cna, cne, cnu, cnp in zip(
                            cc_names, cc_emails, cc_numbers, cc_personals
                        ):
                            findings["emails"].append(cne)
                            findings["numbers"].append(cnu)
                            findings["names"].append(cna)
                            findings["personal"].append(cnp)

    return findings


def get_db(filepath: str):
    if os.path.exists(filepath) and filepath.lower().endswith(".db"):
        engine = create_engine(f'sqlite:///{filepath}')

        " Verify the table exists "
        ins = inspect(engine)
        if "user_data" in ins.get_table_names():
            Session = sessionmaker(bind=engine)
            return Session()
        else:
            # Database might be right but table could not exist
            Base = declarative_base()

            class UserData(Base):
                __tablename__ = 'user_data'
                id = Column(Integer, primary_key=True)
                fullname = Column(String)
                email = Column(String)
                number = Column(String)
                label = Column(String)

                def __repr__(self):
                    return "<User(fullname='{}', email='{}')".format(
                        self.fullname, self.email
                    )

            Base.metadata.create_all(bind=engine)

            " Verify the table exists "
            ins = inspect(engine)
            if "user_data" in ins.get_table_names():
                Session = sessionmaker(bind=engine)
                return Session()
            else:
                print("Could not create table")
                sys.exit()

    else:
        engine = create_engine(f'sqlite:///{filepath}')
        " Create Database Table"
        Base = declarative_base()

        class UserData(Base):
            __tablename__ = 'user_data'
            id = Column(Integer, primary_key=True)
            fullname = Column(String)
            email = Column(String)
            number = Column(String)
            label = Column(String)

            def __repr__(self):
                return "<User(fullname='{}', email='{}')".format(
                    self.fullname, self.email
                )

        Base.metadata.create_all(bind=engine)

        " Verify the table exists "
        ins = inspect(engine)
        if "user_data" in ins.get_table_names():
            Session = sessionmaker(bind=engine)
            return Session()
        else:
            print("Could not create table")
            sys.exit()


def check_insert(results: Dict, database) -> bool:

    pairs = []

    for email, name, number, label in zip(
        results["emails"],
        results["names"],
        results["numbers"],
        results["personal"]
    ):
        pairs.append((email, name, number, label))

    # Remove duplicates
    pruned = list(set(pairs))

    for email, name, number, label in pruned:
        result = db.query(UserData).filter(and_(
            UserData.fullname == name, UserData.email == email,
            UserData.number == number, UserData.label == label
        )).first()

        if not result:
            record = UserData(
                fullname=name, email=email,
                number=number, label=label
            )
            db.add(record)
            db.commit()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="individual filename to parse")
    parser.add_argument("--dir", help="directory to check")
    parser.add_argument("--database", help="new/existing sqlite database")
    parser.add_argument("--method", help=(
        "(contacts/ emails) enter one of them")
    )

    args = parser.parse_args()

    if args.file and args.dir:
        print("Specify either a file or a directory")
        sys.exit()

    if all([x is None for x in [args.file, args.dir, args.database]]):
        parser.print_help()
        sys.exit()

    if args.method not in ("contacts", "emails"):
        print("Method needs to either be 'contacts' or 'emails'")

    if args.database is None or not os.path.exists(args.database):
        time_string = datetime.datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(os.curdir, f"export-{time_string}.db")
    else:
        path = args.database

    if args.dir:
        if os.path.exists(args.dir):
            files = [os.path.join(args.dir, x) for x in os.listdir(args.dir)]
            workload = return_workload(files)
        else:
            print(f"Directory: {args.dir} does not exist!")
            sys.exit()

    if args.file:
        if os.path.exists(args.file):
            workload = return_workload(args.file)
        else:
            print(f"File: {args.file} does not exist!")

    if workload:
        print("Starting")
        dicts = check_csvs(workload)
        print("Data Parsed")
        db = get_db(path)
        print("DB Initialised")
        to_end = check_insert(dicts, db)
        print("DB Finished")
        print("Process Complete")
