# ObjectDetection_data_multiplier
This Repo will add more objects to your current dataset.
The perfect use case for this repo is:
          1. If your dataset has most of its object at same co-ordinates and your model has learned to look
             at those places only.
             So using this repo you can add objects to random places in your current data to make the model 
             more ROBUST.
          2. To Increase the data of Minority classes.
    So far i have been able to think about these two only....
    
    
    
***Way This Repo Works***
It paste crops at random position for every image in your dataset from crop folder.

# CROP FOLDER
      The crop folder should contain hand picked crops which you need to add to your images, It can be objects  
      which your model finds hard to identify.
      
      Inside this crop folder there should be folders for every class with the name of class itself and particular
      crop should be placed inside its folder.
      
      
V2 of this repo is going to come soon.....one in which you wont need the crop folder or any thing else.....
