import datetime
import math

class job:
    def __init__(self,job_id,description,ac,duration=0):
        self.id = job_id
        self.description = description
        # self.duration = duration
        self.aircraft = ac
        self.fixed = False
        # the workorders associated with this WP. Index is wpID
        self.workOrders = {}

        # Pointer to the first WO
        self.firstWorkOrder = None
        # Pointer to the last WO
        self.lastWorkOrder = None
        self.start = self.aircraft.arrival

# #         requiredSkills is a list of required skills
# # 1 string per requied. If it is an 'OR' then seprate the skills using '|'
#         self.requiredCertifications =[]
    
# #     notAllocated is a list of the skills not allocated. Each time a member of staff is allocated, the skill is 
# # removed from notAllocated
#         self.notAllocated =[]
#         self.staff = []
# #         A list of staff allocated
    
    def getListWOs(self):
        return list(self.workOrders.keys())
    
    def getEnd(self):
        if self.lastWorkOrder != None:
            return self.lastWorkOrder.getEnd()
        return aircraft.arrival
    
    def __str__(self):
        # f = ''
        # if self.fixed:
        #     f='*'
        # e= self.getEnd()         f
        # na =""
        # for s in self.notAllocated:
        #     na = na + s +","
        
        # p =""
        # for s in self.staff:
        #     p = p + s.name +","
            
        # return f"{self.id} ({self.start}-{e}) {f} NA={na} S= {p}"
        buf = "WP: " + self.id +"\n"
        if self.firstWorkOrder != None:
            wo = self.firstWorkOrder
            while wo != None:
                buf = buf + str(wo) +"\n"
                wo = wo.next
        return buf


    
    def reset(self):
        self.start = self.aircraft.arrival
        # self.fixed = False
        # self.start =0
        # self.staff = []
        # self.notAllocated = []
        # for sk in self.requiredCertifications:
        #     self.notAllocated.append(sk)
        for wo in self.workOrders.values():
            wo.reset()
    
    # def addCertification(self,skill):
    #     self.requiredCertifications.append(skill)
    #     self.reset()

    def addWorkOrder(self,woID, wo):
        self.workOrders[woID]= wo
        if self.firstWorkOrder == None:
            self.firstWorkOrder = wo
        if self.lastWorkOrder != None:
            self.lastWorkOrder.next = wo
        self.lastWorkOrder = wo

        
    def allocate(self, woID,staffMember):
        if len(self.workOrders)>0:
            return self.workOrders[woID].alocate(staffMember)
        else:
            return False
# #         check if skill is needed
#         found = False
#         i=0
#         for sk in self.notAllocated:
#             if staffMember.certification in sk:
#                 found = True
#                 break
#             i=i+1   
        
#         if found:
#             self.staff.append(staffMember)
#             self.fixed = True
#             staffMember.jobsAllocated.append(self)
#             del self.notAllocated[i]
        
#         return found
    
    def check(self, woID, staffMember):
#        Return True if stffMember has the skill needed
        # found = False
        # i=0
        # for sk in self.requiredCertifications:
        #     if staffMember.certification in sk:
        #         found = True
        #         break
        #     i=i+1   
        # return found
   
        if len(self.workOrders)>0:
            return self.workOrders[woID].check(staffMember)
        return False
    
    def validate(self):
        if len(self.workOrders)==0:
            return "Job "+ str(self.id) +" has no work orders associated."
        return None

class workOrder:
    def __init__(self,wo_id,duration,job):
        self.id = wo_id
        self.job = job

        self.start = job.aircraft.arrival #Default
        self.duration = duration
        # self.aircraft = None
        self.work_package = None
        self.fixed = False
        # Next WO in the sequence
        self.next = None

#         requiredSkills is a list of required skills
# 1 string per requied. If it is an 'OR' then seprate the skills using '|'
        self.requiredCertifications =[]
    
#     notAllocated is a list of the skills not allocated. Each time a member of staff is allocated, the skill is 
# removed from notAllocated
        self.notAllocated =[]

        self.staff = []
