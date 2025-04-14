import datetime


class job:
    def __init__(self, job_id, description, duration):
        self.id = job_id
        self.description = description
        self.start = 0
        self.duration = duration
        self.aircraft = None
        self.fixed = False

        #         requiredSkills is a list of required skills
        # 1 string per requied. If it is an 'OR' then seprate the skills using '|'
        self.requiredCertifications = []

        #     notAllocated is a list of the skills not allocated. Each time a member of staff is allocated, the skill is
        # removed from notAllocated
        self.notAllocated = []
        self.staff = []

    #         A list of staff allocated

    def getEnd(self):
        return self.start + self.duration

    def __str__(self):
        f = ""
        if self.fixed:
            f = "*"
        e = self.getEnd()
        na = ""
        for s in self.notAllocated:
            na = na + s + ","

        p = ""
        for s in self.staff:
            p = p + s.name + ","

        return f"{self.id} ({self.start}-{e}) {f} NA={na} S= {p}"

    def reset(self):
        self.fixed = False
        self.start = 0
        self.staff = []
        self.notAllocated = []
        for sk in self.requiredCertifications:
            self.notAllocated.append(sk)

    def addCertification(self, skill):
        self.requiredCertifications.append(skill)
        self.reset()

    def allocate(self, staffMember):
        #         check if skill is needed
        found = False
        i = 0
        for sk in self.notAllocated:
            if staffMember.certification in sk:
                found = True
                break
            i = i + 1

        if found:
            self.staff.append(staffMember)
            self.fixed = True
            staffMember.jobsAllocated.append(self)
            del self.notAllocated[i]

        return found

    def check(self, staffMember):
        #        Return True if stffMember has the skill needed
        found = False
        i = 0
        for sk in self.requiredCertifications:
            if staffMember.certification in sk:
                found = True
                break
            i = i + 1
        return found

    def validate(self):
        return None


class aircraft:
    def __init__(self, planeID, arrival, departure):
        self.aircraftID = planeID
        #         aircraft id
        self.arrival = arrival
        #     start of maintaince window
        self.departure = departure
        #     end of maintanance window\

        self.jobs = []  # All jobs allocated to this airraft
        self.unscheduled = []  # All jobs not in the job queue
        self.queue = []
        self.timeAvail = arrival  # Time aircraft is available to add the next job

    def over(self):

        if self.available > self.departure:
            return 10
        #             d=self.available-self.departure
        #             p=d.total_seconds()/60
        #             return p*p
        return 0

    def validate(self):
        # check times
        buffer = ""

        time = self.arrival
        for j in self.queue:
            if j.start < time:
                buffer = buffer + "Time err - " + j.id
            time = j.getEnd()

        if len(self.queue) > 0:
            if self.available > self.departure:
                buffer = buffer + " Late Departure"

        if len(self.unscheduled) > 0:
            buffer = buffer + " Unscheduled jobs."
        if buffer == "":
            return None

    def add(self, job):
        self.jobs.append(job)
        self.unscheduled.append(job)
        self.reset()

    def addToQueue(self, job, time=None):
        if job in self.unscheduledJobs:
            self.unscheduledJobs.remove(job)

            self.queue.append(job)
            job.fixed = True
            if time != None:
                job.start = time
            else:
                job.start = self.available

            self.available = job.getEnd()

    def reset(self):
        self.available = self.arrival
        self.unscheduledJobs = []
        self.queue = []
        for j in self.jobs:
            self.unscheduledJobs.append(j)

    def __str__(self):
        err = ""
        if len(self.queue):
            if self.queue[-1].getEnd() > self.departure:
                err = " LATE DEPARTURE!"

        buffer = self.aircraftID + " "
        buffer = (
            buffer
            + "( "
            + str(self.arrival)
            + ":"
            + str(self.departure)
            + "Avail:"
            + str(self.available)
            + " "
            + err
            + " )\n"
        )

        buffer = buffer + "Scheduled Jobs \n"
        for j in self.queue:
            #         while j != None:
            buffer = buffer + "\t" + str(j) + "\n"
        #             j = j.next

        if len(self.unscheduledJobs) > 0:
            buffer = buffer + "Unscheduled jobs:\n"
            for j in self.unscheduledJobs:
                buffer = buffer + str(j.id) + " : " + j.description + "\n"

        return buffer


class staff:
    def __init__(self, name, certification):
        self.name = name
        self.certification = certification
        self.reset()

    def allocJob(self, job):
        self.allocJob.append(job)

    def reset(self):
        self.jobsAllocated = []
        self.timeAvailable = datetime.datetime(1976, 8, 23)

    def validate(self):
        if len(self.jobsAllocated) == 0:
            return None  # "OK - No jobs allocated"
        time = self.jobsAllocated[0].start
        buffer = ""
        for j in self.jobsAllocated:
            if j.start < time:
                buffer = buffer + "Start time error " + j.id
            time = j.getEnd()

        if buffer == "":
            return None
        else:
            return buffer

    def __str__(self):
        buffer = self.name + " Avail:" + str(self.timeAvailable)
        for j in self.jobsAllocated:
            ac = ""
            if j.aircraft != None:
                ac = j.aircraft.aircraftID
            buffer = (
                buffer
                + "\n"
                + j.id
                + " "
                + ac
                + " "
                + " ( "
                + str(j.start)
                + " - "
                + str(j.getEnd())
                + " ) "
                + j.description
            )
        return buffer


