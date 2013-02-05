########################################################################
# Author: Amogh Tolay
# Date: 24th Jan, 2013
# This is an idea, NOT for deployment
# The algorithm is outlined below:
# 	Contrast the image and perform edge detection using canny detector
#	Then identify contour sequence using Hu moments
# 	and reduce problem to simple sequence matching problem
########################################################################
# TODO:
# 1. Change the top5Match function as follows:
#	Ignore nearby matches, apply a threshold and take matches above that only
#	Nearby peaks should be treated as one  peak
# 2. Change the approximateLetters function as follows:
#	Apply DP to it to take max elems matching:
#	http://stackoverflow.com/questions/3243234/algorithm-to-find-the-maximum-sum-in-a-sequence-of-overlapping-intervals
########################################################################
import cv
import sys
import numpy
import time
import heapq

def avg(m, i, j):
  '''
  This function finds the average value that should be stored at a pixel.
  The input is the matrix (cvmat) of a grayscale image and the index at which
  the average is required. 
  '''
  sumNeighbours = m[i,j]
  count = 1

  if i > 0:
    sumNeighbours += m[i - 1, j]
    count += 1

    if j > 0:
      sumNeighbours += m[i - 1, j - 1]
      count += 1
    if j < m.cols - 1:
      sumNeighbours += m[i - 1, j + 1]
      count += 1
  
  if i < m.rows - 1:
    sumNeighbours += m[i + 1, j]
    count += 1

    if j > 0:
      sumNeighbours += m[i + 1, j - 1]
      count += 1
    if j < m.cols - 1:
      sumNeighbours += m[i + 1, j + 1]
      count += 1

  if j > 0:
    sumNeighbours += m[i, j - 1]
    count += 1

  if j < m.cols - 1:
    sumNeighbours += m[i, j + 1]
    count += 1

  return (sumNeighbours * 1.0 / count)

def averageMat(m):
  '''
  Function blurs the image by replacing the value at every pixel by the average
  of the value of the pixel and its neighbours.

  The input matrix should be of type cvmat of a grayscale image.
  '''
  t = cv.CreateMat(m.rows, m.cols, m.type)
  for j in range(m.cols):
    for i in range(m.rows):
      t[i,j] = avg(m, i, j)
  
  return t

def top5Match( m, letter, w ):
	'''
	Returns a list of tuples in ths format:
	(value, (startLoc, endLoc), letter)
	this is done for each letter, and returns a list for one letter
	which has been passed as the argument
	'''
	####################################################################
	# TODO:
	# Change this function to ensure that only far away entries are
	# returned. For eg. if there's an A at location 50,51,52 and 96,
	# then the A will be at location max(val at 50,51,52) and then the
	# A at 96th position
	####################################################################
	
	'''
	tempList = []
	for i in range(m.rows):
		for j in range(m.cols):
			tempList.append( (m[i,j], (j,j+w), letter) )
	top5elems = heapq.nsmallest(5,tempList, key=lambda element: element[0])
	return top5elems
	'''
def approximateLetters( allLetters ):
	'''
	Returns the string that is the possible solution to the captcha
	This is obtained by simply dividing the entire list into five parts
	on the spatial front and then getting best match
	'''
	# IMPORTANT
	# The code written below is a very naive cuts (equal sized cuts)
	# this probably won't work and needs to be modified to increase acc
	# This can be done later in such a way:
	# 	Take 5 subsets such that they are mutually exclusive and their
	#	sum is maximum. No other set of 5 would belong which would be
	#	mutex as well having a greater sum
	
	# DP solution is as follows:
	#best = []
	#best[0] = 0
	tempLetter1 = [(1, (0,0), 'notFound')]
	tempLetter2 = [(1, (0,51), 'notFound')]
	tempLetter3 = [(1, (0,101), 'notFound')]
	tempLetter4 = [(1, (0,151), 'notFound')]
	tempLetter5 = [(1, (0,201), 'notFound')]
	for (value, (startLoc, endLoc), letter) in allLetters:
		if startLoc < 50:
			tempLetter1.append( (value, (startLoc, endLoc), letter) )
		elif startLoc < 100:
			tempLetter2.append( (value, (startLoc, endLoc), letter) )
		elif startLoc < 150:
			tempLetter3.append( (value, (startLoc, endLoc), letter) )
		elif startLoc < 200:
			tempLetter4.append( (value, (startLoc, endLoc), letter) )
		else:
			tempLetter5.append( (value, (startLoc, endLoc), letter) )
	# Now I have divided the list into 5 equal parts
	# now choose max matching letter from each part
	ans = ''
	ans = min( tempLetter1, key=lambda x:x[0] )[2] + ' ' + min( tempLetter2, key=lambda x:x[0] )[2] + ' ' + min( tempLetter3, key=lambda x:x[0] )[2] + ' ' + min( tempLetter3, key=lambda x:x[0] )[2] + ' ' + min( tempLetter4, key=lambda x:x[0] )[2] + min( tempLetter5, key=lambda x:x[0] )[2]
	
	return ans
	
def main():
	captchaImage = sys.argv[1]
	grayImg = cv.LoadImage(captchaImage, cv.CV_LOAD_IMAGE_GRAYSCALE)
	W,H = cv.GetSize(grayImg)

	mat = cv.GetMat(grayImg)
	threshImg = cv.CreateMat(mat.rows, mat.cols, mat.type)
	tempImg = averageMat(averageMat(averageMat(mat)))
	cv.Threshold(tempImg, threshImg, 210, 255, 0)
	cv.SaveImage(captchaImage + "_thresh.png", threshImg)
	# Thresholding complete, instead of increase contrast which might be slower
	'''
	#The following is a code for canny edge detection
	#There isn't much use of canny edges here, but just in case I require it later
	
	canny = cv.CreateMat( mat.rows, mat.cols, mat.type)
	threshold1 = 255
	threshold2 = 255
	cv.Canny( threshImg, canny, threshold1, threshold2 )
	cv.Threshold(canny, canny, 210, 255, 1)
	cv.SaveImage(captchaImage + "_edge.png", canny)
	'''

	# Trying template matching with built-in function
	letterImgValues = []
	# possibleLetters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9']
	possibleLetters = ['A','B','C','D','E','F','G','H','K','M','N','P','R','S','T','V','W','X','Y','Z','2','3','4','5','6','7','8','9']
	# possibleLetters = ['A']
	for letter in possibleLetters:
		templateName = '../segmented/'+letter+'/'+letter+'.png'
		template = cv.LoadImage(templateName, cv.CV_LOAD_IMAGE_GRAYSCALE)
		w,h = cv.GetSize(template)
		width = W-w+1
		height = H-h+1
		result = cv.CreateImage((width, height), 32, 1)
		# Temporary! Remember to remove the following lines
		threshImg = mat		
		# Remove till here
		cv.MatchTemplate(threshImg, template, result, cv.CV_TM_SQDIFF_NORMED)
		minVal,maxVal,minLoc,maxLoc = cv.MinMaxLoc(result)
		
		matTemplate = cv.GetMat(result)
		#print "Best location is at", minLoc, "and matching is: ", minVal
		letterImgValues = letterImgValues + top5Match(matTemplate, letter, w)
	
	#print "All letters top5"
	print letterImgValues
	ans = approximateLetters(letterImgValues)
	print ans

startTime = time.time()
main()
print "It took ", time.time()-startTime, " to execute script"