#         A list of staff allocated
    
    def getStart(self):
        return self.start

    def getEnd(self):
        if self.start == 0:
            return 0
        return self.start +self.duration

    def canMove(self):
        # return True if nothing ahead of this is fixed
        wo = self.next
        while wo != None:
            if wo.fixed == True:
                return False
            wo = wo.next

        return True #True 

    def shunt(self):
        # shunt WOs in front forward

        time = self.getEnd()
        wo = self.next
        while wo != None:
            if wo.fixed == True:
                raise UserWarning("Can't shunt fixed WO. \n"+str(wo))
            
            wo.start = time
            time = wo.getEnd()
            wo = wo.next
        return True #True 
    
    def __str__(self):
        f = ''
        if self.fixed:
            f='*'
        e= self.getEnd()         
        na =""
        for s in self.notAllocated:
            na = na + s +","
        
        p =""
        for s in self.staff:
            p = p + s.name +","
            
        return f"{self.id} ({self.start}-{e}) {f} NA={na} S= {p}"

    
    def reset(self):
        self.fixed = False
        self.start = self.job.aircraft.arrival
        self.staff = []
        self.notAllocated = []
        for sk in self.requiredCertifications:
            self.notAllocated.append(sk)
    
    def addCertification(self,skill):
        skill = skill.strip()
        self.requiredCertifications.append(skill)
        self.reset()
        
    def allocate(self, staffMember):
#         check if skill is needed
        # check if aready allocated:
        if staffMember in self.staff:
            return  False
        
        found = False
        i=0
        for sk in self.notAllocated:
            if staffMember.certification in sk:
                found = True
                break
            i=i+1   
        
        if found:
            self.staff.append(staffMember)
            self.fixed = True
            staffMember.woAllocated.append(self)
            del self.notAllocated[i]
        
        return found
    
    def check(self, staffMember):
#        Return True if staffMember has the skill needed
        found = False
        i=0
        for sk in self.requiredCertifications:
            if staffMember.certification in sk:
                found = True
                break
            i=i+1   
        return found
    
    def alreadyAllocated(self, staffMember):
        # Return True if staff member already allocated

        if staffMember in self.staff:
            return True
        else:
            return False
    
    def validate(self):
        return None

class aircraft:
    def __init__(self,planeID,arrival,departure):
        self.aircraftID = planeID
#         aircraft id
        self.arrival = arrival
#     start of maintaince window
        self.departure = departure
#     end of maintanance window\

        self.jobs =[] #All jobs allocated to this airraft
        self.unscheduled =[] #All jobs not in the job queue
        self.queue =[]
        # self.timeAvail = arrival #Time aircraft is available to add the next job
        
    def getAvailable(self):
        lastJob = self.queue[-1]
        lastWP = lastJob.lastWorkOrder
        if lastWP != None:
            return lastWP.getEnd()
        else:
            return self.arrival
        
    def over(self):
        if self.getAvailable() > self.departure:
            return 10
#             d=self.available-self.departure
#             p=d.total_seconds()/60
#             return p*p
        return 0
    
    def validate(self):
        #check times
        buffer = ""
        
        time = self.arrival
        for j in self.queue:
            if j.start < time:
                buffer = buffer + "Time err - " + j.id
            time = j.getEnd()

            
        if len(self.queue)>0:
            if self.available > self.departure:
                buffer = buffer + " Late Departure"
        
        if len(self.unscheduled) >0 :
            buffer = buffer + " Unscheduled jobs."
        if buffer == "":
            return None
        else:
            return buffer
            
    
    def add(self,job):
        self.jobs.append(job)
        self.unscheduled.append(job)
        self.reset()
        
        
    # def addToQueue(self,job,time=None):
    #     if job in self.unscheduledJobs:
    #         self.unscheduledJobs.remove(job)
            
    #         self.queue.append(job)
    #         job.fixed = True
    #         if time != None:
    #             job.start = time
    #         else:
    #             job.start = self.available
            
    #         self.available = job.getEnd()
                
            

    def reset(self):
        self.available = self.arrival
        self.unscheduledJobs =[]
        self.queue = []
        for j in self.jobs:
            self.unscheduledJobs.append(j)
            
    def __str__(self):
        err =""
        if len(self.queue):
            # if self.queue[-1].getEnd() > self.departure:
            if self.getAvailable() > self.departure:
                err =" LATE DEPARTURE!"

        buffer = self.aircraftID  +" "
        buffer =  buffer + "( "+str(self.arrival)  +":" +str(self.departure) +"Avail:" +str(self.getAvailable()) + " "+err+" )\n"
        
        buffer = buffer + "Scheduled Jobs \n"
        for j in self.queue:
            buffer = buffer +"\t"+ str(j)+"\n"

        
        
        if len(self.unscheduledJobs) >0:
            buffer = buffer + "Unscheduled jobs:\n"
            for j in self.unscheduledJobs:
                # buffer = buffer + str(j.id) +" : " +j.description +"\n"
                buffer = buffer +"\t"+ str(j)+"\n"
                
        return buffer
        
