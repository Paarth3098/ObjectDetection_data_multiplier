import os
import json
import cv2
import random
import numpy as np

"""
    For every frame:
        1. Selects number of crops (between 1 and 4) to paste in frame.(say n)
        2. Randomly selects n classes from classes list.
        For every class:
            1. Selects a random img from particular class directory and if
                the crop size is smaller than 1/10th of frame then resizes to 1/10th of the frame.
            2. Now get x and y co-ordinates to paste crop such that it does not overlap
                rest of the objects.  
            3. If x and y cordinate lie near the edges then we trim the crop partially 
                and paste it to the edge such that the crop looks like it is partially 
                inside the frame and partially.
                If x and y lie near top and left edge then there is a 50% chance of not getting
                trimmed.
"""

classes = ['1', '2', '3', '4', '5', '6', '7', 'a', 'b', 'c', 'd', 'e', 'x', 'y', 'z']

def number_of_crops():
    rand_num = random.random()
    if rand_num < 0.25:
        return 1
    if rand_num < 0.5:
        return 2
    if rand_num < 0.75:
        return 3
    else:
        return 4

def class_list(no_crops):
    list_of_classes = random.sample(classes, k=no_crops)
    return list_of_classes

def getcrop(crops_dir, cls, frame_shape):
    #gets a crop whose width or height is more than 1/10th of frame
    #if not the resizes
    path = os.path.join(crops_dir, cls)
    img = random.choice(os.listdir(path))
    crop = cv2.imread(os.path.join(path, img))
    if crop.shape[0] < frame_shape[0]/10 and crop.shape[1] < frame_shape[1]/10:
        crop = cv2.resize(crop, dsize=(int(frame_shape[1]/9), int(frame_shape[0]/8)))
    return crop



def get_offset(data, image_id, crop_shape, frame_shape):
    """
        Make a list of all the objects x,y,w,h
        Genrate x_offset and y_offset between 0 and edge of frames.
        If these co-ordinates satisfy the requirement that:
           The distance between x_offset and x is more than width of crop
           and width of object of that particular x.(same for y_offset)

           Random x_offset and y_offset are genrated at max 50 times if the
           requirement is not satisfied then an empty array is returned.
    """
    x, y, w, h = [], [], [], []
    for ann in range(len(data['annotations'])):
        if data['annotations'][ann]['image_id'] == image_id:
            x.append(data['annotations'][ann]['bbox'][0])
            y.append(data['annotations'][ann]['bbox'][1])
            w.append(data['annotations'][ann]['bbox'][2])
            h.append(data['annotations'][ann]['bbox'][3])

    req = False
    count = 0
    x_max = frame_shape[1]*0.85
    y_max = frame_shape[0]*0.85



    while(count <= 50 and req == False):
        x_offset = int(random.uniform(0, x_max))
        y_offset = int(random.uniform(0, y_max))
        count += 1
        for i in range(len(x)):
            if (abs(x_offset - x[i]) >= w[i] and abs(x_offset - x[i]) >= crop_shape[1]) or (abs(y_offset - y[i]) >= h[i] and abs(y_offset - y[i]) >= crop_shape[0]):
                req = True
            else:
                req = False
                break
    if count >= 50:
        offset = []
    else:
        offset = [x_offset, y_offset]
    return  offset

def get_trimmed_crop(crop, frame_shape, x_offset, y_offset):
    """
        If x_offset and y_offset lie near the edges then we cut few portion the crop and
        paste the rest at updated x_offset and y_offset such that it looks like original crop
        is partially inside the frame.
    """
    if x_offset < crop.shape[1]/4 and random.random() < 0.5:
        crop = crop[:, x_offset:crop.shape[1]]
        x_offset = 0
    if y_offset < crop.shape[0]/4 and random.random() < 0.5:
        crop = crop[y_offset:crop.shape[0], :]
        y_offset = 0
    if frame_shape[1] - x_offset < crop.shape[1]:
        crop = crop[:, 0:(frame_shape[1] - x_offset)]
    if frame_shape[0] - y_offset < crop.shape[0]:
        crop = crop[0:(frame_shape[0] - y_offset), :]
    return crop, x_offset, y_offset


def update_json(data, x_offset, y_offset, image_id, crop, category_id, id):
    data['annotations'].append({
        'image_id': image_id,
        'is_crowd': 0,
        'ignore': 0,
        'bbox': [x_offset, y_offset, crop.shape[1], crop.shape[0]],
        'segmentations': [[x_offset, y_offset,
                           x_offset+crop.shape[1], y_offset,
                           x_offset, y_offset+crop.shape[0],
                           x_offset+crop.shape[1], y_offset+crop.shape[0]]],
        'area':crop.shape[0]*crop.shape[1],
        'category_id': category_id,
        'id': id
    })
    return data

def main():
    global id
    with open('/home/neo/data/paarth_augmentation_tests/DATA/train1.json') as f:
        data = json.load(f)
    frame_dir = '/home/neo/data/paarth_augmentation_tests/DATA/cctv_frames'
    crops_dir = '/home/neo/data/paarth_augmentation_tests/DATA/sandbox_crops'
    save_dir = '/home/neo/data/paarth_augmentation_tests/DATA/non_seamless/1'

    for i in range(len(data['annotations'])):
        id = data['annotations'][i]['id']

    for i in range(len(data['images'])):
        print('{} / {}'.format(i, len(data['images'])))
        image_id = i
        file_name = data['images'][i]['file_name']
        frame = cv2.imread(os.path.join(frame_dir, file_name))
        no_crops = number_of_crops() # Number of crops to paste for this particular frames
        list_of_classes = class_list(no_crops)

        for cls in list_of_classes:

            crop = getcrop(crops_dir, cls, frame.shape) #Gets the crop
            offset = get_offset(data, image_id, crop_shape=crop.shape, frame_shape=frame.shape)
            if len(offset) == 0:
                print('no available location found for the crop')
                continue
            x_offset, y_offset = offset[0], offset[1]

            #if x_offset or y_offset lie near the edges then we trim the crop
            crop, x_offset, y_offset = get_trimmed_crop(crop, frame.shape, x_offset, y_offset)

            centre = (int(x_offset + crop.shape[1]/2), int(y_offset + crop.shape[0]/2))
            mask = np.zeros((crop.shape[0], crop.shape[1], 3), np.uint8)
            mask = mask.fill(255.0)
            #Paste the crop at x_offset and y_offset
            frame[y_offset:y_offset + crop.shape[0], x_offset:x_offset + crop.shape[1]] = crop #For normal copy paste
            # frame = cv2.seamlessClone(crop, frame, mask, p=centre, flags=cv2.MIXED_CLONE) #for seamless cloning
            data = update_json(data, x_offset, y_offset, image_id, crop, cls, id)
            id += 1
        cv2.imwrite(os.path.join(save_dir, file_name), frame)
    out_file = open("non_seamless_1.json", "w")
    json.dump(data, out_file, indent=4)



if __name__ == '__main__':
    main()