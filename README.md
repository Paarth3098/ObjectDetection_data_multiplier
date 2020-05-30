# ObjectDetection_data_multiplier
This Repo will add more objects to your current dataset.
The perfect use case for this repo is:
          1. If your dataset has most of its object at same co-ordinates and your model has learned to look
             at those places only.
             So using this repo you can add objects to random places in your current data to make the model 
             more ROBUST.
          2. To Increase the data of Minority classes.
    So far i have been able to think about these two only....
    
    
    
# Way This Repo Works
It paste crops seamlessly (if you want) at random position for every image in your dataset from crop folder.
     
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

# CROP FOLDER
      The crop folder should contain hand picked crops which you need to add to your images, It can be objects  
      which your model finds hard to identify.
      
      Inside this crop folder there should be folders for every class with the name of class itself and particular
      crop should be placed inside its folder.
      
      
V2 of this repo is going to come soon.....one in which you won't need the crop folder or any thing else.....