class staff:
    def __init__(self,name,certification):
        self.name = name
        self.certification = certification
        self.reset()
    
    def allocJob(self, job):
        self.allocJob.append(job)
        
    def reset(self):
        # self.jobsAllocated = []
        self.woAllocated = []
        self.timeAvailable = datetime.datetime(1976, 8, 23)
        self.scheduled = False
        
    def validate(self):
        if len(self.woAllocated)== 0:
            return None #"OK - No jobs allocated"
        time = self.woAllocated[0].start
        buffer = ""
        for wo in self.woAllocated:
            if wo.start < time:
                buffer = buffer + "Start time error " + wo.id
            time = wo.getEnd()
        
        if buffer == "":
            return None
        else:
            return buffer
        
    def __str__(self):
        buffer = self.name  + " Avail:" + str(self.timeAvailable)
        for wo in self.woAllocated :
            ac = ""
            if wo.work_package != None:
                ac = wo.work_package.aircraft.aircraftID
            buffer = buffer +"\n"+ wo.id + " "+ac+" "+" ( "+ str(wo.start) +" - "+ str(wo.getEnd())+" ) "
        return buffer
        
class problem:
    def __init__(self,people,planes,work_packages,work_orders):
#         build from suppied Pandas tables
        self.aircraft ={}
        self.jobs ={}
        self.staff={}
        self.WOs ={}
        self.date_format = '%d/%m/%Y'
        self.time_format = '%H:%M'
        
        self.addStaff(people)
        self.addAircraftAndJobs(planes,work_packages,work_orders)
        
    def __str__(self):
        buffer = ""
        for a in self.aircraft:
            buffer = buffer  + str(self.aircraft[a]) +"\n"
        
        return buffer
    
   


    def addStaff(self,people):
        self.certifications = {}# Dict of certifications to people


        for index, row in people.iterrows():
            self.staff[row['NAME']] = staff(row['NAME'],row['Certification'])
            if row['Certification'] not in self.certifications:
                self.certifications[row['Certification']] = []
            self.certifications[row['Certification']].append(row['NAME'])   
       

