import sys
print "Script running on Python", sys.version
print ""

import numpy
from scipy import misc


# -----


def load_image(filename):
	return misc.imread(filename)


def save_image(filename, img):
	return misc.imsave(filename, img)


def flip_image(img):
	return numpy.transpose(img)


def convert_image_to_grayscale(img):
	return numpy.dot(img[...,:3], [0.299, 0.587, 0.114])


# -----


# not used because "that's too easy"
def calc_energy_function_numpy(img):
	dx, dy = numpy.gradient(img)
	energy = abs(dx) + abs(dy)
	return energy


def calc_energy_function(img):
	energy = numpy.zeros(shape=img.shape)
	height, width = energy.shape

	for r in range(height):

		for c in range(width):

			if c==0:
				dx = img[r][c+1] - img[r][c]
			elif c==width-1:
				dx = img[r][c]   - img[r][c-1]
			else:
				dx = img[r][c+1] - img[r][c-1]
				
			if r==0:
				dy = img[r+1][c] - img[r][c]
			elif r==height-1:
				dy = img[r][c]   - img[r-1][c]
			else:
				dy = img[r+1][c] - img[r-1][c]
				
			energy[r][c] = abs(dx) + abs(dy)
			
	return energy


def calc_vertical_seam(energy):
	# == INIT ==
	height, width = energy.shape	
	# intialize working array with zeros
	cost = numpy.zeros(shape=energy.shape)
	# initialize first row of cost with values directly from energy function
	for c in range(width):
		cost[0][c] = energy[0][c]
	
	# == CALCULATE COST ==
	# for all other rows (all rows but the first we just initialized)
	for r in range(1, height):
		# edge case: first column is calculated from first and second columns only
		cost[r][0] = energy[r][0] + min(cost[r-1][0], cost[r-1][1])
		# general case: non-edge columns
		for c in range(1, width-1):
			# calculate from current column and the ones left and right of it
			cost[r][c] = energy[r][c] + min(cost[r-1][c-1], cost[r-1][c], cost[r-1][c+1])
		# edge case: last column is calculated from last and second-to-last columns only
		cost[r][width-1] = energy[r][width-1] + min(cost[r-1][width-2], cost[r-1][width-1])
		
	# DEBUG: export costs array
	# numpy.savetxt('cost.txt', cost, fmt='%4.0f')
	
	# == TRACE SEAM ==
	
	# find smallest value in the last row
	lowest_value = 999999999
	lowest_index = 0
	for c in range(width):
		if cost[height-1][c] < lowest_value:
			lowest_value = cost[height-1][c]
			lowest_index = c
	# DEBUG: show result
	# print "lowest value: ", lowest_value, " @ index ", lowest_index
	
	# init seam object
	seam = [(height-1, lowest_index)]
	
	# find best path in the other rows, one row up at a time
	for r in range(height-2, -1, -1): # first -1: go until 0; second -1: decrease index in each iteration
		# edge case: on the very left, only the first and second column are considered
		if lowest_index == 0:
			if cost[r][lowest_index+1] < cost[r][lowest_index]:
				lowest_index += 1
			#else lowest_index unchanged
		# edge case: on the very right, only the last and second-to-last columns are considered
		elif lowest_index == width-1:
			if cost[r][lowest_index-1] < cost[r][lowest_index]:
				lowest_index -= 1
			#else lowest index unchanged
		# general case: consider the current column and the ones left and right of it
		else:
			candidates = [cost[r][lowest_index-1], cost[r][lowest_index], cost[r][lowest_index+1]]
			if candidates[0] < candidates[1] and candidates[0] < candidates[2]:
				lowest_index -= 1
			elif candidates[2] < candidates[0] and candidates[2] < candidates[1]:
				lowest_index += 1
			#else lowest_index unchanged
		
		# add found point to seam object
		seam.append((r, lowest_index))
	
	# == DONE ==
	return seam


def mark_vertical_seam(img, seam):
	# set color of each pixel that is part of the seam to white
	for p in seam:
		img[p[0]][p[1]] = 255
	return img


def remove_vertical_seam(img, seam):
	# init
	height, width = img.shape
	imgsmall = numpy.ndarray(shape=(height, width-1))

	# go through all rows
	for r in range(height):
		shifting = False
		for c in range(width-1):
			# if the current pixel is the current row's seam pixel (there's always exactly 1 in each row)...
			if (r,c) in seam:
				# ...remember that
				shifting = True
			# if we're past the seam pixel, copy the pixel from 1 step further right
			if shifting:
				imgsmall[r][c] = img[r][c+1]
			# otherwise just copy from the very same location
			else:
				imgsmall[r][c] = img[r][c]
	return imgsmall


def remove_vertical_seams(img, count, is_fake_horizontal=False):
	target_width = img.shape[1] - count
	while img.shape[1] > target_width:
		if is_fake_horizontal:
			print "Reducing to ", img.shape[0], " x ", img.shape[1]-1
		else:
			print "Reducing to ", img.shape[1]-1, " x ", img.shape[0]
		energy = calc_energy_function(img)
		seam = calc_vertical_seam(energy)
		# DEBUG: show seam in image
		# img = mark_vertical_seam(img, seam)
		# save_image('seam.png', img)
		img = remove_vertical_seam(img, seam)
	return img


def remove_horizontal_seams(img, count):
	img = flip_image(img)
	img = remove_vertical_seams(img, count, True)
	img = flip_image(img)
	return img


def remove_seams(img, k, l):
	height, width = img.shape
	target_width = width - l
	target_height = height - k
	print "Image is      ", width, " x ", height
	print "Image will be ", target_width, " x ", target_height
	print ""
	
	print "Reducing width"
	img = remove_vertical_seams(img, l)
	print ""
	
	print "Reducing height"
	img = remove_horizontal_seams(img, k)
	print ""
	
	return img


def main(argv):
	"""Takes four arguments:
	
	1. filename of the image to be seam carved
	2. number k of horizontal seams to be removed
	3. number l of vertical seams to be removed
	4. filename the seam carved image should be written to
	
	For example:
	  tower.png 6 94 tower-seamcarved.png
	"""
	
	img = load_image(argv[1])
	print "Image ", argv[1], " loaded"
	img = convert_image_to_grayscale(img)
	print "Converted to grayscale"
	print ""
	img = remove_seams(img, int(argv[2]), int(argv[3]))
	print "Removed ", argv[2], " horizontal and ", argv[3], " vertical seams"
	save_image(argv[4], img)
	print "Saved image as ", argv[4]
	print ""
	print "DONE"
	print ""


if __name__ == '__main__':
	# DEBUG: always use test image and settings
	# argv = ["seamcarving.py", "tower.png", 6, 94, "tower-seamcarved.png"]
	main(sys.argv)
