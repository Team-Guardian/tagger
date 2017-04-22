import xml.etree.ElementTree as ET
import numpy

# gets the intrinsic matrix values from the xml file, ready to toss into numpy later (as a list of lists)
def getIntrinsicMatrix(intrinsic_matrix_filename):
    intrinsic_matrix_path = './intrinsic_matrices/' + intrinsic_matrix_filename
    tree = ET.parse(intrinsic_matrix_path)  # parse the intrinsic matrix xml file
    root = tree.getroot()
    intrinsic_matrix = None

    if tree is not None:
        for resolution in root.findall('resolution'):
            y = float(resolution.get('y'))  # gets the y attribute from the resolution tag
            x = float(resolution.get('x'))  # gets the x attribute from the resolution tag
            camera = resolution.get('camera')  # getting the camera attribute from the resolution tag
            focalLength = float(resolution.get('fl'))  # getting the focal length 'fl' attribute from the resolution tag

            # if camera == self.cameraModel and y == self.height and x == self.width and focalLength == self.focalLength:

            myArray1 = []  # stores the first three values
            myArray2 = []  # stores the second three values
            myArray3 = []  # the last three values
            finalArray = []  # the final output that numpy wants

            for matrixValues in resolution.findall('a'):
                t = float(matrixValues.text)
                myArray1.append(t)

            for matrixValues in resolution.findall('b'):
                t = float(matrixValues.text)
                myArray2.append(t)

            for matrixValues in resolution.findall('c'):
                t = float(matrixValues.text)
                myArray3.append(t)

            finalArray.append(myArray1)  # add the three arrays into the finalArray which numpy wants
            finalArray.append(myArray2)
            finalArray.append(myArray3)
            intrinsic_matrix = numpy.array(finalArray)

    return intrinsic_matrix