# Create Plane objects and add Jobs

    def getDateTime(self,dateStr,timeStr):
    #     Create a dateTime obect based on the date and time strings

        date = datetime.datetime.strptime(dateStr, self.date_format)
        time = datetime.datetime.strptime(timeStr, self.time_format)
        time_change = datetime.timedelta(minutes=time.minute,hours=time.hour) 
        date = date + time_change
        return date
    
    # def addAircraftAndJobs(self,planes,work_packages):
    #     for index, row in planes.iterrows():
    #         landingTime = self.getDateTime(str(row['A/C Landing Date']),str(row['A/C Landing Time']))
    #         departTime = self.getDateTime(str(row['A/C departure Date']),str(row['A/C departure Time']))
    #         a= aircraft(str(row['Aicraft (A/C) Serial Number']),landingTime,departTime)

    #     #     Add jobs
    #         jobs = row['Work that needs to be carried out'].split(',')
    #         for jID in jobs:
    #             jID= jID.strip()
    #             r = work_packages.loc[jID]
    #             duration = datetime.timedelta(minutes=int(r['Minutes']))
    #             j= job(jID,r['WP description'],duration)
    #             j.aircraft = a
    #             certs = r['Required Certified Personnnel'].split(',')

    #     #         print(certs)
    #             for c in certs:
    #                 j.addCertification(c)
    #             a.add(j)
    #             self.jobs[a.aircraftID+"."+j.id] =j
    #         self.aircraft[a.aircraftID] = a

    def addAircraftAndJobs(self,planes,work_packages,work_orders):
        for index, row in planes.iterrows():
            landingTime = self.getDateTime(str(row['A/C Landing Date']),str(row['A/C Landing Time']))
            departTime = self.getDateTime(str(row['A/C departure Date']),str(row['A/C departure Time']))
            a= aircraft(str(row['Aircraft (A/C) Serial Number']),landingTime,departTime)

        #     Add jobs
            jobs = row['Work that needs to be carried out'].split(',')
            for jID in jobs:
                jID= jID.strip()
                r = work_packages.loc[jID]
                j= job(jID,r['WP description'],a)
                a.add(j)
                self.jobs[a.aircraftID+"."+j.id] =j        
                #  Now add WOs to J
                
                #Add up to 6 work packages
  
                self.addWO("WO1",j,work_orders)
                self.addWO("WO2",j,work_orders)
                self.addWO("WO3",j,work_orders)
                self.addWO("WO4",j,work_orders)
                self.addWO("WO5",j,work_orders)
                self.addWO("WO6",j,work_orders)
                # woRow = work_orders.loc[jID]
                # woID = a.aircraftID+":"+jID+":WO1"
                # wo = workOrder(woID,datetime.timedelta(minutes=int(woRow['WO1'])))
                # woCerts = woRow['WO1_staff'].split(',')
                # for c in woCerts:
                #     wo.addCertification(c)
                # j.addWorkOrder(woID,wo)
              

                
            self.aircraft[a.aircraftID] = a
    
    def addWO(self,woNo,j,work_orders):
        # Add a single WO to job j which is allocated to aircraft a
        a = j.aircraft
        woRow = work_orders.loc[j.id]
        woID = a.aircraftID+":"+j.id+":"+woNo
        try:
            # Catches an exception if this WP is not filled in on the sheet
            duration = datetime.timedelta(minutes=int(woRow[woNo]))
            wo = workOrder(woID,duration,j)
            woCerts = woRow[woNo+'_staff'].split(',')
            for c in woCerts:
                wo.addCertification(c)
            j.addWorkOrder(woID,wo)
            self.WOs[woID] = wo
        except:
            None

    def getUnallocated(self):
        unalloc = 0
        for wo in self.WOs:
            unalloc = unalloc + len(self.WOs[wo].notAllocated)
        return unalloc
    
    def printStaff(self):
        for s in self.staff:
            print(self.staff[s]+"\n")
            
#     def validate(self):
# #         Validate whether the solution held is valid
#         for a in self.aircraft:
#             ac = self.aircraft[a]
#             b = ac.validate()
#             if b != None:
#                 print (a +" "+ b)
            
#         for j in self.jobs:
#             jb = self.jobs[j]
#             b = jb.validate()
#             if b != None:
#                 print(j + " "+ b)
            
#         for s in self.staff:
#             st = self.staff[s]
#             b = st.validate()
#             if b != None:
#                 print(s + " "+ b)
    
    def validate(self):
    #    validate times for WPs and WOs based on a/c

        for acID in self.aircraft:
            ac = self.aircraft[acID]
            wos =[]
            for job in ac.queue:
                for woID in job.workOrders:
                    wos.append(job.workOrders[woID])
            # Sort the WOs into start order 
            wos.sort(key=lambda x: x.getStart())    

            # Now check nothing overlaps
            t = ac.arrival
            prevWO = wos[0]
            for wo in wos:
                if t > wo.start:
                    if prevWO.job == wo.job:
                        errMsg = "Time error: ac= "+acID+"\n"
                        for w in wos:
                            errMsg = errMsg + str(w) +"\n"
                        raise UserWarning(errMsg)
                prevWO = wo
                t = wo.getEnd()

        # for acID in self.aircraft:
        #     ac = self.aircraft[acID]
        #     t = ac.arrival
        #     for job in ac.queue:
        #         for woID in job.workOrders:
        #             wo = job.workOrders[woID]
        #             if t > wo.start:
        #                 raise UserWarning("Time error !! \n"+str(job))
        #             t = wo.getEnd()

        # Valiidate staff times
       
        for sName in self.staff:
           st = self.staff[sName]
           if len(st.woAllocated) > 0:
               # sort  first!
               st.woAllocated.sort(key=lambda x: x.getStart())

               time = st.woAllocated[0].start
               for wo in st.woAllocated:
                   if wo.fixed:
                        if wo.start < time:
                            raise UserWarning("Staff time error !! \n"+str(st))
                   time = wo.getEnd()

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
    
#     def allocate(self, s, woID):
# #         Allocate staff to job
# #         Check qualifications first

#         aID=  woID.split(':')[0]
#         jID=  woID.split(':')[1]
#         woNo = woID.split(':')[2]

