# SnapFFT
SnapFFT - FFT of any image quickly like taking a snapshot.

This is a hobby project I made for myself since I work a lot with atomic resolution, electron microscopy images where checking FFT is needed frequently. Please feel free to use it if you want to use it for a quick FFT check but always recheck the measurements.

These are the capabilities - 

1. Load, paste or drag & drop any image, generate an FFT by drawing a rectangle over the image.
2. Provide calibration scale for image (real space), which is automatically supplied for the FFT (reciprocal space).
3. Draw a line over the image or FFT to measure the distances.  
4. Change colormap of both the image and the FFT.
5. Adjust brightness, contrast and gamma for both the image and FFT.
6. Finally, copy the image or the FFT for your use.


Drawing a rectangle - 
![drawing a box](https://github.com/user-attachments/assets/cc46b80b-eda7-4ee8-8ba8-ab036ec2da5f)



Drawing a line on the image - 
![Drawing line on image](https://github.com/user-attachments/assets/8582428e-1223-463b-a9f3-f7433130fe94)




Drawing a line on the generated FFT - 
![showing FFT distances](https://github.com/user-attachments/assets/2a3f2d10-60d0-48ef-a0b0-81e3e7d38705)


Reading the measurements
![with labels](https://github.com/user-attachments/assets/305cef1b-9d38-4f73-9f71-0055bd0de88a)



Different Color maps
![Different Color maps](https://github.com/user-attachments/assets/51042307-7ca6-4f83-acab-a49bfa91274f)


Using and Installing. 
1. Option-1 : Either run the python file directly or using any interpreter. It is built to be compatible with Python version 3.9.1.
2. Option 2 : Download the folder "SnapFFT.exe" and "_internal" in on folder and run the .exe. files. Make sure the following packages are installed -

numpy	                    pip install numpy	
cv2	                      pip install opencv-python	
tkinter	                  (built-in)	Comes with Python standard library
tkinterdnd2	              pip install tkinterdnd2
matplotlib	              pip install matplotlib	
PIL                       pip install pillow	
win32clipboard, win32con	pip install pywin32
