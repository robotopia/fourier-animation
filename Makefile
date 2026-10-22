NFRAMES = 2000
NPOINTS = 30000
FRAMES = $(shell seq -w 0 $(shell echo $$(($(NFRAMES) - 1)))) # = {0 .. (NFRAMES - 1)}
PNGS = $(patsubst %,frames/frame_%.png,$(FRAMES))

.SECONDARY:

anim.mp4: $(PNGS)
	echo $(NFRAMES)
	ffmpeg -framerate 25 -i frames/frame_%04d.png -c:v libx264 -crf 15 -preset slow -pix_fmt yuv444p $@

frames/frame_%.png: make_fft.py Fourier.jpg
	@mkdir -p $(dir $@)
	python $^ $* $@ --nframes $(NFRAMES) --npoints $(NPOINTS) --accel-param 0.0033

clean:
	$(RM) frames/frame_*.png anim.mpg