#         j= self.jobs[aID+'.'+jID]
#         a= self.aircraft[aID]
#         wo = j.workOrders[woID]

#         if wo.check(s) == False:
#             return False
        
#         # a = j.aircraft
#         # FIX THIS BIT
#         if wo.fixed:
#             if s.timeAvailable <= wo.start: 
#                 wo.allocate(s)
#                 s.timeAvailable = wo.getEnd()
#                 return True
#             else:
# #                 Staff not available in time
#                 return False

 
# #         WP not fixed

#             # wo.allocate(s)
#             # a.addToQueue(j)
#             # s.timeAvailable = wo.getEnd()
#             # return True
            
# #         else:
# # #             Staff avail after 
# #             j.allocate(s)
# #             a.addToQueue(j,time=s.timeAvailable)
# #             s.timeAvailable = j.getEnd()
# #             a.available = j.getEnd()

# #             return True
    def allocate(self,sol):
        #1. Allocate
        for j in sol:#Jobs
            for a in j[1]:
                s = self.staff[a[0]]
                woID = a[1].split('.')[0]#Get WO id
                wo = self.WOs[woID]

                wo.allocate(s)

                job = wo.job
                a = job.aircraft

                if job in a.unscheduledJobs:
                    a.unscheduledJobs.remove(job)
                    a.queue.append(job)


        #2. Add times where possible
        # set default times for wps as follows:
        for acID in self.aircraft:
            ac = self.aircraft[acID]
            t = ac.arrival
            for job in ac.queue:
                job.fixed = False
                for wpID in job.workOrders:
                    wp = job.workOrders[wpID]
                    wp.start = t
                    t = t + wp.duration
                    wp.fixed = False
        
        # 3 .Now check staff times

        # for staff in sol order
        # print("DEBUG START")
        for j in sol:
            for g in j[1]:
                staffID = g[0]
                # print("Staff "+ staffID)
                stff = self.staff[staffID]
                
                if not stff.scheduled:
                    stff.scheduled = True
                # stafftime  =None
            #       for each wo allocated to staff
                    toRemove =[] #Items to remove from stff.woAllocate
                    for wo in stff.woAllocated:
                        # print("WO " +wo.id)
                        if wo.fixed:
                            if wo.start >= stff.timeAvailable: # (after)
                                stff.timeAvailable = wo.getEnd()
                            else: # staff not available in time
                                #     remove staff from Wo 
                                wo.staff.remove(stff)
                                wo.notAllocated.append(stff.certification)
                                # stff.woAllocated.remove(wo)#Can't remove whilst iterating
                                toRemove.append(wo)
                            
                        else : #(wp not fixed)
                        #     if staffTime < wp.startTime
                            if stff.timeAvailable <= wo.start:
                                wo.fixed = True
                                stff.timeAvailable = wo.getEnd()

                            else: #WP commences before staff
                                if wo.canMove():# (TRUE if nothing else is fixed) 
                                    wo.start = stff.timeAvailable
                                    wo.fixed = True
                                    stff.timeAvailable = wo.getEnd()
                                    wo.shunt()
                                else:#   (can't move)
                                    #     remove staff from WP
                                    wo.staff.remove(stff)
                                    wo.notAllocated.append(stff.certification)
                                    # stff.woAllocated.remove(wo)#Can't remove whilst iterating
                                    toRemove.append(wo)
                    # Can't remove from woAllocated whilst iterating, so clean up here
                    for rubbish in toRemove:
                        stff.woAllocated.remove(rubbish)
        

    # def allocate(self,sol):
    #     #1. Allocate
    #     for a in sol:
    #         s = self.staff[a[0]]
    #         woID = a[1].split('.')[0]#Get WO id
    #         wo = self.WOs[woID]

    #         wo.allocate(s)
    #         job = wo.job
    #         a = job.aircraft

    #         if job in a.unscheduledJobs:
    #             a.unscheduledJobs.remove(job)
    #             a.queue.append(job)


    #     #2. Add times where possible
    #     # set default times for wps as follows:
    #     for acID in self.aircraft:
    #         ac = self.aircraft[acID]
    #         t = ac.arrival
    #         for job in ac.queue:
    #             job.fixed = False
    #             for wpID in job.workOrders:
    #                 wp = job.workOrders[wpID]
    #                 wp.start = t
    #                 t = t + wp.duration
    #                 wp.fixed = False
        
    #     # 3 .Now check staff times

    #     # for staff in sol order
    #     # print("DEBUG START")
    #     for g in sol:
    #         staffID = g[0]
    #         # print("Staff "+ staffID)
    #         stff = self.staff[staffID]
            
    #         if not stff.scheduled:
    #             stff.scheduled = True
    #         # stafftime  =None
    #     #       for each wo allocated to staff
    #             toRemove =[] #Items to remove from stff.woAllocate
    #             for wo in stff.woAllocated:
    #                 # print("WO " +wo.id)
    #                 if wo.fixed:
    #                     if wo.start > stff.timeAvailable: # (after)
    #                         stff.timeAvailable = wo.getEnd()
    #                     else: # staff not available in time
    #                         #     remove staff from Wo 
    #                         wo.staff.remove(stff)
    #                         wo.notAllocated.append(stff.certification)
    #                         # stff.woAllocated.remove(wo)#Can't remove whilst iterating
    #                         toRemove.append(wo)
                        
    #                 else : #(wp not fixed)
    #                 #     if staffTime < wp.startTime
    #                     if stff.timeAvailable <= wo.start:
    #                         wo.fixed = True
    #                         stff.timeAvailable = wo.getEnd()

    #                     else: #WP commences before staff
    #                         if wo.canMove():# (TRUE if nothing else is fixed) 
    #                             wo.start = stff.timeAvailable
    #                             wo.fixed = True
    #                             stff.timeAvailable = wo.getEnd()
    #                             wo.shunt()
    #                         else:#   (can't move)
    #                             #     remove staff from WP
    #                             wo.staff.remove(stff)
    #                             wo.notAllocated.append(stff.certification)
    #                             # stff.woAllocated.remove(wo)#Can't remove whilst iterating
    #                             toRemove.append(wo)
    #             # Can't remove from woAllocated whilst iterating, so clean up here
    #             for rubbish in toRemove:
    #                 stff.woAllocated.remove(rubbish)

        
    def getListJobs(self):
