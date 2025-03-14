import os
import cv2
import json
import argparse

# boolean variables
classname = "class"
imagedir = "."
labeldir = "."
newlabeldir = "."
vislabeldir = "."
makelab = 0
jsonf = ""

# initiate parser
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--label_json", help="json file for making labels")
parser.add_argument("-m", "--make_labels", help="new label directory")
parser.add_argument("classname", metavar="classname", type=str, help="class name")
parser.add_argument("imagedir", metavar="imageDIR", type=str, help="directory with original images")
parser.add_argument("labeldir", metavar="labelDIR", type=str, help="directory with generated labels")
parser.add_argument("vislabeldir", metavar="vislabelDIR", type=str, help="directory to put images with bounding boxes")
args = parser.parse_args()
if args.label_json:
    print("Making labels...")
    makelab = 1
    jsonf = args.label_json
if args.make_labels:
    print("Checking labels...")
    makelab = 2
    newlabeldir = args.make_labels + "/"
    if "//" in newlabeldir:
        newlabeldir = args.make_labels
classname = args.classname
imagedir = args.imagedir + "/"
if "//" in imagedir:
    imagedir = args.imagedir
labeldir = args.labeldir + "/"
if "//" in labeldir:
    labeldir = args.labeldir
vislabeldir = args.vislabeldir + "/"
if "//" in vislabeldir:
    vislabeldir = args.vislabeldir

print("image: " + imagedir)
print("label: " + labeldir)
print("vislabel: " + vislabeldir)

# create labels from output file
if makelab == 1:
    f = open(jsonf, "r")
    js = json.loads(f.read())

    for i in js["images"]:
        namel = i["file"].split("/")
        namell = namel[len(namel)-1].split(".")
        namell[len(namell)-1] = "txt"
        name = (".").join(namell)
        label = open(labeldir + name, "w")
        for d in i["detections"]:
            if d["category"] == "1":
                midx = str(float(d["bbox"][0]) + float(d["bbox"][2])/2)
                midy = str(float(d["bbox"][1]) + float(d["bbox"][3])/2)
                label.write(classname + " " + midx + " " + midy + " " + str(d["bbox"][2]) + " " + str(d["bbox"][3]) + "\n")

        label.close()
    f.close()    

# create visualizations for labels
for imgname in os.listdir(imagedir):
    print("Drawing bounding box for image " + imgname + " ...")
    if os.path.exists(vislabeldir + imgname):
        continue
    extl = imgname.split(".")
    ext = extl[len(extl)-1]
    fname = imgname.strip(ext) + "txt"
    img = cv2.imread(imagedir + imgname)
    h, w, c = img.shape
    if h > 1000 or w > 1000:
        img = cv2.resize(img, None, fx=0.3, fy=0.3)
        h, w, c = img.shape
    label = open(labeldir + fname, "r")
    for line in label.readlines():
        name, midx, midy, wid, hei = line.split()
        midx, midy, wid, hei = float(midx), float(midy), float(wid), float(hei)
        x1 = int(midx*w - wid*w/2)
        x2 = int(midx*w + wid*w/2)
        y1 = int(midy*h - hei*h/2)
        y2 = int(midy*h + hei*h/2)
        cv2.rectangle(img, (x1,y1), (x2,y2), (0,0,255))
        if makelab == 2:
            newlabel = open(newlabeldir + fname, "a")
            cv2.imshow("Image", img)
            cv2.waitKey(200)
            if input("Is this wrong? ") != "y":
                newlabel.write(line)
                cv2.imwrite(vislabeldir + imgname, img)
            newlabel.close()
        else:
            cv2.imwrite(vislabeldir + imgname, img)
    label.close()

