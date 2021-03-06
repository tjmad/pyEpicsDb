import re

#read spread sheet tab delimited as csv file. stores spread sheet rows and 
#headings, dig. firmware version.
#can get selected columns, can find rows based on reg exp. 
#can return data as dict, or assoc. array, ex:
#r=getColsD([3,4,5])
##to get row 34 just col, Register Name:
#print r[34]['Register Name]

#to load the module for use
#execfile('speadsheet.py')
#ss=spreadsheet()
#ss.readTabText('MDRM.csv')

#available fields
#ss.headings
#ss.rows
#ss.verdata
#ss.verheadings

class spreadsheet:

	def __init__(self):

		self.delimiter='\t'
		self.rows=[]
		self.headings=[]
		self.verheadings=[]
		self.verdata=[]
		self.verdataD=dict()
		self.s_notwhite=re.compile(r'\S');
		
		self.s_inquotes=re.compile(r"(?<=\").*(?=\")")
		
		self.defheadings=[
			'Comment', 
			'Address', 
			'Register Name', 
			'Register Mode', 
			'Function', 
			'Access Type', 
			'Address', 
			'Bit', 
			'Field Mode', 
			'EPICS type', 
			'EPICS units', 
			'Database Group', 
			'Initial Value', 
			'Register Name', 
			'Software field name',
			'Bitfield Sub-Descriptor', 
			'Human field name', 
			'Field Description for database', 
			'a', 
			'b', 
			'c', 
			'd', 
			'e', 
			'LW Type', 
			'Control Type', 
			'Register X-Y base', 
			'Control X-offset', 
			'Control Y-offset', 
			'f']
		self.headings = list(self.defheadings);


	def write(self,filename):


		fileobj=open(filename,'w')

		#write some comments
		line = '#spreadsheet generated by python scripts- Tim Madden\n'
		fileobj.write(line)

		line='\n'
		fileobj.write(line)
		fileobj.write(line)
		fileobj.write(line)
		fileobj.write(line)
		fileobj.write(line)

		line = '%HDR		Human Documentation Area\n'
		fileobj.write(line)
		
		#write the headings
		line = ''
		for h in self.headings:
			line=line+'\"%s\"%s'%(h,self.delimiter)

		fileobj.write(line+'\n')
		
		#write the rows
		for r in self.rows:
			line=''
			for c in r:
				line=line+'\"%s\"%s'%(c,self.delimiter)
			fileobj.write(line+'\n')


		fileobj.close()

	
	def readTabText(self,fn):
		self.read(fn)	
	
	#readTabText('MDigMap.txt')
	def read(self, filename):
		fileobj=open(filename)
		
		#read col headings
		#We look for the lint starting with "Comment"
		
		line=fileobj.readline();
		
		while(re.search("%HDR",line)==None):
			vh=re.search('%VerHeadings',line);
			vd=re.search('%VerData',line);
			
			if (vh!=None):
				self.verheadings=line.split(self.delimiter)
				
			if (vd!=None):
				self.verdata=line.split(self.delimiter)
					
			line = fileobj.readline();
		
		
		
		#we should have verdata and verheaadings, make a dictionary out of them
		for k in range(len(self.verheadings)):
			self.verdataD[self.verheadings[k].replace('\"','')]=self.verdata[k].replace('\"','')
		
		#line after %HDR is the header row
		line=fileobj.readline();
		
		#file is tabbed
		self.headings = line.split(self.delimiter);
		
		
		
		
		#remove quotes from the headings. SS file has everyting quoted
		for k in range(len(self.headings)):
			q=self.s_inquotes.search(self.headings[k])
			if q!=None:
				self.headings[k] = q.group(0)
				
				
		
		
		notdone = True
		
		self.rows=[]

		N=0
		#while(notdone and N<675):
		while(notdone):
			N=N+1
			
			
			line = fileobj.readline();
			if len(line)==0:
				print "EOF"
				break;
					

			#file is tabbed
			row = line.split(self.delimiter);
			#remove quotes from the row. SS file has everyting quoted
			for k in range(len(row)):
				q=self.s_inquotes.search(row[k])
				if q!=None:
					row[k] = q.group(0)

			self.rows.append(row)	
			
		fileobj.close()
		

	#provide a list of cols to get into a new row list
	def getCols(self,cols):
		newrows=[]
		for r in self.rows:
			nr=[]
			for k in range(len(cols)):
				nr.append(r[cols[k]])
				
			newrows.append(nr)
		
		
		return(newrows);
			

	#get selected cols, cols is [1,2,3,4,7 etc]. ret dict() using headings 
	def getColsD(self,cols):
		newrows=self.delEmptyRows(self.getCols(cols))
		newdict=[]
		for r in newrows:
			#make a dict out of the row so we dont' have to deal with indices.
			#use headings from the ss file.
			#use headings from cols we got from the ss.
			rdict=dict()
			index=0
			for c in cols:
				rdict[self.headings[c]]=r[index]				
				index=index+1;
				
				
			newdict.append(rdict)	
		return(newdict);
						


	def getRegColsD(self):
		mycols = [1,2,3,4]
		addr_rows=self.getColsD(mycols)
		return(addr_rows)


	def getUserColsD(self):
		mycols = range(5,21)
		pv_rows=self.getColsD(mycols)
		return(pv_rows)



	def delEmptyRows(self,oldrows):
		newrows=[]
		for o_r in oldrows:
			empty=True
			for c in o_r:
			
				if c==None:
					print 'XXXXX'
					print o_r


				elif len(c)>0:
					if self.s_notwhite.search(c)!=None:
						empty=False
				
				
					
			
			if empty==False:
				newrows.append(o_r)
				
		return(newrows)
		
		
	
	# return only rows whols col search the rexp
	def find(self,oldrows,col,rexp):
		newrows=[]
		for o_r in oldrows:
			s=re.search(rexp,o_r[col])
			if s!=None:
				newrows.append(o_r)
				
		return(newrows)
	
	
	def createRegRowD(self):
		r=dict()
		for k in [1,2,3,4]:
			#r[self.defheadings[k]]='_%d_'%(k)
			r[self.defheadings[k]]=''

		return(r)



	def createUserRowD(self):
		r=dict()
		for k in range(5,21):
			#r[self.defheadings[k]]='_%d_'%(k)
			r[self.defheadings[k]]=''
		
		return(r)

	def addRegRowD(self,rd):
		r=[]

		for k in range(len(self.defheadings)):
			r.append('')


		
		for k in [1,2,3,4]:
			r[k] = rd[self.defheadings[k]]
		

		self.rows.append(r)


	def addUserRowD(self,rd):
		r=[]

		for k in range(len(self.defheadings)):
			r.append('')

		for k in range(5,21):
			r[k] = rd[self.defheadings[k]]
		

		self.rows.append(r)


	def clear(self):
		self.rows=[]
		self.headings=list(self.defheadings)
		

			
			
			