class problem:
    def __init__(self, people, planes, work_packages):
        #         build from suppied Pandas tables
        self.aircraft = {}
        self.jobs = {}
        self.staff = {}

        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.time_format = "%H:%M:%S"

        self.addStaff(people)
        self.addAircraftAndJobs(planes, work_packages)

    def __str__(self):
        buffer = ""
        for a in self.aircraft:
            buffer = buffer + str(self.aircraft[a]) + "\n"

        return buffer

    def addStaff(self, people):
        for index, row in people.iterrows():
            self.staff[row["NAME"]] = staff(row["NAME"], row["Certification"])

    # Create Plane objects and add Jobs

    def getDateTime(self, dateStr, timeStr):
        # remove the fractional time after the conversion of time string to time object
        # timeStr = timeStr.split(".")[0]
        # print(timeStr)
        # Create a dateTime obect based on the date and time strings
        date = datetime.datetime.strptime(dateStr, self.date_format)
        time = datetime.datetime.strptime(timeStr, self.time_format)
        time_change = datetime.timedelta(minutes=time.minute, hours=time.hour)
        date = date + time_change
        return date

    def addAircraftAndJobs(self, planes, work_packages):
        for index, row in planes.iterrows():
            landingTime = self.getDateTime(
                str(row["A/C Landing Date"]), str(row["A/C Landing Time"])
            )
            departTime = self.getDateTime(
                str(row["A/C departure Date"]), str(row["A/C departure Time"])
            )
            a = aircraft(
                str(row["Aicraft (A/C) Serial Number"]), landingTime, departTime
            )

            #     Add jobs
            jobs = row["Work that needs to be carried out"].split(",")
            for jID in jobs:
                jID = jID.strip()
                r = work_packages.loc[jID]
                duration = datetime.timedelta(minutes=int(r["Minutes"]))
                j = job(jID, r["WP description"], duration)
                j.aircraft = a
                certs = r["Required Certified Personnnel"].split(",")

                #         print(certs)
                for c in certs:
                    j.addCertification(c)
                a.add(j)
                self.jobs[a.aircraftID + "." + j.id] = j
            self.aircraft[a.aircraftID] = a

    def getUnallocated(self):
        unalloc = 0
        for j in self.jobs:
            unalloc = unalloc + len(self.jobs[j].notAllocated)
        #             p=(len(self.jobs[j].notAllocated)*self.jobs[j].duration.total_seconds() / 60)
        #             unalloc = unalloc + (p*p)
        return unalloc

    def printStaff(self):
        for s in self.staff:
            print(self.staff[s] + "\n")

    def validate(self):
        #         Validate whether the solution held is valid
        for a in self.aircraft:
            ac = self.aircraft[a]
            b = ac.validate()
            if b != None:
                print(a + " " + b)

        for j in self.jobs:
            jb = self.jobs[j]
            b = jb.validate()
            if b != None:
                print(j + " " + b)

        for s in self.staff:
            st = self.staff[s]
            b = st.validate()
            if b != None:
                print(s + " " + b)

    def reset(self):
        #         Reset any elements of the solution
        for a in self.aircraft:
            ac = self.aircraft[a]
            ac.reset()

        for j in self.jobs:
            jb = self.jobs[j]
            jb.reset()

        for s in self.staff:
            st = self.staff[s]
            st.reset()

    def allocate(self, s, j):
        #         Allocate staff to job
        #         Check qualifications first

        if j.check(s) == False:
            return False

        a = j.aircraft
        if j.fixed:
            if s.timeAvailable <= j.start:
                j.allocate(s)
                s.timeAvailable = j.getEnd()
                return True
            else:
                #                 Staff not available in time
                return False

        if s.timeAvailable < a.available:
            #         Staff available before aircraft
            j.allocate(s)
            j.start = a.available
            a.addToQueue(j)
            s.timeAvailable = j.getEnd()
            a.available = j.getEnd()
            #             print("**4")
            return True

        else:
            #             Staff avail after aircraft avail
            j.allocate(s)
            a.addToQueue(j, time=s.timeAvailable)
            s.timeAvailable = j.getEnd()
            a.available = j.getEnd()
            #             print("**5")
            return True

    def getListJobs(self):
        #         Return a complete list of jobs
        return list(self.jobs.keys())

    def getListStaff(self):
        #     Retunr a complete list of staff
        return list(self.staff.keys())