#         Return a complete list of jobs
        return list(self.jobs.keys())
    
    def getListWOs(self):
#         Return a complete list of WOs
        wos =[]
        for j in self.jobs.values():
            wos = wos + j.getListWOs()

        return wos
    
    def getListStaff(self):
    #     Retunr a complete list of staff
        return list(self.staff.keys())

# class job:
#     def __init__(self,job_id,description,duration):
#         self.id = job_id
#         self.description = description
#         self.start = 0
#         self.duration = duration
#         self.aircraft = None
#         self.fixed = False
        
# #         requiredSkills is a list of required skills
# # 1 string per requied. If it is an 'OR' then seprate the skills using '|'
#         self.requiredCertifications =[]
    
# #     notAllocated is a list of the skills not allocated. Each time a member of staff is allocated, the skill is 
# # removed from notAllocated
#         self.notAllocated =[]
#         self.staff = []
# #         A list of staff allocated
    
#     def getEnd(self):
#         return self.start +self.duration
    
#     def __str__(self):
#         f = ''
#         if self.fixed:
#             f='*'
#         e= self.getEnd()         
#         na =""
#         for s in self.notAllocated:
#             na = na + s +","
        
#         p =""
#         for s in self.staff:
#             p = p + s.name +","
            
#         return f"{self.id} ({self.start}-{e}) {f} NA={na} S= {p}"

    
#     def reset(self):
#         self.fixed = False
#         self.start =0
#         self.staff = []
#         self.notAllocated = []
#         for sk in self.requiredCertifications:
#             self.notAllocated.append(sk)
    
#     def addCertification(self,skill):
#         self.requiredCertifications.append(skill)
#         self.reset()
        
#     def allocate(self, staffMember):
# #         check if skill is needed
#         found = False
#         i=0
#         for sk in self.notAllocated:
#             if staffMember.certification in sk:
#                 found = True
#                 break
#             i=i+1   
        
#         if found:
#             self.staff.append(staffMember)
#             self.fixed = True
#             staffMember.jobsAllocated.append(self)
#             del self.notAllocated[i]
        
#         return found
    
#     def check(self, staffMember):
# #        Return True if stffMember has the skill needed
#         found = False
#         i=0
#         for sk in self.requiredCertifications:
#             if staffMember.certification in sk:
#                 found = True
#                 break
#             i=i+1   
#         return found
    
#     def validate(self):
#         return None
        