# SnapFFT
SnapFFT - FFT of any image quickly like taking a snapshot.

This is a hobby project I made for myself since I work a lot with atomic resolution, electron microscopy images where checking FFT is needed frequently. I have used a lot of help from ChatGPT for this. 

These are following capabilities - 

1. Load, paste or drag & drop any image, generate an FFT by drawing a rectangle over the image.
2. Provide calibration scale for image (real space), which is automatically supplied for the FFT (reciproval space).
3. Draw a line over the image or FFT to measure the distances.  !! The scale in the FFT image depends on the size of the rectangle. So draw a rectangle over the full image for more accurate measurements in the reciprocal space. !!
4. Change colormap of both the image and the FFT.
5. Adjust brightness, contrast and gamma for both the image and FFT.
6. Finally, copy the image or the FFT for your use. 
