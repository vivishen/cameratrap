import sensor
import image
import lcd
import KPU as kpu

lcd.init()
#sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)
task = kpu.load(0x00200000) # you need put model(face.kfpkg) in flash at address 0x300000
# task = kpu.load("/sd/face.kmodel")
anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
a = kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)
while(True):
    img = sensor.snapshot()
    print(img)
  
    # check if this works: img.save(home/Desktop/CameraTrapImages/img.png)
    code = kpu.run_yolo2(task, img)
    if code:
        for i in code:
            a = img.draw_rectangle(i.rect())
            print(True)
    a = lcd.display(img)
a = kpu.deinit(task)
