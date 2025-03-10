# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

r"""A demo for object detection.

For Raspberry Pi, you need to install 'feh' as image viewer:
sudo apt-get install feh

Example (Running under python-tflite-source/edgetpu directory):

  - Under the parent directory python-tflite-source.

  - Face detection:
    python3.5 edgetpu/demo/object_detection.py \
    --model='test_data/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite' \
    --input='test_data/face.jpg'

  - Pet detection:
    python3.5 edgetpu/demo/object_detection.py \
    --model='test_data/ssd_mobilenet_v1_fine_tuned_edgetpu.tflite' \
    --label='test_data/pet_labels.txt' \
    --input='test_data/pets.jpg'

'--output' is an optional flag to specify file name of output image.
"""

import argparse
import platform
import subprocess
from edgetpu.detection.engine import DetectionEngine
from PIL import Image
from PIL import ImageDraw


# Function to read labels from text files.
def ReadLabelFile(file_path):
  with open(file_path, 'r', encoding="utf-8") as f:
    lines = f.readlines()
  ret = {}
  for line in lines:
    pair = line.strip().split(maxsplit=1)
    ret[int(pair[0])] = pair[1].strip()
  return ret


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--model', help='Path of the detection model.', required=True)
  parser.add_argument('--label', help='Path of the labels file.')
  parser.add_argument( '--input', help='File path of the input image.', required=True)
  parser.add_argument('--output', help='File path of the output image.')
  parser.add_argument('--conf', help='confidence threshold', required=True)
  args = parser.parse_args()

  if not args.output:
    output_name = 'object_detection_result.jpg'
  else:
    output_name = args.output

  # Initialize engine.
  engine = DetectionEngine(args.model)
  labels = ReadLabelFile(args.label) if args.label else None
  if float(args.conf) > 1.0:
      conf = float(args.conf)/100
  else:
      conf = float(args.conf)

  # Open image.
  img = Image.open(args.input)
  draw = ImageDraw.Draw(img)

  # Run inference.
  ans = engine.DetectWithImage(img, threshold=conf, keep_aspect_ratio=True,
                               relative_coord=False, top_k=10)

  # Display result.
  if ans:
    for obj in ans:
      print ('-----------------------------------------')
      if labels:
        print(labels[obj.label_id])
      print ('score = ', obj.score)
      box = obj.bounding_box.flatten().tolist()
      print ('box = ', box)
      # Draw a rectangle.
      draw.rectangle(box, outline='red')
    img.save(output_name)
    if platform.machine() == 'x86_64':
      # For gLinux, simply show the image.
      img.show()
    elif platform.machine() == 'armv7l':
      # For Raspberry Pi, you need to install 'feh' to display image.
      subprocess.Popen(['feh', output_name])
    else:
      print ('Please check ', output_name)
  else:
    print ('No object detected!')

if __name__ == '__main__':
  main()
