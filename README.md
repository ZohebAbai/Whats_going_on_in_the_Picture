# Whats_going_on_in_the_Picture

AI describing an Image.

While deploying an app on Heroku, these two points are important:

1. **Slug Size:** Heroku provides a max slug size of 500 MB, the total data an app can hold after compression.

2. **Request TimeOut:** Due to large sized pre-trained model the PUT request can show time out and app wont land to result page.

You can also try deploying it in AWS, Paperspace or GCloud but they all charge you per hour for the machine and for the storage, Heroku is better option comparatively.
